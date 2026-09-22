#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              C O D E F Y E R P  ·  D A T A  V A L I D A T O R               ║
║              🌊  ADVANCED EXCEL ANALYSIS FOR EGYPTIAN ERP SYSTEM             ║
║──────────────────────────────────────────────────────────────────────────────║
║  This module provides comprehensive Excel data validation and analysis      ║
║  for CodefyERP system, with specialized handling for Egyptian business      ║
║  requirements including phone numbers, Arabic text, and scheduling data.     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import math
import urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union

try:
    import pandas as pd
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font
    from openpyxl.comments import Comment
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install with: pip install pandas openpyxl")
    exit(1)

# Define Arabic-Indic digit mapping
ARABIC_INDIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

# Egyptian phone regex
EG_PHONE_RE = re.compile(r'^01[0125][0-9]{8}$')

# Time conflict modes
TIME_CONFLICT_MODE_NORMALIZE = 'normalize'
TIME_CONFLICT_MODE_FLAGONLY = 'flag_only'

# Column constants
COL_DRIVER_NAME = 'driver_name'
COL_DRIVER_PHONE = 'driver_phone'
COL_SUPPLIER_NAME = 'supplier_name'
COL_SUPPLIER_PHONE = 'supplier_phone'
COL_PLATE = 'plate_number'
COL_SHIFT = 'shift'
COL_SCHEDULE = 'schedule_name'
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

# ERP column specifications
ERP_COLUMN_SPEC = {
    COL_DRIVER_NAME: {'type': 'text', 'required': True},
    COL_DRIVER_PHONE: {'type': 'phone', 'required': True},
    COL_SUPPLIER_NAME: {'type': 'text'},
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
    """Normalize names by removing extra spaces and converting to lowercase."""
    if not name:
        return ''
    return re.sub(r'\s+', ' ', name.strip()).lower()


def is_phone_column_name(col_name: str) -> bool:
    """Check if column name likely represents a phone number."""
    col_lower = col_name.lower()
    return any(keyword in col_lower for keyword in ['phone', 'mobile', 'contact', 'tel', 'hp', 'gsm'])


def is_date_like_column(col_name: str, values: List[Any]) -> bool:
    """Check if column likely represents dates."""
    col_lower = col_name.lower()
    if any(keyword in col_lower for keyword in ['date', 'time', 'start', 'end', 'arrival', 'departure', 'expiry', 'maint']):
        return True
    
    # Check actual values for date-like patterns
    date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}', r'\d{2}-\d{2}-\d{4}']
    date_values = 0
    for val in values:
        if val and isinstance(val, str):
            if any(re.search(pattern, val) for pattern in date_patterns):
                date_values += 1
    return date_values > len(values) * 0.3  # At least 30% of values look like dates


def normalize_time_string(time_str: str, to_hhmm: bool = False, convert_12h: bool = True) -> Optional[str]:
    """Normalize time string to standard format."""
    if not time_str:
        return None
    
    s = to_str(time_str)
    
    # Handle Excel time values
    if isinstance(time_str, (float, int)) and time_str < 1:
        # Excel time as fraction of day
        hours = int(time_str * 24)
        minutes = int((time_str * 24 * 60) % 60)
        return f"{hours:02d}:{minutes:02d}"
    
    # Handle various time formats
    time_formats = [
        '%H:%M:%S', '%I:%M:%S %p', '%H:%M', '%I:%M %p', '%H%M', '%I%M %p',
        '%H.%M', '%I.%M %p', '%H:%M:%S.%f', '%I:%M:%S.%f %p'
    ]
    
    for fmt in time_formats:
        try:
            dt = datetime.strptime(s, fmt)
            if to_hhmm:
                return dt.strftime('%H:%M')
            return dt.strftime('%H:%M:%S')
        except ValueError:
            continue
    
    return None


