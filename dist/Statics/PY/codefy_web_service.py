#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodefyERP Web Service Layer
Wraps CodefyAnalyzer (v11.3.1) for Flask API consumption.
Provides analysis and export operations with JSON-safe serialization
and secure temp file handling.
"""

import os
import sys
import json
import time
import tempfile
import shutil
import atexit
import threading
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    'codefy_analyzer',
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'CodefyExcelAnalyzer_V11.3.1.py'),
)
_analyzer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_analyzer)
CodefyAnalyzer = _analyzer.CodefyAnalyzer
SettingsManager = _analyzer.SettingsManager
ColumnController = _analyzer.ColumnController

ALLOWED_EXTENSIONS = {'.xlsx', '.xlsm', '.csv', '.tsv', '.txt'}

EXPORT_FORMATS = {
    'fixed_xlsx':   {'ext': '.xlsx', 'method': 'export_fixed'},
    'fixed_csv':    {'ext': '.csv',  'method': 'export_fixed_csv'},
    'issues_xlsx':  {'ext': '.xlsx', 'method': 'export_issues_excel'},
    'issues_csv':   {'ext': '.csv',  'method': 'export_issues_csv'},
    'issues_json':  {'ext': '.json', 'method': 'export_issues_json'},
    'issues_txt':   {'ext': '.txt',  'method': '_export_issues_txt'},
    'report_html':  {'ext': '.html', 'method': 'export_html_report'},
    'report_txt':   {'ext': '.txt',  'method': '_export_report_txt'},
}

_CLEANUP_TRACKED = []
_CLEANUP_LOCK = threading.Lock()


def _json_safe(obj):
    """Recursively convert any object to a JSON-safe representation."""
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float, str)):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.strftime('%Y-%m-%dT%H:%M:%S') if isinstance(obj, datetime) else obj.strftime('%Y-%m-%d')
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, set):
        return sorted([_json_safe(v) for v in obj], key=str)
    if isinstance(obj, dict):
        return {_json_safe(k): _json_safe(v) for k, v in obj.items()}
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)


class TempFileManager:
    """Manages temporary files with automatic cleanup."""

    def __init__(self):
        self.base_dir = os.path.join(tempfile.gettempdir(), 'codefy_api')
        os.makedirs(self.base_dir, exist_ok=True)

    def new_dir(self):
        prefix = 'codefy_'
        path = tempfile.mkdtemp(prefix=prefix, dir=self.base_dir)
        with _CLEANUP_LOCK:
            _CLEANUP_TRACKED.append(path)
        return path

    @staticmethod
    def cleanup(path):
        if path and os.path.isdir(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception:
                pass

    @staticmethod
    def cleanup_file(path):
        if path and os.path.isfile(path):
            try:
                os.remove(path)
            except Exception:
                pass


_TEMP_MANAGER = TempFileManager()
atexit.register(lambda: [TempFileManager.cleanup(p) for p in list(_CLEANUP_TRACKED)])


def _is_allowed(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


class CodefyWebService:
    """Service layer wrapping CodefyAnalyzer for the Flask API."""

    def __init__(self):
        self.temp_manager = _TEMP_MANAGER
        self.analyzer = None

    def _build_settings(self, settings_config):
        """Build a SettingsManager from JSON config."""
        sm = SettingsManager()
        if settings_config:
            if isinstance(settings_config.get('main_suppliers'), list):
                sm.main_suppliers = [str(x) for x in settings_config['main_suppliers'] if str(x).strip()]
            sm.shift_engine_enabled = bool(settings_config.get('shift_engine_enabled', True))
            if isinstance(settings_config.get('custom_shift_bases'), dict):
                sm.custom_shift_bases = settings_config['custom_shift_bases']
            if isinstance(settings_config.get('custom_ordinals'), list):
                sm.custom_ordinals = settings_config['custom_ordinals']
            sm.time_conflict_enabled = bool(settings_config.get('time_conflict_enabled', True))
            sm.time_conflict_offset = int(settings_config.get('time_conflict_offset', 30))
            sm.time_conflict_target = str(settings_config.get('time_conflict_target', 'dropoff_arrival_time'))
            sm.time_conflict_mode = str(settings_config.get('time_conflict_mode', 'autofix'))
            sm.time_normalize_enabled = bool(settings_config.get('time_normalize_enabled', True))
            sm.time_convert_12h = bool(settings_config.get('time_convert_12h', True))
            if isinstance(settings_config.get('time_column_rules'), dict):
                sm.time_column_rules = settings_config['time_column_rules']
        return sm

    def _build_column_controller(self, column_rules):
        """Build a ColumnController from JSON config."""
        cc = ColumnController()
        if column_rules and isinstance(column_rules, dict):
            rules = column_rules.get('rules', column_rules)
            if isinstance(rules, dict):
                cc.rules = {}
                for col, rule in rules.items():
                    if isinstance(rule, dict):
                        action = rule.get('action', 'keep')
                        value = rule.get('value')
                        cc.set_rule(col, action, value)
            cc.delete_rejected = column_rules.get('delete_rejected', True)
            cc.erp_mode = column_rules.get('erp_mode', False)
            if isinstance(column_rules.get('default_clear_columns'), list):
                cc.default_clear_columns = set(column_rules['default_clear_columns'])
        return cc

    def analyze(self, file_path, settings_config=None, column_rules=None,
                reorder_rules=None, main_suppliers=None):
        """Run full analysis on a file. Returns a dict with all results."""
        analyzer = CodefyAnalyzer(
            file_path=file_path,
            column_controller=self._build_column_controller(column_rules),
            main_suppliers=main_suppliers,
            settings=self._build_settings(settings_config),
        )
        if reorder_rules and isinstance(reorder_rules, list):
            analyzer.custom_reorder_rules = reorder_rules

        try:
            report, fixes = analyzer.run()
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
            }

        quality_score = analyzer._compute_score()
        grade = ("EXCELLENT" if quality_score >= 90 else "GOOD" if quality_score >= 75 else
                 "FAIR" if quality_score >= 60 else "POOR" if quality_score >= 40 else "CRITICAL")

        issues_flat = analyzer.build_issue_list()

        return {
            'success': True,
            'quality_score': quality_score,
            'grade': grade,
            'upload_ready': analyzer.upload_ready,
            'report': _json_safe(report),
            'fixes': _json_safe(fixes),
            'issues': _json_safe(analyzer.issues),
            'unified_issues': issues_flat,
            'column_profile': _json_safe(analyzer.column_profile),
            'sheets_data': _json_safe({
                s: {
                    'records': _json_safe(d['records']),
                    'cmap': d['cmap'],
                    'hrow': d['hrow'],
                    'skipped': d['skipped'],
                }
                for s, d in analyzer.sheets_data.items()
            }),
            'fixes_count': len(analyzer.fixes),
            'main_suppliers': analyzer.main_suppliers,
            'red_flag_cells': _json_safe(analyzer.red_flag_cells),
            'reorder_plan': _json_safe(analyzer.reorder_plan),
            'erp_issues': _json_safe(analyzer.erp_issues),
            'kpi_quality_breakdown': _json_safe(analyzer.kpi_quality_breakdown()),
            'kpi_rows_breakdown': _json_safe(analyzer.kpi_rows_breakdown()),
            'kpi_fixes_breakdown': _json_safe(analyzer.kpi_fixes_breakdown()),
            'kpi_errors_breakdown': _json_safe(analyzer.kpi_errors_breakdown()),
            'kpi_warnings_breakdown': _json_safe(analyzer.kpi_warnings_breakdown()),
            'kpi_expiry_breakdown': _json_safe(analyzer.kpi_expiry_breakdown()),
        }

    def export(self, file_path, format_name, settings_config=None,
               column_rules=None, reorder_rules=None, main_suppliers=None):
        """Run analysis and export to a file. Returns (output_path, filename)."""
        fmt = EXPORT_FORMATS.get(format_name)
        if not fmt:
            raise ValueError(
                f"Unsupported export format '{format_name}'. "
                f"Available: {', '.join(EXPORT_FORMATS.keys())}"
            )

        analyzer = CodefyAnalyzer(
            file_path=file_path,
            column_controller=self._build_column_controller(column_rules),
            main_suppliers=main_suppliers,
            settings=self._build_settings(settings_config),
        )
        if reorder_rules and isinstance(reorder_rules, list):
            analyzer.custom_reorder_rules = reorder_rules

        analyzer.run()
        self.analyzer = analyzer

        out_dir = self.temp_manager.new_dir()
        base_name = os.path.splitext(os.path.basename(file_path))[0] or 'codefy_export'
        safe_base = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in base_name)[:60]
        out_path = os.path.join(out_dir, f"{safe_base}{fmt['ext']}")

        method_name = fmt['method']
        method = getattr(self, method_name, None)
        if method is None:
            method = getattr(analyzer, method_name)
        method(out_path)

        filename = f"{safe_base}{fmt['ext']}"
        return out_path, filename

    def _export_issues_txt(self, out_path):
        """Export issues as plain text."""
        issues = self.analyzer.build_issue_list()
        lines = []
        lines.append('CodefyERP Issues Report')
        lines.append('=' * 60)
        lines.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append(f'Total issues: {len(issues)}')
        lines.append('')
        for i in issues:
            sev = i.get('severity', 'INFO').upper()
            lines.append(
                f'[{sev}] {i.get("category", "?")}: '
                f'{i.get("message", "")} '
                f'(Sheet: {i.get("sheet", "?")}, '
                f'Row: {i.get("row", "?")}, '
                f'Col: {i.get("column", "?")})'
            )
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

    def _export_report_txt(self, out_path):
        """Export full report as plain text."""
        report = self.analyzer.report
        lines = [text for text, tag in report] if report else []
        if not lines:
            lines = ['No report data.']
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')


service = CodefyWebService()
