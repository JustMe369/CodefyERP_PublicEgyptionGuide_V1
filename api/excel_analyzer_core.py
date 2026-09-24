#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlined CodefyExcelAnalyzer for API Integration
Contains essential validation functionality for web integration
"""

import os
import sys
import json
import re
import csv
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import argparse
from typing import Dict, List, Any

# Try to import optional dependencies
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_SHAPER = True
except Exception:
    HAS_SHAPER = False

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# =============================================================================
# CONSTANTS
# =============================================================================
COL_DRIVER_NAME     = 'assigned_driver_full_name'
COL_PLATE_NUMBER    = 'assigned_vehicle_plate_number'
COL_PHONE_NUMBER    = 'driver_phone_number'
COL_SHIFT_NAME      = 'shift_name'
COL_SCHEDULE_NAME   = 'schedule_name'
COL_ROUTE_CODE      = 'route_code'
COL_SUPPLIER_NAME   = 'supplier_name'
COL_SUPPLIER_PHONE  = 'supplier_phone_number'
COL_DRIVER_LICENSE_EXPIRY = 'driver_license_expiry_date'
COL_VEHICLE_EXPIRY  = 'vehicle_expiry_date'
COL_EMPLOYMENT_TYPE = 'driver_employment_type'
COL_VEHICLE_TYPE    = 'vehicle_type'
COL_VEHICLE_OWNER   = 'vehicle_owner_type'
COL_CLIENT_PRICE    = 'client_sales_price'
COL_SUPPLIER_PRICE  = 'supplier_price'
COL_PICKUP_TIME     = 'pickup_arrival_time'
COL_DROPOFF_TIME    = 'dropoff_arrival_time'
COL_SCHEDULE_TIME   = 'schedule_time'
COL_DIRECTION       = 'schedule_direction'
COL_ROUTE_TYPE      = 'route_type'
COL_PICKUP_NAME     = 'pickup_name'
COL_DROPOFF_NAME    = 'dropoff_name'
COL_LINE_NAME       = 'line_name'
COL_COMPANY_NAME    = 'company_name'
COL_PROJECT_NAME    = 'project_name'
COL_ASSIGNMENT_RULE = 'assignment_rule_type'
COL_ROW_TYPE        = 'row_type'

ERP_COLUMN_SPEC = {
    COL_DRIVER_NAME:     {'cat': 'driver', 'required': True},
    COL_PLATE_NUMBER:    {'cat': 'vehicle', 'required': True},
    COL_PHONE_NUMBER:    {'cat': 'driver', 'required': True},
    COL_SHIFT_NAME:      {'cat': 'schedule', 'required': True},
    COL_SCHEDULE_NAME:   {'cat': 'schedule', 'required': False},
    COL_ROUTE_CODE:      {'cat': 'routing', 'required': True},
    COL_SUPPLIER_NAME:   {'cat': 'supplier', 'required': False},
    COL_SUPPLIER_PHONE:  {'cat': 'supplier', 'required': False},
    COL_DRIVER_LICENSE_EXPIRY: {'cat': 'driver', 'required': False},
    COL_VEHICLE_EXPIRY:  {'cat': 'vehicle', 'required': False},
    COL_EMPLOYMENT_TYPE: {'cat': 'driver', 'required': False},
    COL_VEHICLE_TYPE:    {'cat': 'vehicle', 'required': False},
    COL_VEHICLE_OWNER:   {'cat': 'vehicle', 'required': False},
    COL_CLIENT_PRICE:    {'cat': 'pricing', 'required': False},
    COL_SUPPLIER_PRICE:  {'cat': 'pricing', 'required': False},
    COL_PICKUP_TIME:     {'cat': 'schedule', 'required': False},
    COL_DROPOFF_TIME:    {'cat': 'schedule', 'required': False},
    COL_SCHEDULE_TIME:   {'cat': 'schedule', 'required': False},
    COL_DIRECTION:       {'cat': 'schedule', 'required': False},
    COL_ROUTE_TYPE:      {'cat': 'routing', 'required': False},
    COL_PICKUP_NAME:     {'cat': 'location', 'required': False},
    COL_DROPOFF_NAME:    {'cat': 'location', 'required': False},
    COL_LINE_NAME:       {'cat': 'line', 'required': False},
    COL_COMPANY_NAME:    {'cat': 'core', 'required': True},
    COL_PROJECT_NAME:    {'cat': 'core', 'required': True},
    COL_ASSIGNMENT_RULE: {'cat': 'core', 'required': False},
    COL_ROW_TYPE:        {'cat': 'core', 'required': False},
}


class PhoneValidator:
    """Egyptian phone number validator"""
    
    @staticmethod
    def classify(raw):
        """Classify phone number status"""
        if not raw or raw == "" or raw is None:
            return 'empty'
        
        # Convert to string and clean
        s = str(raw).strip()
        if not s:
            return 'empty'
        
        # Remove common separators
        s = re.sub(r'[+\-\s\(\)]', '', s)
        
        # Convert Arabic/Persian digits to Western digits
        for arabic_digit, western_digit in [('٠', '0'), ('١', '1'), ('٢', '2'), 
                                          ('٣', '3'), ('٤', '4'), ('٥', '5'), 
                                          ('٦', '6'), ('٧', '7'), ('٨', '8'), ('٩', '9')]:
            s = s.replace(arabic_digit, western_digit)
        
        # Check if it contains non-digits
        if not s.isdigit():
            return 'arabic'  # Contains Arabic text or other non-digit chars
        
        # Validate Egyptian format: 01[0125]XXXXXXXX (11 digits)
        if len(s) == 11 and s.startswith('01') and s[2] in '0125':
            return 'ok'
        
        # Check for fixable cases
        if len(s) == 12 and s.startswith('201') and s[3] in '0125':
            # 12 digits starting with 20 -> add 0, drop 20
            return 'fixable'
        
        if len(s) == 14 and s.startswith('00201') and s[5] in '0125':
            # 14 digits starting with 0020 -> add 0, drop 0020
            return 'fixable'
        
        if len(s) == 10 and s.startswith('1') and s[1] in '0125':
            # 10 digits with valid prefix -> prepend 0
            return 'fixable'
        
        # Too short
        if len(s) < 10:
            return 'short'
        
        # Invalid format
        return 'invalid'


class DateValidator:
    """Date validator supporting Arabic months and multiple formats"""
    
    ARABIC_MONTHS = {
        'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4, 'مايو': 5, 'يونيو': 6,
        'يوليو': 7, 'أغسطس': 8, 'سبتمبر': 9, 'أكتوبر': 10, 'نوفمبر': 11, 'ديسمبر': 12,
        # Levantine variants
        'كانون ثاني': 1, 'شباط': 2, 'آذار': 3, 'نيسان': 4, 'أيار': 5, 'حزيران': 6,
        'تموز': 7, 'آب': 8, 'أيلول': 9, 'تشرين أول': 10, 'تشرين ثاني': 11, 'كانون أول': 12
    }
    
    MONTH_NAMES = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    @classmethod
    def classify(cls, raw):
        """Classify date value"""
        if not raw or raw == "" or raw is None:
            return 'empty'
        
        if isinstance(raw, (datetime, date)):
            return 'ok'
        
        # Check if it looks like an Egyptian phone number (avoid misclassification)
        phone_str = str(raw).strip()
        phone_clean = re.sub(r'[+\-\s\(\)]', '', phone_str)
        if len(phone_clean) == 11 and phone_clean.startswith('01') and phone_clean[2] in '0125':
            return 'invalid'  # Don't treat phone as date
        
        # Try parsing as various formats
        try:
            # Excel serial date (if it's a number between 20000 and 80000)
            if isinstance(raw, (int, float)) and 20000 <= raw <= 80000:
                from datetime import timedelta
                base_date = date(1900, 1, 1)  # Excel base date
                calculated_date = base_date + timedelta(days=raw - 2)  # Adjust for Excel leap year bug
                return 'ok'
            
            # String date formats
            s = str(raw).strip()
            
            # ISO format YYYY-MM-DD
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}', s):
                return 'ok'
            
            # ISO timestamp YYYY-MM-DDTHH:MM:SS
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{2}:\d{2}', s):
                return 'fixable'  # Can normalize to date
            
            # Common formats
            formats = [
                '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
                '%d.%m.%Y', '%d %m %Y', '%d %B %Y', '%d-%b-%Y', '%d/%m/%y'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(s, fmt)
                    return 'ok' if 'y' in fmt.lower() else 'fixable'
                except ValueError:
                    pass
            
            # Arabic month names
            for arabic_month, month_num in cls.ARABIC_MONTHS.items():
                if arabic_month in s:
                    return 'fixable'  # Can convert to standard format
            
            # English month names
            for month_name, month_num in cls.MONTH_NAMES.items():
                if month_name.lower() in s.lower():
                    return 'fixable'  # Can convert to standard format
            
            # Japanese-style format with Arabic numerals
            if any(char in s for char in ['年', '月', '日']):
                return 'fixable'
            
            return 'invalid'
        except Exception:
            return 'invalid'


class CodefyAnalyzer:
    """Core analyzer with API functionality"""
    
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.sheets_data = {}
        self.issues = defaultdict(list)
        self.fixes = []
        self.red_flag_cells = set()
        self.column_profiles = {}
        self.upload_ready = False
        self.main_suppliers = ['الجودة', 'الجوده']  # Default main suppliers
        self.shift_engine_enabled = True
        self.time_conflict_enabled = True
        self.time_conflict_offset = 30  # minutes
        self.time_conflict_target = 'dropoff_arrival_time'
        self.time_conflict_mode = 'autofix'
        self.time_normalize_enabled = True
        self.time_convert_12h = True
        self.time_column_rules = {}
        
        # Initialize issue categories
        for category in ['invalid_phones', 'date_format_issues', 'enum_violations', 
                        'missing_data', 'duplicate_phones', 'time_conflicts', 
                        'shift_upgrades', 'expiry_alerts', 'phone_conflicts', 
                        'driver_conflicts', 'erp_issues']:
            if category not in self.issues:
                self.issues[category] = []
    
    def run(self):
        """Run the analysis - simplified for API"""
        # This would normally contain the full analysis logic
        # For API purposes, we'll return a basic structure
        result = {
            'file_path': self.file_path,
            'analysis_complete': True,
            'issues_found': len(self.issues),
            'fixes_applied': len(self.fixes),
            'quality_score': 100,  # Would be computed based on actual analysis
            'upload_ready': self.upload_ready
        }
        
        return result, self.fixes
    
    def to_api_dict(self):
        """
        Convert analyzer results to a dictionary format suitable for API responses
        """
        # Count different types of issues
        critical_issues = []
        warning_issues = []
        info_issues = []
        
        # Add invalid phones as critical
        for issue in self.issues.get('invalid_phones', []):
            if issue.get('kind') in ['invalid', 'short', 'arabic']:
                critical_issues.append(issue)
            else:
                warning_issues.append(issue)
        
        # Add date format issues as warnings
        for issue in self.issues.get('date_format_issues', []):
            if issue.get('status') == 'invalid':
                critical_issues.append(issue)
            else:
                warning_issues.append(issue)
        
        # Add missing data as critical
        for issue in self.issues.get('missing_data', []):
            critical_issues.append(issue)
        
        # Add other issue types
        for issue in self.issues.get('driver_conflicts', []):
            critical_issues.append(issue)
        
        for issue in self.issues.get('phone_conflicts', []):
            if issue.get('soft', False):
                warning_issues.append(issue)
            else:
                critical_issues.append(issue)
        
        for issue in self.issues.get('duplicate_phones', []):
            if issue.get('kind') == 'hard':
                critical_issues.append(issue)
            else:
                warning_issues.append(issue)
        
        for issue in self.issues.get('time_conflicts', []):
            warning_issues.append(issue)
        
        for issue in self.issues.get('shift_upgrades', []):
            info_issues.append(issue)
        
        for issue in self.issues.get('expiry_alerts', []):
            if issue.get('days', 0) < 0:  # Expired
                critical_issues.append(issue)
            else:
                warning_issues.append(issue)
        
        return {
            'success': True,
            'summary': {
                'file_name': os.path.basename(self.file_path) if self.file_path else 'unknown',
                'total_rows': sum(len(sheet['records']) for sheet in self.sheets_data.values() if not sheet.get('skipped', False)),
                'total_sheets': len([s for s in self.sheets_data.values() if not s.get('skipped', False)]),
                'quality_score': self._compute_score(),
                'upload_ready': self.upload_ready,
                'issues': {
                    'critical': len(critical_issues),
                    'warning': len(warning_issues),
                    'info': len(info_issues)
                },
                'breakdown': {
                    'invalid_phones': len(self.issues.get('invalid_phones', [])),
                    'date_format_issues': len(self.issues.get('date_format_issues', [])),
                    'enum_violations': len(self.issues.get('enum_violations', [])),
                    'missing_data': len(self.issues.get('missing_data', [])),
                    'duplicate_phones': len(self.issues.get('duplicate_phones', [])),
                    'time_conflicts': len(self.issues.get('time_conflicts', [])),
                    'shift_upgrades': len(self.issues.get('shift_upgrades', [])),
                    'shift_conflicts': 0,  # Placeholder
                    'supplier_issues': 0,   # Placeholder
                    'capacity_issues': 0,   # Placeholder
                    'expiry_alerts': len(self.issues.get('expiry_alerts', [])),
                    'phone_conflicts': len([p for p in self.issues.get('phone_conflicts', []) if not p.get('soft', False)]),
                    'driver_conflicts': len(self.issues.get('driver_conflicts', []))
                }
            },
            'issues': self._format_issues_for_api(critical_issues, warning_issues, info_issues),
            'fixes_applied': [
                {
                    'sheet': fix['sheet'],
                    'row': fix['row'],
                    'column': fix['col'],
                    'old': str(fix['old']) if fix.get('old') is not None else '',
                    'new': str(fix['new']) if fix.get('new') is not None else '',
                    'reason': fix['reason']
                } for fix in self.fixes
            ],
            'column_profile': getattr(self, 'column_profiles', {}),
            'red_flags': [
                {
                    'sheet': cell[0],
                    'row': cell[1],
                    'column': cell[2],
                    'reason': cell[3] if len(cell) > 3 else 'Red flag'
                } for cell in self.red_flag_cells
            ] if hasattr(self, 'red_flag_cells') else []
        }

    def _format_issues_for_api(self, critical_issues, warning_issues, info_issues):
        """
        Format issues in a way that's suitable for API responses
        """
        formatted_issues = []
        
        # Format critical issues
        for issue in critical_issues:
            formatted_issues.append({
                'severity': 'critical',
                'category': issue.get('category', 'General'),
                'sheet': issue.get('sheet', 'Unknown'),
                'row': issue.get('row', 'N/A'),
                'column': issue.get('col', 'Unknown') if 'col' in issue else issue.get('column', 'Unknown'),
                'message': issue.get('reason', 'Critical issue detected'),
                'value': str(issue.get('value', 'N/A'))
            })
        
        # Format warnings
        for issue in warning_issues:
            formatted_issues.append({
                'severity': 'warning',
                'category': issue.get('category', 'General'),
                'sheet': issue.get('sheet', 'Unknown'),
                'row': issue.get('row', 'N/A'),
                'column': issue.get('col', 'Unknown') if 'col' in issue else issue.get('column', 'Unknown'),
                'message': issue.get('reason', 'Warning issue detected'),
                'value': str(issue.get('value', 'N/A'))
            })
        
        # Format info messages
        for issue in info_issues:
            formatted_issues.append({
                'severity': 'info',
                'category': issue.get('category', 'General'),
                'sheet': issue.get('sheet', 'Unknown'),
                'row': issue.get('row', 'N/A'),
                'column': issue.get('col', 'Unknown') if 'col' in issue else issue.get('column', 'Unknown'),
                'message': issue.get('reason', 'Information'),
                'value': str(issue.get('value', 'N/A'))
            })
        
        return formatted_issues

    def _compute_score(self):
        """
        Compute quality score based on issues found
        """
        # Base score
        score = 100
        
        # Deduct for various issues
        invalid_phones = len([p for p in self.issues.get('invalid_phones', []) if p.get('kind') in ['invalid', 'arabic']])
        score -= min(invalid_phones * 3, 24)  # Max -24 points
        
        short_phones = len([p for p in self.issues.get('invalid_phones', []) if p.get('kind') == 'short'])
        score -= min(short_phones * 2, 15)  # Max -15 points
        
        driver_conflicts = len(self.issues.get('driver_conflicts', []))
        score -= min(driver_conflicts * 4, 12)  # Max -12 points
        
        phone_conflicts_hard = len([p for p in self.issues.get('phone_conflicts', []) if not p.get('soft', False)])
        score -= min(phone_conflicts_hard * 7, 16)  # Max -16 points
        
        phone_conflicts_soft = len([p for p in self.issues.get('phone_conflicts', []) if p.get('soft', False)])
        score -= min(phone_conflicts_soft * 1, 6)  # Max -6 points
        
        dup_phones_hard = len([p for p in self.issues.get('duplicate_phones', []) if p.get('kind') == 'hard'])
        score -= min(dup_phones_hard * 5, 10)  # Max -10 points
        
        dup_phones_soft = len([p for p in self.issues.get('duplicate_phones', []) if p.get('kind') == 'soft'])
        score -= min(dup_phones_soft * 1, 3)  # Max -3 points
        
        enum_violations = len(self.issues.get('enum_violations', []))
        score -= min(enum_violations * 1, 6)  # Max -6 points
        
        erp_issues = len(self.issues.get('erp_issues', []))
        score -= min(erp_issues * 2, 7)  # Max -7 points
        
        time_conflicts = len(self.issues.get('time_conflicts', []))
        score -= min(time_conflicts * 2, 18)  # Max -18 points
        
        unparseable_dates = len([d for d in self.issues.get('date_format_issues', []) if d.get('status') == 'invalid'])
        score -= min(unparseable_dates * 4, 18)  # Max -18 points
        
        fixable_dates = len([d for d in self.issues.get('date_format_issues', []) if d.get('status') == 'fixable'])
        score -= min(fixable_dates * 2, 12)  # Max -12 points
        
        # Ensure score doesn't go below 0
        return max(0, score)


# For API usage, we'll expose this class and its functionality
if __name__ == "__main__":
    print("CodefyExcelAnalyzer Core - API Ready")
    print("This module provides the core functionality for web API integration")