def offset_time_min(time_str: str, minutes: int) -> Optional[str]:
    """Offset a time by specified minutes."""
    if not time_str:
        return None
    
    s = to_str(time_str)
    
    # Parse time
    time_formats = ['%H:%M:%S', '%H:%M', '%I:%M %p', '%I:%M:%S %p']
    dt = None
    
    for fmt in time_formats:
        try:
            dt = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    
    if not dt:
        return None
    
    # Apply offset
    total_minutes = dt.hour * 60 + dt.minute + minutes
    new_hour = (total_minutes // 60) % 24
    new_minute = total_minutes % 60
    
    return f"{new_hour:02d}:{new_minute:02d}"


class PhoneValidator:
    """Validate and classify Egyptian phone numbers."""
    
    @staticmethod
    def classify(raw):
        s = to_str(raw)
        if not s: 
            return 'empty', None, ''
        
        sn = s.translate(ARABIC_INDIC_DIGITS)
        d = re.sub(r'\D', '', sn)
        
        if not d:
            if is_arabic(s):
                return 'arabic', None, f'ملاحظة نصية في عمود الهاتف: {s[:25]}'
            return 'empty', None, ''
        
        if len(d) == 12 and d.startswith('20') and EG_PHONE_RE.match('0' + d[2:]):
            return 'fixable', '0' + d[2:], 'تم تحويل رمز الدولة +20'
        
        if len(d) == 14 and d.startswith('0020') and EG_PHONE_RE.match('0' + d[4:]):
            return 'fixable', '0' + d[4:], 'تم تحويل رمز الدولة 0020'
        
        if len(d) == 11:
            if EG_PHONE_RE.match(d):
                if d != s: 
                    return 'fixable', d, 'تم التطبيع إلى هاتف مكون من 11 رقماً'
                return 'ok', d, ''
            
            return 'invalid', None, (
                f'رمز غير صالح "{d[:3]}" — يجب أن يبدأ بـ 010/011/012/015')
        
        if len(d) == 10:
            cand = '0' + d
            if EG_PHONE_RE.match(cand):
                return 'fixable', cand, f'تم الإصلاح بإضافة صفر في البداية → {cand}'
            return 'invalid', None, f'10 أرقام برمز غير صالح "{cand[:3]}"'
        
        if len(d) > 11:
            return 'invalid', None, (
                f'عدد كبير جداً من الأرقام ({len(d)}) — يجب أن يكون 11 رقماً بالضبط (مثلاً 01099831981)')
        
        return 'short', None, (
            f'🚩 الهاتف يحتوي فقط على {len(d)} رقم(أرقام) — مطلوب 11 رقماً بالضبط. '
            f'القيمة غير مُعدّلة؛ تم تعليم الخلية باللون الأحمر للمراجعة اليدوية.')

    @staticmethod
    def effective(phone_value):
        """Get effective phone number after classification."""
        status, fixed, msg = PhoneValidator.classify(phone_value)
        if status == 'ok' or status == 'fixable':
            return fixed
        return None


class DateValidator:
    """Validate and classify date formats."""
    
    @staticmethod
    def classify(raw):
        s = to_str(raw)
        if not s: 
            return 'empty', None, ''
        
        # Handle datetime objects
        if isinstance(raw, (datetime, date)) and not isinstance(raw, bool):
            if isinstance(raw, datetime):
                return 'ok', raw.strftime('%Y-%m-%d'), 'تم تحويل كائن التاريخ'
            return 'ok', raw.strftime('%Y-%m-%d'), 'تم تحويل كائن التاريخ'
        
        # Try common date formats
        formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
            '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',
            '%m-%d-%Y', '%m/%d/%Y', '%m.%d.%Y',
            '%d-%m-%y', '%d/%m/%y', '%d.%m/%y',
            '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S',
            '%Y-%m-%d %H:%M', '%d-%m-%Y %H:%M'
        ]
        
        for fmt in formats:
            try:
                d = datetime.strptime(s, fmt)
                # Convert to standard format
                s_dash = s.replace('/', '-').replace('.', '-')
                if fmt.count('-') == 2 and s_dash != s:
                    return 'fixable', d.strftime('%Y-%m-%d'), 'تم تطبيع الفواصل'
                if d.strftime('%Y-%m-%d') != s:
                    return 'fixable', d.strftime('%Y-%m-%d'), 'تم توحيد التنسيق'
                return 'ok', s, ''
            except ValueError:
                continue
        
        # Try flexible parsing
        try:
            # Replace various separators with dashes
            s_dash = re.sub(r'[/\.\\]', '-', s)
            # Try different format variations
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']:
                try:
                    d = datetime.strptime(s_dash, fmt)
                    if '%y' in fmt and d.year < 1950: 
                        d = d.replace(year=d.year + 2000)
                    return 'fixable', d.strftime('%Y-%m-%d'), 'تم تطبيع الفواصل'
                except ValueError: 
                    continue
        except Exception: 
            pass
        
        return 'invalid', None, f'تاريخ غير معروف: "{s[:32]}"'


class ShiftEngine:
    """Advanced shift processing engine with ordinal recognition."""
    
    def __init__(self, settings=None):
        self.settings = settings
        # Base shift patterns
        self.base_patterns = dict(SHIFT_BASE_PATTERNS)
        
        # Ordinal patterns
        self.ordinals = list(SHIFT_ORDINALS)
        
        if settings:
            for base_display, triggers in settings.custom_shift_bases.items():
                if isinstance(triggers, list) and triggers:
                    self.base_patterns[base_display] = triggers
            for entry in settings.custom_ordinals:
                try:
                    kws, canon, short = entry
                    self.ordinals.append((list(kws), canon, short))
                except Exception: 
                    continue

    def _detect_base(self, shift_value):
        """Detect base shift from value."""
        if not shift_value:
            return None
        s = normalize_name(to_str(shift_value))
        for base, keywords in self.base_patterns.items():
            if any(keyword in s for keyword in keywords):
                return base
        return None

    def _detect_ordinal(self, schedule_value):
        """Detect ordinal from schedule value."""
        if not schedule_value:
            return None
        s = normalize_name(to_str(schedule_value))
        for keywords, canonical, short in self.ordinals:
            if any(keyword in s for keyword in keywords):
                return canonical, short
        return None

    def _normalize_schedule_first_word(self, schedule_value):
        """Normalize the first word of schedule value."""
        if not schedule_value:
            return None
        parts = to_str(schedule_value).split(None, 1)  # Split on first whitespace
        if not parts:
            return None
        first_word = parts[0]
        normalized_first = normalize_name(first_word)
        
        # Check if first word needs normalization
        for base, keywords in self.base_patterns.items():
            if normalized_first in keywords and base.lower() != normalized_first:
                if len(parts) > 1:
                    return f"{base} {parts[1]}"
                return base
        return None

    def process(self, shift_value, schedule_value):
        """Process shift and schedule values to generate improvements."""
        base = self._detect_base(shift_value)
        ordinal = self._detect_ordinal(schedule_value) if base else None
        
        new_shift = None
        new_schedule = None
        reasons = []
        
        if base and ordinal:
            canonical, short = ordinal
            new_shift = f"{base} - {short}"
            reasons.append(f"shift '{base}' + ordinal '{short}' → '{new_shift}'")
        
        normalized_schedule = self._normalize_schedule_first_word(schedule_value)
        if normalized_schedule and normalized_schedule != to_str(schedule_value):
            new_schedule = normalized_schedule
            reasons.append(f"schedule first-word normalized")
        
        if not new_shift and not new_schedule: 
            return None
        
        return {
            'new_shift': new_shift, 
            'new_schedule': new_schedule,
            'reason': ' · '.join(reasons), 
            'base': base,
            'ordinal': ordinal[0] if ordinal else None
        }


