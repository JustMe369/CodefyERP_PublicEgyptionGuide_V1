#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    C O D E F Y E R P  ·  D A T A  V A L I D A T O R       ║
║              Advanced Excel Data Validation Engine for Egyptian ERP          ║
║──────────────────────────────────────────────────────────────────────────────║
║  This module provides comprehensive validation for CodefyERP systems,        ║
║  including Egyptian business logic, phone number validation, shift engines,  ║
║  time controls, and supplier management validations.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import PatternFill
import calendar

# Define column constants for Egyptian ERP system
COL_DRIVER_NAME = 'driver_name'
COL_DRIVER_PHONE = 'driver_phone'
COL_SUPPLIER_NAME = 'supplier_name'
COL_SUPPLIER_PHONE = 'supplier_phone'
COL_PLATE = 'plate_number'
COL_SHIFT = 'shift'
COL_SCHEDULE = 'schedule'
COL_ROUTE = 'route'
COL_PICKUP_ARR = 'pickup_arrival'
COL_PICKUP_DEP = 'pickup_departure'
COL_DROPOFF_ARR = 'dropoff_arrival'
COL_DROPOFF_TIME = 'dropoff_time'
COL_WORKING_DAYS = 'working_days'
COL_DIRECTION = 'direction'
COL_EMP_TYPE = 'employee_type'
COL_START_DATE = 'start_date'
COL_END_DATE = 'end_date'
COL_SERVICE_TYPE = 'service_type'
COL_CAPACITY = 'capacity'
COL_VEHICLE_TYPE = 'vehicle_type'
COL_DRIVER_LICENSE = 'driver_license'
COL_INSURANCE_EXPIRY = 'insurance_expiry'
COL_MAINTENANCE_DATE = 'maintenance_date'
COL_FUEL_TYPE = 'fuel_type'
COL_VEHICLE_STATUS = 'vehicle_status'
COL_COMPANY_NAME = 'company_name'
COL_COMPANY_PHONE = 'company_phone'
COL_COMPANY_ADDRESS = 'company_address'
COL_COMPANY_EMAIL = 'company_email'
COL_CONTACT_PERSON = 'contact_person'
COL_TAX_ID = 'tax_id'
COL_BANK_ACCOUNT = 'bank_account'
COL_CREDIT_LIMIT = 'credit_limit'
COL_PAYMENT_TERMS = 'payment_terms'
COL_SUPPLIER_CATEGORY = 'supplier_category'
COL_DELIVERY_TIME = 'delivery_time'
COL_MIN_ORDER_VALUE = 'min_order_value'
COL_DISCOUNT_RATE = 'discount_rate'

