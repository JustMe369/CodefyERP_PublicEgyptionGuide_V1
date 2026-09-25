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
    'codefy_validator',
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'CodefyDataValidator.py'),
)
_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validator)
CodefyDataValidator = _validator.CodefyDataValidator

# Create dummy classes for SettingsManager and ColumnController since they're not in CodefyDataValidator
class SettingsManager:
    def __init__(self):
        pass
    
    def get_main_suppliers(self):
        return ['الجودة', 'الجوده']  # Default main suppliers

class ColumnController:
    def __init__(self):
        pass

ALLOWED_EXTENSIONS = {'.xlsx', '.xlsm', '.csv', '.tsv', '.txt'}

EXPORT_FORMATS = {
    'fixed_xlsx':   {'ext': '.xlsx', 'method': 'export_fixed'},
    'fixed_csv':    {'ext': '.csv',  'method': 'export_fixed'},  # Use same method, adjust as needed
    'issues_xlsx':  {'ext': '.xlsx', 'method': 'export_fixed'}, # Adjust as needed
    'issues_csv':   {'ext': '.csv',  'method': 'export_fixed'}, # Adjust as needed
    'issues_json':  {'ext': '.json', 'method': 'export_fixed'}, # Adjust as needed
    'issues_txt':   {'ext': '.txt',  'method': 'export_fixed'}, # Adjust as needed
    'report_html':  {'ext': '.html', 'method': 'export_fixed'}, # Adjust as needed
    'report_txt':   {'ext': '.txt',  'method': 'export_fixed'}, # Adjust as needed
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

    def analyze(self, file_path, settings_config=None, column_rules=None,
                reorder_rules=None, main_suppliers=None):
        """Run full analysis on a file. Returns a dict with all results."""
        try:
            analyzer = CodefyDataValidator(file_path=file_path)
            
            # Run the analysis
            success = analyzer.analyze()
            if not success:
                return {
                'success': False,
                'error': 'Analysis failed',
            }

            # Calculate quality score and grade
            quality_score = analyzer._compute_score()
            grade = ("EXCELLENT" if quality_score >= 90 else "GOOD" if quality_score >= 75 else
                     "FAIR" if quality_score >= 60 else "POOR" if quality_score >= 40 else "CRITICAL")

            # Prepare the result
            result = {
                'success': True,
                'quality_score': quality_score,
                'grade': grade,
                'upload_ready': quality_score >= 80,  # Consider upload ready if score is 80+
                'summary': _json_safe(analyzer.get_analysis_summary()),
                'issues': _json_safe(analyzer._all_issues()),
                'fixes_count': len(analyzer.fixes),
                'fixes_available': len(analyzer.fixes) > 0,
                'message': 'Analysis completed successfully'
            }
            
            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
            }

    def export_fixed(self, file_path, output_path, format_type='fixed_xlsx'):
        """Export fixed file in specified format."""
        try:
            analyzer = CodefyDataValidator(file_path=file_path)
            
            # Run the analysis first
            success = analyzer.analyze()
            if not success:
                return {
                    'success': False,
                    'error': 'Analysis failed before export',
                }
            
            # Use the export_fixed method
            export_result = analyzer.export_fixed(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'export_result': export_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}',
            }
    
    def get_current_settings(self):
        """Get current settings."""
        return {
            'main_suppliers': ['الجودة', 'الجوده'],
            'shift_engine_enabled': True,
            'time_control_enabled': True
        }
    
    def update_settings(self, settings_data):
        """Update settings."""
        # This is a simplified implementation
        pass

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