class MainSuppliersManager:
    """Manage main/internal suppliers and their configurations."""
    
    def __init__(self):
        self.main_suppliers = set()
        self.supplier_configs = {}
        
    def add_main_supplier(self, supplier_name):
        """Add a main supplier to the list."""
        self.main_suppliers.add(normalize_name(supplier_name))
        
    def configure_supplier(self, supplier_name, config):
        """Configure a supplier with specific rules."""
        self.supplier_configs[normalize_name(supplier_name)] = config
        
    def is_main_supplier(self, supplier_name):
        """Check if supplier is a main/internal supplier."""
        normalized = normalize_name(supplier_name)
        return any(internal in normalized for internal in self.main_suppliers) or \
               any(internal.lower() in normalized for internal in ['codefy', 'internal', 'main', 'رئيسي', 'داخلي'])


class TimeConflictDetector:
    """Advanced time conflict detection and resolution."""
    
    def __init__(self, offset_minutes=30, target_column=COL_DROPOFF_TIME, mode=TIME_CONFLICT_MODE_NORMALIZE):
        self.offset_minutes = offset_minutes
        self.target_column = target_column
        self.mode = mode
        
    def detect_conflict(self, pickup_time, dropoff_time):
        """Detect if there's a time conflict."""
        if not pickup_time or not dropoff_time:
            return False
        return to_str(pickup_time) == to_str(dropoff_time)
        
    def suggest_resolution(self, target_time):
        """Suggest a resolution for the conflict."""
        return offset_time_min(target_time, self.offset_minutes)