# ERP column specifications with Egyptian business context
ERP_COLUMN_SPEC = {
    COL_DRIVER_NAME: {'type': 'text', 'required': True},
    COL_DRIVER_PHONE: {'type': 'phone', 'required': True},
    COL_SUPPLIER_NAME: {'type': 'text', 'required': True},
    COL_SUPPLIER_PHONE: {'type': 'phone'},
    COL_PLATE: {'type': 'text', 'required': True},
    COL_SHIFT: {'type': 'text', 'required': True},
    COL_SCHEDULE: {'type': 'text', 'required': True},
    COL_ROUTE: {'type': 'text', 'required': True},
    COL_PICKUP_ARR: {'type': 'time'},
    COL_PICKUP_DEP: {'type': 'time'},
    COL_DROPOFF_ARR: {'type': 'time'},
    COL_DROPOFF_TIME: {'type': 'time'},
    COL_WORKING_DAYS: {'type': 'enum', 'enum': ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']},
    COL_DIRECTION: {'type': 'enum', 'enum': ['north', 'south', 'east', 'west', 'round_trip']},
    COL_START_DATE: {'type': 'date'},
    COL_END_DATE: {'type': 'date'},
    COL_SERVICE_TYPE: {'type': 'enum', 'enum': ['daily', 'weekly', 'monthly', 'event']},
    COL_CAPACITY: {'type': 'number'},
    COL_VEHICLE_TYPE: {'type': 'enum', 'enum': ['bus', 'van', 'truck', 'car']},
    COL_DRIVER_LICENSE: {'type': 'text'},
    COL_INSURANCE_EXPIRY: {'type': 'date'},
    COL_MAINTENANCE_DATE: {'type': 'date'},
    COL_FUEL_TYPE: {'type': 'enum', 'enum': ['gasoline', 'diesel', 'electric', 'hybrid']},
    COL_VEHICLE_STATUS: {'type': 'enum', 'enum': ['active', 'inactive', 'maintenance', 'decommissioned']},
    # Supplier-specific columns
    COL_COMPANY_NAME: {'type': 'text', 'required': True},
    COL_COMPANY_PHONE: {'type': 'phone', 'required': True},
    COL_COMPANY_ADDRESS: {'type': 'text', 'required': True},
    COL_COMPANY_EMAIL: {'type': 'email'},
    COL_CONTACT_PERSON: {'type': 'text', 'required': True},
    COL_TAX_ID: {'type': 'text'},  # Egyptian Tax ID format
    COL_BANK_ACCOUNT: {'type': 'text'},  # Bank account number
    COL_CREDIT_LIMIT: {'type': 'number'},
    COL_PAYMENT_TERMS: {'type': 'enum', 'enum': ['cash', 'credit', 'net_7', 'net_15', 'net_30', 'net_60']},
    COL_SUPPLIER_CATEGORY: {'type': 'enum', 'enum': ['raw_materials', 'services', 'equipment', 'maintenance', 'utilities', 'transportation']},
    COL_DELIVERY_TIME: {'type': 'number'},  # In days
    COL_MIN_ORDER_VALUE: {'type': 'number'},
    COL_DISCOUNT_RATE: {'type': 'number'},  # Percentage
}

# Day aliases for working days
DAY_ALIAS_LOOKUP = {
    'sat': 'Saturday', 'saturday': 'Saturday', 'السبت': 'Saturday',
    'sun': 'Sunday', 'sunday': 'Sunday', 'الاحد': 'Sunday',
    'mon': 'Monday', 'monday': 'Monday', 'الاثنين': 'Monday',
    'tue': 'Tuesday', 'tuesday': 'Tuesday', 'الثلاثاء': 'Tuesday',
    'wed': 'Wednesday', 'wednesday': 'Wednesday', 'الاربعاء': 'Wednesday',
    'thu': 'Thursday', 'thursday': 'Thursday', 'الخميس': 'Thursday',
    'fri': 'Friday', 'friday': 'Friday', 'الجمعة': 'Friday'
}

DAY_CANONICAL_ORDER = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Working days separators
WORKING_DAYS_SEPARATORS = re.compile(r'[,\s\n\t;/\\|]+|و|and', re.IGNORECASE)

# Shift patterns and ordinals
SHIFT_BASE_PATTERNS = {
    'Morning': ['morning', 'صباحي', 'am', 'early', 'فجر'],
    'Evening': ['evening', 'مسائي', 'pm', 'late', 'مغرب'],
    'Night': ['night', 'ليلي', 'night', ' полночной'],
    'Day': ['day', 'نهار', 'normal', ' يومي'],
    'Special': ['special', 'خاصة', 'extra', ' مميز'],
    'Holiday': ['holiday', 'عطلة', 'weekend', ' عطلة'],
    'Weekend': ['weekend', 'نهاية الاسبوع', 'off', ' اسبوعية']
}

SHIFT_ORDINALS = [
    (['first', 'primary', 'main', 'الاول', 'الرئيسي'], 'Primary', 'Pri'),
    (['second', 'secondary', 'الثاني', 'الفرعي'], 'Secondary', 'Sec'),
    (['third', 'tertiary', 'الثالث'], 'Tertiary', 'Ter'),
    (['round', 'both', '往返', 'both ways', '往返'], 'Round Trip', 'RT'),
    (['express', 'fast', 'سريع', ' express'], 'Express', 'Exp'),
    (['regular', 'normal', 'عادي', ' standard'], 'Regular', 'Reg'),
    (['vip', 'premium', ' vip', ' مميز'], 'VIP', 'VIP')
]

# Egyptian phone number patterns
EGYPTIAN_PHONE_PATTERNS = [
    re.compile(r'^01[0-9]{9}$'),  # Egyptian mobile numbers
    re.compile(r'^\+201[0-9]{9}$'),  # International format
    re.compile(r'^201[0-9]{9}$'),  # Without +
]

# Egyptian tax ID format (14 digits)
EGYPTIAN_TAX_ID_PATTERN = re.compile(r'^\d{14}$')

# Email validation pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def to_str(value: Any) -> str:
    """Convert any value to string, handling None and other types."""
    if value is None:
        return ''
    if isinstance(value, (str, int, float)):
        return str(value).strip()
    return str(value).strip()


def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    if not text:
        return False
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))


def normalize_name(name: str) -> str:
    """Normalize names by removing extra spaces and standardizing format."""
    if not name:
        return ''
    # Remove extra whitespace and standardize
    normalized = re.sub(r'\s+', ' ', str(name).strip())
    return normalized


def is_valid_egyptian_phone(phone: str) -> bool:
    """Validate Egyptian phone number format."""
    if not phone:
        return False
    phone = str(phone).replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    for pattern in EGYPTIAN_PHONE_PATTERNS:
        if pattern.match(phone):
            return True
    return False


def normalize_phone(phone: str) -> str:
    """Normalize phone number to Egyptian standard format."""
    if not phone:
        return ''
    
    # Remove all non-digit characters except the leading +
    phone = str(phone)
    if phone.startswith('+'):
        digits = '+' + ''.join(filter(str.isdigit, phone[1:]))
    else:
        digits = ''.join(filter(str.isdigit, phone))
    
    # Convert to Egyptian format if applicable
    if len(digits) == 11 and digits.startswith('01'):
        return digits  # Already in Egyptian format
    elif len(digits) == 12 and digits.startswith('201'):
        return '0' + digits[2:]  # Convert from international to local
    elif len(digits) == 13 and digits.startswith('+201'):
        return '0' + digits[3:]  # Convert from +international to local
    
    return phone  # Return original if can't normalize


def is_valid_date(date_str: str) -> bool:
    """Validate date format and convert to standard format."""
    if not date_str:
        return False
    
    date_str = to_str(date_str)
    
    # Try different date formats
    formats = [
        '%Y-%m-%d',      # Standard: 2023-01-15
        '%d/%m/%Y',      # Egyptian: 15/01/2023
        '%m/%d/%Y',      # US: 01/15/2023
        '%d-%m-%Y',      # Egyptian: 15-01-2023
        '%m-%d-%Y',      # US: 01-15-2023
        '%d.%m.%Y',      # European: 15.01.2023
        '%Y/%m/%d',      # Alternative: 2023/01/15
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False


def normalize_date(date_str: str) -> str:
    """Normalize date to standard format YYYY-MM-DD."""
    if not date_str:
        return ''
    
    date_str = to_str(date_str)
    
    # Try different date formats
    formats = [
        '%Y-%m-%d',      # Standard: 2023-01-15
        '%d/%m/%Y',      # Egyptian: 15/01/2023
        '%m/%d/%Y',      # US: 01/15/2023
        '%d-%m-%Y',      # Egyptian: 15-01-2023
        '%m-%d-%Y',      # US: 01-15-2023
        '%d.%m.%Y',      # European: 15.01.2023
        '%Y/%m/%d',      # Alternative: 2023/01/15
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return date_str  # Return original if can't parse


def is_valid_time(time_str: str) -> bool:
    """Validate time format."""
    if not time_str:
        return False
    
    time_str = to_str(time_str)
    
    # Try different time formats
    formats = [
        '%H:%M',         # 24-hour: 14:30
        '%H:%M:%S',      # 24-hour with seconds: 14:30:00
        '%I:%M %p',      # 12-hour: 02:30 PM
        '%I:%M%p',       # 12-hour: 02:30PM
    ]
    
    for fmt in formats:
        try:
            datetime.strptime(time_str, fmt)
            return True
        except ValueError:
            continue
    
    return False


def normalize_working_days(working_days_str: str) -> str:
    """Normalize working days string to canonical format."""
    if not working_days_str:
        return ''
    
    # Split by various separators
    days = WORKING_DAYS_SEPARATORS.split(to_str(working_days_str))
    normalized_days = []
    
    for day in days:
        day = day.strip().lower()
        if day in DAY_ALIAS_LOOKUP:
            canonical_day = DAY_ALIAS_LOOKUP[day]
            if canonical_day not in normalized_days:
                normalized_days.append(canonical_day)
        elif day.title() in DAY_CANONICAL_ORDER:
            canonical_day = day.title()
            if canonical_day not in normalized_days:
                normalized_days.append(canonical_day)
    
    # Sort days according to Egyptian work week (Saturday is first)
    sorted_days = []
    for day in DAY_CANONICAL_ORDER:
        if day in normalized_days:
            sorted_days.append(day)
    
    return ', '.join(sorted_days)


def infer_shift_from_schedule(schedule: str) -> str:
    """Infer shift type from schedule description."""
    if not schedule:
        return ''
    
    schedule_lower = to_str(schedule).lower()
    
    # Look for shift indicators
    for shift_type, keywords in SHIFT_BASE_PATTERNS.items():
        for keyword in keywords:
            if keyword in schedule_lower:
                return shift_type
    
    # Try to infer from time ranges in schedule
    time_match = re.search(r'(\d{1,2}):(\d{2})', schedule_lower)
    if time_match:
        hour = int(time_match.group(1))
        if 5 <= hour <= 11:
            return 'Morning'
        elif 12 <= hour <= 17:
            return 'Afternoon'
        elif 18 <= hour <= 22:
            return 'Evening'
        else:
            return 'Night'
    
    return 'Day'


def analyze_shift_patterns(shift_str: str) -> Dict[str, Any]:
    """Analyze shift string for base type and ordinals."""
    if not shift_str:
        return {'base': '', 'ordinals': []}
    
    shift_lower = to_str(shift_str).lower()
    result = {'base': '', 'ordinals': []}
    
    # Identify base shift type
    for shift_type, keywords in SHIFT_BASE_PATTERNS.items():
        for keyword in keywords:
            if keyword in shift_lower:
                result['base'] = shift_type
                break
        if result['base']:
            break
    
    # Identify ordinals
    for ordinal_group, full_name, abbr in SHIFT_ORDINALS:
        for keyword in ordinal_group:
            if keyword in shift_lower:
                result['ordinals'].append({'full': full_name, 'abbr': abbr})
                break
    
    return result


def is_valid_tax_id(tax_id: str) -> bool:
    """Validate Egyptian tax ID format (14 digits)."""
    if not tax_id:
        return False
    tax_id = str(tax_id).replace(' ', '').replace('-', '')
    return bool(EGYPTIAN_TAX_ID_PATTERN.match(tax_id))


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    email = str(email).strip().lower()
    return bool(EMAIL_PATTERN.match(email))


def validate_supplier_record(record: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate supplier-specific record fields."""
    issues = []
    
    # Validate company phone
    if COL_COMPANY_PHONE in record and record[COL_COMPANY_PHONE]:
        if not is_valid_egyptian_phone(record[COL_COMPANY_PHONE]):
            issues.append({
                'field': COL_COMPANY_PHONE,
                'issue': 'Invalid Egyptian phone number format',
                'severity': 'critical'
            })
    
    # Validate tax ID
    if COL_TAX_ID in record and record[COL_TAX_ID]:
        if not is_valid_tax_id(record[COL_TAX_ID]):
            issues.append({
                'field': COL_TAX_ID,
                'issue': 'Invalid Egyptian tax ID format (should be 14 digits)',
                'severity': 'warning'
            })
    
    # Validate email
    if COL_COMPANY_EMAIL in record and record[COL_COMPANY_EMAIL]:
        if not is_valid_email(record[COL_COMPANY_EMAIL]):
            issues.append({
                'field': COL_COMPANY_EMAIL,
                'issue': 'Invalid email format',
                'severity': 'warning'
            })
    
    # Validate credit limit
    if COL_CREDIT_LIMIT in record and record[COL_CREDIT_LIMIT]:
        try:
            credit_limit = float(to_str(record[COL_CREDIT_LIMIT]))
            if credit_limit < 0:
                issues.append({
                    'field': COL_CREDIT_LIMIT,
                    'issue': 'Credit limit cannot be negative',
                    'severity': 'critical'
                })
        except ValueError:
            issues.append({
                'field': COL_CREDIT_LIMIT,
                'issue': 'Credit limit must be a valid number',
                'severity': 'critical'
            })
    
    return issues


def detect_shift_conflicts(shifts: List[str], schedules: List[str]) -> List[Dict[str, Any]]:
    """Detect conflicts between shifts and schedules."""
    conflicts = []
    
    for i, (shift, schedule) in enumerate(zip(shifts, schedules)):
        inferred_shift = infer_shift_from_schedule(schedule)
        
        if shift and inferred_shift and shift.lower() != inferred_shift.lower():
            conflicts.append({
                'index': i,
                'actual_shift': shift,
                'inferred_shift': inferred_shift,
                'conflict_type': 'shift_schedule_mismatch'
            })
    
    return conflicts


def detect_time_conflicts(times: List[str], start_times: List[str], end_times: List[str]) -> List[Dict[str, Any]]:
    """Detect time conflicts in schedules."""
    conflicts = []
    
    for i, (time, start_time, end_time) in enumerate(zip(times, start_times, end_times)):
        if time and start_time and end_time:
            try:
                time_obj = datetime.strptime(to_str(time), '%H:%M')
                start_obj = datetime.strptime(to_str(start_time), '%H:%M')
                end_obj = datetime.strptime(to_str(end_time), '%H:%M')
                
                if start_obj > end_obj:  # Handle overnight shifts
                    end_obj += timedelta(days=1)
                
                if not (start_obj <= time_obj <= end_obj):
                    conflicts.append({
                        'index': i,
                        'time': time,
                        'start_time': start_time,
                        'end_time': end_time,
                        'conflict_type': 'time_outside_range'
                    })
            except ValueError:
                # Invalid time format, already caught elsewhere
                continue
    
    return conflicts


class CodefyDataValidator:
    """Advanced data validation engine for CodefyERP with Egyptian business logic."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = None
        self.issues = {
            'invalid_phones': [],
            'date_format_issues': [],
            'enum_violations': [],
            'missing_data': [],
            'duplicate_phones': [],
            'time_conflicts': [],
            'shift_conflicts': [],
            'supplier_issues': [],
            'capacity_issues': [],
            'vehicle_status_issues': [],
            'insurance_expiry_issues': [],
            'expiry_alerts': [],  # For upcoming expiries
            'shift_upgrades': [],  # For shift improvements
            'tax_id_issues': [],  # For supplier tax ID issues
            'email_issues': [],  # For email validation issues
        }
        self.fixes = []
        self.analysis_summary = {}
        
    def find_header(self, worksheet) -> Tuple[int, Dict[str, int]]:
        """Find header row and map column names to indices."""
        # Look for header in first 5 rows
        for row_idx in range(1, min(6, worksheet.max_row + 1)):
            header_map = {}
            for col_idx in range(1, worksheet.max_column + 1):
                cell_value = worksheet.cell(row=row_idx, column=col_idx).value
                if cell_value:
                    # Normalize column name
                    col_name = to_str(cell_value).lower().replace(' ', '_').replace('-', '_')
                    if col_name in ERP_COLUMN_SPEC:
                        header_map[col_name] = col_idx
            # If we found some valid headers, return them
            if len(header_map) > 0:
                return row_idx, header_map
        return 0, {}  # No valid headers found
    
    def validate_cell(self, value: Any, col_name: str, sheet_name: str, row_num: int, col_num: int) -> List[Dict[str, str]]:
        """Validate a single cell based on its column specification."""
        issues = []
        spec = ERP_COLUMN_SPEC.get(col_name, {})
        
        # Check for required fields
        if spec.get('required') and (value is None or to_str(value) == ''):
            issues.append({
                'sheet': sheet_name,
                'row': row_num,
                'col': col_name,
                'value': to_str(value),
                'issue': f'Required field {col_name} is missing',
                'severity': 'critical'
            })
            return issues  # Don't continue with other validations if required field is missing
        
        # Skip validation if value is empty and not required
        if value is None or to_str(value) == '':
            return issues
        
        # Validate based on type
        col_type = spec.get('type', 'text')
        
        if col_type == 'phone':
            if not is_valid_egyptian_phone(value):
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': 'Invalid Egyptian phone number format',
                    'severity': 'critical'
                })
        
        elif col_type == 'date':
            if not is_valid_date(value):
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': 'Invalid date format (expected YYYY-MM-DD)',
                    'severity': 'warning'
                })
        
        elif col_type == 'time':
            if not is_valid_time(value):
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': 'Invalid time format (expected HH:MM)',
                    'severity': 'warning'
                })
        
        elif col_type == 'enum':
            allowed_values = spec.get('enum', [])
            if to_str(value).lower() not in [v.lower() for v in allowed_values]:
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': f'Invalid value. Expected one of: {", ".join(allowed_values)}',
                    'severity': 'warning'
                })
        
        elif col_type == 'number':
            try:
                float(to_str(value))
            except ValueError:
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': 'Expected a numeric value',
                    'severity': 'critical'
                })
        
        elif col_type == 'email':
            if not is_valid_email(value):
                issues.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': 'Invalid email format',
                    'severity': 'warning'
                })
        
        return issues
    
    def normalize_cell_value(self, value: Any, col_name: str) -> Tuple[Any, str]:
        """Normalize a cell value and return the normalized value with a reason."""
        if value is None or to_str(value) == '':
            return value, 'no_normalization_needed'
        
        spec = ERP_COLUMN_SPEC.get(col_name, {})
        col_type = spec.get('type', 'text')
        
        if col_type == 'phone':
            normalized = normalize_phone(value)
            if normalized != to_str(value):
                return normalized, 'normalized_to_standard_format'
        elif col_type == 'date':
            normalized = normalize_date(value)
            if normalized != to_str(value):
                return normalized, 'normalized_to_standard_date_format'
        elif col_type == 'text':
            if col_name == COL_WORKING_DAYS:
                normalized = normalize_working_days(value)
                if normalized != to_str(value):
                    return normalized, 'normalized_working_days_format'
        elif col_name == COL_SHIFT:
            # Analyze and potentially upgrade shift descriptions
            shift_analysis = analyze_shift_patterns(to_str(value))
            if shift_analysis['ordinals']:  # If there are ordinals to improve
                # Create improved shift name
                base_shift = shift_analysis['base'] or 'Day'
                ordinals = [o['abbr'] for o in shift_analysis['ordinals']]
                improved_name = f"{base_shift} ({'-'.join(ordinals)})" if ordinals else base_shift
                if improved_name.lower() != to_str(value).lower():
                    return improved_name, 'improved_shift_description_with_ordinals'
        
        return value, 'no_normalization_needed'
    
    def analyze_duplicates(self, df: pd.DataFrame, col_name: str, sheet_name: str):
        """Analyze duplicates in a specific column."""
        if col_name not in df.columns:
            return
        
        # Get non-null values
        series = df[col_name].dropna()
        if series.empty:
            return
        
        # Find duplicates
        duplicates = series[series.duplicated(keep=False)]
        
        if not duplicates.empty:
            for idx, value in duplicates.items():
                # idx in pandas is 0-based, but Excel rows are 1-based, and we have headers in row 1
                excel_row = idx + 2  # +2 because pandas is 0-indexed and Excel headers are in row 1
                self.issues['duplicate_phones'].append({
                    'sheet': sheet_name,
                    'row': excel_row,
                    'col': col_name,
                    'value': to_str(value),
                    'issue': f'Duplicate value found in {col_name}'
                })
    
    def analyze_vehicle_capacity(self, df: pd.DataFrame, sheet_name: str):
        """Analyze vehicle capacity constraints."""
        required_cols = [COL_VEHICLE_TYPE, COL_CAPACITY]
        if not all(col in df.columns for col in required_cols):
            return
        
        # Define reasonable capacity ranges for different vehicle types
        capacity_ranges = {
            'car': (1, 6),
            'van': (7, 15),
            'bus': (16, 60),
            'truck': (1, 3),
        }
        
        for idx, row in df.iterrows():
            vehicle_type = to_str(row.get(COL_VEHICLE_TYPE, '')).lower()
            capacity = row.get(COL_CAPACITY)
            
            if not vehicle_type or capacity is None:
                continue
            
            try:
                capacity_val = float(to_str(capacity))
                
                if vehicle_type in capacity_ranges:
                    min_cap, max_cap = capacity_ranges[vehicle_type]
                    
                    if capacity_val < min_cap or capacity_val > max_cap:
                        excel_row = idx + 2  # Convert pandas index to Excel row
                        issue_level = 'warning' if min_cap <= capacity_val <= max_cap * 2 else 'critical'
                        
                        self.issues['capacity_issues'].append({
                            'sheet': sheet_name,
                            'row': excel_row,
                            'col': COL_CAPACITY,
                            'value': to_str(capacity_val),
                            'issue': f'Capacity {capacity_val} seems unusual for {vehicle_type}. Expected range: {min_cap}-{max_cap}',
                            'severity': issue_level
                        })
            except ValueError:
                continue  # Skip if capacity is not a valid number
    
    def analyze_expiry_dates(self, df: pd.DataFrame, sheet_name: str):
        """Analyze expiry dates like insurance expiry."""
        if COL_INSURANCE_EXPIRY not in df.columns:
            return
        
        today = datetime.today().date()
        
        for idx, row in df.iterrows():
            expiry_date_str = row.get(COL_INSURANCE_EXPIRY)
            if not expiry_date_str:
                continue
            
            expiry_date_normalized = normalize_date(expiry_date_str)
            if not expiry_date_normalized:
                continue
            
            try:
                expiry_date = datetime.strptime(expiry_date_normalized, '%Y-%m-%d').date()
                
                # Calculate days difference
                days_diff = (expiry_date - today).days
                excel_row = idx + 2  # Convert pandas index to Excel row
                
                if days_diff < 0:  # Already expired
                    self.issues['insurance_expiry_issues'].append({
                        'sheet': sheet_name,
                        'row': excel_row,
                        'col': COL_INSURANCE_EXPIRY,
                        'value': expiry_date_normalized,
                        'issue': f'Insurance expired {abs(days_diff)} days ago',
                        'days_overdue': abs(days_diff)
                    })
                elif 0 <= days_diff <= 30:  # Expires soon
                    self.issues['expiry_alerts'].append({
                        'sheet': sheet_name,
                        'row': excel_row,
                        'col': COL_INSURANCE_EXPIRY,
                        'value': expiry_date_normalized,
                        'issue': f'Insurance expires in {days_diff} days',
                        'days_until_expiry': days_diff
                    })
            except ValueError:
                continue  # Skip if date parsing fails
    
    def analyze_suppliers(self, df: pd.DataFrame, sheet_name: str):
        """Analyze supplier-specific records."""
        # Check if this looks like a supplier sheet
        supplier_related_cols = [COL_COMPANY_NAME, COL_COMPANY_PHONE, COL_CONTACT_PERSON, COL_TAX_ID]
        present_cols = [col for col in supplier_related_cols if col in df.columns]
        
        if len(present_cols) < 2:  # At least 2 supplier-related columns
            return
        
        for idx, row in df.iterrows():
            excel_row = idx + 2  # Convert pandas index to Excel row
            
            # Validate supplier record
            supplier_issues = validate_supplier_record(row)
            
            for issue in supplier_issues:
                self.issues['supplier_issues'].append({
                    'sheet': sheet_name,
                    'row': excel_row,
                    'col': issue['field'],
                    'value': to_str(row.get(issue['field'], '')),
                    'issue': issue['issue'],
                    'severity': issue['severity']
                })
    
    def analyze_shifts_and_schedules(self, df: pd.DataFrame, sheet_name: str):
        """Analyze shift and schedule relationships."""
        shift_cols = [COL_SHIFT, COL_SCHEDULE]
        time_cols = [COL_PICKUP_ARR, COL_PICKUP_DEP, COL_DROPOFF_ARR, COL_DROPOFF_TIME]
        
        # Check for shift/schedule conflicts
        if COL_SHIFT in df.columns and COL_SCHEDULE in df.columns:
            shifts = df[COL_SHIFT].tolist()
            schedules = df[COL_SCHEDULE].tolist()
            
            conflicts = detect_shift_conflicts(shifts, schedules)
            
            for conflict in conflicts:
                idx = conflict['index']
                excel_row = idx + 2  # Convert pandas index to Excel row
                
                self.issues['shift_conflicts'].append({
                    'sheet': sheet_name,
                    'row': excel_row,
                    'col': COL_SHIFT,
                    'value': conflict['actual_shift'],
                    'issue': f'Shift "{conflict["actual_shift"]}" conflicts with schedule inference "{conflict["inferred_shift"]}"',
                    'severity': 'warning'
                })
        
        # Check for time conflicts
        time_present_cols = [col for col in time_cols if col in df.columns]
        if len(time_present_cols) >= 3:  # Need at least 3 time-related columns
            times = df.get(COL_DROPOFF_TIME, []).tolist()
            start_times = df.get(COL_PICKUP_DEP, []).tolist()
            end_times = df.get(COL_DROPOFF_ARR, []).tolist()
            
            # Ensure all lists are the same length
            min_len = min(len(times), len(start_times), len(end_times))
            times = times[:min_len]
            start_times = start_times[:min_len]
            end_times = end_times[:min_len]
            
            conflicts = detect_time_conflicts(times, start_times, end_times)
            
            for conflict in conflicts:
                idx = conflict['index']
                excel_row = idx + 2  # Convert pandas index to Excel row
                
                self.issues['time_conflicts'].append({
                    'sheet': sheet_name,
                    'row': excel_row,
                    'col': COL_DROPOFF_TIME,
                    'value': conflict['time'],
                    'issue': f'Time {conflict["time"]} is outside range {conflict["start_time"]}-{conflict["end_time"]}',
                    'severity': 'warning'
                })
    
    def analyze(self) -> bool:
        """Perform comprehensive analysis of the Excel file."""
        try:
            self.workbook = load_workbook(self.file_path)
            total_rows = 0
            
            for sheet_name in self.workbook.sheetnames:
                worksheet = self.workbook[sheet_name]
                
                # Find header row and column mapping
                header_row, column_map = self.find_header(worksheet)
                if not header_row:
                    continue  # Skip sheets without recognizable headers
                
                # Convert worksheet to DataFrame for easier analysis
                data_rows = []
                for row in worksheet.iter_rows(min_row=header_row + 1, values_only=True):
                    data_rows.append(row)
                
                if not data_rows:
                    continue
                
                # Create DataFrame with proper column names
                columns = [worksheet.cell(row=header_row, column=col_idx).value 
                          for col_idx in column_map.values()]
                columns = [to_str(col).lower().replace(' ', '_').replace('-', '_') 
                          for col in columns]
                
                df = pd.DataFrame(data_rows, columns=columns)
                df = df.dropna(how='all')  # Remove completely empty rows
                total_rows += len(df)
                
                # Validate each cell in mapped columns
                for col_name, col_idx in column_map.items():
                    if col_name not in df.columns:
                        continue
                    
                    for idx, value in df[col_name].items():
                        if pd.isna(value):
                            continue
                        
                        cell_issues = self.validate_cell(value, col_name, sheet_name, idx + 2, col_idx)
                        for issue in cell_issues:
                            issue_type = f"{issue['severity']}_issues"
                            if issue_type in self.issues:
                                self.issues[issue_type].append(issue)
                            else:
                                # Add to general issues list
                                self.issues['enum_violations'].append(issue)
                
                # Apply fixes where possible
                for col_name, col_idx in column_map.items():
                    if col_name not in df.columns:
                        continue
                    
                    for idx, value in df[col_name].items():
                        if pd.isna(value):
                            continue
                        
                        normalized_value, reason = self.normalize_cell_value(value, col_name)
                        if reason != 'no_normalization_needed':
                            excel_row = idx + 2
                            self.fixes.append({
                                'sheet': sheet_name,
                                'row': excel_row,
                                'col': col_name,
                                'old': value,
                                'new': normalized_value,
                                'reason': reason
                            })
                
                # Perform specialized analyses
                self.analyze_duplicates(df, COL_DRIVER_PHONE, sheet_name)
                self.analyze_duplicates(df, COL_SUPPLIER_PHONE, sheet_name)
                self.analyze_vehicle_capacity(df, sheet_name)
                self.analyze_expiry_dates(df, sheet_name)
                self.analyze_suppliers(df, sheet_name)
                self.analyze_shifts_and_schedules(df, sheet_name)
            
            # Generate analysis summary
            self.analysis_summary = {
                'file_name': self.file_path.split('/')[-1].split('\\')[-1],
                'total_sheets': len(self.workbook.sheetnames),
                'total_rows': total_rows,
                'quality_score': self._compute_score(),
                'issues': {
                    'critical': len(self.issues['invalid_phones']) + len(self.issues['missing_data']) + len(self.issues['capacity_issues']) + len(self.issues['insurance_expiry_issues']),
                    'warning': len(self.issues['date_format_issues']) + len(self.issues['enum_violations']) + len(self.issues['time_conflicts']) + len(self.issues['shift_conflicts']) + len(self.issues['expiry_alerts']) + len(self.issues['supplier_issues']),
                    'info': len(self.issues['shift_upgrades']) + len(self.issues['duplicate_phones'])
                },
                'breakdown': {
                    'invalid_phones': len(self.issues['invalid_phones']),
                    'date_format_issues': len(self.issues['date_format_issues']),
                    'enum_violations': len(self.issues['enum_violations']),
                    'missing_data': len(self.issues['missing_data']),
                    'duplicate_phones': len(self.issues['duplicate_phones']),
                    'time_conflicts': len(self.issues['time_conflicts']),
                    'shift_conflicts': len(self.issues['shift_conflicts']),
                    'supplier_issues': len(self.issues['supplier_issues']),
                    'capacity_issues': len(self.issues['capacity_issues']),
                    'insurance_expiry_issues': len(self.issues['insurance_expiry_issues']),
                    'expiry_alerts': len(self.issues['expiry_alerts']),
                    'shift_upgrades': len(self.issues['shift_upgrades'])
                }
            }
            
            return True
            
        except Exception as e:
            print(f"Error analyzing file: {e}")
            return False
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get the analysis summary."""
        return self.analysis_summary
    
    def _all_issues(self) -> List[Dict[str, Any]]:
        """Get all issues in a flattened format."""
        out = []
        
        # Invalid phones
        for ip in self.issues['invalid_phones']:
            out.append({
                'severity': 'critical',
                'category': 'Invalid Phone',
                'sheet': ip['sheet'],
                'row': ip['row'],
                'column': ip['col'],
                'value': str(ip['value']),
                'message': ip['issue']
            })
        
        # Date format issues
        for dfi in self.issues['date_format_issues']:
            out.append({
                'severity': 'warning',
                'category': 'Date Format',
                'sheet': dfi['sheet'],
                'row': dfi['row'],
                'column': dfi['col'],
                'value': str(dfi['value']),
                'message': dfi['issue']
            })
        
        # Enum violations
        for ev in self.issues['enum_violations']:
            out.append({
                'severity': 'warning',
                'category': 'Enum Violation',
                'sheet': ev['sheet'],
                'row': ev['row'],
                'column': ev['col'],
                'value': str(ev['value']),
                'message': ev['issue']
            })
        
        # Missing data
        for md in self.issues['missing_data']:
            out.append({
                'severity': 'critical',
                'category': 'Missing Data',
                'sheet': md['sheet'],
                'row': md['row'],
                'column': md['col'],
                'value': str(md['value']),
                'message': md['issue']
            })
        
        # Duplicate phones
        for dp in self.issues['duplicate_phones']:
            out.append({
                'severity': 'warning',
                'category': 'Duplicate Value',
                'sheet': dp['sheet'],
                'row': dp['row'],
                'column': dp['col'],
                'value': str(dp['value']),
                'message': dp['issue']
            })
        
        # Time conflicts
        for tc in self.issues['time_conflicts']:
            out.append({
                'severity': 'warning',
                'category': 'Time Conflict',
                'sheet': tc['sheet'],
                'row': tc['row'],
                'column': tc['col'],
                'value': str(tc['value']),
                'message': tc['issue']
            })
        
        # Shift conflicts
        for sc in self.issues['shift_conflicts']:
            out.append({
                'severity': 'warning',
                'category': 'Shift Conflict',
                'sheet': sc['sheet'],
                'row': sc['row'],
                'column': sc['col'],
                'value': str(sc['value']),
                'message': sc['issue']
            })
        
        # Supplier issues
        for si in self.issues['supplier_issues']:
            out.append({
                'severity': si['severity'],
                'category': 'Supplier Issue',
                'sheet': si['sheet'],
                'row': si['row'],
                'column': si['col'],
                'value': str(si['value']),
                'message': si['issue']
            })
        
        # Capacity issues
        for ci in self.issues['capacity_issues']:
            out.append({
                'severity': 'critical',
                'category': 'Capacity Issue',
                'sheet': ci['sheet'],
                'row': ci['row'],
                'column': ci['col'],
                'value': str(ci['value']),
                'message': ci['issue']
            })
        
        # Vehicle status issues
        for vs in self.issues['vehicle_status_issues']:
            out.append({
                'severity': 'warning',
                'category': 'Vehicle Status',
                'sheet': vs['sheet'],
                'row': vs['row'],
                'column': vs['col'],
                'value': vs['value'],
                'message': vs['issue']
            })
        
        # Insurance expiry issues
        for ie in self.issues['insurance_expiry_issues']:
            out.append({
                'severity': 'critical',
                'category': 'Insurance Expired',
                'sheet': ie['sheet'],
                'row': ie['row'],
                'column': ie['col'],
                'value': ie['value'],
                'message': f"Expired {ie['days_overdue']} days ago"
            })
        
        # Expiry alerts
        for ea in self.issues['expiry_alerts']:
            out.append({
                'severity': 'warning',
                'category': 'Expiry Alert',
                'sheet': ea['sheet'],
                'row': ea['row'],
                'column': ea['col'],
                'value': ea['value'],
                'message': f"Expires in {ea['days_until_expiry']} days"
            })
        
        # Shift upgrades
        for su in self.issues['shift_upgrades']:
            out.append({
                'severity': 'info',
                'category': 'Shift Upgrade',
                'sheet': su['sheet'],
                'row': su['row'],
                'column': su['col'],
                'value': su['value'],
                'message': su['issue']
            })
        
        # Add other issue types similarly...
        
        return out

    def _compute_score(self) -> int:
        """Compute quality score based on issues."""
        total_points = 100
        issue_points = 0
        
        # Deduct points for various issues
        issue_points += len(self.issues['invalid_phones']) * 3  # 3 points per invalid phone
        issue_points += len(self.issues['missing_data']) * 5   # 5 points per missing data
        issue_points += len(self.issues['enum_violations']) * 2 # 2 points per enum violation
        issue_points += len(self.issues['time_conflicts']) * 4  # 4 points per time conflict
        issue_points += len(self.issues['date_format_issues']) * 1 # 1 point per date issue
        issue_points += len(self.issues['capacity_issues']) * 3 # 3 points per capacity issue
        issue_points += len(self.issues['insurance_expiry_issues']) * 5 # 5 points per expired insurance
        issue_points += len(self.issues['shift_conflicts']) * 2 # 2 points per shift conflict
        issue_points += len(self.issues['supplier_issues']) * 2 # 2 points per supplier issue
        
        # Bonus points for good practices (up to 10 bonus points)
        bonus_points = min(len(self.issues['shift_upgrades']) * 0.5, 10)
        
        total_deduction = min(issue_points, 95)  # Cap at 95 points deducted
        final_score = max(5, min(100, 100 - total_deduction + bonus_points))  # Minimum score is 5, max is 100
        
        return int(final_score)

    def apply_fixes(self, output_path: str) -> bool:
        """Apply all fixes and save to new file."""
        try:
            # Reload the original workbook
            wb = load_workbook(self.file_path)
            
            # Apply all fixes
            for fix in self.fixes:
                sheet_name = fix['sheet']
                if sheet_name not in wb.sheetnames:
                    continue
                
                ws = wb[sheet_name]
                # Find header row and column mapping again
                hrow, cmap = self.find_header(ws)
                if not hrow:
                    continue
                
                col_idx = cmap.get(fix['col'])
                if not col_idx:
                    continue
                
                # Apply the fix
                cell = ws.cell(fix['row'], col_idx)
                cell.value = fix['new']
                
                # Add comment to explain the fix
                cell.comment = Comment(
                    f"Codefy Auto-Fix:\n• Reason: {fix['reason']}\n"
                    f"• Original: '{to_str(fix['old'])}'\n"
                    f"• Changed to: '{to_str(fix['new'])}'", 
                    "Codefy Analyzer"
                )
                
                # Highlight fixed cells
                cell.fill = PatternFill(start_color="FFFACD", end_color="FFFACD", fill_type="solid")
            
            # Save the modified workbook
            wb.save(output_path)
            return True
        except Exception as e:
            print(f"Error applying fixes: {e}")
            return False

    def export_fixed(self, output_path: str):
        """Export the fixed file with audit log."""
        try:
            # Apply fixes first
            success = self.apply_fixes(output_path)
            if not success:
                raise Exception("Failed to apply fixes")
            
            # Reload the fixed workbook to add audit log
            wb = load_workbook(output_path)
            
            # Create audit log sheet
            audit_sheet_name = "Audit_Log | سجل التعديلات"
            if audit_sheet_name in wb.sheetnames:
                del wb[audit_sheet_name]
            
            audit_ws = wb.create_sheet(title=audit_sheet_name)
            audit_ws.sheet_view.rightToLeft = True
            
            # Add headers
            headers = ["Timestamp | الوقت", "Sheet | الورقة", "Row | الصف",
                      "Column | العمود", "Original | القيمة السابقة",
                      "Fixed | القيمة المصححة", "Reason | السبب"]
            audit_ws.append(headers)
            
            # Style headers
            header_font = Font(bold=True, color="FFFFFF", size=11)
            header_fill = PatternFill(start_color="4da6ff", end_color="4da6ff", fill_type="solid")
            for c in range(1, len(headers)+1):
                cell = audit_ws.cell(1, c)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Add fix records
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for fix in self.fixes:
                audit_ws.append([
                    now,
                    fix['sheet'],
                    fix['row'],
                    fix['col'],
                    to_str(fix['old']),
                    to_str(fix['new']),
                    fix['reason']
                ])
            
            # Set column widths
            for c in range(1, len(headers)+1):
                audit_ws.column_dimensions[get_column_letter(c)].width = 26
            
            # Freeze header row
            audit_ws.freeze_panes = "A2"
            
            # Save the workbook with audit log
            wb.save(output_path)
            
            # Return result
            return {
                'applied_fixes': len(self.fixes),
                'output_path': output_path,
                'success': True
            }
        except Exception as e:
            print(f"Error exporting fixed file: {e}")
            raise e


def validate_excel_file(file_path: str) -> Dict[str, Any]:
    """
    Main function to validate an Excel file and return analysis results.
    
    Args:
        file_path: Path to the Excel file to validate
        
    Returns:
        Dictionary containing analysis results
    """
    validator = CodefyDataValidator(file_path)
    
    if not validator.analyze():
        return {
            'error': 'Failed to analyze the file',
            'success': False
        }
    
    return {
        'success': True,
        'summary': validator.get_analysis_summary(),
        'issues': validator._all_issues(),
        'fixes_available': len(validator.fixes) > 0
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python CodefyDataValidator.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    results = validate_excel_file(file_path)
    
    if results['success']:
        print(f"File: {results['summary']['file_name']}")
        print(f"Quality Score: {results['summary']['quality_score']}/100")
        print(f"Total Rows: {results['summary']['total_rows']}")
        print(f"Issues Found: {sum(results['summary']['issues'].values())}")
        print("\nDetailed Issues:")
        for issue in results['issues'][:10]:  # Show first 10 issues
            print(f"  {issue['severity'].upper()}: {issue['message']} "
                  f"(Sheet: {issue['sheet']}, Row: {issue['row']})")
    else:
        print(f"Error: {results['error']}")