class CodefyDataValidator:
    """
    Comprehensive Excel data validator for CodefyERP system.
    Performs deep analysis of Excel files to identify issues before import.
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.wb = None
        self.sheets_data = {}
        self.fixes = []
        self.issues = {
            'invalid_phones': [],
            'date_format_issues': [],
            'enum_violations': [],
            'missing_data': [],
            'duplicate_phones': [],
            'time_conflicts': [],
            'time_normalizations': [],
            'shift_upgrades': [],
            'internal_supplier_fixes': [],
            'erp_issues': [],
            'expiry_alerts': [],
            'driver_conflicts': [],
            'phone_conflicts': [],
            'capacity_issues': [],
            'vehicle_status_issues': [],
            'license_expiry_issues': [],
            'insurance_expiry_issues': []
        }
        self.red_flag_cells = []
        self.time_conflict_enabled = True
        self.time_conflict_mode = TIME_CONFLICT_MODE_NORMALIZE
        self.time_conflict_offset = 30  # minutes
        self.time_conflict_target = COL_DROPOFF_TIME
        self.shift_engine_enabled = True
        self.shift_engine = ShiftEngine()
        self.time_normalize_enabled = True
        self.time_convert_12h = True
        self.main_suppliers_manager = MainSuppliersManager()
        self.time_conflict_detector = TimeConflictDetector(
            offset_minutes=self.time_conflict_offset,
            target_column=self.time_conflict_target,
            mode=self.time_conflict_mode
        )
        
        # Add default main suppliers
        self.main_suppliers_manager.add_main_supplier("Codefy Internal")
        self.main_suppliers_manager.add_main_supplier("النظام الداخلي")
        self.main_suppliers_manager.add_main_supplier("الادارة")
        
    def load_workbook(self):
        """Load the Excel workbook."""
        try:
            self.wb = load_workbook(self.file_path)
            return True
        except Exception as e:
            print(f"Error loading workbook: {e}")
            return False

    def find_header(self, ws):
        """Find header row and map column names to indices."""
        # Look for header row (first row with meaningful text)
        for r_idx in range(1, min(10, ws.max_row + 1)):  # Check first 10 rows
            row_values = [ws.cell(r_idx, c).value for c in range(1, min(20, ws.max_column + 1))]
            non_empty = [v for v in row_values if v and to_str(v)]
            if len(non_empty) >= 3:  # At least 3 non-empty cells in row
                # Create mapping from column names to indices
                cmap = {}
                for c_idx, cell_value in enumerate(row_values, 1):
                    col_name = normalize_name(to_str(cell_value))
                    if col_name:
                        # Map to standard column names if possible
                        std_col = self._map_to_standard_column(col_name)
                        if std_col:
                            cmap[std_col] = c_idx
                        else:
                            cmap[f'_{col_name}'] = c_idx  # Custom column
                return r_idx, cmap
        return None, {}

    def _map_to_standard_column(self, col_name: str) -> Optional[str]:
        """Map column name to standard ERP column."""
        col_lower = col_name.lower()
        mappings = {
            'driver_name': ['driver', 'drivername', 'driver_name', 'chauffeur', 'سائق', 'السائق'],
            'driver_phone': ['driver_phone', 'driverphone', 'phone', 'mobile', 'contact', 'هاتف', 'رقم الهاتف'],
            'supplier_name': ['supplier', 'suppliername', 'supplier_name', 'vendor', 'provider', 'مورد', 'المورد'],
            'supplier_phone': ['supplier_phone', 'supplierphone', 'sup_phone', 'vendor_phone', 'مورد_الهاتف'],
            'plate_number': ['plate', 'platenumber', 'plate_number', 'vehicle', 'car', 'رقم_لوحة', 'اللوحة'],
            'shift': ['shift', 'shift_name', 'shiftname', 'turn', 'وردية', 'الوردية'],
            'schedule_name': ['schedule', 'schedulename', 'schedule_name', 'program', 'جدول', 'الجدول'],
            'route': ['route', 'routename', 'route_name', 'path', 'طريق', 'ال маршрут'],
            'pickup_arrival': ['pickup_arr', 'pickup_arrival', 'pick_arr', 'arr_pickup', 'وصول_الاستلام'],
            'pickup_departure': ['pickup_dep', 'pickup_departure', 'pick_dep', 'dep_pickup', 'مغادرة_الاستلام'],
            'dropoff_arrival': ['dropoff_arr', 'dropoff_arrival', 'drop_arr', 'arr_dropoff', 'وصول_التسليم'],
            'dropoff_time': ['dropoff', 'dropoff_time', 'drop_time', 'delivery_time', 'time_drop', 'وقت_التسليم'],
            'working_days': ['working_days', 'workdays', 'days', 'operating_days', 'ايام', 'أيام_العمل'],
            'direction': ['direction', 'dir', 'orientation', 'اتجاه', 'الاتجاه'],
            'employee_type': ['emp_type', 'employee_type', 'emptype', 'staff_type', 'نوع_الموظف', 'نوع_العامل'],
            'start_date': ['start_date', 'start', 'begin', 'from', 'تاريخ_البدء', 'البدء'],
            'end_date': ['end_date', 'end', 'finish', 'to', 'until', 'تاريخ_الانتهاء', 'الانتهاء'],
            'service_type': ['service_type', 'service', 'type', 'kind', 'نوع_الخدمة', 'نوع'],
            'capacity': ['capacity', 'cap', 'seats', 'passengers', 'السعة', 'عدد_الركاب'],
            'vehicle_type': ['vehicle_type', 'v_type', 'type', 'model', 'نوع_المركبة', 'نوع_العربية'],
            'driver_license': ['license', 'driver_license', 'license_no', 'رخصة_القيادة', 'الرخصة'],
            'insurance_expiry': ['insurance_exp', 'insurance_expiry', 'insurance', 'insurance_end', 'انتهاء_التأمين'],
            'maintenance_date': ['maint_date', 'maintenance', 'maint', 'صيان', 'service_date', 'Maintenance'],
            'fuel_type': ['fuel_type', 'fuel', 'gas', 'petrol', 'diesel', 'نوع_الوقود', 'الوقود'],
            'vehicle_status': ['status', 'vehicle_status', 'v_status', 'state', 'condition', 'الحالة']
        }
        
        for std_col, patterns in mappings.items():
            if any(pattern in col_lower for pattern in patterns):
                return std_col
        return None

    def read_sheet(self, ws, hrow, cmap):
        """Read sheet data into records."""
        recs = []
        for r in range(hrow + 1, ws.max_row + 1):
            rec = {'_row': r}
            for name, ci in cmap.items():
                cell = ws.cell(r, ci)
                rec[name] = cell.value
            # Skip completely empty rows
            if all(to_str(v) == '' for k, v in rec.items() if k != '_row'): 
                continue
            recs.append(rec)
        return recs

    def analyze(self):
        """Perform comprehensive analysis of the Excel file."""
        if not self.load_workbook():
            return False
        
        # Load all sheets
        self._load_all()
        
        # Run all validation checks
        self._supporting_checks()
        self._validate_enums()
        self._validate_pickup_dropoff_time()
        self._upgrade_shifts()
        self._normalize_times()
        self._fix_schedule_directions()
        self._normalize_working_days()
        self._internal_supplier_normalization()
        self._duplicate_driver_phones()
        self._scan_all_dates_deep()
        self._validate_capacity_and_vehicle_status()
        self._check_expiry_dates()
        
        return True

    def _load_all(self):
        """Load all sheets into internal data structure."""
        for sheet in self.wb.sheetnames:
            ws = self.wb[sheet]
            hrow, cmap = self.find_header(ws)
            if not hrow:
                self.sheets_data[sheet] = {
                    'records': [], 
                    'cmap': {},
                    'hrow': None, 
                    'skipped': True
                }
                continue
            
            recs = self.read_sheet(ws, hrow, cmap)
            self.sheets_data[sheet] = {
                'records': recs, 
                'cmap': cmap,
                'hrow': hrow, 
                'skipped': False
            }

    def _supporting_checks(self):
        """Run basic validation checks."""
        self._phone_validation()
        self._missing_data()

    def _phone_validation(self):
        """Validate phone numbers in all sheets."""
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            phone_cols = self._all_phone_columns(info['cmap'])
            for rec in info['records']:
                for col in phone_cols:
                    val = rec.get(col)
                    st, fx, msg = PhoneValidator.classify(val)
                    
                    if st == 'empty' or st == 'ok': 
                        continue
                    
                    if st == 'arabic':
                        self.issues['invalid_phones'].append({
                            'sheet': sheet, 
                            'row': rec['_row'], 
                            'col': col,
                            'value': to_str(val), 
                            'reason': msg,
                            'kind': 'arabic', 
                            'fixable': False
                        })
                        self.red_flag_cells.append((sheet, rec['_row'], col, msg))
                        continue
                    
                    if st == 'fixable':
                        self.fixes.append({
                            'sheet': sheet, 
                            'row': rec['_row'],
                            'col': col, 
                            'old': val, 
                            'new': fx,
                            'reason': msg
                        })
                        continue
                    
                    if st == 'short':
                        self.issues['invalid_phones'].append({
                            'sheet': sheet, 
                            'row': rec['_row'], 
                            'col': col,
                            'value': to_str(val), 
                            'reason': msg,
                            'kind': 'short', 
                            'fixable': True
                        })
                        self.red_flag_cells.append((sheet, rec['_row'], col, msg))
                        continue
                    
                    # Invalid cases
                    self.issues['invalid_phones'].append({
                        'sheet': sheet, 
                        'row': rec['_row'], 
                        'col': col,
                        'value': to_str(val), 
                        'reason': msg,
                        'kind': 'invalid', 
                        'fixable': False
                    })
                    self.red_flag_cells.append((sheet, rec['_row'], col, msg))

    def _all_phone_columns(self, cmap):
        """Get all columns that might contain phone numbers."""
        cols = set()
        for c in cmap.keys():
            if c.startswith('_'): 
                continue
            if c in (COL_DRIVER_PHONE, COL_SUPPLIER_PHONE):
                cols.add(c)
                continue
            if is_phone_column_name(c): 
                cols.add(c)
                continue
        return cols

    def _missing_data(self):
        """Check for missing critical data."""
        critical = [COL_DRIVER_NAME, COL_DRIVER_PHONE, COL_PLATE, COL_SHIFT, COL_ROUTE]
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            recs = info['records']
            for col in critical:
                if not recs or col not in info['cmap']: 
                    continue
                for r in recs:
                    if not to_str(r.get(col)):
                        self.issues['missing_data'].append({
                            'sheet': sheet, 
                            'row': r['_row'], 
                            'col': col
                        })

    def _validate_enums(self):
        """Validate enum values."""
        enum_cols = {c: spec['enum'] for c, spec in ERP_COLUMN_SPEC.items()
                     if 'enum' in spec}
        
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            for col, allowed in enum_cols.items():
                if col not in info['cmap']: 
                    continue
                allowed_norm = {a.lower() for a in allowed}
                
                for rec in info['records']:
                    v = to_str(rec.get(col))
                    if not v: 
                        continue
                    if v.lower() not in allowed_norm:
                        if col == 'schedule_direction' and v.lower() in ('round_trip','both'):
                            continue
                        self.issues['enum_violations'].append({
                            'sheet': sheet, 
                            'row': rec['_row'],
                            'col': col, 
                            'value': v,
                            'allowed': ERP_COLUMN_SPEC[col]['enum']
                        })

    def _validate_pickup_dropoff_time(self):
        """Validate pickup/dropoff time conflicts."""
        if not self.time_conflict_enabled:
            return
        
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            pick_col = next((c for c in (COL_PICKUP_ARR, COL_PICKUP_DEP)
                             if c in cmap), None)
            drop_col = next((c for c in (COL_DROPOFF_ARR, COL_DROPOFF_TIME)
                             if c in cmap), None)
            
            if not pick_col or not drop_col: 
                continue
            
            for rec in info['records']:
                pv = to_str(rec.get(pick_col))
                dv = to_str(rec.get(drop_col))
                
                if not pv or not dv: 
                    continue
                if not self.time_conflict_detector.detect_conflict(pv, dv): 
                    continue
                
                target_col = self.time_conflict_target
                if target_col not in cmap:
                    target_col = drop_col
                
                target_val = to_str(rec.get(target_col)) if target_col != drop_col else dv
                suggested = self.time_conflict_detector.suggest_resolution(target_val)
                
                conflict_info = {
                    'sheet': sheet,
                    'row': rec['_row'],
                    'pickup_col': pick_col,
                    'dropoff_col': drop_col,
                    'pickup': pv,
                    'dropoff': dv,
                    'target_col': target_col,
                    'suggested_dropoff': suggested,
                    'mode': self.time_conflict_mode,
                    'offset': self.time_conflict_offset
                }
                
                if self.time_conflict_mode == TIME_CONFLICT_MODE_FLAGONLY:
                    conflict_info['mode'] = 'FLAG_ONLY'
                
                self.issues['time_conflicts'].append(conflict_info)

    def _upgrade_shifts(self):
        """Upgrade shifts using the shift engine."""
        if not self.shift_engine_enabled or not self.shift_engine: 
            return
        
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            if COL_SHIFT not in cmap or COL_SCHEDULE not in cmap: 
                continue
            
            for rec in info['records']:
                sv = rec.get(COL_SHIFT)
                schv = rec.get(COL_SCHEDULE)
                
                if not to_str(sv) and not to_str(schv): 
                    continue
                
                res = self.shift_engine.process(sv, schv)
                if not res: 
                    continue
                
                if res['new_shift']:
                    self.fixes.append({
                        'sheet': sheet, 
                        'row': rec['_row'], 
                        'col': COL_SHIFT,
                        'old': sv, 
                        'new': res['new_shift'],
                        'reason': f"Shift Engine — {res['reason']}"
                    })
                    rec[COL_SHIFT] = res['new_shift']
                    self.issues['shift_upgrades'].append({
                        'sheet': sheet,
                        'row': rec['_row'],
                        'old_shift': to_str(sv),
                        'new_shift': res['new_shift'],
                        'old_schedule': to_str(schv),
                        'new_schedule': to_str(res['new_schedule']) if res['new_schedule'] else to_str(schv),
                        'reason': res['reason']
                    })
                
                if res['new_schedule']:
                    self.fixes.append({
                        'sheet': sheet, 
                        'row': rec['_row'], 
                        'col': COL_SCHEDULE,
                        'old': schv, 
                        'new': res['new_schedule'],
                        'reason': f"Shift Engine — {res['reason']}"
                    })
                    rec[COL_SCHEDULE] = res['new_schedule']

    def _normalize_times(self):
        """Normalize time formats."""
        if not self.time_normalize_enabled:
            return
        
        TIME_COLUMNS = [
            (COL_PICKUP_ARR, 'pickup_arrival', 'Pickup Arrival'),
            (COL_PICKUP_DEP, 'pickup_departure', 'Pickup Departure'),
            (COL_DROPOFF_ARR, 'dropoff_arrival', 'Dropoff Arrival'),
            (COL_DROPOFF_TIME, 'dropoff_time', 'Dropoff Time')
        ]
        
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            for col, _, _ in TIME_COLUMNS:
                if col not in cmap: 
                    continue
                for rec in info['records']:
                    raw = rec.get(col)
                    if not to_str(raw): 
                        continue
                    
                    norm = normalize_time_string(raw,
                                              to_hhmm=True,
                                              convert_12h=self.time_convert_12h)
                    
                    if norm and norm != to_str(raw):
                        self.fixes.append({
                            'sheet': sheet, 
                            'row': rec['_row'], 
                            'col': col,
                            'old': raw, 
                            'new': norm,
                            'reason': f'Time normalized → {norm}'
                        })
                        self.issues['time_normalizations'].append({
                            'sheet': sheet, 
                            'row': rec['_row'], 
                            'col': col,
                            'old': to_str(raw), 
                            'new': norm
                        })
                        rec[col] = norm

    def _fix_schedule_directions(self):
        """Fix schedule directions based on schedule names."""
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            if COL_DIRECTION not in info['cmap']: 
                continue
            if COL_SCHEDULE not in info['cmap']: 
                continue
            
            for rec in info['records']:
                sched = to_str(rec.get(COL_SCHEDULE))
                if not sched: 
                    continue
                
                expected = self._detect_direction_from_schedule(sched)
                if not expected: 
                    continue
                
                current = to_str(rec.get(COL_DIRECTION))
                if current == expected: 
                    continue
                
                self.fixes.append({
                    'sheet': sheet, 
                    'row': rec['_row'], 
                    'col': COL_DIRECTION,
                    'old': current, 
                    'new': expected,
                    'reason': f"From schedule_name '{sched[:30]}'"
                })

    def _detect_direction_from_schedule(self, schedule_name: str) -> Optional[str]:
        """Detect direction from schedule name."""
        s = normalize_name(schedule_name)
        if 'north' in s or 'شمال' in s:
            return 'north'
        if 'south' in s or 'جنوب' in s:
            return 'south'
        if 'east' in s or 'شرق' in s:
            return 'east'
        if 'west' in s or 'غرب' in s:
            return 'west'
        if any(word in s for word in ['round', 'both', '往返', 'both ways', 'ذهاب وعودة', '往返']):
            return 'round_trip'
        return None

    def _normalize_working_days(self):
        """Normalize working days."""
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            if COL_WORKING_DAYS not in info['cmap']: 
                continue
            
            for rec in info['records']:
                raw = rec.get(COL_WORKING_DAYS)
                if not to_str(raw): 
                    continue
                
                norm = self.normalize_working_days(raw)
                if norm and norm != to_str(raw):
                    self.fixes.append({
                        'sheet': sheet, 
                        'row': rec['_row'],
                        'col': COL_WORKING_DAYS,
                        'old': raw, 
                        'new': norm,
                        'reason': 'Normalized working days'
                    })

    def normalize_working_days(self, raw):
        """Normalize working days string."""
        s = to_str(raw)
        if not s: 
            return ''
        
        s = s.translate(ARABIC_INDIC_DIGITS)
        parts = WORKING_DAYS_SEPARATORS.split(s)
        found = set()
        
        for p in parts:
            p_clean = to_str(p).lower()
            p_clean = re.sub(r'\bو\b', ' ', p_clean)
            p_clean = re.sub(r'\band\b', ' ', p_clean).strip()
            if p_clean.startswith('و'): 
                p_clean = p_clean[1:].strip()
            if p_clean.endswith('و'): 
                p_clean = p_clean[:-1].strip()
            if not p_clean: 
                continue
            
            if p_clean in DAY_ALIAS_LOOKUP:
                found.add(DAY_ALIAS_LOOKUP[p_clean])
                continue
            
            p_norm = normalize_name(p_clean)
            if p_norm in DAY_ALIAS_LOOKUP:
                found.add(DAY_ALIAS_LOOKUP[p_norm])
                continue
        
        if not found:
            s_norm = normalize_name(s)
            for k_norm, v in DAY_ALIAS_LOOKUP.items():
                if k_norm and k_norm in s_norm: 
                    found.add(v)
        
        return ', '.join(d for d in DAY_CANONICAL_ORDER if d in found)

    def _internal_supplier_normalization(self):
        """Normalize internal supplier data."""
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            col_sn = COL_SUPPLIER_NAME if COL_SUPPLIER_NAME in cmap else None
            col_sp = COL_SUPPLIER_PHONE if COL_SUPPLIER_PHONE in cmap else None
            col_et = COL_EMP_TYPE if COL_EMP_TYPE in cmap else None
            
            if not col_sn: 
                continue
            
            for rec in info['records']:
                raw_sn = to_str(rec.get(col_sn)).strip()
                if not raw_sn: 
                    continue
                if self.main_suppliers_manager.is_main_supplier(raw_sn): 
                    continue
                
                old_sn = rec.get(col_sn)
                if to_str(old_sn) != '':
                    self.fixes.append({
                        'sheet': sheet, 
                        'row': rec['_row'],
                        'col': col_sn, 
                        'old': old_sn, 
                        'new': '',
                        'reason': f'Main supplier "{raw_sn}" → cleared'
                    })
                    rec[col_sn] = ''
                
                if col_sp:
                    old_sp = rec.get(col_sp)
                    if old_sp and to_str(old_sp) != '':
                        self.fixes.append({
                            'sheet': sheet, 
                            'row': rec['_row'],
                            'col': col_sp, 
                            'old': old_sp, 
                            'new': raw_sn,
                            'reason': f'Main supplier "{raw_sn}" → use supplier name as phone'
                        })
                        rec[col_sp] = raw_sn
                        
                        self.issues['internal_supplier_fixes'].append({
                            'sheet': sheet,
                            'row': rec['_row'],
                            'match': raw_sn,
                            'actions': ['Cleared supplier name', 'Used supplier name as phone']
                        })

    def _duplicate_driver_phones(self):
        """Detect duplicate driver phones."""
        occ = defaultdict(list)
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            for rec in info['records']:
                ph = PhoneValidator.effective(rec.get(COL_DRIVER_PHONE))
                if not ph: 
                    continue
                occ[ph].append({
                    'sheet': sheet, 
                    'row': rec['_row'],
                    'driver_norm': normalize_name(rec.get(COL_DRIVER_NAME)),
                    'driver_raw': to_str(rec.get(COL_DRIVER_NAME))
                })
        
        for ph, rows in occ.items():
            if len(rows) <= 1: 
                continue
            drv = {r['driver_norm'] for r in rows if r['driver_norm']}
            kind = 'hard' if len(drv) > 1 else 'soft'
            self.issues['duplicate_phones'].append({
                'phone': ph, 
                'kind': kind,
                'occurrences': [
                    {'sheet': r['sheet'], 'row': r['row'], 'driver': r['driver_raw']} 
                    for r in rows
                ]
            })

    def _scan_all_dates_deep(self):
        """Deep scan all columns for date-like values."""
        seen_cells = set()
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            date_cols = set()
            
            # Find explicit date columns
            for col in cmap:
                if col.startswith('_'): 
                    continue
                spec = ERP_COLUMN_SPEC.get(col, {})
                if spec.get('type') == 'date': 
                    date_cols.add(col)
                    continue
                # Heuristically detect date-like columns
                vals = [rec.get(col) for rec in info['records']]
                if is_date_like_column(col, vals): 
                    date_cols.add(col)
            
            # Validate dates in identified columns
            for col in date_cols:
                if col not in cmap: 
                    continue
                for rec in info['records']:
                    raw = rec.get(col)
                    if raw is None or to_str(raw) == '': 
                        continue
                    if isinstance(raw, (datetime, date)) and not isinstance(raw, bool):
                        continue
                    
                    st, fx, msg = DateValidator.classify(raw)
                    if st == 'ok' or st == 'empty': 
                        continue
                    
                    key = (sheet, rec['_row'], col)
                    if key in seen_cells: 
                        continue
                    seen_cells.add(key)
                    
                    self.issues['date_format_issues'].append({
                        'sheet': sheet, 
                        'row': rec['_row'], 
                        'col': col,
                        'value': to_str(raw), 
                        'status': st,
                        'suggested': fx, 
                        'reason': msg
                    })
                    
                    if st == 'fixable' and fx:
                        self.fixes.append({
                            'sheet': sheet, 
                            'row': rec['_row'],
                            'col': col, 
                            'old': raw, 
                            'new': fx,
                            'reason': f'Deep date scan — {msg}'
                        })
                        rec[col] = fx

    def _validate_capacity_and_vehicle_status(self):
        """Validate capacity and vehicle status."""
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            
            # Check capacity values
            if COL_CAPACITY in cmap:
                for rec in info['records']:
                    cap = rec.get(COL_CAPACITY)
                    if cap is not None:
                        try:
                            cap_val = int(float(cap))
                            if cap_val <= 0:
                                self.issues['capacity_issues'].append({
                                    'sheet': sheet,
                                    'row': rec['_row'],
                                    'col': COL_CAPACITY,
                                    'value': cap,
                                    'issue': 'Capacity must be greater than 0'
                                })
                        except (ValueError, TypeError):
                            self.issues['capacity_issues'].append({
                                'sheet': sheet,
                                'row': rec['_row'],
                                'col': COL_CAPACITY,
                                'value': cap,
                                'issue': 'Invalid capacity value (not a number)'
                            })
            
            # Check vehicle status
            if COL_VEHICLE_STATUS in cmap:
                for rec in info['records']:
                    status = to_str(rec.get(COL_VEHICLE_STATUS))
                    if status and status.lower() not in ['active', 'inactive', 'maintenance', 'decommissioned']:
                        self.issues['vehicle_status_issues'].append({
                            'sheet': sheet,
                            'row': rec['_row'],
                            'col': COL_VEHICLE_STATUS,
                            'value': status,
                            'issue': 'Invalid vehicle status'
                        })

    def _check_expiry_dates(self):
        """Check for expiry dates."""
        today = datetime.now().date()
        
        for sheet, info in self.sheets_data.items():
            if info['skipped']: 
                continue
            
            cmap = info['cmap']
            
            # Check insurance expiry
            if COL_INSURANCE_EXPIRY in cmap:
                for rec in info['records']:
                    expiry_str = to_str(rec.get(COL_INSURANCE_EXPIRY))
                    if not expiry_str:
                        continue
                    
                    try:
                        expiry = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                        days_diff = (expiry - today).days
                        
                        if days_diff < 0:
                            self.issues['insurance_expiry_issues'].append({
                                'sheet': sheet,
                                'row': rec['_row'],
                                'col': COL_INSURANCE_EXPIRY,
                                'value': expiry_str,
                                'days_overdue': abs(days_diff),
                                'issue': 'Insurance has expired'
                            })
                        elif days_diff <= 30:  # Expires within 30 days
                            self.issues['expiry_alerts'].append({
                                'sheet': sheet,
                                'row': rec['_row'],
                                'col': COL_INSURANCE_EXPIRY,
                                'value': expiry_str,
                                'days_until_expiry': days_diff,
                                'issue': f'Insurance expires in {days_diff} days'
                            })
                    except ValueError:
                        self.issues['date_format_issues'].append({
                            'sheet': sheet,
                            'row': rec['_row'],
                            'col': COL_INSURANCE_EXPIRY,
                            'value': expiry_str,
                            'status': 'invalid',
                            'suggested': None,
                            'reason': 'Invalid insurance expiry date format'
                        })

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis."""
        total_rows = sum(len(info['records']) for info in self.sheets_data.values() if not info['skipped'])
        total_sheets = sum(1 for info in self.sheets_data.values() if not info['skipped'])
        
        # Calculate quality score
        score = self._compute_score()
        
        return {
            'file_name': os.path.basename(self.file_path),
            'total_rows': total_rows,
            'total_sheets': total_sheets,
            'total_fixes': len(self.fixes),
            'quality_score': score,
            'issues': {
                'critical': len([i for i in self._all_issues() if i['severity'] == 'critical']),
                'warning': len([i for i in self._all_issues() if i['severity'] == 'warning']),
                'info': len([i for i in self._all_issues() if i['severity'] == 'info'])
            },
            'breakdown': {
                'invalid_phones': len(self.issues['invalid_phones']),
                'date_format_issues': len(self.issues['date_format_issues']),
                'enum_violations': len(self.issues['enum_violations']),
                'missing_data': len(self.issues['missing_data']),
                'duplicate_phones': len(self.issues['duplicate_phones']),
                'time_conflicts': len(self.issues['time_conflicts']),
                'shift_upgrades': len(self.issues['shift_upgrades']),
                'capacity_issues': len(self.issues['capacity_issues']),
                'vehicle_status_issues': len(self.issues['vehicle_status_issues']),
                'insurance_expiry_issues': len(self.issues['insurance_expiry_issues'])
            }
        }

    def _all_issues(self):
        """Get all issues in a unified format."""
        out = []
        
        # Invalid phones
        for ip in self.issues['invalid_phones']:
            sev = 'critical' if ip['kind'] in ('invalid', 'short') else 'warning'
            out.append({
                'severity': sev,
                'category': f"Phone ({ip['kind']})" if ip['kind'] != 'arabic' else "Phone Note",
                'sheet': ip['sheet'],
                'row': ip['row'],
                'column': ip['col'],
                'value': ip['value'],
                'message': ip['reason']
            })
        
        # Enum violations
        for ev in self.issues['enum_violations']:
            out.append({
                'severity': 'critical',
                'category': 'Enum Violation',
                'sheet': ev['sheet'],
                'row': ev['row'],
                'column': ev['col'],
                'value': ev['value'],
                'message': f"Allowed: {', '.join(ev['allowed'])}"
            })
        
        # Missing data
        for md in self.issues['missing_data']:
            out.append({
                'severity': 'critical',
                'category': 'Missing Data',
                'sheet': md['sheet'],
                'row': md['row'],
                'column': md['col'],
                'value': '—',
                'message': 'Required field missing'
            })
        
        # Date format issues
        for df in self.issues['date_format_issues']:
            sev = 'critical' if df.get('status') == 'invalid' else 'warning'
            out.append({
                'severity': sev,
                'category': 'Date Format',
                'sheet': df['sheet'],
                'row': df['row'],
                'column': df['col'],
                'value': df['value'],
                'message': df.get('reason', '')
            })
        
        # Time conflicts
        for tc in self.issues['time_conflicts']:
            out.append({
                'severity': 'critical',
                'category': 'Time Conflict',
                'sheet': tc['sheet'],
                'row': tc['row'],
                'column': f"{tc['pickup_col']} vs {tc['dropoff_col']}",
                'value': f"{tc['pickup']} == {tc['dropoff']}",
                'message': f"Suggested: {tc.get('suggested_dropoff', '—')}"
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
        
        # Cap at 95 points deducted
        total_deduction = min(issue_points, 95)
        final_score = max(5, 100 - total_deduction)  # Minimum score is 5
        
        return final_score

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