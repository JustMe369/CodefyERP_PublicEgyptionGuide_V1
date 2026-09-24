#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         C O D E F Y E R P  ·  S H E E T S A N A L Y Z E R S  v11.3.1        ║
║      🌊  DARK BLUE · TIME-CONTROL-CENTER  ·  SHIFT-ENGINE  🌊                ║
║──────────────────────────────────────────────────────────────────────────────║
║  v11.3.1 — HOTFIX                                                             ║
║    ✔ Fixed TclError: "bad screen distance" in Tooltip (tuple → int pady)     ║
║    ✔ All v11.3 features retained                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import re, os, sys, csv, json, copy, subprocess, traceback
import threading, queue, webbrowser, urllib.parse
import argparse
from typing import Dict, List, Any

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_SHAPER = True
except Exception:
    HAS_SHAPER = False


# =============================================================================
# CONSTANTS
# =============================================================================
COL_DRIVER_NAME     = 'assigned_driver_full_name'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CodefyExcelAnalyzer - Advanced Fleet Data Quality Tool')
    parser.add_argument('file_path', nargs='?', help='Path to Excel/CSV file to analyze')
    parser.add_argument('--analyze', dest='file_path_cmd', help='Analyze specified file (for API usage)')
    parser.add_argument('--export-fixed', dest='export_fixed', help='Export fixed file to specified path')
    parser.add_argument('--export-issues', dest='export_issues', help='Export issues to specified path')
    parser.add_argument('--format', choices=['excel', 'csv', 'json', 'html'], default='excel', 
                        help='Export format (default: excel)')
    
    args = parser.parse_args()
    
    file_path = args.file_path or args.file_path_cmd
    
    if file_path:
        if not os.path.exists(file_path):
            print(f"Error: File does not exist: {file_path}")
            sys.exit(1)
        
        try:
            analyzer = CodefyAnalyzer(file_path)
            report, fixes = analyzer.run()
            
            # Output results as JSON for API consumption
            result = analyzer.to_dict()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # Optionally export files
            if args.export_fixed:
                if args.format == 'csv':
                    analyzer.export_fixed_csv(args.export_fixed)
                else:
                    analyzer.export_fixed(args.export_fixed)
                print(f"Fixed file exported to: {args.export_fixed}")
                
            if args.export_issues:
                if args.format == 'json':
                    analyzer.export_issues_json(args.export_issues)
                elif args.format == 'excel':
                    analyzer.export_issues_excel(args.export_issues)
                elif args.format == 'csv':
                    analyzer.export_issues_csv(args.export_issues)
                else:  # html
                    analyzer.export_html_report(args.export_issues)
                print(f"Issues exported to: {args.export_issues}")
                
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'traceback': str(traceback.format_exc()) if 'traceback' in globals() else 'Import error occurred'
            }
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        # If no file provided, launch GUI as before
        try:
            import tkinter as tk
            from tkinter import ttk, filedialog, messagebox
            # Launch the GUI application
            root = tk.Tk()
            app = App(root)
            root.mainloop()
        except ImportError:
            print("GUI dependencies not available. Please provide a file path to analyze.")
            print("Usage: python CodefyExcelAnalyzer_V11.3.1.py <file_path>")

# Handle the HAS_SHAPER exception
except Exception:
    HAS_SHAPER = False


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

COLUMN_CLEAR_DEFAULTS = {
    COL_ASSIGNMENT_RULE, COL_ROW_TYPE,  # Technical columns
    COL_SUPPLIER_NAME, COL_SUPPLIER_PHONE,  # May be cleared for main suppliers
    COL_SUPPLIER_PRICE  # Often not needed
}

# ... existing code continues ...
COL_PICKUP_NAME     = 'pickup_name'
COL_PICKUP_RADIUS   = 'pickup_radius'
COL_PICKUP_ARR      = 'pickup_arrival_time'
COL_PICKUP_DEP      = 'pickup_departure_time'
COL_DROPOFF_RADIUS  = 'dropoff_radius'
COL_PRIMARY_LINE    = 'primary_line'
COL_SECONDARY_LINE  = 'secondary_line'
COL_LINE_NAME       = 'line_name'
COL_ASSIGNMENT_TYPE = 'assignment_type'

TIME_COLUMNS = [
    (COL_PICKUP_ARR,   '🛫', 'pickup_arrival_time'),
    (COL_PICKUP_DEP,   '🛫', 'pickup_departure_time'),
    (COL_DROPOFF_ARR,  '🛬', 'dropoff_arrival_time'),
    (COL_DROPOFF_TIME, '🛬', 'dropoff_departure_time'),
    (COL_SCHEDULE_TIME,'📅', 'schedule_time'),
]

EG_PHONE_RE = re.compile(r'^01[0125]\d{8}$')
EMAIL_RE    = re.compile(r'^[\w\.\-\+]+@[\w\-]+(\.[\w\-]+)+$')
URL_RE      = re.compile(r'^https?://[\w\-\.]+\.[a-z]{2,}(/.*)?$', re.I)
TIME_RE     = re.compile(r'^([0-1]?\d|2[0-3]):[0-5]\d(:[0-5]\d)?$')
ARABIC_RE   = re.compile(r'[\u0600-\u06FF]')
LATIN_RE    = re.compile(r'[A-Za-z]')
DATE_ISO_RE = re.compile(r'^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')
EXPIRY_WARN_DAYS = 90

DEFAULT_TIME_CONFLICT_OFFSET_MIN = 30
DEFAULT_TIME_TARGET_COLUMN       = COL_DROPOFF_ARR
TIME_CONFLICT_MODE_AUTOFIX       = 'autofix'
TIME_CONFLICT_MODE_FLAGONLY      = 'flagonly'

PHONE_REQUIRED_DIGITS = 11
PHONE_MIN_ACCEPTABLE  = 10

DEFAULT_MAIN_SUPPLIERS = ['الجودة', 'الجوده']
INTERNAL_ASSIGNMENT_VALUES = {'internal', 'داخلي', 'internal assignment'}

DATE_KEYWORDS_IN_NAME = (
    'date', 'expiry', 'expire', 'valid', 'birth', 'issued', 'due',
    'created', 'updated', 'scheduled', 'start_d', 'end_d', '_at', '_on',
    'تاريخ', 'انتهاء', 'صلاحية', 'بداية', 'نهاية', 'ميلاد', 'استحقاق',
    'انتهت', 'بدء',
)
EXCEL_SERIAL_MIN = 20000
EXCEL_SERIAL_MAX = 80000

ARABIC_INDIC_DIGITS = str.maketrans("٠٢٢٣٤٥٦٧٨٩", "0123456789")
CSV_ENCODINGS = ['utf-8-sig', 'utf-8', 'cp1256', 'iso-8859-6', 'latin1']
CSV_DELIMS    = [',', ';', '\t', '|']

DAY_CANONICAL_ORDER = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
DAY_ALIAS_MAP = {
    'sun':'sun','mon':'mon','tue':'tue','wed':'wed','thu':'thu','fri':'fri','sat':'sat',
    'sunday':'sun','monday':'mon','tuesday':'tue','wednesday':'wed',
    'thursday':'thu','friday':'fri','saturday':'sat',
    'الاحد':'sun','أحد':'sun','احد':'sun',
    'الاثنين':'mon','الأثنين':'mon','أثنين':'mon','اثنين':'mon',
    'إثنين':'mon','الاتنين':'mon','اتنين':'mon','الاثنان':'mon',
    'الثلاثاء':'tue','ثلاثاء':'tue','التلاتاء':'tue','تلاتاء':'tue',
    'الاربعاء':'wed','أربعاء':'wed','اربعاء':'wed','الأربعاء':'wed',
    'الخميس':'thu','خميس':'thu',
    'الجمعة':'fri','الجمعه':'fri','جمعة':'fri','جمعه':'fri',
    'السبت':'sat','سبت':'sat',
}
WORKING_DAYS_SEPARATORS = re.compile(r'[,;،/\-|]+')
DIRECTION_OUTBOUND_KEYWORDS = ['ذهاب']
DIRECTION_INBOUND_KEYWORDS  = ['عودة', 'عوده']

ERP_REQUIRED_COLUMNS = ['company_name', 'project_name', 'route_code']
ERP_REJECTED_COLUMNS = ['row_type', 'assignment_rule_type']

SHIFT_BASE_PATTERNS = {
    'ثلاث ورادي': [
        'ثلاث ورادي', 'ثلاث ورادى', 'ثلاث وردي', 'ثلاث وردى',
        '3 ورادي', '3 وردي', '3ورادي',
        'ورادي', 'ورادى', 'وردي', 'وردى'],
    'وردتين':      ['وردتين', 'وردتان', '2 وردية', 'شفتين'],
    'اربع ورادي':  ['اربع ورادي', 'أربع ورادي', '4 ورادي'],
}

SHIFT_ORDINALS = [
    (['اولى', 'أولى', 'اول', 'أول', 'الاولى', 'الأولى'], 'أولى',   'أولي'),
    (['تانية', 'ثانية', 'تانى', 'ثانى', 'التانية', 'الثانية'], 'ثانية', 'ثانية'),
    (['تالتة', 'ثالثة', 'تالت', 'ثالث', 'التالتة', 'الثالثة'], 'ثالثة', 'ثلاث'),
    (['رابعة', 'رابع', 'الرابعة', 'الرابع'], 'رابعة', 'رابعة'),
    (['خامسة', 'خامس', 'الخامسة', 'الخامس'], 'خامسة', 'خامسة'),
]

ERP_COLUMN_SPEC = {
    'company_name':        {'cat': 'core',     'required': True},
    'project_name':        {'cat': 'core',     'required': True},
    'route_code':          {'cat': 'core',     'required': True},
    'assigned_driver_full_name': {'cat': 'driver'},
    'driver_phone_number':       {'cat': 'driver'},
    'driver_license_number':     {'cat': 'driver'},
    'driver_license_expiry_date':{'cat': 'driver', 'type': 'date'},
    'driver_employment_type':    {'cat': 'driver',
                                  'enum': ['employee','contractor','freelancer']},
    'driver_code':               {'cat': 'driver'},
    'driver_monthly_salary':     {'cat': 'driver', 'type': 'number'},
    'driver_salary_currency':    {'cat': 'driver'},
    'assigned_vehicle_plate_number': {'cat': 'vehicle'},
    'vehicle_make':         {'cat': 'vehicle'},
    'vehicle_type':         {'cat': 'vehicle',
                             'enum': ['Sedan','Taxi','Van 7','Van 8',
                                      'Microbus 14','Minibus 26',
                                      'Minibus 28','Minibus 30','Bus 50']},
    'vehicle_year':         {'cat': 'vehicle', 'type': 'year'},
    'vehicle_expiry_date':  {'cat': 'vehicle', 'type': 'date'},
    'vehicle_code':         {'cat': 'vehicle'},
    'vehicle_owner_type':   {'cat': 'vehicle',
                             'enum': ['tenant','supplier','driver']},
    'vehicle_monthly_cost': {'cat': 'vehicle', 'type': 'number'},
    'vehicle_cost_currency':{'cat': 'vehicle'},
    'supplier_full_name':          {'cat': 'supplier'},
    'supplier_phone_number':       {'cat': 'supplier'},
    'supplier_price':              {'cat': 'supplier', 'type': 'number'},
    'supplier_price_valid_from':   {'cat': 'supplier', 'type': 'date'},
    'supplier_price_valid_to':     {'cat': 'supplier', 'type': 'date'},
    'supplier_price_weekdays':     {'cat': 'supplier'},
    'supplier_pricing_unit':       {'cat': 'supplier', 'enum': ['per_trip']},
    'client_sales_price':          {'cat': 'pricing', 'type': 'number'},
    'client_pricing_unit':         {'cat': 'pricing', 'enum': ['per_trip']},
    'schedule_name':        {'cat': 'schedule'},
    'schedule_time':        {'cat': 'schedule'},
    'schedule_direction':   {'cat': 'schedule',
                             'enum': ['home_to_office','office_to_home',
                                      'round_trip','both']},
    'schedule_pair_key':    {'cat': 'schedule'},
    'shift_name':           {'cat': 'schedule'},
    'shift_check_in_time':  {'cat': 'schedule'},
    'shift_check_out_time': {'cat': 'schedule'},
    'working_days':         {'cat': 'schedule'},
    'route_type':            {'cat': 'routing',
                              'enum': ['fixed_line','pooled','on_demand']},
    'on_demand_schedule_mode':{'cat': 'routing'},
    'service_window_start':  {'cat': 'routing'},
    'service_window_end':    {'cat': 'routing'},
    'on_demand_vehicle_type_price': {'cat': 'routing', 'type': 'number'},
    'pickup_name':           {'cat': 'location'},
    'pickup_lat':            {'cat': 'location', 'type': 'coord_lat'},
    'pickup_long':           {'cat': 'location', 'type': 'coord_long'},
    'pickup_radius':         {'cat': 'location', 'type': 'number'},
    'pickup_arrival_time':   {'cat': 'location', 'type': 'time'},
    'pickup_departure_time': {'cat': 'location', 'type': 'time'},
    'dropoff_name':          {'cat': 'location'},
    'dropoff_lat':           {'cat': 'location', 'type': 'coord_lat'},
    'dropoff_long':          {'cat': 'location', 'type': 'coord_long'},
    'dropoff_radius':        {'cat': 'location', 'type': 'number'},
    'dropoff_arrival_time':  {'cat': 'location', 'type': 'time'},
    'dropoff_departure_time':{'cat': 'location', 'type': 'time'},
    'primary_line':    {'cat': 'line'},
    'secondary_line':  {'cat': 'line'},
    'line_name':       {'cat': 'line'},
}

COLUMN_CLEAR_DEFAULTS = set()

COLUMN_ALIASES = {
    COL_DRIVER_NAME:    ['assigned_driver_full_name','driver_name','اسم السائق',
                         'السائق','اسم السائق الثلاثي','driver','اسم_السائق'],
    COL_DRIVER_PHONE:   ['driver_phone_number','driver_phone','mobile',
                         'موبايل السائق','رقم الهاتف','هاتف السائق',
                         'رقم التليفون','رقم الموبايل','هاتف_السائق'],
    COL_DRIVER_LIC_NUM: ['driver_license_number','license_number',
                         'رقم الرخصة','رقم رخصة السائق'],
    COL_DRIVER_LIC_EXP: ['driver_license_expiry_date','lic_exp',
                         'انتهاء رخصة السائق','تاريخ انتهاء الرخصة','انتهاء الرخصة'],
    COL_EMP_TYPE:       ['driver_employment_type','employment_type','نوع التوظيف'],
    COL_SUPPLIER_PRICE: ['supplier_price','سعر المورد','تكلفة المورد','سعر الشراء'],
    COL_PLATE:          ['assigned_vehicle_plate_number','plate_number','رقم اللوحة',
                         'رقم السيارة','لوحة السيارة','اللوحة'],
    COL_VEHICLE_MAKE:   ['vehicle_make','ماركة السيارة','نوع السيارة','ماركة'],
    COL_VEHICLE_TYPE:   ['vehicle_type','فئة السيارة','سعة السيارة'],
    COL_VEHICLE_YEAR:   ['vehicle_year','سنة الصنع','موديل','سنة الموديل'],
    COL_VEHICLE_EXP:    ['vehicle_expiry_date','انتهاء رخصة السيارة',
                         'تاريخ رخصة السيارة'],
    COL_SUPPLIER_UNIT:  ['supplier_pricing_unit','وحدة تسعير المورد'],
    COL_DIRECTION:      ['schedule_direction','direction','الاتجاه'],
    COL_COMPANY:        ['company_name','الشركة','اسم الشركة'],
    COL_PROJECT:        ['project_name','المشروع','اسم المشروع'],
    COL_SHIFT:          ['shift_name','shift','الوردية','اسم الوردية','فترة',
                         'الورديات','الورديه'],
    COL_ROUTE:          ['route_code','route','كود الخط','خط السير'],
    COL_SCHEDULE:       ['schedule_name','جدول','اسم الجدول','الجدول',
                         'جدول الرحلة','اسم الرحلة'],
    COL_SCHEDULE_TIME:  ['schedule_time','وقت الجدول','وقت الرحلة'],
    COL_SUPPLIER_NAME:  ['supplier_name','supplier','supplier_full_name',
                         'اسم المورد','المورد','اسم المورد بالكامل'],
    COL_SUPPLIER_PHONE: ['supplier_phone_number','موبايل المورد',
                         'هاتف المورد','تليفون المورد'],
    COL_WORKING_DAYS:   ['working_days','ايام العمل','أيام العمل'],
    COL_CLIENT_PRICE:   ['client_sales_price','client_price','سعر البيع','سعر العميل'],
    COL_CLIENT_UNIT:    ['client_pricing_unit','وحدة تسعير العميل'],
    COL_DROPOFF_ARR:    ['dropoff_arrival_time','وقت الوصول'],
    COL_DROPOFF_TIME:   ['dropoff_departure_time','drop_off_departure_time',
                         'dropoff_time','drop_off_time',
                         'وقت المغادرة','وقت التوصيل','وقت الانصراف'],
    COL_DROPOFF_LAT:    ['dropoff_lat','خط عرض التسليم'],
    COL_DROPOFF_LONG:   ['dropoff_long','خط طول التسليم'],
    COL_DROPOFF_NAME:   ['dropoff_name','اسم موقع التسليم'],
    COL_PICKUP_LAT:     ['pickup_lat','خط عرض الالتقاط'],
    COL_PICKUP_LONG:    ['pickup_long','خط طول الالتقاط'],
    COL_PICKUP_NAME:    ['pickup_name','اسم موقع الالتقاط'],
    COL_PICKUP_RADIUS:  ['pickup_radius','نطاق الالتقاط'],
    COL_PICKUP_ARR:     ['pickup_arrival_time','وقت وصول الالتقاط'],
    COL_PICKUP_DEP:     ['pickup_departure_time','وقت مغادرة الالتقاط'],
    COL_DROPOFF_RADIUS: ['dropoff_radius','نطاق التسليم'],
    COL_PRIMARY_LINE:   ['primary_line','الخط الأساسي'],
    COL_SECONDARY_LINE: ['secondary_line','الخط الثانوي'],
    COL_LINE_NAME:      ['line_name','اسم الخط'],
    COL_ASSIGNMENT_TYPE:['assignment_type','assignment','نوع التعيين','نوع التكليف'],
}

# ═══════════════════════════════ UTILITIES ════════════════════════════════════
def to_str(v):
    if v is None: return ''
    if isinstance(v, float) and v.is_integer(): v = int(v)
    return str(v).strip()

def _clean_header_key(h):
    if not h: return ''
    h = to_str(h).lower().translate(ARABIC_INDIC_DIGITS)
    h = re.sub(r'[\s_\-]+', '', h)
    h = re.sub(r'[أإآٱ]', 'ا', h)
    h = re.sub(r'ة', 'ه', h)
    h = re.sub(r'ى', 'ي', h)
    h = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', h)
    return h

ALIAS_LOOKUP = {}
for ck, aliases in COLUMN_ALIASES.items():
    ALIAS_LOOKUP[_clean_header_key(ck)] = ck
    for a in aliases:
        ALIAS_LOOKUP[_clean_header_key(a)] = ck

def normalize_name(n):
    n = to_str(n).translate(ARABIC_INDIC_DIGITS)
    n = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', n)
    n = re.sub(r'[أإآٱ]', 'ا', n)
    n = re.sub(r'ة', 'ه', n)
    n = re.sub(r'ى', 'ي', n)
    n = re.sub(r'\s+', ' ', n)
    return n.strip().lower()

DAY_ALIAS_LOOKUP = {normalize_name(k): v for k, v in DAY_ALIAS_MAP.items()}
def is_arabic(s): return bool(ARABIC_RE.search(to_str(s)))

def to_num(v):
    try:
        if v is None or v == '': return None
        if isinstance(v, str):
            v = v.translate(ARABIC_INDIC_DIGITS).replace(',', '').strip()
        return float(v)
    except (TypeError, ValueError):
        return None

def parse_date(v):
    if v is None: return None
    if isinstance(v, datetime): return v
    if isinstance(v, date):     return datetime(v.year, v.month, v.day)
    if isinstance(v, (int, float)):
        try:
            if EXCEL_SERIAL_MIN <= v <= EXCEL_SERIAL_MAX:
                return datetime(1899, 12, 30) + timedelta(days=float(v))
        except Exception: pass
    s = to_str(v).translate(ARABIC_INDIC_DIGITS)
    if not s: return None
    s = s.split('T')[0].split(' ')[0]
    for fmt in ('%Y-%m-%d','%d/%m/%Y','%m/%d/%Y','%d-%m-%Y',
                '%Y/%m/%d','%d.%m.%Y'):
        try: return datetime.strptime(s, fmt)
        except ValueError: pass
    return None

def parse_time_to_min(tstr):
    s = to_str(tstr).translate(ARABIC_INDIC_DIGITS).strip()
    if not s: return None
    m = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$', s)
    if not m: return None
    h = int(m.group(1)); mi = int(m.group(2))
    if not (0 <= h < 24 and 0 <= mi < 60): return None
    return h * 60 + mi

def offset_time_min(tstr, minutes):
    tot = parse_time_to_min(tstr)
    if tot is None: return None
    tot = (tot + minutes) % (24 * 60)
    return f"{tot // 60:02d}:{tot % 60:02d}"

def normalize_time_string(tstr, to_hhmm=True, convert_12h=True):
    s = to_str(tstr).translate(ARABIC_INDIC_DIGITS).strip()
    if not s: return None
    if convert_12h:
        m = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp][Mm])$', s)
        if m:
            h = int(m.group(1)); mi = int(m.group(2))
            ampm = m.group(4).upper()
            if h == 12: h = 0
            if ampm == 'PM': h += 12
            s = f"{h:02d}:{mi:02d}"
    if to_hhmm:
        m = re.match(r'^(\d{1,2}):(\d{2})(?::\d{2})?$', s)
        if m:
            h = int(m.group(1)); mi = int(m.group(2))
            return f"{h:02d}:{mi:02d}"
    return s

def bar(pct, width=30):
    pct = max(0, min(100, pct))
    filled = int(round(width * pct / 100))
    return '█' * filled + '░' * (width - filled)

def is_rtl_line(t):
    if not t: return False
    ar = len(ARABIC_RE.findall(t)); la = len(LATIN_RE.findall(t))
    return ar >= 3 and ar > la

def shape_for_display(s):
    if not HAS_SHAPER: return s
    if not ARABIC_RE.search(s): return s
    try: return get_display(arabic_reshaper.reshape(s))
    except Exception: return s

def detect_column_type(values):
    vals = [v for v in values if v not in (None, '')]
    if not vals: return 'empty'
    n = len(vals)
    ph = sum(1 for v in vals if EG_PHONE_RE.match(
        re.sub(r'\D', '', to_str(v).translate(ARABIC_INDIC_DIGITS))))
    nu = sum(1 for v in vals if to_num(v) is not None)
    da = sum(1 for v in vals if parse_date(v) is not None)
    ar = sum(1 for v in vals if is_arabic(v))
    if ph/n > 0.7: return 'phone'
    if da/n > 0.7: return 'date'
    if nu/n > 0.7: return 'number'
    if ar/n > 0.5: return 'arabic-text'
    return 'text'

def html_escape(s):
    return (to_str(s).replace('&','&amp;').replace('<','&lt;')
            .replace('>','&gt;').replace('"','&quot;'))

def _lighten(hex_color, amount=0.22):
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception: return hex_color
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"

def is_date_like_column(col_name, values):
    if not col_name or col_name.startswith('_'): return False
    cn = to_str(col_name).lower()
    name_hit = any(kw in cn for kw in DATE_KEYWORDS_IN_NAME)
    non_empty = [v for v in values if to_str(v) != '']
    if not non_empty: return name_hit
    phone_count = sum(1 for v in non_empty
                      if EG_PHONE_RE.match(
                          re.sub(r'\D', '', to_str(v).translate(ARABIC_INDIC_DIGITS))))
    if phone_count and phone_count / len(non_empty) > 0.5: return False
    native = sum(1 for v in non_empty if isinstance(v, (datetime, date)))
    parseable = 0
    for v in non_empty:
        st, _, _ = DateValidator.classify(v)
        if st in ('ok', 'fixable'): parseable += 1
    total_like = native + parseable
    ratio = total_like / len(non_empty)
    return name_hit or ratio >= 0.30

def is_phone_column_name(col_name):
    if not col_name: return False
    cn = to_str(col_name).lower()
    kws = ('phone', 'mobile', 'msisdn', 'telephone',
           'هاتف', 'تليفون', 'موبايل', 'جوال', 'رقم_الهاتف', 'رقم_هاتف')
    return any(k in cn for k in kws)

# ═══════════════════════════════ SETTINGS MANAGER ═════════════════════════════
DEFAULT_SETTINGS_FILE = os.path.join(os.path.expanduser('~'),
                                      '.codefy_settings_v11.json')

class SettingsManager:
    def __init__(self, path=None):
        self.file_path = path or DEFAULT_SETTINGS_FILE
        self.main_suppliers = list(DEFAULT_MAIN_SUPPLIERS)
        self.shift_engine_enabled = True
        self.custom_shift_bases = {}
        self.custom_ordinals = []
        self.time_conflict_enabled = True
        self.time_conflict_offset = DEFAULT_TIME_CONFLICT_OFFSET_MIN
        self.time_conflict_target = DEFAULT_TIME_TARGET_COLUMN
        self.time_conflict_mode = TIME_CONFLICT_MODE_AUTOFIX
        self.time_normalize_enabled = True
        self.time_convert_12h = True
        self.time_column_rules = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                s = data.get('main_suppliers', [])
                if isinstance(s, list):
                    cleaned = [to_str(x) for x in s if to_str(x)]
                    if cleaned: self.main_suppliers = cleaned
                self.shift_engine_enabled = bool(data.get('shift_engine_enabled', True))
                c = data.get('custom_shift_bases', {})
                if isinstance(c, dict): self.custom_shift_bases = c
                o = data.get('custom_ordinals', [])
                if isinstance(o, list): self.custom_ordinals = o
                self.time_conflict_enabled  = bool(data.get('time_conflict_enabled', True))
                self.time_conflict_offset   = int(data.get('time_conflict_offset',
                                                            DEFAULT_TIME_CONFLICT_OFFSET_MIN))
                self.time_conflict_target   = to_str(data.get('time_conflict_target',
                                                              DEFAULT_TIME_TARGET_COLUMN))
                self.time_conflict_mode     = to_str(data.get('time_conflict_mode',
                                                              TIME_CONFLICT_MODE_AUTOFIX))
                self.time_normalize_enabled = bool(data.get('time_normalize_enabled', True))
                self.time_convert_12h       = bool(data.get('time_convert_12h', True))
                tcr = data.get('time_column_rules', {})
                if isinstance(tcr, dict): self.time_column_rules = tcr
        except Exception: pass

    def save(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'main_suppliers': self.main_suppliers,
                    'shift_engine_enabled': self.shift_engine_enabled,
                    'custom_shift_bases': self.custom_shift_bases,
                    'custom_ordinals': self.custom_ordinals,
                    'time_conflict_enabled': self.time_conflict_enabled,
                    'time_conflict_offset': self.time_conflict_offset,
                    'time_conflict_target': self.time_conflict_target,
                    'time_conflict_mode': self.time_conflict_mode,
                    'time_normalize_enabled': self.time_normalize_enabled,
                    'time_convert_12h': self.time_convert_12h,
                    'time_column_rules': self.time_column_rules,
                }, f, ensure_ascii=False, indent=2)
        except Exception: pass

    def get_main_suppliers(self): return list(self.main_suppliers)

    def add(self, name):
        s = to_str(name)
        if not s: return False
        k = normalize_name(s)
        if k in {normalize_name(x) for x in self.main_suppliers}: return False
        self.main_suppliers.append(s); self.save(); return True

    def remove(self, name):
        k = normalize_name(name)
        before = len(self.main_suppliers)
        self.main_suppliers = [x for x in self.main_suppliers
                                if normalize_name(x) != k]
        if len(self.main_suppliers) < before:
            self.save(); return True
        return False

    def reset(self):
        self.main_suppliers = list(DEFAULT_MAIN_SUPPLIERS); self.save()

    def get_normalized_set(self):
        return {normalize_name(x) for x in self.main_suppliers}

# ═══════════════════════════════ PHONE VALIDATOR ═════════════════════════════
class PhoneValidator:
    REQUIRED_DIGITS = 11
    MIN_FIXABLE     = 10

    @staticmethod
    def classify(raw):
        s = to_str(raw)
        if not s: return 'empty', None, ''
        sn = s.translate(ARABIC_INDIC_DIGITS)
        d = re.sub(r'\D', '', sn)
        if not d:
            if is_arabic(s):
                return 'arabic', None, f'Text note in phone column: {s[:25]}'
            return 'empty', None, ''
        if len(d) == 12 and d.startswith('20') and EG_PHONE_RE.match('0' + d[2:]):
            return 'fixable', '0' + d[2:], 'Converted +20 country code'
        if len(d) == 14 and d.startswith('0020') and EG_PHONE_RE.match('0' + d[4:]):
            return 'fixable', '0' + d[4:], 'Converted 0020 country code'
        if len(d) == 11:
            if EG_PHONE_RE.match(d):
                if d != s: return 'fixable', d, 'Normalized to 11-digit phone'
                return 'ok', d, ''
            return 'invalid', None, (
                f'Invalid prefix "{d[:3]}" — must start with 010/011/012/015')
        if len(d) == 10:
            cand = '0' + d
            if EG_PHONE_RE.match(cand):
                return 'fixable', cand, f'Fixed by adding leading 0 → {cand}'
            return 'invalid', None, f'10 digits with invalid prefix "{cand[:3]}"'
        if len(d) > 11:
            return 'invalid', None, (
                f'Too many digits ({len(d)}) — must be exactly 11 (e.g. 01099831981)')
        return 'short', None, (
            f'🚩 Phone has only {len(d)} digit(s) — REQUIRED 11 digits. '
            f'Value NOT modified; cell marked RED for manual review.')

    @staticmethod
    def effective(raw):
        st, fx, _ = PhoneValidator.classify(raw)
        if st == 'fixable' and fx: return fx
        if st == 'ok':
            return re.sub(r'\D', '', to_str(raw).translate(ARABIC_INDIC_DIGITS))
        return None

# ═══════════════════════════════ DATE VALIDATOR ═══════════════════════════════
ARABIC_MONTHS = {
    'يناير':1,'فبراير':2,'مارس':3,'أبريل':4,'ابريل':4,'مايو':5,'يونيو':6,
    'يوليو':7,'أغسطس':8,'اغسطس':8,'سبتمبر':9,'أكتوبر':10,'اكتوبر':10,
    'نوفمبر':11,'ديسمبر':12,
    'كانون الثاني':1,'شباط':2,'آذار':3,'اذار':3,'نيسان':4,'أيار':5,'ايار':5,
    'حزيران':6,'تموز':7,'آب':8,'اب':8,'أيلول':9,'ايلول':9,
    'تشرين الأول':10,'تشرين الثاني':11,'كانون الأول':12,
}
ARABIC_MONTH_LOOKUP = {normalize_name(k): v for k, v in ARABIC_MONTHS.items()}

class DateValidator:
    DATE_FORMATS = (
        '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
        '%Y/%m/%d', '%Y.%m.%d', '%Y%m%d', '%d.%m.%Y',
        '%d-%b-%Y', '%b-%d-%Y', '%d %b %Y', '%b %d %Y', '%d %b, %Y', '%b %d, %Y',
        '%d-%B-%Y', '%B-%d-%Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y', '%B %d, %Y',
        '%Y年%m月%d日',
        '%m/%d/%y', '%d/%m/%y', '%d-%m-%y', '%m-%d-%y',
        '%Y.%m.%d %H:%M:%S', '%Y-%m-%d %H:%M:%S',
    )

    @staticmethod
    def _try_arabic_month(s):
        try:
            s_clean = s.replace(',', ' ').replace('،', ' ')
            s_clean = re.sub(r'\s+', ' ', s_clean).strip()
            parts = re.split(r'[\s\-/.]+', s_clean)
            day = month = year = None
            for p in parts:
                if not p: continue
                if re.match(r'^\d{1,4}$', p):
                    n = int(p)
                    if n > 1900: year = n
                    elif 1 <= n <= 31 and day is None: day = n
                    elif 1 <= n <= 12 and month is None: month = n
                else:
                    key = normalize_name(p)
                    if key in ARABIC_MONTH_LOOKUP: month = ARABIC_MONTH_LOOKUP[key]
            if day and month and year: return datetime(year, month, day)
        except Exception: pass
        return None

    @staticmethod
    def classify(raw):
        if raw is None: return 'empty', None, ''
        if isinstance(raw, bool): return 'invalid', None, 'Boolean is not a date'
        if isinstance(raw, datetime):
            iso = raw.strftime('%Y-%m-%d')
            if raw.hour or raw.minute or raw.second:
                return 'fixable', iso, f'Stripped time ({raw.strftime("%H:%M:%S")})'
            return 'ok', iso, ''
        if isinstance(raw, date):
            return 'ok', datetime(raw.year, raw.month, raw.day).strftime('%Y-%m-%d'), ''
        if isinstance(raw, (int, float)):
            try:
                fv = float(raw)
                if EXCEL_SERIAL_MIN <= fv <= EXCEL_SERIAL_MAX:
                    d = datetime(1899, 12, 30) + timedelta(days=fv)
                    if 1950 <= d.year <= 2100:
                        return 'fixable', d.strftime('%Y-%m-%d'), 'Excel serial date'
            except Exception: pass
            return 'empty', None, ''
        s = to_str(raw).translate(ARABIC_INDIC_DIGITS)
        if not s: return 'empty', None, ''
        digits_only = re.sub(r'\D', '', s)
        if EG_PHONE_RE.match(digits_only):
            return 'invalid', None, 'Looks like an Egyptian phone number'
        if DATE_ISO_RE.match(s):
            try:
                datetime.strptime(s, '%Y-%m-%d'); return 'ok', s, ''
            except ValueError: pass
        s_clean = s.strip()
        if 'T' in s_clean:
            head = s_clean.split('T')[0]
            if DATE_ISO_RE.match(head):
                try:
                    datetime.strptime(head, '%Y-%m-%d')
                    return 'fixable', head, 'Stripped ISO timestamp'
                except ValueError: pass
        m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+\d{1,2}:\d{2}(:\d{2})?\s*$', s_clean)
        if m:
            try:
                datetime.strptime(m.group(1), '%Y-%m-%d')
                return 'fixable', m.group(1), 'Stripped time-of-day'
            except ValueError: pass
        d = DateValidator._try_arabic_month(s)
        if d: return 'fixable', d.strftime('%Y-%m-%d'), 'Arabic month → ISO'
        for fmt in DateValidator.DATE_FORMATS:
            try:
                d = datetime.strptime(s_clean, fmt)
                if '%y' in fmt and d.year < 1950: d = d.replace(year=d.year + 2000)
                iso = d.strftime('%Y-%m-%d')
                return 'fixable', iso, f'Reformatted "{fmt}" → YYYY-MM-DD'
            except ValueError: continue
        try:
            s_dash = re.sub(r'[./年月]', '-', s_clean)
            s_dash = s_dash.replace('日', '').strip('-')
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%y-%m-%d'):
                try:
                    d = datetime.strptime(s_dash, fmt)
                    if '%y' in fmt and d.year < 1950: d = d.replace(year=d.year + 2000)
                    return 'fixable', d.strftime('%Y-%m-%d'), 'Normalized separators'
                except ValueError: continue
        except Exception: pass
        return 'invalid', None, f'Unrecognized date: "{s[:32]}"'

    @staticmethod
    def effective(raw):
        st, fx, _ = DateValidator.classify(raw)
        if st in ('fixable', 'ok'): return fx
        return None

# ═══════════════════════════════ CSV LOADER ═══════════════════════════════════
class CSVLoader:
    @staticmethod
    def detect_encoding(path):
        for enc in CSV_ENCODINGS:
            try:
                with open(path, 'r', encoding=enc, newline='') as f: f.read(4096)
                return enc
            except (UnicodeDecodeError, LookupError): continue
        return 'utf-8-sig'

    @staticmethod
    def detect_delimiter(sample):
        try:
            return csv.Sniffer().sniff(sample, delimiters=''.join(CSV_DELIMS)).delimiter
        except Exception:
            best, bc = ',', 0
            for d in CSV_DELIMS:
                c = sample.count(d)
                if c > bc: best, bc = d, c
            return best

    @staticmethod
    def load(path):
        enc = CSVLoader.detect_encoding(path)
        with open(path, 'r', encoding=enc, newline='') as f:
            sample = f.read(8192)
        delim = CSVLoader.detect_delimiter(sample)
        rows = []
        with open(path, 'r', encoding=enc, newline='') as f:
            for row in csv.reader(f, delimiter=delim): rows.append(row)
        while rows and not any(to_str(c) for c in rows[-1]): rows.pop()
        wb = openpyxl.Workbook()
        sn = os.path.splitext(os.path.basename(path))[0][:31] or 'Data'
        sn = re.sub(r'[\\/*?:\[\]]', '_', sn)
        ws = wb.active; ws.title = sn
        for ri, row in enumerate(rows, 1):
            for ci, val in enumerate(row, 1):
                ws.cell(ri, ci, value=CSVLoader._coerce(val))
        return wb, enc, delim

    @staticmethod
    def _coerce(v):
        if v is None: return None
        s = to_str(v)
        if not s: return None
        if re.match(r'^0\d{9,10}$', s): return s
        if s.startswith('0') and len(s) > 1 and s[1:].isdigit(): return s
        try:
            if re.match(r'^-?\d+$', s): return int(s)
            if re.match(r'^-?\d+\.\d+$', s): return float(s)
        except Exception: pass
        return s

# ═══════════════════════════════ COLUMN CONTROLLER ════════════════════════════
class ColumnController:
    ACTIONS = ['keep', 'clear', 'delete', 'override']
    def __init__(self):
        self.rules = {}
        self.delete_rejected = True
        self.erp_mode = False
        self.default_clear_columns = set(COLUMN_CLEAR_DEFAULTS)
    def get(self, column):
        if column in self.rules: return dict(self.rules[column])
        if column in self.default_clear_columns:
            return {'action': 'clear', 'value': None}
        return {'action': 'keep', 'value': None}
    def set_rule(self, column, action, value=None):
        if action not in self.ACTIONS: action = 'keep'
        if action == 'keep' and column not in self.default_clear_columns:
            self.rules.pop(column, None)
        else:
            self.rules[column] = {'action': action, 'value': value}
    def reset(self): self.rules = {}
    def apply_preset(self, name, all_columns):
        self.reset()
        if name == 'keep_all': return
        if name == 'erp_upload':
            for c in all_columns:
                if c in ERP_REJECTED_COLUMNS: self.set_rule(c, 'delete')
            return
        if name == 'erp_minimal':
            keep = set(ERP_REQUIRED_COLUMNS) | {
                'assigned_driver_full_name','driver_phone_number',
                'assigned_vehicle_plate_number','vehicle_type','vehicle_year',
                'schedule_name','schedule_time','schedule_direction',
                'shift_name','working_days','supplier_full_name',
                'supplier_price','client_sales_price',
                'pickup_name','dropoff_name','line_name'}
            for c in all_columns:
                if c not in keep: self.set_rule(c, 'delete')
            return
        if name in ('clear_dropoff', 'farm_frites'):
            self.set_rule('dropoff_departure_time', 'clear'); return
    def to_dict(self):
        return {'rules': self.rules, 'delete_rejected': self.delete_rejected,
                'erp_mode': self.erp_mode,
                'default_clear_columns': list(self.default_clear_columns)}
    @classmethod
    def from_dict(cls, d):
        cc = cls()
        cc.rules = dict(d.get('rules', {}))
        cc.delete_rejected = d.get('delete_rejected', True)
        cc.erp_mode = d.get('erp_mode', False)
        cc.default_clear_columns = set(d.get('default_clear_columns',
                                              COLUMN_CLEAR_DEFAULTS))
        return cc
    def apply_to_worksheet(self, ws, hrow, cmap, logger=None):
        counts = {'cleared': 0, 'overridden': 0, 'deleted': 0}
        if hrow is None: return counts
        for col_name, col_idx in list(cmap.items()):
            rule = self.get(col_name); action = rule['action']
            if action in ('keep', 'delete'): continue
            for r in range(hrow + 1, ws.max_row + 1):
                cell = ws.cell(r, col_idx)
                if action == 'clear':
                    if cell.value is not None and to_str(cell.value) != '':
                        cell.value = None; counts['cleared'] += 1
                elif action == 'override':
                    new_val = rule.get('value') or ''
                    if to_str(cell.value) != new_val:
                        cell.value = new_val
                        cell.fill = PatternFill(start_color="DBEAFE",
                                                end_color="DBEAFE", fill_type="solid")
                        counts['overridden'] += 1
        delete_indices = []
        for col_name, col_idx in cmap.items():
            if self.get(col_name)['action'] == 'delete':
                delete_indices.append((col_name, col_idx))
        if self.delete_rejected:
            for c in ERP_REJECTED_COLUMNS:
                if c in cmap: delete_indices.append((c, cmap[c]))
        seen = set(); unique_deletes = []
        for name, idx in delete_indices:
            if idx not in seen:
                seen.add(idx); unique_deletes.append((name, idx))
        for name, idx in sorted(unique_deletes, key=lambda x: -x[1]):
            try:
                ws.delete_cols(idx, 1); counts['deleted'] += 1
            except Exception: pass
        return counts

# ═══════════════════════════════ SHIFT ENGINE ════════════════════════════════
class ShiftEngine:
    def __init__(self, settings=None):
        self.settings = settings
        self.base_patterns = dict(SHIFT_BASE_PATTERNS)
        self.ordinals = list(SHIFT_ORDINALS)
        if settings:
            for base_display, triggers in settings.custom_shift_bases.items():
                if isinstance(triggers, list) and triggers:
                    self.base_patterns[base_display] = triggers
            for entry in settings.custom_ordinals:
                try:
                    kws, canon, short = entry
                    self.ordinals.append((list(kws), canon, short))
                except Exception: continue

    def _detect_base(self, shift_value):
        s = to_str(shift_value)
        if not s: return None
        if re.search(r'\s[-–—]\s', s): return None
        s_norm = normalize_name(s)
        all_triggers = []
        for base_display, triggers in self.base_patterns.items():
            for trig in triggers:
                all_triggers.append((normalize_name(trig), base_display))
        all_triggers.sort(key=lambda x: -len(x[0]))
        for trig_norm, base_display in all_triggers:
            if trig_norm and trig_norm in s_norm: return base_display
        return None

    def _detect_ordinal(self, schedule_value):
        s = to_str(schedule_value)
        if not s: return None
        first_word = s.split()[0] if s.split() else s
        fw_norm = normalize_name(first_word)
        for keywords, canonical, short in self.ordinals:
            for kw in keywords:
                if fw_norm == normalize_name(kw): return (canonical, short)
        for keywords, canonical, short in self.ordinals:
            for kw in keywords:
                if normalize_name(kw) in fw_norm: return (canonical, short)
        return None

    def _normalize_schedule_first_word(self, schedule_value):
        s = to_str(schedule_value)
        if not s: return None
        parts = s.split(maxsplit=1)
        if not parts: return None
        first = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        for keywords, canonical, _ in self.ordinals:
            for kw in keywords:
                if normalize_name(first) == normalize_name(kw):
                    if to_str(first) == canonical: return None
                    return (canonical + (' ' + rest if rest else ''))
        return None

    def process(self, shift_value, schedule_value):
        base = self._detect_base(shift_value)
        ordinal = self._detect_ordinal(schedule_value) if base else None
        new_shift = None; new_schedule = None; reasons = []
        if base and ordinal:
            canonical, short = ordinal
            new_shift = f"{base} - {short}"
            reasons.append(f"shift '{base}' + ordinal '{short}' → '{new_shift}'")
        normalized_schedule = self._normalize_schedule_first_word(schedule_value)
        if normalized_schedule and normalized_schedule != to_str(schedule_value):
            new_schedule = normalized_schedule
            reasons.append(f"schedule first-word normalized")
        if not new_shift and not new_schedule: return None
        return {'new_shift': new_shift, 'new_schedule': new_schedule,
                'reason': ' · '.join(reasons), 'base': base,
                'ordinal': ordinal[0] if ordinal else None}

# ═══════════════════════════════ ANALYZER ════════════════════════════════════
class CodefyAnalyzer:
    def __init__(self, file_path, column_controller=None, main_suppliers=None,
                 settings=None):
        self.file_path = file_path
        self.file_ext  = os.path.splitext(file_path)[1].lower()
        self.is_csv    = self.file_ext in ('.csv', '.tsv', '.txt')
        self.csv_encoding  = None; self.csv_delimiter = None
        if self.is_csv:
            self.wb, self.csv_encoding, self.csv_delimiter = CSVLoader.load(file_path)
        else:
            self.wb = openpyxl.load_workbook(file_path, data_only=True)
        self.fixes = []; self.sheets_data = {}; self.report = []
        self.column_profile = {}; self.upload_ready = False
        self.custom_reorder_rules = []; self.reorder_plan = {}
        self.group_by_supplier = True
        self.column_controller = column_controller or ColumnController()
        self.main_suppliers = list(main_suppliers or DEFAULT_MAIN_SUPPLIERS)
        self.main_suppliers_norm = {normalize_name(x)
                                     for x in self.main_suppliers if to_str(x)}
        self.settings = settings
        self.shift_engine_enabled = (settings.shift_engine_enabled
                                      if settings else True)
        self.shift_engine = ShiftEngine(settings) if self.shift_engine_enabled else None
        self.time_conflict_enabled = (settings.time_conflict_enabled
                                       if settings else True)
        self.time_conflict_offset = (settings.time_conflict_offset
                                      if settings else DEFAULT_TIME_CONFLICT_OFFSET_MIN)
        self.time_conflict_target = (settings.time_conflict_target
                                      if settings else DEFAULT_TIME_TARGET_COLUMN)
        self.time_conflict_mode = (settings.time_conflict_mode
                                    if settings else TIME_CONFLICT_MODE_AUTOFIX)
        self.time_normalize_enabled = (settings.time_normalize_enabled
                                        if settings else True)
        self.time_convert_12h = (settings.time_convert_12h
                                  if settings else True)
        self.time_column_rules = dict(settings.time_column_rules) if settings else {}
        self.erp_issues = []; self.red_flag_cells = []
        self.issues = {
            'invalid_phones':   [], 'driver_conflicts': [], 'phone_conflicts': [],
            'expiry_alerts':    [], 'missing_data':     [], 'shift_names':      [],
            'duplicate_phones': [], 'enum_violations':  [], 'time_conflicts':   [],
            'date_format_issues': [], 'internal_supplier_fixes': [],
            'shift_upgrades':   [], 'time_normalizations': []}

    def out(self, text="", tag=None): self.report.append((text, tag))
    def hr(self, ch='─', n=80): self.out(ch*n, 'info')

    def _is_main_supplier(self, value):
        s = normalize_name(value)
        return bool(s) and s in self.main_suppliers_norm

    def find_header(self, ws):
        br, bc, bm = None, {}, 0
        for r in range(1, min(ws.max_row+1, 35)):
            cmap, matched = {}, set()
            for cc in range(1, ws.max_column+1):
                raw = to_str(ws.cell(r, cc).value)
                if not raw: continue
                if raw not in cmap: cmap[raw] = cc
                cl = _clean_header_key(raw)
                if cl in ALIAS_LOOKUP:
                    cmap[ALIAS_LOOKUP[cl]] = cc; matched.add(ALIAS_LOOKUP[cl])
            if len(matched) >= 2 or COL_DRIVER_NAME in matched:
                if len(matched) > bm:
                    bm, br, bc = len(matched), r, cmap
        return (br, bc) if br else (None, {})

    def read_sheet(self, ws, hrow, cmap):
        recs = []
        for r in range(hrow+1, ws.max_row+1):
            rec = {'_row': r}
            for name, ci in cmap.items(): rec[name] = ws.cell(r, ci).value
            if all(to_str(v) == '' for k, v in rec.items() if k != '_row'): continue
            recs.append(rec)
        return recs

    def get_all_supplier_names(self):
        names = Counter()
        for info in self.sheets_data.values():
            if info['skipped']: continue
            for rec in info['records']:
                v = to_str(rec.get(COL_SUPPLIER_NAME))
                if v: names[v] += 1
        return names

    def _all_phone_columns(self, cmap):
        cols = set()
        for c in cmap.keys():
            if c.startswith('_'): continue
            if c in (COL_DRIVER_PHONE, COL_SUPPLIER_PHONE):
                cols.add(c); continue
            if is_phone_column_name(c): cols.add(c); continue
        return cols

    def run(self):
        self._banner(); self._load_all(); self._profile_columns()
        self._erp_compatibility_check()
        self._critical_checks(); self._supporting_checks()
        self._advanced_checks()
        self._plan_reorder(); self._executive_summary(); self._final_review()
        return self.report, self.fixes

    def _banner(self):
        self.out("═"*80, 'h1')
        self.out("  ╔══════════════════════════════════════════════════════════════╗", 'h1')
        self.out("  ║      C O D E F Y E R P  ·  S H E E T S A N A L Y Z E R S      ║", 'h1')
        self.out("  ║   🌊  Dark Blue · Time Control Center · v11.3.1  🌊          ║", 'h1')
        self.out("  ╚══════════════════════════════════════════════════════════════╝", 'h1')
        self.out("═"*80, 'h1')
        self.out(f"  File       : {os.path.basename(self.file_path)}", 'info')
        self.out(f"  Size       : {os.path.getsize(self.file_path):,} bytes", 'info')
        self.out(f"  Generated  : {datetime.now():%Y-%m-%d %H:%M:%S}", 'info')
        self.out(f"  Main suppliers : {len(self.main_suppliers)} configured", 'val')
        self.out(f"  Shift Engine   : "
                 f"{'ENABLED 🌊' if self.shift_engine_enabled else 'DISABLED'}", 'val')
        self.out(f"  Time Conflict  : "
                 f"{'ON' if self.time_conflict_enabled else 'OFF'}"
                 f"  (offset={self.time_conflict_offset}min, "
                 f"target={self.time_conflict_target}, "
                 f"mode={self.time_conflict_mode})", 'val')
        self.out()

    def _load_all(self):
        for sheet in self.wb.sheetnames:
            ws = self.wb[sheet]
            hrow, cmap = self.find_header(ws)
            if not hrow:
                self.sheets_data[sheet] = {'records': [], 'cmap': {},
                                           'hrow': None, 'skipped': True}
                continue
            recs = self.read_sheet(ws, hrow, cmap)
            self.sheets_data[sheet] = {'records': recs, 'cmap': cmap,
                                       'hrow': hrow, 'skipped': False}

    def _erp_compatibility_check(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']; present = set(cmap.keys())
            canonical_present = {c for c in present if c in ERP_COLUMN_SPEC}
            missing_required = [c for c in ERP_REQUIRED_COLUMNS
                                if c not in canonical_present]
            rejected = [c for c in ERP_REJECTED_COLUMNS if c in present]
            for c in missing_required:
                self.erp_issues.append({'sheet': sheet, 'kind': 'missing_required',
                                        'column': c})
            for c in rejected:
                self.erp_issues.append({'sheet': sheet, 'kind': 'rejected_column',
                                        'column': c})
        self._validate_enums()

    def _validate_enums(self):
        enum_cols = {c: spec['enum'] for c, spec in ERP_COLUMN_SPEC.items()
                     if 'enum' in spec}
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            for col, allowed in enum_cols.items():
                if col not in info['cmap']: continue
                allowed_norm = {a.lower() for a in allowed}
                for rec in info['records']:
                    v = to_str(rec.get(col))
                    if not v: continue
                    if v.lower() not in allowed_norm:
                        if col == 'schedule_direction' and v.lower() in ('round_trip','both'):
                            continue
                        self.issues['enum_violations'].append({
                            'sheet': sheet, 'row': rec['_row'],
                            'col': col, 'value': v,
                            'allowed': ERP_COLUMN_SPEC[col]['enum']})

    def _profile_columns(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            recs = info['records']; total = len(recs); profile = {}
            for col_name, _ in info['cmap'].items():
                values = [rec.get(col_name) for rec in recs]
                filled = [v for v in values if to_str(v) != '']
                fp = (len(filled) * 100 / total) if total else 0
                uq = len({to_str(v) for v in filled})
                ct = detect_column_type(values)
                if ct != 'date' and is_date_like_column(col_name, values):
                    ct = 'date'
                sm = to_str(filled[0])[:28] if filled else ''
                profile[col_name] = {'type': ct, 'fill_pct': fp, 'unique': uq,
                                     'sample': sm, 'filled': len(filled),
                                     'total': total}
            self.column_profile[sheet] = profile

    def _critical_checks(self):
        self._unique_shift_names()
        self._phone_driver_uniqueness()
        self._driver_phone_consistency()
        self._duplicate_driver_phones()

    def _unique_shift_names(self):
        gc = Counter()
        for info in self.sheets_data.values():
            if info['skipped']: continue
            for rec in info['records']:
                v = to_str(rec.get(COL_SHIFT))
                if v: gc[v] += 1
        for name, cnt in gc.most_common():
            self.issues['shift_names'].append({'shift': name, 'count': cnt})

    def _phone_driver_uniqueness(self):
        pmap = defaultdict(lambda: defaultdict(int))
        for info in self.sheets_data.values():
            if info['skipped']: continue
            for rec in info['records']:
                ph = PhoneValidator.effective(rec.get(COL_DRIVER_PHONE))
                nm = normalize_name(rec.get(COL_DRIVER_NAME))
                if ph and nm: pmap[ph][nm] += 1
        for ph, names in pmap.items():
            if len(names) <= 1: continue
            keys = list(names.keys()); toks = [set(k.split()) for k in keys]
            is_soft = True
            for i in range(len(toks)):
                for j in range(i+1, len(toks)):
                    sh = toks[i] & toks[j]
                    if not (len(sh) >= 2 or (len(toks[i]) == 1 and toks[i] == toks[j])):
                        is_soft = False; break
                if not is_soft: break
            self.issues['phone_conflicts'].append({
                'phone': ph, 'soft': is_soft,
                'names': [{'name': n, 'count': c}
                          for n, c in sorted(names.items(), key=lambda x: -x[1])]})

    def _driver_phone_consistency(self):
        dmap = defaultdict(lambda: defaultdict(int))
        for info in self.sheets_data.values():
            if info['skipped']: continue
            for rec in info['records']:
                nm = normalize_name(rec.get(COL_DRIVER_NAME))
                ph = PhoneValidator.effective(rec.get(COL_DRIVER_PHONE))
                if nm and ph: dmap[nm][ph] += 1
        for nm, phones in {n: c for n, c in dmap.items() if len(c) > 1}.items():
            self.issues['driver_conflicts'].append({
                'driver': nm,
                'phones': [{'phone': p, 'count': c}
                           for p, c in sorted(phones.items(), key=lambda x: -x[1])]})

    def _duplicate_driver_phones(self):
        occ = defaultdict(list)
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            for rec in info['records']:
                ph = PhoneValidator.effective(rec.get(COL_DRIVER_PHONE))
                if not ph: continue
                occ[ph].append({'sheet': sheet, 'row': rec['_row'],
                                'driver_norm': normalize_name(rec.get(COL_DRIVER_NAME)),
                                'driver_raw': to_str(rec.get(COL_DRIVER_NAME))})
        for ph, rows in occ.items():
            if len(rows) <= 1: continue
            drv = {r['driver_norm'] for r in rows if r['driver_norm']}
            kind = 'hard' if len(drv) > 1 else 'soft'
            self.issues['duplicate_phones'].append({
                'phone': ph, 'kind': kind,
                'occurrences': [{'sheet': r['sheet'], 'row': r['row'],
                                 'driver': r['driver_raw']} for r in rows]})

    def _supporting_checks(self):
        self._phone_validation(); self._missing_data(); self._expiry()

    def _phone_validation(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            phone_cols = self._all_phone_columns(info['cmap'])
            for rec in info['records']:
                for col in phone_cols:
                    val = rec.get(col)
                    st, fx, msg = PhoneValidator.classify(val)
                    if st == 'empty' or st == 'ok': continue
                    if st == 'arabic':
                        self.issues['invalid_phones'].append({
                            'sheet': sheet, 'row': rec['_row'], 'col': col,
                            'value': to_str(val), 'reason': msg,
                            'kind': 'arabic', 'fixable': False})
                        self.red_flag_cells.append((sheet, rec['_row'], col, msg))
                        continue
                    if st == 'fixable':
                        self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                           'col': col, 'old': val, 'new': fx,
                                           'reason': msg})
                        continue
                    if st == 'short':
                        self.issues['invalid_phones'].append({
                            'sheet': sheet, 'row': rec['_row'], 'col': col,
                            'value': to_str(val), 'reason': msg,
                            'kind': 'short', 'fixable': False, 'red_flag': True})
                        self.red_flag_cells.append((sheet, rec['_row'], col, msg))
                        continue
                    self.issues['invalid_phones'].append({
                        'sheet': sheet, 'row': rec['_row'], 'col': col,
                        'value': to_str(val), 'reason': msg,
                        'kind': 'invalid', 'fixable': False})
                    self.red_flag_cells.append((sheet, rec['_row'], col, msg))

    def _missing_data(self):
        critical = [COL_DRIVER_NAME, COL_DRIVER_PHONE, COL_PLATE, COL_SHIFT, COL_ROUTE]
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            recs = info['records']
            for col in critical:
                if not recs or col not in info['cmap']: continue
                for r in recs:
                    if not to_str(r.get(col)):
                        self.issues['missing_data'].append(
                            {'sheet': sheet, 'row': r['_row'], 'col': col})

    def _expiry(self):
        today = datetime.today(); th = today + timedelta(days=EXPIRY_WARN_DAYS)
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            for rec in info['records']:
                dl = parse_date(rec.get(COL_DRIVER_LIC_EXP))
                vd = parse_date(rec.get(COL_VEHICLE_EXP))
                nm = to_str(rec.get(COL_DRIVER_NAME)) or '—'
                pl = to_str(rec.get(COL_PLATE)) or '—'
                if dl:
                    if dl < today:
                        self.issues['expiry_alerts'].append(
                            {'kind': 'Driver license EXPIRED', 'identifier': nm,
                             'date': dl.strftime('%Y-%m-%d'),
                             'days': (dl - today).days, 'sheet': sheet})
                    elif dl < th:
                        self.issues['expiry_alerts'].append(
                            {'kind': 'Driver license expiring soon', 'identifier': nm,
                             'date': dl.strftime('%Y-%m-%d'),
                             'days': (dl - today).days, 'sheet': sheet})
                if vd:
                    if vd < today:
                        self.issues['expiry_alerts'].append(
                            {'kind': 'Vehicle license EXPIRED', 'identifier': pl,
                             'date': vd.strftime('%Y-%m-%d'),
                             'days': (vd - today).days, 'sheet': sheet})
                    elif vd < th:
                        self.issues['expiry_alerts'].append(
                            {'kind': 'Vehicle license expiring soon', 'identifier': pl,
                             'date': vd.strftime('%Y-%m-%d'),
                             'days': (vd - today).days, 'sheet': sheet})

    def normalize_working_days(self, raw):
        s = to_str(raw)
        if not s: return ''
        s = s.translate(ARABIC_INDIC_DIGITS)
        parts = WORKING_DAYS_SEPARATORS.split(s)
        found = set()
        for p in parts:
            p_clean = to_str(p).lower()
            p_clean = re.sub(r'\bو\b', ' ', p_clean)
            p_clean = re.sub(r'\band\b', ' ', p_clean).strip()
            if p_clean.startswith('و'): p_clean = p_clean[1:].strip()
            if p_clean.endswith('و'): p_clean = p_clean[:-1].strip()
            if not p_clean: continue
            if p_clean in DAY_ALIAS_LOOKUP:
                found.add(DAY_ALIAS_LOOKUP[p_clean]); continue
            p_norm = normalize_name(p_clean)
            if p_norm in DAY_ALIAS_LOOKUP:
                found.add(DAY_ALIAS_LOOKUP[p_norm]); continue
        if not found:
            s_norm = normalize_name(s)
            for k_norm, v in DAY_ALIAS_LOOKUP.items():
                if k_norm and k_norm in s_norm: found.add(v)
        return ', '.join(d for d in DAY_CANONICAL_ORDER if d in found)

    def _detect_direction_from_schedule(self, schedule_name):
        s = to_str(schedule_name)
        if not s: return None
        s_norm = normalize_name(s)
        for kw in DIRECTION_OUTBOUND_KEYWORDS:
            if normalize_name(kw) in s_norm: return 'home_to_office'
        for kw in DIRECTION_INBOUND_KEYWORDS:
            if normalize_name(kw) in s_norm: return 'office_to_home'
        return None

    def _advanced_checks(self):
        self._normalize_working_days()
        self._upgrade_shifts()
        self._fix_schedule_directions()
        self._scan_all_dates_deep()
        self._internal_supplier_normalization()
        self._normalize_times()
        self._validate_pickup_dropoff_time()

    def _normalize_times(self):
        if not self.time_normalize_enabled:
            return
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']
            for col, _, _ in TIME_COLUMNS:
                if col not in cmap: continue
                for rec in info['records']:
                    raw = rec.get(col)
                    if not to_str(raw): continue
                    norm = normalize_time_string(raw,
                                                  to_hhmm=True,
                                                  convert_12h=self.time_convert_12h)
                    if norm and norm != to_str(raw):
                        self.fixes.append({
                            'sheet': sheet, 'row': rec['_row'], 'col': col,
                            'old': raw, 'new': norm,
                            'reason': f'Time normalized → {norm}'})
                        self.issues['time_normalizations'].append({
                            'sheet': sheet, 'row': rec['_row'], 'col': col,
                            'old': to_str(raw), 'new': norm})
                        rec[col] = norm

    def _validate_pickup_dropoff_time(self):
        if not self.time_conflict_enabled:
            self.out("  ▸ Time-conflict rule — DISABLED by user", 'info')
            self.out()
            return
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']
            pick_col = next((c for c in (COL_PICKUP_ARR, COL_PICKUP_DEP)
                              if c in cmap), None)
            drop_col = next((c for c in (COL_DROPOFF_ARR, COL_DROPOFF_TIME)
                              if c in cmap), None)
            if not pick_col or not drop_col: continue
            for rec in info['records']:
                pv = to_str(rec.get(pick_col))
                dv = to_str(rec.get(drop_col))
                if not pv or not dv: continue
                if pv != dv: continue
                target_col = self.time_conflict_target
                if target_col not in cmap:
                    target_col = drop_col
                target_val = to_str(rec.get(target_col)) if target_col != drop_col else dv
                suggested = offset_time_min(target_val, self.time_conflict_offset)
                if suggested and suggested == pv:
                    suggested = offset_time_min(target_val,
                                                 self.time_conflict_offset * 2)
                is_autofix = (self.time_conflict_mode == TIME_CONFLICT_MODE_AUTOFIX)
                self.issues['time_conflicts'].append({
                    'sheet': sheet, 'row': rec['_row'],
                    'pickup_col': pick_col, 'pickup': pv,
                    'dropoff_col': drop_col, 'dropoff': dv,
                    'target_col': target_col,
                    'suggested_dropoff': suggested,
                    'mode': self.time_conflict_mode,
                    'offset': self.time_conflict_offset})
                if is_autofix and suggested:
                    self.fixes.append({
                        'sheet': sheet, 'row': rec['_row'],
                        'col': target_col, 'old': target_val, 'new': suggested,
                        'reason': (f'{pick_col} == {drop_col} — offset '
                                   f'+{self.time_conflict_offset}min on {target_col}')})

    def _internal_supplier_normalization(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']
            col_sn = COL_SUPPLIER_NAME if COL_SUPPLIER_NAME in cmap else None
            col_sp = COL_SUPPLIER_PHONE if COL_SUPPLIER_PHONE in cmap else None
            col_et = COL_EMP_TYPE if COL_EMP_TYPE in cmap else None
            if not col_sn: continue
            for rec in info['records']:
                raw_sn = to_str(rec.get(col_sn)).strip()
                if not raw_sn: continue
                if not self._is_main_supplier(raw_sn): continue
                old_sn = rec.get(col_sn)
                if to_str(old_sn) != '':
                    self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                       'col': col_sn, 'old': old_sn, 'new': '',
                                       'reason': f'Main supplier "{raw_sn}" → cleared'})
                    rec[col_sn] = ''
                if col_sp:
                    old_sp = rec.get(col_sp)
                    if to_str(old_sp).strip() != '':
                        self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                           'col': col_sp, 'old': old_sp, 'new': '',
                                           'reason': f'Main supplier "{raw_sn}" → cleared phone'})
                        rec[col_sp] = ''
                if col_et:
                    old_et = to_str(rec.get(col_et)).strip().lower()
                    if old_et != 'employee':
                        orig_et = rec.get(col_et)
                        self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                           'col': col_et, 'old': orig_et, 'new': 'employee',
                                           'reason': f'Main supplier "{raw_sn}" → employee'})
                        rec[col_et] = 'employee'
                self.issues['internal_supplier_fixes'].append({
                    'sheet': sheet, 'row': rec['_row'], 'match': raw_sn,
                    'actions': ['cleared name/phone, set employee']})

    def _upgrade_shifts(self):
        if not self.shift_engine: return
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']
            if COL_SHIFT not in cmap or COL_SCHEDULE not in cmap: continue
            for rec in info['records']:
                sv = rec.get(COL_SHIFT); schv = rec.get(COL_SCHEDULE)
                if not to_str(sv) and not to_str(schv): continue
                res = self.shift_engine.process(sv, schv)
                if not res: continue
                if res['new_shift']:
                    self.fixes.append({
                        'sheet': sheet, 'row': rec['_row'], 'col': COL_SHIFT,
                        'old': sv, 'new': res['new_shift'],
                        'reason': f"Shift Engine — {res['reason']}"})
                    rec[COL_SHIFT] = res['new_shift']
                if res['new_schedule']:
                    self.fixes.append({
                        'sheet': sheet, 'row': rec['_row'], 'col': COL_SCHEDULE,
                        'old': schv, 'new': res['new_schedule'],
                        'reason': "Shift Engine — normalized schedule_name"})
                    rec[COL_SCHEDULE] = res['new_schedule']
                self.issues['shift_upgrades'].append({
                    'sheet': sheet, 'row': rec['_row'],
                    'old_shift': to_str(sv), 'new_shift': res['new_shift'] or to_str(sv),
                    'old_schedule': to_str(schv),
                    'new_schedule': res['new_schedule'] or to_str(schv),
                    'reason': res['reason']})

    def _fix_schedule_directions(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            if COL_DIRECTION not in info['cmap']: continue
            if COL_SCHEDULE not in info['cmap']: continue
            for rec in info['records']:
                sched = to_str(rec.get(COL_SCHEDULE))
                if not sched: continue
                expected = self._detect_direction_from_schedule(sched)
                if not expected: continue
                current = to_str(rec.get(COL_DIRECTION))
                if current == expected: continue
                self.fixes.append({
                    'sheet': sheet, 'row': rec['_row'], 'col': COL_DIRECTION,
                    'old': current, 'new': expected,
                    'reason': f"From schedule_name '{sched[:30]}'"})

    def _normalize_working_days(self):
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            if COL_WORKING_DAYS not in info['cmap']: continue
            for rec in info['records']:
                raw = rec.get(COL_WORKING_DAYS)
                if not to_str(raw): continue
                norm = self.normalize_working_days(raw)
                if norm and norm != to_str(raw):
                    self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                       'col': COL_WORKING_DAYS,
                                       'old': raw, 'new': norm,
                                       'reason': 'Normalized working days'})

    def _scan_all_dates_deep(self):
        seen_cells = set()
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            cmap = info['cmap']; date_cols = set()
            for col in cmap:
                if col.startswith('_'): continue
                spec = ERP_COLUMN_SPEC.get(col, {})
                if spec.get('type') == 'date': date_cols.add(col); continue
                vals = [rec.get(col) for rec in info['records']]
                if is_date_like_column(col, vals): date_cols.add(col)
            for col in date_cols:
                if col not in cmap: continue
                for rec in info['records']:
                    raw = rec.get(col)
                    if raw is None or to_str(raw) == '': continue
                    if isinstance(raw, (datetime, date)) and not isinstance(raw, bool):
                        continue
                    st, fx, msg = DateValidator.classify(raw)
                    if st == 'ok' or st == 'empty': continue
                    key = (sheet, rec['_row'], col)
                    if key in seen_cells: continue
                    seen_cells.add(key)
                    self.issues['date_format_issues'].append({
                        'sheet': sheet, 'row': rec['_row'], 'col': col,
                        'value': to_str(raw), 'status': st,
                        'suggested': fx, 'reason': msg})
                    if st == 'fixable' and fx:
                        self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                           'col': col, 'old': raw, 'new': fx,
                                           'reason': f'Deep date scan — {msg}'})
                        rec[col] = fx
            for rec in info['records']:
                for col, raw in list(rec.items()):
                    if col == '_row' or col.startswith('_'): continue
                    if not isinstance(raw, (datetime, date)) or isinstance(raw, bool):
                        continue
                    key = (sheet, rec['_row'], col)
                    if key in seen_cells: continue
                    seen_cells.add(key)
                    if isinstance(raw, datetime):
                        iso = raw.strftime('%Y-%m-%d')
                        has_time = bool(raw.hour or raw.minute or raw.second)
                    else:
                        iso = datetime(raw.year, raw.month, raw.day).strftime('%Y-%m-%d')
                        has_time = False
                    if iso == to_str(raw) and not has_time: continue
                    reason = ('Native datetime → YYYY-MM-DD (time stripped)'
                              if has_time else 'Native date → YYYY-MM-DD')
                    self.issues['date_format_issues'].append({
                        'sheet': sheet, 'row': rec['_row'], 'col': col,
                        'value': to_str(raw), 'status': 'fixable',
                        'suggested': iso, 'reason': reason})
                    self.fixes.append({'sheet': sheet, 'row': rec['_row'],
                                       'col': col, 'old': raw, 'new': iso,
                                       'reason': f'Deep date scan — {reason}'})
                    rec[col] = iso

    def _is_internal_row(self, rec):
        at = normalize_name(rec.get(COL_ASSIGNMENT_TYPE))
        if at and at in {normalize_name(v) for v in INTERNAL_ASSIGNMENT_VALUES}:
            return True
        sn = to_str(rec.get(COL_SUPPLIER_NAME))
        if self._is_main_supplier(sn): return True
        for m in self.main_suppliers:
            if m and to_str(m) in sn: return True
        sup = to_num(rec.get(COL_SUPPLIER_PRICE))
        cli = to_num(rec.get(COL_CLIENT_PRICE))
        if (sup is None or sup == 0) and cli and cli > 0: return True
        return False

    def _plan_reorder(self, log=True):
        tn = {normalize_name(r['supplier'])
              for r in self.custom_reorder_rules if r['position'] == 'top'}
        bn = {normalize_name(r['supplier'])
              for r in self.custom_reorder_rules if r['position'] == 'bottom'}
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            plan = (self._build_grouped_plan(info, tn, bn) if self.group_by_supplier
                    else self._build_perrow_plan(info, tn, bn))
            self.reorder_plan[sheet] = plan

    def _build_grouped_plan(self, info, tn, bn):
        blocks, order, no_sup = {}, [], []
        for rec in info['records']:
            raw = to_str(rec.get(COL_SUPPLIER_NAME))
            key = normalize_name(raw)
            if not key: no_sup.append(rec['_row']); continue
            if key not in blocks: order.append(key); blocks[key] = {'rows': []}
            blocks[key]['rows'].append(rec['_row'])
        placed = set(); top, normal, ubot, aint = [], [], [], []
        for rule in self.custom_reorder_rules:
            if rule['position'] != 'top': continue
            k = normalize_name(rule['supplier'])
            for r in blocks.get(k, {}).get('rows', []):
                if r not in placed: top.append(r); placed.add(r)
        for rule in self.custom_reorder_rules:
            if rule['position'] != 'bottom': continue
            k = normalize_name(rule['supplier'])
            for r in blocks.get(k, {}).get('rows', []):
                if r not in placed: ubot.append(r); placed.add(r)
        for k in order:
            if k in tn or k in bn: continue
            for r in blocks[k]['rows']:
                if r not in placed: normal.append(r); placed.add(r)
        for r in no_sup:
            if r not in placed: normal.append(r); placed.add(r)
        for rec in info['records']:
            if rec['_row'] in placed: continue
            if self._is_internal_row(rec):
                aint.append(rec['_row']); placed.add(rec['_row'])
        for rec in info['records']:
            if rec['_row'] not in placed:
                normal.append(rec['_row']); placed.add(rec['_row'])
        return {'top': top, 'normal': normal, 'bottom': aint + ubot}

    def _build_perrow_plan(self, info, tn, bn):
        top, internal, bsup, normal = [], [], [], []
        for rec in info['records']:
            row = rec['_row']
            sup = normalize_name(rec.get(COL_SUPPLIER_NAME))
            if sup and sup in tn: top.append(row)
            elif sup and sup in bn: bsup.append(row)
            elif self._is_internal_row(rec): internal.append(row)
            else: normal.append(row)
        return {'top': top, 'normal': normal, 'bottom': internal + bsup}

    def _compute_score(self):
        ip_all = self.issues['invalid_phones']
        ip_short = sum(1 for x in ip_all if x.get('kind') == 'short')
        ip_hard  = len(ip_all) - ip_short
        nc = len(self.issues['driver_conflicts'])
        ph = sum(1 for p in self.issues['phone_conflicts'] if not p['soft'])
        ps = sum(1 for p in self.issues['phone_conflicts'] if p['soft'])
        dh = sum(1 for p in self.issues['duplicate_phones'] if p['kind'] == 'hard')
        ds = sum(1 for p in self.issues['duplicate_phones'] if p['kind'] == 'soft')
        ev = len(self.issues['enum_violations']); ei = len(self.erp_issues)
        tc = len(self.issues['time_conflicts'])
        df_invalid = sum(1 for d in self.issues['date_format_issues']
                         if d.get('status') == 'invalid')
        df_fixable = sum(1 for d in self.issues['date_format_issues']
                         if d.get('status') == 'fixable')
        s = 100
        s -= min(24, ip_hard * 3); s -= min(15, ip_short * 2)
        s -= min(12, nc*4); s -= min(16, ph*7); s -= min(6, ps*1)
        s -= min(10, dh*5); s -= min(3, ds*1)
        s -= min(6, ev*1); s -= min(7, ei*2)
        s -= min(18, tc*2)
        s -= min(18, df_invalid * 4); s -= min(12, df_fixable * 2)
        return max(0, s)

    def _executive_summary(self):
        total = sum(len(i['records']) for i in self.sheets_data.values()
                    if not i['skipped'])
        ip_all = self.issues['invalid_phones']
        ip_short = sum(1 for x in ip_all if x.get('kind') == 'short')
        ip_hard  = len(ip_all) - ip_short
        score = self._compute_score()
        grade = ("EXCELLENT" if score >= 90 else "GOOD" if score >= 75 else
                 "FAIR" if score >= 60 else "POOR" if score >= 40 else "CRITICAL")
        self.out("═"*80, 'h1')
        self.out("  🌊 EXECUTIVE SUMMARY", 'h1')
        self.out("═"*80, 'h1')
        self.out(f"  Quality Score : [{bar(score, 30)}] {score}/100 ({grade})", 'h1')
        self.out(f"  Total rows    : {total}", 'info')
        self.out(f"  Total fixes   : {len(self.fixes)}", 'info')
        self.out(f"  🌊 Shift upgrades : {len(self.issues['shift_upgrades'])}",
                 'warn' if self.issues['shift_upgrades'] else 'ok')
        self.out(f"  ⏰ Time conflicts : {len(self.issues['time_conflicts'])}",
                 'warn' if self.issues['time_conflicts'] else 'ok')
        self.out(f"  🕐 Time normalizations : {len(self.issues['time_normalizations'])}",
                 'info' if self.issues['time_normalizations'] else 'ok')
        self.out(f"  🚩 RED-flagged cells : {len(self.red_flag_cells)}",
                 'err' if self.red_flag_cells else 'ok')
        self.out(f"  📞 Short phones : {ip_short}",
                 'warn' if ip_short else 'ok')
        self.out(f"  ✗ Invalid phones : {ip_hard}",
                 'err' if ip_hard else 'ok')
        self.out()

    def _final_review(self):
        dh = sum(1 for p in self.issues['duplicate_phones'] if p['kind'] == 'hard')
        ph = sum(1 for p in self.issues['phone_conflicts'] if not p['soft'])
        nc = len(self.issues['driver_conflicts'])
        tc = len(self.issues['time_conflicts'])
        df_invalid = sum(1 for d in self.issues['date_format_issues']
                         if d.get('status') == 'invalid')
        ip_bad = sum(1 for x in self.issues['invalid_phones']
                     if x.get('kind') not in ('short',))
        ip_short = sum(1 for x in self.issues['invalid_phones']
                       if x.get('kind') == 'short')
        missing_required = [i for i in self.erp_issues
                            if i['kind'] == 'missing_required']
        tc_blocking = (tc > 0 and self.time_conflict_mode == TIME_CONFLICT_MODE_FLAGONLY)
        self.upload_ready = (dh == 0 and ph == 0 and nc == 0
                              and not tc_blocking
                              and df_invalid == 0 and ip_bad == 0 and ip_short == 0
                              and not missing_required)
        self.out("═"*80, 'h1')
        self.out("  VERDICT:  ✅ READY TO UPLOAD" if self.upload_ready
                 else "  VERDICT:  🚩 NOT READY — resolve critical issues first",
                 'ok' if self.upload_ready else 'err')
        if tc and self.time_conflict_mode == TIME_CONFLICT_MODE_AUTOFIX:
            self.out(f"  ℹ  {tc} time-conflict(s) — auto-fix mode is ON "
                     f"(offset +{self.time_conflict_offset}min)", 'info')
        self.out("═"*80, 'h1')

    def _any_dropoff_col(self):
        return any(not i['skipped'] and COL_DROPOFF_TIME in i['cmap']
                   for i in self.sheets_data.values())

    def kpi_quality_breakdown(self):
        ip_all = self.issues['invalid_phones']
        ip_short = sum(1 for x in ip_all if x.get('kind') == 'short')
        ip_hard  = len(ip_all) - ip_short
        return [
            ("Invalid phone numbers", min(24, ip_hard*3), ip_hard, "3 pts"),
            ("Short phones (<10 digits)", min(15, ip_short*2), ip_short, "2 pts"),
            ("Drivers w/ multiple phones",
             min(12, len(self.issues['driver_conflicts'])*4),
             len(self.issues['driver_conflicts']), "4 pts"),
            ("Phones w/ multiple drivers",
             min(16, sum(1 for p in self.issues['phone_conflicts'] if not p['soft'])*7),
             sum(1 for p in self.issues['phone_conflicts'] if not p['soft']), "7 pts"),
            ("Duplicate phones",
             min(10, sum(1 for p in self.issues['duplicate_phones']
                          if p['kind']=='hard')*5),
             sum(1 for p in self.issues['duplicate_phones']
                 if p['kind']=='hard'), "5 pts"),
            ("Enum violations", min(6, len(self.issues['enum_violations'])),
             len(self.issues['enum_violations']), "1 pt"),
            ("ERP issues", min(7, len(self.erp_issues)*2),
             len(self.erp_issues), "2 pts"),
            ("Time conflicts", min(18, len(self.issues['time_conflicts'])*2),
             len(self.issues['time_conflicts']), "2 pts"),
            ("Date — unparseable",
             min(18, sum(1 for d in self.issues['date_format_issues']
                         if d.get('status')=='invalid')*4),
             sum(1 for d in self.issues['date_format_issues']
                 if d.get('status')=='invalid'), "4 pts")]

    def kpi_rows_breakdown(self):
        per_sheet = {}; by_supplier = Counter(); by_direction = Counter()
        by_shift = Counter(); by_project = Counter()
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            per_sheet[sheet] = len(info['records'])
            for rec in info['records']:
                s = to_str(rec.get(COL_SUPPLIER_NAME))
                if s: by_supplier[s] += 1
                d = to_str(rec.get(COL_DIRECTION))
                if d: by_direction[d] += 1
                sh = to_str(rec.get(COL_SHIFT))
                if sh: by_shift[sh] += 1
                p = to_str(rec.get(COL_PROJECT))
                if p: by_project[p] += 1
        return {'per_sheet': per_sheet, 'by_supplier': by_supplier,
                'by_direction': by_direction, 'by_shift': by_shift,
                'by_project': by_project}

    def kpi_fixes_breakdown(self):
        by_col = defaultdict(list)
        for f in self.fixes: by_col[f['col']].append(f)
        return by_col

    def kpi_errors_breakdown(self):
        ip_all = self.issues['invalid_phones']
        ip_short = [x for x in ip_all if x.get('kind') == 'short']
        ip_hard = [x for x in ip_all if x.get('kind') not in ('short',)]
        return {
            'invalid_phones':   ip_hard,
            'short_phones':     ip_short,
            'driver_conflicts': self.issues['driver_conflicts'],
            'duplicate_hard':   [p for p in self.issues['duplicate_phones']
                                 if p['kind'] == 'hard'],
            'phone_hard':       [p for p in self.issues['phone_conflicts']
                                 if not p['soft']],
            'enum_violations':  self.issues['enum_violations'],
            'erp_issues':       self.erp_issues,
            'time_conflicts':   self.issues['time_conflicts'],
            'date_invalid':     [d for d in self.issues['date_format_issues']
                                 if d.get('status') == 'invalid']}

    def kpi_warnings_breakdown(self):
        return {
            'phone_soft':    [p for p in self.issues['phone_conflicts'] if p['soft']],
            'phone_short':   [x for x in self.issues['invalid_phones']
                              if x.get('kind') == 'short'],
            'duplicate_soft':[p for p in self.issues['duplicate_phones']
                              if p['kind'] == 'soft'],
            'missing_data':  self.issues['missing_data'],
            'expiry':        self.issues['expiry_alerts'],
            'date_wrong_fmt':[d for d in self.issues['date_format_issues']
                              if d.get('status') == 'fixable'],
            'internal_supplier_fix': self.issues['internal_supplier_fixes'],
            'shift_upgrades': self.issues['shift_upgrades'],
            'time_normalizations': self.issues['time_normalizations']}

    def kpi_expiry_breakdown(self):
        buckets = {'driver_expired': [], 'driver_soon': [],
                   'vehicle_expired': [], 'vehicle_soon': []}
        for e in self.issues['expiry_alerts']:
            k = e['kind']
            if 'Driver' in k and 'EXPIRED' in k: buckets['driver_expired'].append(e)
            elif 'Driver' in k: buckets['driver_soon'].append(e)
            elif 'Vehicle' in k and 'EXPIRED' in k: buckets['vehicle_expired'].append(e)
            elif 'Vehicle' in k: buckets['vehicle_soon'].append(e)
        return buckets

    def build_issue_list(self):
        out = []; iid = 0
        def _add(**kw):
            nonlocal iid
            iid += 1; kw['id'] = iid; out.append(kw)

        for su in self.issues['shift_upgrades']:
            shift_changed = su['old_shift'] != su['new_shift']
            sched_changed = su['old_schedule'] != su['new_schedule']
            msg_parts = []
            if shift_changed:
                msg_parts.append(f"shift: '{su['old_shift']}' → '{su['new_shift']}'")
            if sched_changed:
                msg_parts.append(f"schedule: '{su['old_schedule']}' → '{su['new_schedule']}'")
            _add(severity='info', category='Shift Engine',
                 sheet=su['sheet'], row=su['row'],
                 column='shift_name / schedule_name',
                 value=su['old_shift'] + ' + ' + su['old_schedule'],
                 message=' · '.join(msg_parts),
                 fixable=False, fix_action=None)

        for tn in self.issues['time_normalizations']:
            _add(severity='info', category='Time Normalized',
                 sheet=tn['sheet'], row=tn['row'], column=tn['col'],
                 value=tn['old'],
                 message=f"'{tn['old']}' → '{tn['new']}'",
                 fixable=False, fix_action=None)

        for df in self.issues['date_format_issues']:
            is_invalid = df.get('status') == 'invalid'
            suggested = df.get('suggested')
            _add(severity='critical' if is_invalid else 'warning',
                 category='Date Format',
                 sheet=df['sheet'], row=df['row'], column=df['col'],
                 value=df['value'],
                 message=(('UNPARSEABLE date — ' if is_invalid
                           else 'Not YYYY-MM-DD — ') + df.get('reason','')),
                 fixable=(suggested is not None and not is_invalid),
                 fix_action=(('override', suggested)
                             if suggested is not None and not is_invalid else None),
                 override_col=df['col'])

        for isf in self.issues['internal_supplier_fixes']:
            _add(severity='info', category='Main Supplier',
                 sheet=isf['sheet'], row=isf['row'],
                 column='supplier_full_name / supplier_phone_number',
                 value=isf['match'],
                 message="Main-supplier match — " + "; ".join(isf['actions']),
                 fixable=False, fix_action=None)

        for tc in self.issues['time_conflicts']:
            is_autofix = tc.get('mode') == TIME_CONFLICT_MODE_AUTOFIX
            _add(severity='warning' if is_autofix else 'critical',
                 category='Time Conflict',
                 sheet=tc['sheet'], row=tc['row'],
                 column=f"{tc['pickup_col']} = {tc['dropoff_col']}",
                 value=f"{tc['pickup']} == {tc['dropoff']}",
                 message=(f"Conflict — {'auto-fixed' if is_autofix else 'flagged'} "
                          f"+{tc.get('offset', 30)}min on "
                          f"{tc.get('target_col', '—')} → "
                          f"{tc.get('suggested_dropoff') or '—'}"),
                 fixable=tc.get('suggested_dropoff') is not None,
                 fix_action=(('override', tc['suggested_dropoff'])
                             if tc.get('suggested_dropoff') else None),
                 override_col=tc.get('target_col') or tc['dropoff_col'])

        for p in self.issues['phone_conflicts']:
            for n in p['names']:
                _add(severity='critical' if not p['soft'] else 'warning',
                     category='Phone Conflict',
                     sheet='—', row='—', column='driver_phone_number',
                     value=p['phone'],
                     message=f"{'Multiple drivers' if not p['soft'] else 'Name variant'}: {n['name']} ×{n['count']}",
                     fixable=False, fix_action=None)
        for d in self.issues['driver_conflicts']:
            for ph in d['phones']:
                _add(severity='critical', category='Driver Conflict',
                     sheet='—', row='—', column='assigned_driver_full_name',
                     value=d['driver'],
                     message=f"Multiple phones: {ph['phone']} ×{ph['count']}",
                     fixable=False, fix_action=None)
        for p in self.issues['duplicate_phones']:
            for o in p['occurrences']:
                _add(severity='critical' if p['kind'] == 'hard' else 'warning',
                     category='Duplicate Phone',
                     sheet=o['sheet'], row=o['row'],
                     column='driver_phone_number',
                     value=p['phone'],
                     message=f"{p['kind'].upper()} duplicate — driver='{o['driver']}'",
                     fixable=False, fix_action=None)

        for ip in self.issues['invalid_phones']:
            kind = ip.get('kind', 'invalid')
            fixable = ip.get('fixable', False)
            suggested = ip.get('suggested')
            severity = 'critical' if kind in ('invalid', 'arabic', 'short') else 'warning'
            category = ('Invalid Phone' if kind == 'invalid'
                         else 'Short Phone (<10)' if kind == 'short'
                         else 'Phone Note')
            _add(severity=severity, category=category,
                 sheet=ip['sheet'], row=ip['row'], column=ip['col'],
                 value=ip['value'], message=ip['reason'],
                 fixable=fixable,
                 fix_action=(('override', suggested)
                             if fixable and suggested else None),
                 override_col=ip['col'])

        for ev in self.issues['enum_violations']:
            _add(severity='critical', category='Enum Violation',
                 sheet=ev['sheet'], row=ev['row'], column=ev['col'],
                 value=ev['value'],
                 message=f"Allowed: {', '.join(ev['allowed'])}",
                 fixable=False, fix_action=None)
        for ei in self.erp_issues:
            _add(severity='critical' if ei['kind'] == 'missing_required' else 'warning',
                 category='ERP Issue',
                 sheet=ei['sheet'], row='—', column=ei['column'],
                 value='—', message=ei['kind'].replace('_', ' ').title(),
                 fixable=False, fix_action=None)
        for md in self.issues['missing_data']:
            _add(severity='warning', category='Missing Data',
                 sheet=md['sheet'], row=md['row'], column=md['col'],
                 value='', message='Empty required cell',
                 fixable=False, fix_action=None)
        for ex in self.issues['expiry_alerts']:
            sev = 'critical' if 'EXPIRED' in ex['kind'] else 'warning'
            _add(severity=sev, category='Expiry Alert',
                 sheet=ex['sheet'], row='—',
                 column=('driver_license_expiry_date' if 'Driver' in ex['kind']
                         else 'vehicle_expiry_date'),
                 value=ex['identifier'],
                 message=f"{ex['kind']} — {ex['date']} ({ex['days']}d)",
                 fixable=False, fix_action=None)
        for f in self.fixes:
            _add(severity='info', category='Auto-Fix',
                 sheet=f['sheet'], row=f['row'], column=f['col'],
                 value=to_str(f['old']),
                 message=f"→ {to_str(f['new'])}  ({f['reason']})",
                 fixable=False, fix_action=None)
        return out

    def _load_fresh_workbook(self):
        if self.is_csv:
            wb, _, _ = CSVLoader.load(self.file_path); return wb
        return openpyxl.load_workbook(self.file_path, data_only=True)

    def _apply_all_transformations(self, wb, add_highlight=True):
        by_sheet = defaultdict(list)
        for f in self.fixes: by_sheet[f['sheet']].append(f)
        applied = 0
        for sheet, items in by_sheet.items():
            if sheet not in wb.sheetnames: continue
            ws = wb[sheet]
            hrow, cmap = self.find_header(ws)
            if not hrow: continue
            for f in items:
                ci = cmap.get(f['col'])
                if not ci: continue
                cell = ws.cell(f['row'], ci)
                cell.value = f['new']
                if add_highlight:
                    cell.fill = PatternFill(start_color="FFF3CD",
                                            end_color="FFF3CD", fill_type="solid")
                    cell.comment = Comment(
                        f"Codefy Auto-Fix:\n• Reason: {f['reason']}\n"
                        f"• Original: '{to_str(f['old'])}'\n"
                        f"• Cleaned: '{to_str(f['new'])}'", "Codefy Analyzer")
                applied += 1

        red_count = 0
        RED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE",
                                fill_type="solid")
        RED_FONT = Font(color="9C0006", bold=True)
        for sheet, row, col, reason in self.red_flag_cells:
            if sheet not in wb.sheetnames: continue
            ws = wb[sheet]
            hrow, cmap = self.find_header(ws)
            if not hrow: continue
            ci = cmap.get(col)
            if not ci: continue
            cell = ws.cell(row, ci)
            cell.fill = RED_FILL
            try: cell.font = RED_FONT
            except Exception: pass
            if add_highlight:
                cell.comment = Comment(
                    f"🚩 Codefy RED FLAG — phone issue (NOT modified):\n"
                    f"• {reason}", "Codefy Analyzer")
            red_count += 1

        for col, rule in self.time_column_rules.items():
            action = rule.get('action', 'keep')
            if action == 'keep': continue
            for sheet, info in self.sheets_data.items():
                if info['skipped']: continue
                if sheet not in wb.sheetnames: continue
                ws = wb[sheet]
                hrow, cmap = self.find_header(ws)
                if not hrow: continue
                ci = cmap.get(col)
                if not ci: continue
                for r in range(hrow + 1, ws.max_row + 1):
                    cell = ws.cell(r, ci)
                    if action == 'clear':
                        if cell.value is not None and to_str(cell.value) != '':
                            cell.value = None
                    elif action == 'override':
                        nv = rule.get('value') or ''
                        if to_str(cell.value) != nv:
                            cell.value = nv
                            if add_highlight:
                                cell.fill = PatternFill(
                                    start_color="DBEAFE", end_color="DBEAFE",
                                    fill_type="solid")
            if action == 'delete':
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    hrow, cmap = self.find_header(ws)
                    if not hrow: continue
                    ci = cmap.get(col)
                    if ci:
                        try: ws.delete_cols(ci, 1)
                        except Exception: pass

        col_counts = {'cleared': 0, 'overridden': 0, 'deleted': 0}
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            if sheet not in wb.sheetnames: continue
            ws = wb[sheet]
            hrow, cmap = self.find_header(ws)
            if not hrow: continue
            counts = self.column_controller.apply_to_worksheet(ws, hrow, cmap)
            for k in col_counts: col_counts[k] += counts[k]
        reordered = 0
        for sheet, plan in self.reorder_plan.items():
            if not plan['top'] and not plan['bottom']: continue
            if sheet not in wb.sheetnames: continue
            info = self.sheets_data[sheet]
            if info['hrow'] is None: continue
            reordered += self._reorder_sheet_rows(wb[sheet], info['hrow'], plan)
        return {'applied_fixes': applied,
                'cleared_dropoff': col_counts['cleared'],
                'cleared_columns': col_counts['cleared'],
                'overridden_cells': col_counts['overridden'],
                'deleted_columns': col_counts['deleted'],
                'reordered_rows': reordered,
                'red_flagged': red_count,
                'shift_upgrades': len(self.issues['shift_upgrades'])}

    def export_fixed(self, out_path):
        self._plan_reorder(log=False)
        wb = self._load_fresh_workbook()
        result = self._apply_all_transformations(wb, add_highlight=True)
        an = "Audit_Log | سجل التعديلات"
        if an in wb.sheetnames: del wb[an]
        aws = wb.create_sheet(title=an); aws.sheet_view.rightToLeft = True
        headers = ["Timestamp | الوقت", "Sheet | الورقة", "Row | الصف",
                   "Column | العمود", "Original | القيمة السابقة",
                   "Fixed | القيمة المصححة", "Reason | السبب"]
        aws.append(headers)
        hf = Font(bold=True, color="FFFFFF", size=11)
        hfill = PatternFill(start_color="4da6ff", end_color="4da6ff", fill_type="solid")
        for c in range(1, len(headers)+1):
            cell = aws.cell(1, c); cell.font = hf; cell.fill = hfill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for f in self.fixes:
            aws.append([now, f['sheet'], f['row'], f['col'],
                        to_str(f['old']), to_str(f['new']), f['reason']])
        for sheet, row, col, reason in self.red_flag_cells:
            aws.append([now, sheet, row, col, "(RED FLAG)",
                        "(NOT MODIFIED)", f"🚩 {reason}"])
        for col, rule in self.column_controller.rules.items():
            aws.append([now, "—", "—", col, f"<{rule['action']}>",
                        str(rule.get('value', '') or ''),
                        f"Column rule — {rule['action']}"])
        for col, rule in self.time_column_rules.items():
            aws.append([now, "—", "—", col, f"<TIME:{rule.get('action','keep')}>",
                        str(rule.get('value', '') or ''),
                        f"Time Control — {rule.get('action','keep')}"])
        for c in range(1, len(headers)+1):
            aws.column_dimensions[get_column_letter(c)].width = 26
        aws.freeze_panes = "A2"
        wb.save(out_path)
        return result

    def export_fixed_csv(self, out_path):
        self._plan_reorder(log=False)
        wb = self._load_fresh_workbook()
        result = self._apply_all_transformations(wb, add_highlight=False)
        target_sheet = None; best_rows = -1
        for sheet, info in self.sheets_data.items():
            if info['skipped']: continue
            n = len(info['records'])
            if n > best_rows: best_rows = n; target_sheet = sheet
        if not target_sheet: raise ValueError("No data sheet found")
        ws = wb[target_sheet]
        hrow, cmap = self.find_header(ws)
        headers = []
        for c in range(1, ws.max_column + 1):
            headers.append(to_str(ws.cell(hrow, c).value))
        while headers and not headers[-1]: headers.pop()
        rows_written = 0
        with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(headers)
            for r in range(hrow + 1, ws.max_row + 1):
                row_vals = []
                for c in range(1, len(headers) + 1):
                    v = ws.cell(r, c).value
                    if v is None: row_vals.append('')
                    elif isinstance(v, datetime): row_vals.append(v.strftime('%Y-%m-%d'))
                    elif isinstance(v, date): row_vals.append(v.strftime('%Y-%m-%d'))
                    else: row_vals.append(to_str(v))
                if not any(row_vals): continue
                w.writerow(row_vals); rows_written += 1
        result['target_sheet'] = target_sheet
        result['csv_rows'] = rows_written
        return result

    def _reorder_sheet_rows(self, ws, header_row, plan):
        if not plan['top'] and not plan['bottom']: return 0
        ds = header_row + 1; de = ws.max_row
        all_rows = list(range(ds, de + 1))
        planned = set(plan['top']) | set(plan['normal']) | set(plan['bottom'])
        ordered = (list(plan['top']) + list(plan['normal']) + list(plan['bottom']) +
                   [r for r in all_rows if r not in planned])
        snaps = {}
        for r in all_rows:
            rc = []
            for c in range(1, ws.max_column + 1):
                cell = ws.cell(r, c)
                rc.append({'value': cell.value,
                           'style': copy.copy(cell._style) if cell._style is not None else None,
                           'comment': cell.comment, 'hyperlink': cell.hyperlink})
            snaps[r] = rc
        for idx, src in enumerate(ordered):
            tgt = ds + idx
            for ci, s in enumerate(snaps[src], start=1):
                cell = ws.cell(tgt, ci)
                cell.value = s['value']
                if s['style'] is not None: cell._style = copy.copy(s['style'])
                if s['comment'] is not None:
                    cell.comment = Comment(s['comment'].text, s['comment'].author or "")
                else: cell.comment = None
        return len(plan['top']) + len(plan['bottom'])

    def export_issues_excel(self, out_path):
        wb = openpyxl.Workbook(); wb.remove(wb.active)
        hf = Font(bold=True, color="FFFFFF", size=11)
        hfill = PatternFill(start_color="4da6ff", end_color="4da6ff", fill_type="solid")
        def _sh(t, h, rows):
            ws = wb.create_sheet(t); ws.sheet_view.rightToLeft = True
            ws.append(h)
            for c in range(1, len(h)+1):
                cell = ws.cell(1, c); cell.font = hf; cell.fill = hfill
            for r in rows: ws.append(r)
            ws.freeze_panes = "A2"
        all_issues = self.build_issue_list()
        _sh("Unified Issues",
            ["ID","Severity","Category","Sheet","Row","Column","Value","Message","Fixable"],
            [[i['id'], i['severity'], i['category'], i['sheet'], i['row'],
              i['column'], i['value'], i['message'],
              'YES' if i['fixable'] else 'NO'] for i in all_issues])
        if self.issues['shift_upgrades']:
            _sh("Shift Upgrades",
                ["Sheet","Row","Old Shift","New Shift",
                 "Old Schedule","New Schedule","Reason"],
                [[s['sheet'], s['row'], s['old_shift'], s['new_shift'],
                  s['old_schedule'], s['new_schedule'], s['reason']]
                 for s in self.issues['shift_upgrades']])
        if self.issues['time_conflicts']:
            _sh("Time Conflicts",
                ["Sheet","Row","Pickup Col","Dropoff Col","Target Col",
                 "Pickup","Dropoff","Suggested","Mode","Offset"],
                [[t['sheet'], t['row'], t['pickup_col'], t['dropoff_col'],
                  t.get('target_col',''), t['pickup'], t['dropoff'],
                  t.get('suggested_dropoff',''), t.get('mode',''),
                  t.get('offset', '')] for t in self.issues['time_conflicts']])
        rows_short = [[i['sheet'], i['row'], i['col'], i['value'], i['reason']]
                      for i in self.issues['invalid_phones']
                      if i.get('kind') == 'short']
        if rows_short:
            _sh("RED-flagged Phones",
                ["Sheet","Row","Column","Value","Reason"], rows_short)
        if not wb.sheetnames:
            wb.create_sheet("No Issues")["A1"] = "✅ No issues found."
        wb.save(out_path)
        return len(wb.sheetnames)

    def export_issues_csv(self, out_path):
        all_issues = self.build_issue_list()
        with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(["ID","Severity","Category","Sheet","Row","Column",
                        "Value","Message","Fixable"])
            for i in all_issues:
                w.writerow([i['id'], i['severity'], i['category'], i['sheet'],
                            i['row'], i['column'], i['value'], i['message'],
                            "YES" if i['fixable'] else "NO"])

    def export_issues_json(self, out_path):
        payload = {
            "file": os.path.basename(self.file_path),
            "generated_at": datetime.now().isoformat(),
            "version": "11.3.1",
            "quality_score": self._compute_score(),
            "upload_ready": self.upload_ready,
            "main_suppliers": self.main_suppliers,
            "shift_engine_enabled": self.shift_engine_enabled,
            "time_rules": {
                "conflict_enabled": self.time_conflict_enabled,
                "offset": self.time_conflict_offset,
                "target": self.time_conflict_target,
                "mode": self.time_conflict_mode,
                "normalize_enabled": self.time_normalize_enabled,
                "convert_12h": self.time_convert_12h,
                "column_rules": self.time_column_rules,
            },
            "shift_upgrades_count": len(self.issues['shift_upgrades']),
            "red_flag_cells_count": len(self.red_flag_cells),
            "fixes_count": len(self.fixes),
            "issues": self.issues,
            "unified_issues": self.build_issue_list(),
            "fixes": [{'sheet': f['sheet'], 'row': f['row'], 'col': f['col'],
                       'old': to_str(f['old']), 'new': to_str(f['new']),
                       'reason': f['reason']} for f in self.fixes]}
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def export_html_report(self, out_path):
        score = self._compute_score()
        total = sum(len(i['records']) for i in self.sheets_data.values()
                    if not i['skipped'])
        ip_short = sum(1 for x in self.issues['invalid_phones']
                       if x.get('kind') == 'short')
        unified = self.build_issue_list()
        vc = "#4ade80" if self.upload_ready else "#ef4444"
        vt = "READY TO UPLOAD ✅" if self.upload_ready else "NOT READY 🚩"
        shift_n = len(self.issues['shift_upgrades'])
        tc_n = len(self.issues['time_conflicts'])
        def _tbl(h, rows):
            if not rows: return ""
            hh = "".join(f"<th>{html_escape(x)}</th>" for x in h)
            b = "".join("<tr>" + "".join(f"<td>{html_escape(c)}</td>" for c in r)
                        + "</tr>" for r in rows)
            return f'<table><thead><tr>{hh}</tr></thead><tbody>{b}</tbody></table>'
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CodefyERP v11.3.1 Report</title>
<style>
body{{background:#0a1628;color:#e8f0ff;font-family:'Segoe UI',sans-serif;
margin:0;padding:24px}}
.c{{max-width:1200px;margin:0 auto}}
h1{{color:#4da6ff}} h2{{color:#38bdf8}}
.card{{background:#122340;border:1px solid #2d4a75;border-radius:12px;
padding:20px;margin:16px 0}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#1a2f52;color:#4da6ff;padding:10px;text-align:left}}
td{{padding:8px;border-bottom:1px solid #2d4a75}}
.v{{display:inline-block;padding:8px 20px;border-radius:20px;
background:{vc}22;color:{vc};border:2px solid {vc}66;font-weight:800}}
.s{{display:inline-block;padding:6px 14px;border-radius:16px;
background:#38bdf822;color:#38bdf8;border:1px solid #38bdf866;font-weight:700;
margin:2px}}
</style></head><body><div class="c">
<h1>🌊 CodefyERP v11.3.1 — Time Control Center Edition</h1>
<div class="card"><h2>📄 {html_escape(os.path.basename(self.file_path))}</h2>
<p>Score: <b>{score}/100</b> · Rows: <b>{total:,}</b> · Fixes: <b>{len(self.fixes)}</b></p>
<p><span class="s">🌊 Shift upgrades: {shift_n}</span>
<span class="s">⏰ Time conflicts: {tc_n}</span>
<span class="s">🚩 RED flags: {len(self.red_flag_cells)}</span>
<span class="s">📞 Short phones: {ip_short}</span></p>
<div class="v">{vt}</div></div>
<div class="card"><h2>⏰ Time Conflicts ({tc_n})</h2>
{_tbl(["Sheet","Row","Pickup","Dropoff","Target","Suggested","Mode"],
      [[t['sheet'], t['row'], t['pickup'], t['dropoff'],
        t.get('target_col',''), t.get('suggested_dropoff',''),
        t.get('mode','')] for t in self.issues['time_conflicts']])
 if self.issues['time_conflicts'] else
 '<p style="color:#4ade80">✅ No time conflicts.</p>'}</div>
<div class="card"><h2>🌊 Shift Engine — Upgrades ({shift_n})</h2>
{_tbl(["Sheet","Row","Old Shift","New Shift","Old Schedule","New Schedule"],
      [[s['sheet'], s['row'], s['old_shift'], s['new_shift'],
        s['old_schedule'], s['new_schedule']]
       for s in self.issues['shift_upgrades']])
 if self.issues['shift_upgrades'] else
 '<p style="color:#4ade80">✅ No shift upgrades needed.</p>'}</div>
<div class="card"><h2>🎯 Unified Issues ({len(unified)})</h2>
{_tbl(["ID","Sev","Category","Sheet","Row","Col","Value","Message"],
     [[i['id'], i['severity'].upper(), i['category'], i['sheet'], i['row'],
       i['column'], i['value'], i['message']] for i in unified]) if unified
 else '<p style="color:#4ade80">✅ No issues.</p>'}</div>
<p style="text-align:center;color:#7a90b8;font-size:12px">
Generated {datetime.now():%Y-%m-%d %H:%M:%S} · CodefyERP v11.3.1 🌊</p>
</div></body></html>"""
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def to_api_dict(self):
        """
        Convert analyzer results to a dictionary format suitable for API responses
        """
        # Count different types of issues
        critical_count = 0
        warning_count = 0
        info_count = 0
        
        # Calculate issue counts
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
                'total_rows': sum(len(sheet['records']) for sheet in self.sheets_data.values() if not sheet['skipped']),
                'total_sheets': len([s for s in self.sheets_data.values() if not s['skipped']]),
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
                    'old': fix['old'],
                    'new': fix['new'],
                    'reason': fix['reason']
                } for fix in self.fixes
            ],
            'column_profile': getattr(self, 'column_profiles', {}),
            'red_flags': [
                {
                    'sheet': cell[0],
                    'row': cell[1],
                    'column': cell[2],
                    'reason': cell[3]
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
                'value': issue.get('value', 'N/A')
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
                'value': issue.get('value', 'N/A')
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
                'value': issue.get('value', 'N/A')
            })
        
        return formatted_issues

# ═══════════════════════════════ WHATSAPP MESSAGE ═════════════════════════════
def _build_whatsapp_message(analyzer, file_name):
    i = analyzer.issues
    ip_short = sum(1 for x in i['invalid_phones'] if x.get('kind') == 'short')
    ip_hard = len(i['invalid_phones']) - ip_short
    nc = len(i['driver_conflicts'])
    ph = sum(1 for p in i['phone_conflicts'] if not p['soft'])
    dh = sum(1 for p in i['duplicate_phones'] if p['kind'] == 'hard')
    tc = len(i.get('time_conflicts', []))
    tcn = len(i.get('time_normalizations', []))
    df_invalid = sum(1 for d in i.get('date_format_issues', [])
                     if d.get('status') == 'invalid')
    shift_n = len(i.get('shift_upgrades', []))
    sc = analyzer._compute_score()
    gr = ("EXCELLENT" if sc >= 90 else "GOOD" if sc >= 75 else
          "FAIR" if sc >= 60 else "POOR" if sc >= 40 else "CRITICAL")
    rdy = "✅ READY TO UPLOAD" if analyzer.upload_ready else "🚩 NOT READY"
    return "\n".join([
        "🌊━━━━━━━━━━━━━━━━━━━━━━━━🌊",
        "⚡ *CodefyERP v11.3.1*",
        "        Time Control Center 🌊",
        "🌊━━━━━━━━━━━━━━━━━━━━━━━━🌊",
        f"📄 `{file_name}`",
        f"🕐 {datetime.now():%Y-%m-%d %H:%M}", "",
        f"📊 *Score: {sc}/100*  — {gr}", "",
        rdy, "",
        f"🌊 Shift upgrades : *{shift_n}*",
        f"⏰ Time conflicts : *{tc}*",
        f"🕐 Time normalized: *{tcn}*",
        f"📅 Bad dates      : *{df_invalid}*",
        f"📞 Bad phones     : *{ip_hard}*",
        f"🚩 Short phones   : *{ip_short}*",
        f"⚡ Multi-driver   : *{ph}*",
        f"👤 Multi-phone    : *{nc}*",
        f"🔁 Duplicates     : *{dh}*",
        f"🔧 Auto-fixes     : *{len(analyzer.fixes)}*",
        "",
        "🌊━━━━━━━━━━━━━━━━━━━━━━━━🌊",
        "_Powered by CodefyERP v11.3.1_"])

# ═══════════════════════════════════════════════════════════════════════════════
#                          UI HELPERS — v11.3.1
# ═══════════════════════════════════════════════════════════════════════════════

class Tooltip:
    """Rich multi-line tooltip — FIXED: pady must be int, not tuple."""
    def __init__(self, widget, text, delay=400, bg=None, fg=None, title=None):
        self.widget = widget; self.text = text; self.delay = delay
        self.bg = bg or "#122340"; self.fg = fg or "#e8f0ff"
        self.title = title
        self.tip = None; self._after_id = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
    def _schedule(self, _=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)
    def _cancel(self):
        if self._after_id:
            try: self.widget.after_cancel(self._after_id)
            except Exception: pass
            self._after_id = None
    def _show(self):
        if self.tip: return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except Exception: return
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True); tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        outer = tk.Frame(tw, bg="#4da6ff", bd=0); outer.pack()
        inner = tk.Frame(outer, bg=self.bg); inner.pack(padx=2, pady=2)
        # ── FIX: use single int for pady, not tuple ──────────────────────
        if self.title:
            title_wrap = tk.Frame(inner, bg=self.bg)
            title_wrap.pack(fill='x', padx=8, pady=(6, 0))
            tk.Label(title_wrap, text=self.title, justify='left',
                     bg=self.bg, fg="#4da6ff",
                     font=("Segoe UI", 9, "bold"),
                     anchor='w').pack(fill='x')
        body_wrap = tk.Frame(inner, bg=self.bg)
        body_wrap.pack(fill='x', padx=8, pady=(2, 6))
        tk.Label(body_wrap, text=self.text, justify='left',
                 bg=self.bg, fg=self.fg, font=("Segoe UI", 9),
                 anchor='w', wraplength=320).pack(fill='x')
        self.tip = tw
    def _hide(self, _=None):
        self._cancel()
        if self.tip:
            try: self.tip.destroy()
            except Exception: pass
            self.tip = None

class CollapsibleSection:
    """A collapsible group in the sidebar."""
    def __init__(self, parent, title, icon, color, app, expanded=True,
                 badge_text=None, badge_color=None):
        self.app = app
        self.color = color
        self.expanded = tk.BooleanVar(value=expanded)
        self.title = title
        self._on_toggle_callbacks = []
        self._badge_label = None
        self._badge_text = badge_text
        self._badge_color = badge_color

        self.wrapper = tk.Frame(parent, bg=app.SURFACE)
        self.wrapper.pack(fill='x', pady=(3, 0))

        self.header = tk.Frame(self.wrapper, bg=app.SURFACE2, cursor='hand2')
        self.header.pack(fill='x')
        self.header_inner = tk.Frame(self.header, bg=app.SURFACE2)
        self.header_inner.pack(fill='x', padx=8, pady=6)

        self.chevron = tk.Label(self.header_inner, text="▾", font=(app.FONT, 10, "bold"),
                                fg=color, bg=app.SURFACE2, cursor='hand2')
        self.chevron.pack(side='left', padx=(2, 6))

        self.icon_lbl = tk.Label(self.header_inner, text=icon, font=(app.FONT, 11, "bold"),
                                  fg=color, bg=app.SURFACE2, cursor='hand2')
        self.icon_lbl.pack(side='left', padx=(0, 6))

        self.title_lbl = tk.Label(self.header_inner, text=title.upper(),
                                   font=(app.FONT, 8, "bold"),
                                   fg=color, bg=app.SURFACE2, cursor='hand2',
                                   anchor='w')
        self.title_lbl.pack(side='left', fill='x', expand=True)

        if badge_text:
            self._badge_label = tk.Label(self.header_inner, text=badge_text,
                                          font=(app.FONT, 7, "bold"),
                                          fg=app.BG, bg=badge_color or color,
                                          padx=6, pady=1, cursor='hand2')
            self._badge_label.pack(side='right')

        self.body = tk.Frame(self.wrapper, bg=app.SURFACE)
        self.body.pack(fill='x')

        for w in (self.header, self.header_inner, self.chevron,
                  self.icon_lbl, self.title_lbl):
            w.bind("<Button-1>", self.toggle)
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(False))

        if not expanded:
            self.body.pack_forget()
            self.chevron.config(text="▸")

    def _hover(self, on):
        bg = self.app.SURFACE3 if on else self.app.SURFACE2
        for w in (self.header, self.header_inner, self.chevron,
                  self.icon_lbl, self.title_lbl, self._badge_label):
            if w:
                try: w.config(bg=bg)
                except Exception: pass

    def toggle(self, _=None):
        self.expanded.set(not self.expanded.get())
        if self.expanded.get():
            self.body.pack(fill='x')
            self.chevron.config(text="▾")
        else:
            self.body.pack_forget()
            self.chevron.config(text="▸")
        for cb in self._on_toggle_callbacks:
            try: cb()
            except Exception: pass

    def set_badge(self, text, color=None):
        if not self._badge_label:
            return
        self._badge_label.config(text=text)
        if color: self._badge_label.config(bg=color)

    def add_child(self, widget):
        widget.pack(fill='x', padx=10, pady=1)

class Toast:
    """Non-blocking sliding notification in the top-right corner."""
    _active = []
    def __init__(self, root, message, kind='info', duration=3500):
        colors = {
            'info':    ('#4da6ff', 'ℹ'),
            'success': ('#5af5c0', '✓'),
            'warning': ('#ffd93d', '⚠'),
            'error':   ('#ff4d6d', '✕'),
        }
        accent, icon = colors.get(kind, colors['info'])
        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        try: self.top.attributes("-alpha", 0.96)
        except Exception: pass
        w, h = 380, 78
        try:
            rx = root.winfo_rootx(); ry = root.winfo_rooty()
            rw = root.winfo_width()
            x = rx + rw - w - 24
            y = ry + 60 + len(Toast._active) * (h + 10)
        except Exception:
            x = 40; y = 40
        self.top.geometry(f"{w}x{h}+{x}+{y}")
        outer = tk.Frame(self.top, bg=accent, bd=0)
        outer.pack(fill='both', expand=True)
        inner = tk.Frame(outer, bg='#122340')
        inner.pack(fill='both', expand=True, padx=2, pady=2)
        tk.Label(inner, text=icon, font=("Segoe UI", 18, "bold"),
                 fg=accent, bg='#122340', padx=12).pack(side='left', fill='y')
        tk.Label(inner, text=message, font=("Segoe UI", 9, "bold"),
                 fg='#e8f0ff', bg='#122340', justify='left',
                 anchor='w', wraplength=w - 80).pack(side='left',
                                                     fill='both', expand=True,
                                                     padx=6, pady=8)
        Toast._active.append(self)
        self.top.after(duration, self._close)
    def _close(self):
        try:
            Toast._active.remove(self)
            self.top.destroy()
        except Exception: pass

# ═══════════════════════════════════════════════════════════════════════════════
#                            🌊  MAIN APPLICATION  ·  v11.3.1
# ═══════════════════════════════════════════════════════════════════════════════

class App:
    BG          = "#0a1628"
    BG2         = "#0f1e33"
    SURFACE     = "#122340"
    SURFACE2    = "#1a2f52"
    SURFACE3    = "#234670"
    BORDER      = "#2d4a75"
    BORDER2     = "#3d5f94"
    FG          = "#e8f0ff"
    FG_SOFT     = "#c5d5f0"
    MUTED       = "#7a90b8"
    PRIMARY     = "#4da6ff"
    CYAN        = "#00d4ff"
    SKY         = "#38bdf8"
    BLUE        = "#4a90ff"
    NAVY        = "#1e40af"
    INDIGO      = "#818cf8"
    VIOLET      = "#8e7dff"
    PURPLE      = "#8e7dff"
    MAGENTA     = "#e879f9"
    PINK        = "#ff6ec7"
    ROSE        = "#fb7185"
    RED         = "#ff4d6d"
    CORAL       = "#ff8a65"
    ORANGE      = "#ff9d40"
    AMBER       = "#fbbf24"
    YELLOW      = "#ffd93d"
    LIME        = "#a4ff5f"
    MINT        = "#5af5c0"
    GREEN       = "#5af5c0"
    EMERALD     = "#34d399"
    TEAL        = "#14b8a6"
    ACCENT      = "#4da6ff"
    FONT        = "Segoe UI"
    MONO        = "Consolas"

    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.analyzer = None
        self._analysis_queue = queue.Queue()
        self._running = False
        self._n_err = 0; self._n_wrn = 0
        self.arabic_shaping = tk.BooleanVar(value=False)
        self.column_controller = ColumnController()
        self.settings = SettingsManager()
        self._issue_store = []
        self._issue_filter_sev = 'all'
        self._issue_sort_col = None; self._issue_sort_desc = False
        self._selected_category = None
        self._category_cards = {}
        self._sidebar_sections = {}
        self._card_cols = 8

        root.title("🌊 CodefyERP · v11.3.1 · Time Control Center")
        root.geometry("1500x920")
        root.minsize(1080, 660)
        root.configure(bg=self.BG)

        self._setup_style()
        self._build_menu()
        self._build_ui()
        self._animate_logo()
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.bind("<Configure>", self._on_root_configure)

    def _setup_style(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except Exception: pass
        s.configure("TNotebook", background=self.SURFACE, borderwidth=0)
        s.configure("TNotebook.Tab", background=self.SURFACE2,
                    foreground=self.MUTED,
                    padding=[22,10], font=(self.FONT, 10, "bold"), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", self.BG)],
              foreground=[("selected", self.PRIMARY)])
        s.configure("TFrame", background=self.BG)
        s.configure("Vertical.TScrollbar", background=self.PRIMARY,
                    troughcolor=self.BG, borderwidth=0,
                    arrowcolor=self.SKY, relief="flat")
        s.configure("Horizontal.TScrollbar", background=self.PRIMARY,
                    troughcolor=self.BG, borderwidth=0,
                    arrowcolor=self.SKY, relief="flat")
        s.configure("Horizontal.TProgressbar", troughcolor=self.SURFACE2,
                    background=self.PRIMARY, borderwidth=0, thickness=6)
        s.configure("TCombobox", fieldbackground=self.SURFACE3,
                    background=self.SURFACE3, foreground=self.FG,
                    arrowcolor=self.PRIMARY, bordercolor=self.BORDER2)
        s.map("TCombobox",
              fieldbackground=[("readonly", self.SURFACE3)],
              foreground=[("readonly", self.FG)])
        s.configure("Issues.Treeview",
                    background=self.SURFACE, fieldbackground=self.SURFACE,
                    foreground=self.FG, rowheight=28,
                    font=(self.FONT, 9), borderwidth=0)
        s.configure("Issues.Treeview.Heading",
                    background=self.SURFACE2, foreground=self.PRIMARY,
                    font=(self.FONT, 9, 'bold'), relief='flat', borderwidth=0)
        s.map("Issues.Treeview",
              background=[("selected", self.SURFACE3)],
              foreground=[("selected", self.YELLOW)])
        s.configure("Fixes.Treeview",
                    background=self.SURFACE, fieldbackground=self.SURFACE,
                    foreground=self.FG, rowheight=26,
                    font=(self.FONT, 9), borderwidth=0)
        s.configure("Fixes.Treeview.Heading",
                    background=self.SURFACE2, foreground=self.PRIMARY,
                    font=(self.FONT, 9, 'bold'), relief='flat', borderwidth=0)

    def _build_menu(self):
        menubar = tk.Menu(self.root, bg=self.SURFACE2, fg=self.FG,
                          activebackground=self.PRIMARY,
                          activeforeground=self.BG,
                          borderwidth=0, tearoff=0)
        def _mk_menu(name):
            m = tk.Menu(menubar, tearoff=0, bg=self.SURFACE2, fg=self.FG,
                        activebackground=self.PRIMARY, activeforeground=self.BG,
                        borderwidth=0)
            menubar.add_cascade(label=name, menu=m)
            return m

        fm = _mk_menu("📁  File")
        fm.add_command(label="📂  Browse File…              Ctrl+O",
                       command=self.browse_file, accelerator="Ctrl+O")
        fm.add_command(label="🗑  Clear Results", command=self._clear_all)
        fm.add_separator()
        fm.add_command(label="💾  Export Fixed Excel…       Ctrl+S",
                       command=self.export_fixed, accelerator="Ctrl+S")
        fm.add_command(label="📤  Export Fixed CSV…",
                       command=self.export_fixed_csv)
        fm.add_command(label="🌐  Export HTML Report…",
                       command=self.export_html)
        fm.add_separator()
        fm.add_command(label="🚪  Exit", command=self._on_close)

        am = _mk_menu("🔍  Analyze")
        am.add_command(label="🔍  Analyze File            F5",
                       command=self.analyze, accelerator="F5")
        am.add_command(label="🎛️  Column Control…",
                       command=self._show_column_dialog)
        am.add_command(label="🎯  Supplier Reorder…",
                       command=self._show_reorder_dialog)
        am.add_command(label="🔧  Auto-Fix Log…",
                       command=self._show_auto_fix_log)

        cm = _mk_menu("⚙  Configure")
        cm.add_command(label="🏢  Main Suppliers…",
                       command=self._show_main_suppliers_dialog)
        cm.add_command(label="🌊  Shift Engine…",
                       command=self._show_shift_engine_dialog)
        cm.add_command(label="🕐  Time Control Center…",
                       command=self._show_time_control_center)

        em = _mk_menu("📤  Export")
        em.add_command(label="📊  Issues → Excel", command=self.export_issues_excel)
        em.add_command(label="📑  Issues → CSV",   command=self.export_issues_csv)
        em.add_command(label="🧾  Issues → JSON",  command=self.export_issues_json)
        em.add_command(label="📄  Issues → TXT",   command=self.export_issues_txt)
        em.add_separator()
        em.add_command(label="📋  Full Report → TXT", command=self.export_full_txt)

        sm = _mk_menu("💬  Share")
        sm.add_command(label="📲  Send via WhatsApp…", command=self.send_whatsapp)
        sm.add_command(label="📋  Copy Summary",       command=self.copy_summary)

        vm = _mk_menu("🎨  View")
        vm.add_checkbutton(label="🔤  Reshape Arabic",
                           variable=self.arabic_shaping,
                           command=self._reapply_shaping)
        vm.add_separator()
        vm.add_command(label="⬇️  Collapse All Sidebar",
                       command=lambda: self._set_all_sidebar(False))
        vm.add_command(label="⬆️  Expand All Sidebar",
                       command=lambda: self._set_all_sidebar(True))

        hm = _mk_menu("❓  Help")
        hm.add_command(label="📖  Quick Guide", command=self._show_help)
        hm.add_command(label="ℹ️  About CodefyERP v11.3.1",
                       command=self._show_about)

        self.root.config(menu=menubar)
        self.root.bind_all("<Control-o>", lambda e: self.browse_file())
        self.root.bind_all("<Control-O>", lambda e: self.browse_file())
        self.root.bind_all("<Control-s>", lambda e: self.export_fixed())
        self.root.bind_all("<Control-S>", lambda e: self.export_fixed())
        self.root.bind_all("<F5>", lambda e: self.analyze())

    def _build_ui(self):
        self._topbar = tk.Frame(self.root, bg=self.SURFACE, height=68)
        self._topbar.pack(fill='x', side='top')
        self._topbar.pack_propagate(False)
        self._topbar.grid_columnconfigure(1, weight=1)
        self._topbar.grid_rowconfigure(0, weight=1)

        lf = tk.Frame(self._topbar, bg=self.SURFACE)
        lf.grid(row=0, column=0, sticky='w', padx=(20, 0))
        self._logo_lbl = tk.Label(lf, text="🌊", font=(self.FONT, 24, "bold"),
                                  fg=self.PRIMARY, bg=self.SURFACE)
        self._logo_lbl.pack(side='left')
        tf = tk.Frame(lf, bg=self.SURFACE); tf.pack(side='left', padx=(6,0))
        tk.Label(tf, text="Codefy", font=(self.FONT, 17, "bold"),
                 fg=self.PRIMARY, bg=self.SURFACE).pack(side='left')
        tk.Label(tf, text="ERP", font=(self.FONT, 17, "bold"),
                 fg=self.CYAN, bg=self.SURFACE).pack(side='left')
        tk.Label(tf, text=" v11.3.1", font=(self.FONT, 10, "italic"),
                 fg=self.SKY, bg=self.SURFACE).pack(side='left', pady=(4,0))

        bf = tk.Frame(self._topbar, bg=self.SURFACE)
        bf.grid(row=0, column=2, sticky='e', padx=20, pady=10)

        self._supplier_badge = tk.Label(
            bf, text=f"🏢 {len(self.settings.main_suppliers)}",
            font=(self.FONT, 9, "bold"),
            fg=self.FG, bg=self.VIOLET, padx=10, pady=4, cursor='hand2')
        self._supplier_badge.pack(side='left', padx=3)
        self._supplier_badge.bind("<Button-1>",
            lambda e: self._show_main_suppliers_dialog())
        Tooltip(self._supplier_badge,
                "Open the Main Suppliers manager",
                title="🏢 Main Suppliers")

        self._shift_badge = tk.Label(
            bf, text=f"🌊 Shift {'ON' if self.settings.shift_engine_enabled else 'OFF'}",
            font=(self.FONT, 9, "bold"), fg=self.BG,
            bg=self.MINT if self.settings.shift_engine_enabled else self.MUTED,
            padx=10, pady=4, cursor='hand2')
        self._shift_badge.pack(side='left', padx=3)
        self._shift_badge.bind("<Button-1>",
            lambda e: self._show_shift_engine_dialog())
        Tooltip(self._shift_badge,
                "Configure automatic shift name upgrades",
                title="🌊 Shift Engine")

        self._time_badge = tk.Label(
            bf, text=f"🕐 Time {'ON' if self.settings.time_conflict_enabled else 'OFF'}",
            font=(self.FONT, 9, "bold"), fg=self.BG,
            bg=self.YELLOW if self.settings.time_conflict_enabled else self.MUTED,
            padx=10, pady=4, cursor='hand2')
        self._time_badge.pack(side='left', padx=3)
        self._time_badge.bind("<Button-1>",
            lambda e: self._show_time_control_center())
        Tooltip(self._time_badge,
                "Time conflict rules, offsets, per-column actions",
                title="🕐 Time Control Center")

        strip = tk.Frame(self.root, bg=self.BG, height=4)
        strip.pack(fill='x')
        for col in [self.NAVY, self.PRIMARY, self.SKY,
                    self.CYAN, self.TEAL, self.MINT, self.EMERALD]:
            tk.Frame(strip, bg=col).pack(side='left', fill='both', expand=True)

        pf = tk.Frame(self.root, bg=self.BG, height=6); pf.pack(fill='x')
        self._pbar = ttk.Progressbar(pf, mode='indeterminate',
                                     style="Horizontal.TProgressbar")
        self._pbar.pack(fill='x'); self._pbar.pack_forget()

        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill='both', expand=True)
        self._sidebar = self._make_scrollable_sidebar(content, width=280)
        main = tk.Frame(content, bg=self.BG)
        main.pack(side='left', fill='both', expand=True)
        self._build_file_strip(main)
        self._build_dashboard(main)
        self._build_notebook(main)

        sb = tk.Frame(self.root, bg=self.SURFACE2, height=28)
        sb.pack(fill='x', side='bottom'); sb.pack_propagate(False)
        self._status_dot = tk.Label(sb, text="●", font=(self.FONT, 11),
                                    fg=self.MINT, bg=self.SURFACE2)
        self._status_dot.pack(side='left', padx=(14,6), pady=5)
        self._status_lbl = tk.Label(
            sb, text="✨ Ready — Time Control Center armed 🌊",
            font=(self.FONT, 9, "bold"), fg=self.SKY,
            bg=self.SURFACE2, anchor='w')
        self._status_lbl.pack(side='left', fill='x', expand=True)
        tk.Label(sb, text=f"🌊 v11.3.1 · Py {sys.version.split()[0]}",
                 font=(self.FONT, 8, "bold"), fg=self.PRIMARY,
                 bg=self.SURFACE2).pack(side='right', padx=14)

    def _make_scrollable_sidebar(self, parent, width=280):
        wrapper = tk.Frame(parent, bg=self.SURFACE, width=width)
        wrapper.pack(side='left', fill='y'); wrapper.pack_propagate(False)
        canvas = tk.Canvas(wrapper, bg=self.SURFACE, highlightthickness=0, width=width)
        vsb = ttk.Scrollbar(wrapper, orient='vertical', command=canvas.yview,
                             style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(canvas, bg=self.SURFACE)
        win_id = canvas.create_window((0, 0), window=inner, anchor='nw')
        def _on_inner_config(e): canvas.configure(scrollregion=canvas.bbox('all'))
        inner.bind('<Configure>', _on_inner_config)
        def _on_canvas_config(e): canvas.itemconfigure(win_id, width=e.width)
        canvas.bind('<Configure>', _on_canvas_config)
        def _on_wheel(e): canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        canvas.bind('<MouseWheel>', _on_wheel)
        inner.bind('<MouseWheel>', _on_wheel)
        self._sidebar_canvas = canvas
        self._build_sidebar_content(inner)
        return wrapper

    def _build_sidebar_content(self, parent):
        self._sidebar_inner = parent

        hdr = tk.Frame(parent, bg=self.SURFACE)
        hdr.pack(fill='x', padx=14, pady=(10, 4))
        tk.Label(hdr, text="⚡  CONTROL PANEL",
                 font=(self.FONT, 9, "bold"), fg=self.PRIMARY,
                 bg=self.SURFACE).pack(side='left')
        for txt, expand in [("⬆", True), ("⬇", False)]:
            b = tk.Label(hdr, text=txt, font=(self.FONT, 10, "bold"),
                         fg=self.SKY, bg=self.SURFACE, cursor='hand2', padx=4)
            b.pack(side='right')
            b.bind("<Button-1>", lambda e, x=expand: self._set_all_sidebar(x))
            b.bind("<Enter>", lambda e, w=b: w.config(fg=self.YELLOW))
            b.bind("<Leave>", lambda e, w=b: w.config(fg=self.SKY))

        def _btn(section, txt, icon, cmd, color, tip_title=None, tip_body=None):
            f = tk.Frame(section.body, bg=self.SURFACE, cursor='hand2')
            section.add_child(f)
            inner = tk.Frame(f, bg=self.SURFACE); inner.pack(fill='x')
            accent = tk.Frame(inner, bg=color, width=4)
            accent.pack(side='left', fill='y')
            il = tk.Label(inner, text=f" {icon}", font=(self.FONT, 12),
                          fg=color, bg=self.SURFACE, cursor='hand2')
            il.pack(side='left', padx=(6,0))
            lb = tk.Label(inner, text=txt, font=(self.FONT, 9, "bold"),
                          fg=self.FG, bg=self.SURFACE, anchor='w', cursor='hand2')
            lb.pack(side='left', fill='x', expand=True, padx=(6,0), pady=6)
            def _ho(e):
                for w in (f, inner, il, lb):
                    w.config(bg=self.SURFACE3)
                lb.config(fg=color)
            def _hf(e):
                for w in (f, inner, il, lb):
                    w.config(bg=self.SURFACE)
                lb.config(fg=self.FG)
            for w in (f, inner, il, lb):
                w.bind("<Enter>", _ho); w.bind("<Leave>", _hf)
                w.bind("<Button-1>", lambda e, c=cmd: c())
            if tip_body:
                Tooltip(f, tip_body, title=tip_title)
            return f

        s_file = CollapsibleSection(parent, "File", "📁", self.YELLOW,
                                     self, expanded=True)
        self._sidebar_sections['file'] = s_file
        _btn(s_file, "Browse File…", "📂", self.browse_file, self.YELLOW,
             "📂 Browse File", "Pick an Excel or CSV file to analyze.\nCtrl+O")
        _btn(s_file, "Clear Results", "🗑", self._clear_all, self.RED,
             "🗑 Clear Results", "Reset all views and analysis data.")

        s_ana = CollapsibleSection(parent, "Analyze", "🔍", self.PRIMARY,
                                    self, expanded=True)
        self._sidebar_sections['analyze'] = s_ana
        _btn(s_ana, "Run Full Analysis", "🔍", self.analyze, self.PRIMARY,
             "🔍 Full Analysis", "Audit + Shift Engine + Time Control.\nF5")

        s_cfg = CollapsibleSection(parent, "Configure", "⚙", self.CORAL,
                                    self, expanded=False)
        self._sidebar_sections['configure'] = s_cfg
        _btn(s_cfg, "Column Control", "🎛️", self._show_column_dialog, self.VIOLET,
             "🎛️ Column Control", "Keep / clear / delete / override columns.")
        _btn(s_cfg, "Supplier Reorder", "🎯", self._show_reorder_dialog, self.CYAN,
             "🎯 Supplier Reorder", "Pin suppliers to top or bottom of the sheet.")
        _btn(s_cfg, "Auto-Fix Log", "🔧", self._show_auto_fix_log, self.MINT,
             "🔧 Auto-Fix Log", "Inspect every queued change before export.")

        s_sh = CollapsibleSection(parent, "Shift Engine", "🌊", self.SKY,
                                    self, expanded=False,
                                    badge_text="ON" if self.settings.shift_engine_enabled else "OFF",
                                    badge_color=self.MINT if self.settings.shift_engine_enabled else self.MUTED)
        self._sidebar_sections['shift'] = s_sh
        _btn(s_sh, "Shift Rules", "🌊", self._show_shift_engine_dialog, self.SKY,
             "🌊 Shift Rules", "Configure automatic shift-name upgrades.")
        _btn(s_sh, "Preview Upgrades", "👁", self._show_shift_preview, self.MINT,
             "👁 Preview Upgrades", "See exactly what shift names will change.")

        s_tm = CollapsibleSection(parent, "Time Control", "🕐", self.YELLOW,
                                    self, expanded=False,
                                    badge_text="ON" if self.settings.time_conflict_enabled else "OFF",
                                    badge_color=self.YELLOW if self.settings.time_conflict_enabled else self.MUTED)
        self._sidebar_sections['time'] = s_tm
        _btn(s_tm, "Time Center", "🕐", self._show_time_control_center, self.YELLOW,
             "🕐 Time Center", "Offset rules, modes, per-column actions.")
        _btn(s_tm, "Time Preview", "👁", self._show_time_preview, self.AMBER,
             "👁 Time Preview", "Preview how conflicts will be handled.")

        s_ex = CollapsibleSection(parent, "Export", "📤", self.CYAN,
                                    self, expanded=True)
        self._sidebar_sections['export'] = s_ex
        self._sb_fixed     = _btn(s_ex, "Fixed Excel",   "💾", self.export_fixed, self.MINT,
                                   "💾 Fixed Excel", "Apply all fixes and save .xlsx with Audit Log.")
        self._sb_fixed_csv = _btn(s_ex, "Fixed CSV",     "📤", self.export_fixed_csv, self.CYAN,
                                   "📤 Fixed CSV", "Save the largest sheet as UTF-8 CSV.")
        self._sb_html      = _btn(s_ex, "HTML Report",   "🌐", self.export_html, self.VIOLET,
                                   "🌐 HTML Report", "Dark-themed stand-alone report.")
        self._sb_xlsx      = _btn(s_ex, "Issues Excel",  "📊", self.export_issues_excel, self.YELLOW,
                                   "📊 Issues Excel", "Multi-sheet issue dump.")
        self._sb_csv       = _btn(s_ex, "Issues CSV",    "📑", self.export_issues_csv, self.LIME,
                                   "📑 Issues CSV", "Flat CSV of every detected issue.")
        self._sb_json      = _btn(s_ex, "Issues JSON",   "🧾", self.export_issues_json, self.MINT,
                                   "🧾 Issues JSON", "Machine-readable full payload.")
        self._sb_txt       = _btn(s_ex, "Issues TXT",    "📄", self.export_issues_txt, self.MUTED,
                                   "📄 Issues TXT", "Plain-text issue list.")
        self._sb_report    = _btn(s_ex, "Full Report",   "📋", self.export_full_txt, self.BLUE,
                                   "📋 Full Report", "Full console output as text.")

        s_shr = CollapsibleSection(parent, "Share", "💬", self.MINT,
                                     self, expanded=False)
        self._sidebar_sections['share'] = s_shr
        self._sb_wa   = _btn(s_shr, "Send WhatsApp", "💬", self.send_whatsapp, "#25D366",
                              "💬 Send WhatsApp", "Open WhatsApp Web with a summary.")
        self._sb_copy = _btn(s_shr, "Copy Summary", "📋", self.copy_summary, self.MAGENTA,
                              "📋 Copy Summary", "Copy the summary to clipboard.")

        s_disp = CollapsibleSection(parent, "Display", "🎨", self.VIOLET,
                                      self, expanded=False)
        self._sidebar_sections['display'] = s_disp
        chk_wrap = tk.Frame(s_disp.body, bg=self.SURFACE)
        s_disp.add_child(chk_wrap)
        tk.Checkbutton(chk_wrap, text="  🔤  Reshape Arabic",
                       variable=self.arabic_shaping,
                       command=self._reapply_shaping,
                       font=(self.FONT, 9, "bold"), fg=self.VIOLET,
                       bg=self.SURFACE, activebackground=self.SURFACE,
                       activeforeground=self.PRIMARY,
                       selectcolor=self.SURFACE2, cursor='hand2',
                       anchor='w').pack(fill='x', pady=4)

        tk.Label(parent, text="🌊 CodefyERP v11.3.1\n© 2026 · Time Control Center",
                 font=(self.FONT, 8, "bold"), fg=self.PRIMARY, bg=self.SURFACE,
                 justify='center').pack(pady=14)

        self._export_btns = [self._sb_fixed, self._sb_fixed_csv, self._sb_html,
                             self._sb_xlsx, self._sb_csv, self._sb_json,
                             self._sb_txt, self._sb_report, self._sb_wa,
                             self._sb_copy]
        for b in self._export_btns: self._set_btn_color(b, self.MUTED)

    def _set_all_sidebar(self, expand):
        for s in self._sidebar_sections.values():
            if s.expanded.get() != expand:
                s.toggle()

    def _set_btn_color(self, btn_frame, color):
        try:
            for inner in btn_frame.winfo_children():
                for w in inner.winfo_children():
                    try:
                        if isinstance(w, tk.Label): w.config(fg=color)
                        elif isinstance(w, tk.Frame): w.config(bg=color)
                    except Exception: pass
        except Exception: pass

    def _build_file_strip(self, parent):
        strip = tk.Frame(parent, bg=self.SURFACE, height=56)
        strip.pack(fill='x', padx=14, pady=(10,6))
        strip.pack_propagate(False)
        self._file_icon = tk.Label(strip, text="📁", font=(self.FONT, 15),
                                   fg=self.PRIMARY, bg=self.SURFACE)
        self._file_icon.pack(side='left', padx=(14,8), pady=14)
        self._file_lbl = tk.Label(strip,
            text="✨ No file selected — click Browse to start!",
            font=(self.FONT, 10, "bold"), fg=self.MUTED,
            bg=self.SURFACE, anchor='w')
        self._file_lbl.pack(side='left', fill='x', expand=True, pady=18)

        self._analyze_btn = self._make_btn(strip, "🔍 Analyze", self.analyze,
                                           self.PRIMARY, padx=18, fg=self.FG)
        self._analyze_btn.pack(side='right', padx=10, pady=8)
        b = self._make_btn(strip, "📂 Browse", self.browse_file,
                           self.VIOLET, padx=14, fg=self.FG)
        b.pack(side='right', padx=(0,4), pady=8)

        pill_wrap = tk.Frame(strip, bg=self.SURFACE)
        pill_wrap.pack(side='right', padx=(0, 4), pady=10)
        self._time_pill = tk.Frame(pill_wrap, bg=self.YELLOW, cursor='hand2')
        self._time_pill.pack()
        self._time_pill_lbl = tk.Label(
            self._time_pill, text="🕐 TIME CENTER",
            font=(self.FONT, 9, "bold"),
            fg=self.BG, bg=self.YELLOW, padx=10, pady=6, cursor='hand2')
        self._time_pill_lbl.pack()
        for w in (self._time_pill, self._time_pill_lbl):
            w.bind("<Button-1>", lambda e: self._show_time_control_center())
        Tooltip(self._time_pill, "Open the Time Control Center",
                title="🕐 Time Center")
        self._refresh_time_pill()

    def _refresh_time_pill(self):
        if not hasattr(self, '_time_pill'): return
        on = self.settings.time_conflict_enabled
        bg = self.YELLOW if on else self.MUTED
        self._time_pill.config(bg=bg)
        self._time_pill_lbl.config(
            bg=bg, text=f"🕐 TIME {'ON' if on else 'OFF'} · +{self.settings.time_conflict_offset}m")

    def _build_dashboard(self, parent):
        self._dash_wrap = tk.Frame(parent, bg=self.BG)
        self._dash_wrap.pack(fill='x', padx=14, pady=(0, 6))

        self._cards = {}
        self._card_defs = [
            ("quality_score",  "🎯", "Score",       self.PRIMARY, self.BLUE,
             "Quality Score", "Weighted score out of 100.\nClick for the full breakdown."),
            ("total_rows",     "📋", "Rows",        self.CYAN,    self.SKY,
             "Total Rows", "Total data rows across all sheets."),
            ("auto_fixes",     "🔧", "Fixes",       self.YELLOW,  self.AMBER,
             "Auto-Fixes", "Number of automatic corrections queued.\nClick to open the fix log."),
            ("shift_upgrades", "🌊", "Shift Upgr.", self.SKY,     self.CYAN,
             "Shift Upgrades", "Shift names detected for automatic upgrade."),
            ("time_conflicts", "⏰", "Time Confl.", self.ORANGE,  self.AMBER,
             "Time Conflicts", "Pickup/dropoff time equalities.\nClick for details."),
            ("errors_count",   "✗",  "Errors",      self.RED,     self.CORAL,
             "Errors", "Blocking issues that prevent upload."),
            ("short_phones",   "🚩", "Red Flags",   self.PINK,    self.MAGENTA,
             "Red Flags", "Un-fixable phones marked red for manual review."),
            ("expiry_alerts",  "📅", "Expiring",    self.MINT,    self.TEAL,
             "Expiry Alerts", "Driver / vehicle licenses within 90 days or already expired."),
        ]
        for key, icon, label, c1, c2, tip_t, tip_b in self._card_defs:
            card = self._make_kpi_card(self._dash_wrap, key, icon, label, c1, c2,
                                        tip_t, tip_b)
            self._cards[key] = (card['val'], c1)
        self._reflow_dashboard(cols=8)

    def _make_kpi_card(self, parent, key, icon, label, c1, c2, tip_t, tip_b):
        glow = tk.Frame(parent, bg=c1, cursor='hand2')
        card = tk.Frame(glow, bg=self.SURFACE, cursor='hand2')
        card.pack(fill='both', expand=True, padx=2, pady=2)
        topbar = tk.Frame(card, bg=c2, height=3, cursor='hand2')
        topbar.pack(fill='x')
        body = tk.Frame(card, bg=self.SURFACE, cursor='hand2')
        body.pack(fill='both', expand=True, padx=8, pady=(6, 8))
        icon_l = tk.Label(body, text=icon, font=(self.FONT, 13),
                          fg=c1, bg=self.SURFACE, cursor='hand2')
        icon_l.pack(anchor='w')
        val_l = tk.Label(body, text="—", font=(self.FONT, 17, "bold"),
                         fg=c1, bg=self.SURFACE, cursor='hand2')
        val_l.pack(anchor='w', pady=(1, 0))
        lbl_l = tk.Label(body, text=label, font=(self.FONT, 8, "bold"),
                         fg=self.MUTED, bg=self.SURFACE, cursor='hand2')
        lbl_l.pack(anchor='w')

        def _ho(e):
            for w in (card, body, icon_l, val_l, lbl_l):
                w.config(bg=self.SURFACE3)
        def _hf(e):
            for w in (card, body, icon_l, val_l, lbl_l):
                w.config(bg=self.SURFACE)
        for w in (glow, card, topbar, body, icon_l, val_l, lbl_l):
            w.bind("<Enter>", _ho); w.bind("<Leave>", _hf)
            w.bind("<Button-1>", lambda e, k=key: self._show_kpi_popup(k))
        Tooltip(glow, tip_b, title=tip_t)
        return {'glow': glow, 'card': card, 'val': val_l, 'icon': icon_l}

    def _reflow_dashboard(self, cols):
        if not hasattr(self, '_cards'): return
        self._card_cols = cols
        for w in self._dash_wrap.winfo_children():
            w.grid_forget()
        for i, (key, *_rest) in enumerate(self._card_defs):
            row = i // cols; col = i % cols
            glow = self._dash_wrap.winfo_children()[i]
            glow.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
        for c in range(cols):
            self._dash_wrap.grid_columnconfigure(c, weight=1, uniform='kpi')
        for r in range((len(self._card_defs) + cols - 1) // cols):
            self._dash_wrap.grid_rowconfigure(r, weight=0)

    def _on_root_configure(self, event):
        if event.widget is not self.root: return
        if not hasattr(self, '_cards'): return
        try:
            w = self.root.winfo_width()
        except Exception:
            return
        if getattr(self, '_last_w', 0) == w: return
        self._last_w = w
        if w >= 1500: cols = 8
        elif w >= 1200: cols = 8
        elif w >= 1000: cols = 4
        elif w >= 700:  cols = 4
        else:            cols = 2
        if cols != self._card_cols:
            self._reflow_dashboard(cols)

    def _build_notebook(self, parent):
        w = tk.Frame(parent, bg=self.BG)
        w.pack(fill='both', expand=True, padx=14, pady=(0,8))
        self.nb = ttk.Notebook(w); self.nb.pack(fill='both', expand=True)
        self._tab_overview = tk.Frame(self.nb, bg=self.BG)
        self._tab_issues   = tk.Frame(self.nb, bg=self.BG)
        self._tab_full     = tk.Frame(self.nb, bg=self.BG)
        self.nb.add(self._tab_overview, text="  📊  Overview  ")
        self.nb.add(self._tab_issues,   text="  🗂  Issues  ")
        self.nb.add(self._tab_full,     text="  📄  Full  ")
        self._txt_overview = self._make_text_view(self._tab_overview)
        self._txt_full     = self._make_text_view(self._tab_full)
        self._build_issues_center(self._tab_issues)

    def _make_text_view(self, parent):
        txt = tk.Text(parent, font=(self.MONO, 9), bg=self.SURFACE, fg=self.FG,
                      relief='flat', wrap='none', padx=18, pady=14,
                      insertbackground=self.PRIMARY, selectbackground=self.VIOLET,
                      selectforeground=self.YELLOW, bd=0, highlightthickness=0)
        txt.pack(side='left', fill='both', expand=True)
        vsb = ttk.Scrollbar(parent, command=txt.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y'); txt.config(yscrollcommand=vsb.set)
        txt.tag_config('h1',        foreground=self.PRIMARY, font=(self.FONT, 11, 'bold'))
        txt.tag_config('h2',        foreground=self.CYAN,    font=(self.FONT, 10, 'bold'))
        txt.tag_config('ok',        foreground=self.MINT)
        txt.tag_config('warn',      foreground=self.YELLOW)
        txt.tag_config('err',       foreground=self.CORAL)
        txt.tag_config('info',      foreground=self.MUTED)
        txt.tag_config('val',       foreground=self.SKY)
        txt.tag_config('rtl',       justify='right')
        txt.tag_config('arabic_hdr',foreground=self.MAGENTA,
                                    font=(self.FONT, 10, 'bold'),
                                    justify='right')
        return txt

    def _build_issues_center(self, parent):
        parent.configure(bg=self.BG)
        toolbar = tk.Frame(parent, bg=self.SURFACE, height=52)
        toolbar.pack(fill='x'); toolbar.pack_propagate(False)
        tk.Label(toolbar, text="🗂  INFORMATION PAGES",
                 font=(self.FONT, 11, "bold"),
                 fg=self.PRIMARY, bg=self.SURFACE).pack(side='left',
                                                         padx=(14,16), pady=14)
        self._sev_filter_btns = {}
        pill_defs = [
            ('all',      '✨ All',      self.YELLOW, "Show every issue"),
            ('critical', '🔴 Critical', self.RED,    "Only blocking issues"),
            ('warning',  '🟠 Warning',  self.CORAL,  "Only warnings"),
            ('info',     '🔵 Info',     self.CYAN,   "Only informational items"),
        ]
        for key, text, color, tip in pill_defs:
            b = self._make_pill(toolbar, text, color,
                                 lambda k=key: self._set_sev_filter(k))
            b.pack(side='left', padx=2, pady=11)
            self._sev_filter_btns[key] = b
            if tip: Tooltip(b, tip)

        tk.Label(toolbar, text="🔍",
                 font=(self.FONT, 11, "bold"),
                 fg=self.PRIMARY, bg=self.SURFACE).pack(side='right', padx=(0,2))
        self._issue_search_var = tk.StringVar()
        self._issue_search_var.trace_add('write',
            lambda *_: self._refresh_issue_tree())
        tk.Entry(toolbar, textvariable=self._issue_search_var,
                 font=(self.FONT, 9), bg=self.SURFACE2, fg=self.FG,
                 insertbackground=self.PRIMARY, relief='flat', width=22, bd=0
                ).pack(side='right', ipady=4, padx=(0,14))
        self._issue_count_lbl = tk.Label(toolbar, text="0",
                                          font=(self.FONT, 10, "bold"),
                                          fg=self.BG, bg=self.SKY,
                                          padx=12, pady=4)
        self._issue_count_lbl.pack(side='right', padx=(6, 14), pady=15)

        cards_wrap = tk.Frame(parent, bg=self.BG)
        cards_wrap.pack(fill='x', padx=8, pady=(8, 4))
        self._cards_canvas = tk.Canvas(cards_wrap, bg=self.BG,
                                       highlightthickness=0, height=190)
        self._cards_canvas.pack(fill='x')
        self._cards_inner = tk.Frame(self._cards_canvas, bg=self.BG)
        win_id = self._cards_canvas.create_window((0, 0), window=self._cards_inner,
                                                    anchor='nw')
        def _on_cfg(e):
            self._cards_canvas.configure(scrollregion=self._cards_canvas.bbox('all'))
        def _on_ccfg(e):
            self._cards_canvas.itemconfigure(win_id, width=e.width)
        self._cards_inner.bind('<Configure>', _on_cfg)
        self._cards_canvas.bind('<Configure>', _on_ccfg)

        self._detail_header = tk.Frame(parent, bg=self.SURFACE2, height=42)
        self._detail_header.pack(fill='x', padx=8, pady=(6, 0))
        self._detail_header.pack_propagate(False)
        self._detail_title_lbl = tk.Label(
            self._detail_header,
            text="📋  All Categories  —  Click any KPI card above to filter",
            font=(self.FONT, 10, "bold"), fg=self.SKY, bg=self.SURFACE2,
            anchor='w')
        self._detail_title_lbl.pack(side='left', padx=14, pady=12)

        self._detail_actions = tk.Frame(self._detail_header, bg=self.SURFACE2)
        self._detail_actions.pack(side='right', padx=6)
        def _act(text, cmd, color, tip=None):
            lbl = tk.Label(self._detail_actions, text=text,
                           font=(self.FONT, 9, "bold"),
                           fg=color, bg=self.SURFACE2,
                           padx=8, pady=4, cursor='hand2')
            lbl.pack(side='left', padx=2, pady=8)
            def _ho(e): lbl.config(bg=self.SURFACE3, fg=self.YELLOW)
            def _hf(e): lbl.config(bg=self.SURFACE2, fg=color)
            lbl.bind("<Enter>", _ho); lbl.bind("<Leave>", _hf)
            lbl.bind("<Button-1>", lambda e: cmd())
            if tip: Tooltip(lbl, tip)
        _act("🔧 Fix",     self._fix_selected_issues, self.MINT,
             "Apply fixable corrections to selected issues")
        _act("🪄 Fix All", self._fix_all_auto,        self.CYAN,
             "Apply every fixable correction")
        _act("🗑 Clear",   self._clear_selected_cells, self.YELLOW,
             "Clear the offending cells")
        _act("❌ Del Row", self._delete_selected_rows, self.CORAL,
             "Mark rows for deletion")
        _act("↗ Jump",     self._jump_to_cell,        self.BLUE,
             "Preview the row in a popup")
        _act("📋 Copy",    self._copy_selected_row,   self.VIOLET,
             "Copy issue details to clipboard")

        detail_wrap = tk.Frame(parent, bg=self.BG)
        detail_wrap.pack(fill='both', expand=True, padx=8, pady=(4, 10))
        cols = ('id','sev','sheet','row','col','value','msg','fix')
        headings = {'id':'#','sev':'Severity','sheet':'Sheet','row':'Row',
                    'col':'Column','value':'Value','msg':'Message','fix':'Fix?'}
        widths = {'id':50,'sev':90,'sheet':110,'row':55,'col':200,
                  'value':180,'msg':440,'fix':50}
        self._issue_tree = ttk.Treeview(detail_wrap, columns=cols, show='headings',
                                        style="Issues.Treeview", selectmode='extended')
        for c in cols:
            self._issue_tree.heading(c, text=headings[c],
                                     command=lambda cc=c: self._sort_issue_tree(cc))
            self._issue_tree.column(c, width=widths[c], anchor='w',
                                     stretch=(c == 'msg'))
        self._issue_tree.tag_configure('critical', foreground=self.RED)
        self._issue_tree.tag_configure('warning',  foreground=self.CORAL)
        self._issue_tree.tag_configure('info',     foreground=self.CYAN)
        self._issue_tree.tag_configure('even',     background=self.SURFACE)
        self._issue_tree.tag_configure('odd',      background=self.SURFACE2)
        vsb = ttk.Scrollbar(detail_wrap, orient='vertical',
                            command=self._issue_tree.yview,
                            style="Vertical.TScrollbar")
        hsb = ttk.Scrollbar(detail_wrap, orient='horizontal',
                            command=self._issue_tree.xview,
                            style="Horizontal.TScrollbar")
        self._issue_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y'); hsb.pack(side='bottom', fill='x')
        self._issue_tree.pack(side='left', fill='both', expand=True)
        self._issue_tree.bind("<Double-1>", lambda e: self._show_issue_details())

        self._issue_empty = tk.Label(detail_wrap,
            text="🌊 Run an analysis to populate the Information Pages ✨",
            font=(self.FONT, 12, "bold"),
            fg=self.PRIMARY, bg=self.BG)
        self._issue_empty.place(relx=0.5, rely=0.5, anchor='center')
        self._set_sev_filter('all')

    def _make_pill(self, parent, text, color, cmd):
        f = tk.Frame(parent, bg=self.SURFACE, cursor='hand2')
        lbl = tk.Label(f, text=text, font=(self.FONT, 9, "bold"),
                       fg=color, bg=self.SURFACE, padx=10, pady=4, cursor='hand2')
        lbl.pack(padx=1, pady=2)
        f._pill = {'color': color, 'label': lbl, 'selected': False}
        def _ho(e):
            if not f._pill['selected']:
                lbl.config(bg=self.SURFACE3); f.config(bg=self.SURFACE3)
        def _hf(e):
            if not f._pill['selected']:
                lbl.config(bg=self.SURFACE); f.config(bg=self.SURFACE)
        for w in (f, lbl):
            w.bind("<Enter>", _ho); w.bind("<Leave>", _hf)
            w.bind("<Button-1>", lambda e, c=cmd: c())
        return f

    def _set_pill_state(self, pill, selected):
        pill._pill['selected'] = selected
        color = pill._pill['color']
        if selected:
            pill.config(bg=color); pill._pill['label'].config(bg=color, fg=self.BG)
        else:
            pill.config(bg=self.SURFACE)
            pill._pill['label'].config(bg=self.SURFACE, fg=color)

    def _set_sev_filter(self, key):
        self._issue_filter_sev = key
        for k, b in self._sev_filter_btns.items():
            self._set_pill_state(b, k == key)
        self._refresh_issue_tree()

    def _sort_issue_tree(self, col):
        if self._issue_sort_col == col:
            self._issue_sort_desc = not self._issue_sort_desc
        else:
            self._issue_sort_col = col; self._issue_sort_desc = False
        self._refresh_detail_tree()

    CATEGORY_META = {
        'Short Phone (<10)': ('📱', 'critical'),
        'Invalid Phone':     ('📞', 'critical'),
        'Phone Note':        ('📝', 'warning'),
        'Phone Conflict':    ('⚡', 'critical'),
        'Driver Conflict':   ('👤', 'critical'),
        'Duplicate Phone':   ('🔁', 'warning'),
        'Date Format':       ('📅', 'warning'),
        'Time Conflict':     ('⏰', 'critical'),
        'Time Normalized':   ('🕐', 'info'),
        'Enum Violation':    ('🎯', 'critical'),
        'ERP Issue':         ('⚙️', 'warning'),
        'Missing Data':      ('❓', 'warning'),
        'Expiry Alert':      ('⏳', 'warning'),
        'Shift Engine':      ('🌊', 'info'),
        'Main Supplier':     ('🏢', 'info'),
        'Auto-Fix':          ('🔧', 'info'),
    }

    def _refresh_issue_tree(self):
        if not hasattr(self, '_issue_tree'): return
        self._rebuild_category_cards()
        self._refresh_detail_tree()
        total = len(self._issue_store)
        try: self.nb.tab(1, text=f"  🗂  Issues ({total})  ")
        except Exception: pass
        if hasattr(self, '_issue_count_lbl'):
            self._issue_count_lbl.config(text=str(total))

    def _rebuild_category_cards(self):
        for w in self._cards_inner.winfo_children():
            w.destroy()
        self._category_cards.clear()
        sev_filter = self._issue_filter_sev
        q = self._issue_search_var.get().strip().lower() if hasattr(self, '_issue_search_var') else ''
        cat_counts = defaultdict(lambda: {'count': 0, 'sev': 'info'})
        for i in self._issue_store:
            if sev_filter != 'all' and i['severity'] != sev_filter: continue
            if q:
                hay = f"{i.get('category','')} {i.get('sheet','')} {i.get('row','')} " \
                      f"{i.get('column','')} {i.get('value','')} {i.get('message','')}".lower()
                if q not in hay: continue
            cat = i['category']
            cat_counts[cat]['count'] += 1
            if i['severity'] == 'critical':
                cat_counts[cat]['sev'] = 'critical'
            elif i['severity'] == 'warning' and cat_counts[cat]['sev'] != 'critical':
                cat_counts[cat]['sev'] = 'warning'
        if not cat_counts:
            tk.Label(self._cards_inner,
                     text="🎉 No issues match current filters",
                     font=(self.FONT, 12, "bold"), fg=self.MINT, bg=self.BG
                    ).pack(pady=50, padx=20)
            return
        sev_order = {'critical': 0, 'warning': 1, 'info': 2}
        sorted_cats = sorted(cat_counts.items(),
                             key=lambda x: (sev_order[x[1]['sev']], -x[1]['count']))
        try:
            avail = self._cards_canvas.winfo_width()
        except Exception:
            avail = 1200
        cols_per_row = max(2, min(6, avail // 200))
        for idx, (cat, info) in enumerate(sorted_cats):
            row = idx // cols_per_row; col = idx % cols_per_row
            sev = info['sev']; count = info['count']
            meta = self.CATEGORY_META.get(cat, ('📌', sev))
            icon = meta[0]
            color_map = {'critical': self.RED, 'warning': self.CORAL, 'info': self.CYAN}
            color = color_map.get(sev, self.MUTED)
            card = self._make_category_card(
                self._cards_inner, cat, count, icon, color, sev,
                is_selected=(self._selected_category == cat))
            card.grid(row=row, column=col, padx=4, pady=4, sticky='nsew')
        for c in range(cols_per_row):
            self._cards_inner.grid_columnconfigure(c, weight=1, uniform='catcard')

    def _make_category_card(self, parent, cat, count, icon, color, sev, is_selected):
        outline = color if is_selected else self.BORDER
        card = tk.Frame(parent, bg=outline, cursor='hand2', bd=0, height=110)
        card.grid_propagate(False)
        base_bg = self.SURFACE3 if is_selected else self.SURFACE
        inner = tk.Frame(card, bg=base_bg, cursor='hand2')
        inner.pack(fill='both', expand=True, padx=2, pady=2)
        top = tk.Frame(inner, bg=color, height=4, cursor='hand2')
        top.pack(fill='x')
        body = tk.Frame(inner, bg=base_bg, cursor='hand2')
        body.pack(fill='both', expand=True, padx=10, pady=(6, 8))
        hdr = tk.Frame(body, bg=base_bg, cursor='hand2')
        hdr.pack(fill='x', anchor='w')
        icon_lbl = tk.Label(hdr, text=icon, font=(self.FONT, 20), fg=color,
                            bg=base_bg, cursor='hand2')
        icon_lbl.pack(side='left', padx=(0, 8))
        cnt_lbl = tk.Label(hdr, text=str(count), font=(self.FONT, 24, "bold"),
                           fg=color, bg=base_bg, cursor='hand2')
        cnt_lbl.pack(side='left')
        name_lbl = tk.Label(body, text=cat[:26], font=(self.FONT, 9, "bold"),
                            fg=self.FG, bg=base_bg, cursor='hand2',
                            anchor='w', wraplength=170, justify='left')
        name_lbl.pack(anchor='w', pady=(4, 0))
        sev_lbl = tk.Label(body, text=sev.upper(), font=(self.FONT, 7, "bold"),
                           fg=color, bg=base_bg, cursor='hand2')
        sev_lbl.pack(anchor='w', pady=(2, 0))
        all_widgets = [card, inner, top, body, hdr, icon_lbl, cnt_lbl,
                       name_lbl, sev_lbl]
        def _ho(e):
            for w in [inner, body, hdr, icon_lbl, cnt_lbl, name_lbl, sev_lbl]:
                try: w.config(bg=self.SURFACE3)
                except Exception: pass
        def _hf(e):
            base = self.SURFACE3 if is_selected else self.SURFACE
            for w in [inner, body, hdr, icon_lbl, cnt_lbl, name_lbl, sev_lbl]:
                try: w.config(bg=base)
                except Exception: pass
        for w in all_widgets:
            w.bind("<Enter>", _ho, add="+")
            w.bind("<Leave>", _hf, add="+")
            w.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
        return card

    def _select_category(self, cat):
        self._selected_category = None if self._selected_category == cat else cat
        self._rebuild_category_cards()
        self._refresh_detail_tree()

    def _refresh_detail_tree(self):
        if not hasattr(self, '_issue_tree'): return
        self._issue_tree.delete(*self._issue_tree.get_children())
        sev_filter = self._issue_filter_sev
        q = self._issue_search_var.get().strip().lower() if hasattr(self, '_issue_search_var') else ''
        cat_filter = self._selected_category
        def _pass(i):
            if sev_filter != 'all' and i['severity'] != sev_filter: return False
            if cat_filter and i['category'] != cat_filter: return False
            if q:
                hay = f"{i.get('category','')} {i.get('sheet','')} {i.get('row','')} " \
                      f"{i.get('column','')} {i.get('value','')} {i.get('message','')}".lower()
                if q not in hay: return False
            return True
        items = [i for i in self._issue_store if _pass(i)]
        if self._issue_sort_col:
            key = self._issue_sort_col
            items.sort(key=lambda i: str(i.get(key, '')).lower(),
                       reverse=self._issue_sort_desc)
        sev_icon = {'critical': '🔴', 'warning': '🟠', 'info': '🔵'}
        for idx, i in enumerate(items):
            parity = 'even' if idx % 2 == 0 else 'odd'
            self._issue_tree.insert('', 'end',
                values=(i['id'], sev_icon.get(i['severity'], i['severity'].upper()),
                        i['sheet'], i['row'], i['column'],
                        i['value'], i['message'],
                        '✔' if i['fixable'] else ''),
                tags=(i['severity'], parity))
        if hasattr(self, '_detail_title_lbl'):
            if cat_filter:
                self._detail_title_lbl.config(
                    text=f"📂  {cat_filter}  —  {len(items)} item(s)  "
                         f"(click card again to clear)")
            else:
                self._detail_title_lbl.config(
                    text=f"📋  All Categories  —  {len(items)} item(s)  ·  "
                         f"Click a KPI card above to filter")
        if items:
            self._issue_empty.place_forget()
        else:
            self._issue_empty.config(
                text=("🌊 Run an analysis to populate the Information Pages ✨"
                      if not self._issue_store else "🎉 No issues match!"))
            self._issue_empty.place(relx=0.5, rely=0.5, anchor='center')

    def _selected_issue_indices(self):
        return [int(self._issue_tree.item(sid, 'values')[0])
                for sid in self._issue_tree.selection()
                if self._issue_tree.item(sid, 'values')]

    def _issue_by_id(self, iid):
        for i in self._issue_store:
            if i['id'] == iid: return i
        return None

    def _apply_issue_fix(self, issue):
        if not issue['fixable']: return False
        action = issue.get('fix_action')
        if not action: return False
        kind, value = action
        a = self.analyzer
        sheet = issue['sheet']; row = issue['row']
        col = issue.get('override_col') or issue['column']
        if sheet not in a.sheets_data: return False
        info = a.sheets_data[sheet]
        if info['skipped']: return False
        rec = next((r for r in info['records'] if r['_row'] == row), None)
        if not rec: return False
        old = rec.get(col)
        if kind == 'override':
            a.fixes.append({'sheet': sheet, 'row': row, 'col': col,
                            'old': old, 'new': value,
                            'reason': f'Manual fix — {issue["message"][:60]}'})
        rec[col] = value
        return True

    def _fix_selected_issues(self):
        if not self.analyzer: return
        ids = self._selected_issue_indices()
        if not ids:
            Toast(self.root, "Select issues first", kind='warning'); return
        applied = 0
        for iid in ids:
            issue = self._issue_by_id(iid)
            if issue and self._apply_issue_fix(issue): applied += 1
        self._set_status(f"✨ Applied {applied} fix(es)", self.MINT)
        Toast(self.root, f"Applied {applied} fix(es)", kind='success')
        self._recompute_after_fix()

    def _fix_all_auto(self):
        if not self.analyzer: return
        applied = 0
        for issue in list(self._issue_store):
            if issue['fixable'] and self._apply_issue_fix(issue): applied += 1
        self._set_status(f"🪄 Applied {applied} auto-fix(es)", self.CYAN)
        Toast(self.root, f"Applied {applied} auto-fix(es)", kind='success')
        self._recompute_after_fix()

    def _clear_selected_cells(self):
        if not self.analyzer: return
        ids = self._selected_issue_indices()
        cleared = 0
        for iid in ids:
            issue = self._issue_by_id(iid)
            if not issue: continue
            sheet = issue['sheet']; row = issue['row']; col = issue['column']
            if sheet not in self.analyzer.sheets_data: continue
            rec = next((r for r in self.analyzer.sheets_data[sheet]['records']
                        if r['_row'] == row), None)
            if rec:
                old = rec.get(col); rec[col] = None
                self.analyzer.fixes.append({'sheet': sheet, 'row': row, 'col': col,
                                             'old': old, 'new': '',
                                             'reason': 'Cleared'})
                cleared += 1
        self._set_status(f"🗑 Cleared {cleared}", self.YELLOW)
        Toast(self.root, f"Cleared {cleared} cell(s)", kind='info')
        self._recompute_after_fix()

    def _delete_selected_rows(self):
        if not self.analyzer: return
        ids = self._selected_issue_indices()
        pairs = set()
        for iid in ids:
            issue = self._issue_by_id(iid)
            if issue and isinstance(issue['row'], int):
                pairs.add((issue['sheet'], issue['row']))
        if not pairs: return
        if not messagebox.askyesno("Delete rows?",
            f"Mark {len(pairs)} row(s) for deletion?"): return
        for sheet, row in pairs:
            if sheet not in self.analyzer.sheets_data: continue
            rec = next((r for r in self.analyzer.sheets_data[sheet]['records']
                        if r['_row'] == row), None)
            if rec:
                for col in list(rec.keys()):
                    if col == '_row': continue
                    self.analyzer.fixes.append({'sheet': sheet, 'row': row,
                                                 'col': col, 'old': rec.get(col),
                                                 'new': '', 'reason': 'Row deleted'})
        self._set_status(f"❌ Marked {len(pairs)} row(s)", self.CORAL)
        Toast(self.root, f"Marked {len(pairs)} row(s) for deletion", kind='warning')
        self._recompute_after_fix()

    def _jump_to_cell(self):
        if not self.analyzer: return
        ids = self._selected_issue_indices()
        if not ids: return
        issue = self._issue_by_id(ids[0])
        if not issue or not isinstance(issue['row'], int): return
        sheet = issue['sheet']; row = issue['row']
        if sheet not in self.analyzer.sheets_data: return
        rec = next((r for r in self.analyzer.sheets_data[sheet]['records']
                    if r['_row'] == row), None)
        if not rec: return
        self._show_row_preview(sheet, row, rec, issue.get('column'))

    def _show_row_preview(self, sheet, row, rec, hl_col=None):
        d = tk.Toplevel(self.root)
        d.title(f"↗ [{sheet}] row {row}")
        d.geometry("820x580"); d.minsize(600, 420)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text=f"↗ [{sheet}] · Row {row}",
                 font=(self.FONT, 13, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(pady=(16,8), padx=20, anchor='w')
        body = tk.Frame(d, bg=self.SURFACE); body.pack(fill='both', expand=True,
                                                       padx=20, pady=(0,16))
        txt = tk.Text(body, font=(self.MONO, 10), bg=self.SURFACE, fg=self.FG,
                      relief='flat', padx=16, pady=12, wrap='word', bd=0,
                      highlightthickness=0)
        txt.pack(side='left', fill='both', expand=True)
        vsb = ttk.Scrollbar(body, command=txt.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y'); txt.config(yscrollcommand=vsb.set)
        txt.tag_config('key', foreground=self.CYAN, font=(self.MONO, 10, 'bold'))
        txt.tag_config('hl',  background=self.YELLOW, foreground=self.BG)
        for k, v in rec.items():
            if k == '_row': continue
            txt.insert('end', f"{k:<32}", 'key')
            txt.insert('end', f"  {to_str(v)}\n", 'hl' if k == hl_col else ())
        txt.config(state='disabled')
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 12, self.FG
                      ).pack(pady=(0,14))

    def _show_issue_details(self):
        ids = self._selected_issue_indices()
        if not ids: return
        issue = self._issue_by_id(ids[0])
        if not issue: return
        d = tk.Toplevel(self.root)
        d.title(f"Issue #{issue['id']}")
        d.geometry("620x480"); d.minsize(500, 360)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text=f"🔍 Issue #{issue['id']}",
                 font=(self.FONT, 14, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(pady=(16,8), padx=20, anchor='w')
        body = tk.Frame(d, bg=self.SURFACE); body.pack(fill='both', expand=True,
                                                       padx=20, pady=(0,16))
        txt = tk.Text(body, font=(self.MONO, 10), bg=self.SURFACE, fg=self.FG,
                      relief='flat', padx=14, pady=12, wrap='word', bd=0,
                      highlightthickness=0)
        txt.pack(fill='both', expand=True)
        txt.tag_config('key', foreground=self.CYAN, font=(self.MONO, 10, 'bold'))
        for k, v in issue.items():
            if k == 'id': continue
            txt.insert('end', f"{k:<16}", 'key')
            txt.insert('end', f"  {to_str(v)}\n")
        txt.config(state='disabled')
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 12, self.FG
                      ).pack(pady=(0,14))

    def _copy_selected_row(self):
        ids = self._selected_issue_indices()
        lines = []
        for iid in ids:
            issue = self._issue_by_id(iid)
            if issue:
                lines.append(f"[{issue['severity'].upper()}] {issue['category']} — "
                             f"[{issue['sheet']}] row {issue['row']} col "
                             f"{issue['column']} = '{issue['value']}' → {issue['message']}")
        if lines:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(lines))
            self._set_status(f"📋 Copied {len(lines)}", self.MINT)
            Toast(self.root, f"Copied {len(lines)} issue(s) to clipboard", kind='success')

    def _recompute_after_fix(self):
        if not self.analyzer: return
        try: self._issue_store = self.analyzer.build_issue_list()
        except Exception: self._issue_store = []
        self._refresh_issue_tree()
        try:
            total_rows = sum(len(i['records'])
                              for i in self.analyzer.sheets_data.values()
                              if not i['skipped'])
            expiry_n = len(self.analyzer.issues['expiry_alerts'])
            short_n = sum(1 for x in self.analyzer.issues['invalid_phones']
                          if x.get('kind') == 'short')
            shift_n = len(self.analyzer.issues['shift_upgrades'])
            tc_n = len(self.analyzer.issues['time_conflicts'])
            score = self.analyzer._compute_score()
            self._update_cards(score, total_rows, len(self.analyzer.fixes),
                                self._n_err, self._n_wrn, expiry_n, short_n,
                                shift_n, tc_n)
        except Exception: pass

    def _collect_unresolved(self):
        a = self.analyzer
        if not a:
            return []
        out = []
        for p in a.issues['phone_conflicts']:
            if not p['soft']:
                out.append({'sev': 'CRITICAL',
                    'kind': 'Phone shared by multiple drivers',
                    'sheet': '—', 'row': '—', 'col': 'driver_phone_number',
                    'value': p['phone'],
                    'msg': f"Used by {len(p['names'])} different driver names"})
        for d in a.issues['driver_conflicts']:
            out.append({'sev': 'CRITICAL',
                'kind': 'Driver has multiple phone numbers',
                'sheet': '—', 'row': '—', 'col': 'assigned_driver_full_name',
                'value': d['driver'],
                'msg': f"Has {len(d['phones'])} phone(s): " +
                       ", ".join(ph['phone'] for ph in d['phones'][:3])})
        for p in a.issues['duplicate_phones']:
            if p['kind'] == 'hard':
                out.append({'sev': 'CRITICAL',
                    'kind': 'Duplicate phone (hard)',
                    'sheet': '—', 'row': '—', 'col': 'driver_phone_number',
                    'value': p['phone'],
                    'msg': f"Appears {len(p['occurrences'])} times across different drivers"})
        for ip in a.issues['invalid_phones']:
            k = ip.get('kind', 'invalid')
            sev = 'CRITICAL' if k in ('invalid', 'arabic') else 'WARNING'
            out.append({'sev': sev,
                'kind': {'invalid': 'Invalid phone number',
                          'arabic': 'Text in phone column',
                          'short': 'Short phone (<11 digits)'}.get(k, 'Phone issue'),
                'sheet': ip['sheet'], 'row': ip['row'], 'col': ip['col'],
                'value': ip['value'], 'msg': ip['reason']})
        for ev in a.issues['enum_violations']:
            out.append({'sev': 'CRITICAL', 'kind': 'Enum violation',
                'sheet': ev['sheet'], 'row': ev['row'], 'col': ev['col'],
                'value': ev['value'],
                'msg': f"Allowed: {', '.join(ev['allowed'])}"})
        for ei in a.erp_issues:
            if ei['kind'] == 'missing_required':
                out.append({'sev': 'CRITICAL', 'kind': 'Missing required column',
                    'sheet': ei['sheet'], 'row': '—', 'col': ei['column'],
                    'value': '—', 'msg': 'Required by ERP upload schema'})
        for df in a.issues['date_format_issues']:
            if df.get('status') == 'invalid':
                out.append({'sev': 'CRITICAL', 'kind': 'Unparseable date',
                    'sheet': df['sheet'], 'row': df['row'], 'col': df['col'],
                    'value': df['value'],
                    'msg': df.get('reason', 'Could not be parsed')})
        for tc in a.issues['time_conflicts']:
            if tc.get('mode') == TIME_CONFLICT_MODE_FLAGONLY:
                out.append({'sev': 'CRITICAL', 'kind': 'Unresolved time conflict',
                    'sheet': tc['sheet'], 'row': tc['row'],
                    'col': f"{tc['pickup_col']} = {tc['dropoff_col']}",
                    'value': f"{tc['pickup']} == {tc['dropoff']}",
                    'msg': f"Flag-only mode — suggested: {tc.get('suggested_dropoff') or '—'}"})
        return out

    def _show_export_warning(self, on_proceed, export_label="Export"):
        issues = self._collect_unresolved()
        if not issues:
            on_proceed()
            return
        n_crit = sum(1 for i in issues if i['sev'] == 'CRITICAL')
        n_warn = len(issues) - n_crit
        d = tk.Toplevel(self.root)
        d.title(f"⚠  {export_label} — Unresolved Issues Detected")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(1100, sw - 80); h = min(760, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(700, 480)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()

        hdr = tk.Frame(d, bg=self.RED, height=80)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="⚠", font=(self.FONT, 32, "bold"),
                 fg=self.BG, bg=self.RED).pack(side='left', padx=(20,12), pady=14)
        tf = tk.Frame(hdr, bg=self.RED); tf.pack(side='left', pady=16)
        tk.Label(tf, text="UNRESOLVED ISSUES DETECTED",
                 font=(self.FONT, 15, "bold"), fg=self.BG, bg=self.RED
                 ).pack(anchor='w')
        tk.Label(tf, text=f"{n_crit} critical  ·  {n_warn} warning(s)  ·  "
                          f"You can still export, but the file may be rejected.",
                 font=(self.FONT, 9, "italic"), fg="#2a0000", bg=self.RED
                 ).pack(anchor='w', pady=(2,0))

        pane = tk.Frame(d, bg=self.BG)
        pane.pack(fill='both', expand=True, padx=14, pady=(12, 6))

        left = tk.Frame(pane, bg=self.SURFACE)
        left.pack(side='left', fill='both', expand=True)
        tk.Label(left, text="📋  Issue List",
                 font=(self.FONT, 10, "bold"), fg=self.RED, bg=self.SURFACE
                 ).pack(anchor='w', padx=12, pady=(10, 4))
        tree_wrap = tk.Frame(left, bg=self.SURFACE)
        tree_wrap.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        cols = ('sev', 'kind', 'sheet', 'row', 'col', 'value')
        tree = ttk.Treeview(tree_wrap, columns=cols, show='headings',
                             style="Issues.Treeview")
        headings = {'sev': 'Severity', 'kind': 'Category', 'sheet': 'Sheet',
                    'row': 'Row', 'col': 'Column', 'value': 'Value'}
        widths = {'sev': 90, 'kind': 260, 'sheet': 120, 'row': 60,
                  'col': 190, 'value': 220}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=widths[c], anchor='w',
                         stretch=(c in ('kind', 'value')))
        tree.tag_configure('CRITICAL', foreground=self.RED)
        tree.tag_configure('WARNING',  foreground=self.CORAL)
        vsb = ttk.Scrollbar(tree_wrap, orient='vertical',
                             command=tree.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        tree.configure(yscrollcommand=vsb.set)

        right = tk.Frame(pane, bg=self.SURFACE)
        right.pack(side='left', fill='both', expand=True, padx=(10, 0))
        tk.Label(right, text="🔎  Detail",
                 font=(self.FONT, 10, "bold"), fg=self.SKY, bg=self.SURFACE
                 ).pack(anchor='w', padx=12, pady=(10, 4))
        detail_txt = tk.Text(right, font=(self.MONO, 10), bg=self.SURFACE,
                              fg=self.FG, relief='flat', wrap='word',
                              padx=14, pady=12, bd=0, highlightthickness=0,
                              state='disabled')
        detail_txt.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        detail_txt.tag_config('sev_c', foreground=self.RED,
                               font=(self.FONT, 11, 'bold'))
        detail_txt.tag_config('sev_w', foreground=self.CORAL,
                               font=(self.FONT, 11, 'bold'))
        detail_txt.tag_config('key', foreground=self.CYAN,
                               font=(self.MONO, 10, 'bold'))

        for i, it in enumerate(issues):
            tag = it['sev']
            tree.insert('', 'end', iid=str(i), tags=(tag,),
                        values=(it['sev'], it['kind'], it['sheet'], it['row'],
                                it['col'], it['value']))

        def _show_detail(_=None):
            sel = tree.selection()
            detail_txt.config(state='normal')
            detail_txt.delete('1.0', 'end')
            if not sel:
                detail_txt.insert('end', "Select an issue to see details.\n", 'key')
            else:
                idx = int(sel[0])
                it = issues[idx]
                sev_tag = 'sev_c' if it['sev'] == 'CRITICAL' else 'sev_w'
                detail_txt.insert('end', f"{it['sev']}\n", sev_tag)
                for k, v in [('Category', it['kind']),
                              ('Sheet', it['sheet']),
                              ('Row', it['row']),
                              ('Column', it['col']),
                              ('Value', it['value']),
                              ('Message', it['msg'])]:
                    detail_txt.insert('end', f"{k:<12}", 'key')
                    detail_txt.insert('end', f" {v}\n")
            detail_txt.config(state='disabled')
        tree.bind("<<TreeviewSelect>>", _show_detail)
        if issues:
            tree.selection_set('0'); _show_detail()

        foot = tk.Frame(d, bg=self.BG, height=56)
        foot.pack(fill='x', padx=14, pady=(0, 12)); foot.pack_propagate(False)

        def _cancel():
            d.destroy()
            Toast(self.root, "Export cancelled", kind='warning')

        def _proceed():
            d.destroy()
            on_proceed()

        self._make_btn(foot, "✕  Cancel Export", _cancel,
                       self.SURFACE3, 18, self.FG).pack(side='right', pady=12,
                                                        padx=(8, 0))
        self._make_btn(foot, "⚠  Continue Anyway",
                       _proceed, self.RED, 22, self.BG).pack(side='right', pady=12)
        tk.Label(foot, text=f"⚠  {n_crit} critical issue(s) will remain in the exported file",
                 font=(self.FONT, 9, "bold"), fg=self.RED, bg=self.BG
                 ).pack(side='left', pady=18)

    # ══════════════════════════════════════════════════════════════════
    #  🕐  TIME CONTROL CENTER
    # ══════════════════════════════════════════════════════════════════
    def _show_time_control_center(self):
        d = tk.Toplevel(self.root)
        d.title("🕐 Time Control Center — v11.3.1")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(980, sw - 80); h = min(820, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(820, 640)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()

        hdr = tk.Frame(d, bg=self.SURFACE, height=100)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="🕐", font=(self.FONT, 40),
                 fg=self.YELLOW, bg=self.SURFACE
                 ).pack(side='left', padx=(24,14), pady=18)
        tf = tk.Frame(hdr, bg=self.SURFACE); tf.pack(side='left', pady=22)
        tk.Label(tf, text="Time Control Center",
                 font=(self.FONT, 19, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE).pack(anchor='w')
        tk.Label(tf, text="Advanced time rules & column actions",
                 font=(self.FONT, 10, "italic"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor='w', pady=(2,0))
        rb = tk.Frame(d, bg=self.BG, height=4); rb.pack(fill='x')
        for c in (self.YELLOW, self.ORANGE, self.CORAL, self.PINK, self.MAGENTA):
            tk.Frame(rb, bg=c).pack(side='left', fill='both', expand=True)

        body_wrap = tk.Frame(d, bg=self.BG)
        body_wrap.pack(fill='both', expand=True)
        canvas = tk.Canvas(body_wrap, bg=self.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(body_wrap, orient='vertical', command=canvas.yview,
                             style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(canvas, bg=self.BG)
        win_id = canvas.create_window((0, 0), window=body, anchor='nw')
        def _on_cfg(e=None): canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_ccfg(e): canvas.itemconfigure(win_id, width=e.width)
        body.bind('<Configure>', _on_cfg)
        canvas.bind('<Configure>', _on_ccfg)
        def _wh(e): canvas.yview_scroll(int(-1*(e.delta/120)), 'units')
        canvas.bind('<MouseWheel>', _wh); body.bind('<MouseWheel>', _wh)

        sec1 = tk.Frame(body, bg=self.SURFACE2)
        sec1.pack(fill='x', padx=20, pady=(14, 8))
        tk.Label(sec1, text="⚙  MASTER SWITCH",
                 font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE2
                 ).pack(anchor='w', padx=16, pady=(10, 4))
        enable_var = tk.BooleanVar(value=self.settings.time_conflict_enabled)
        tk.Checkbutton(sec1,
            text="  🕐  Enable Time Conflict Rule  —  "
                 "'pickup_arrival_time == dropoff_arrival_time' → offset",
            variable=enable_var, font=(self.FONT, 11, "bold"),
            fg=self.MINT, bg=self.SURFACE2,
            activebackground=self.SURFACE2, activeforeground=self.SKY,
            selectcolor=self.SURFACE, cursor='hand2', anchor='w'
        ).pack(anchor='w', padx=16, pady=(0, 4))
        tk.Label(sec1,
            text="When ON: conflicting rows will be detected and handled per rule below.",
            font=(self.FONT, 9, "italic"), fg=self.MUTED, bg=self.SURFACE2
        ).pack(anchor='w', padx=(48, 16), pady=(0, 12))

        sec2 = tk.Frame(body, bg=self.SURFACE)
        sec2.pack(fill='x', padx=20, pady=(0, 8))
        tk.Label(sec2, text="🎯  CONFLICT RULE CONFIGURATION",
                 font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE
                 ).pack(anchor='w', padx=16, pady=(12, 8))

        row1 = tk.Frame(sec2, bg=self.SURFACE); row1.pack(fill='x', padx=16, pady=4)
        tk.Label(row1, text="Offset (minutes):",
                 font=(self.FONT, 10, "bold"), fg=self.FG, bg=self.SURFACE,
                 width=20, anchor='w').pack(side='left')
        offset_var = tk.StringVar(value=str(self.settings.time_conflict_offset))
        tk.Entry(row1, textvariable=offset_var, font=(self.FONT, 11),
                 bg=self.SURFACE2, fg=self.FG, insertbackground=self.YELLOW,
                 relief='flat', bd=0, width=10).pack(side='left', padx=(0, 12), ipady=5)
        for preset in ('15', '30', '45', '60'):
            tk.Button(row1, text=f"+{preset}m",
                      command=lambda p=preset: offset_var.set(p),
                      font=(self.FONT, 9, "bold"),
                      bg=self.SURFACE2, fg=self.SKY,
                      activebackground=self.SKY, activeforeground=self.BG,
                      relief='flat', cursor='hand2', bd=0,
                      padx=8, pady=4).pack(side='left', padx=2)

        row2 = tk.Frame(sec2, bg=self.SURFACE); row2.pack(fill='x', padx=16, pady=4)
        tk.Label(row2, text="Apply offset to:",
                 font=(self.FONT, 10, "bold"), fg=self.FG, bg=self.SURFACE,
                 width=20, anchor='w').pack(side='left')
        target_var = tk.StringVar(value=self.settings.time_conflict_target)
        for val, lbl in [(COL_DROPOFF_ARR, '🛬 dropoff_arrival_time'),
                          (COL_DROPOFF_TIME, '🛬 dropoff_departure_time'),
                          (COL_PICKUP_ARR, '🛫 pickup_arrival_time'),
                          (COL_PICKUP_DEP, '🛫 pickup_departure_time')]:
            tk.Radiobutton(row2, text=lbl, variable=target_var, value=val,
                           font=(self.FONT, 9), fg=self.FG, bg=self.SURFACE,
                           activebackground=self.SURFACE,
                           activeforeground=self.PRIMARY,
                           selectcolor=self.SURFACE2, cursor='hand2'
                          ).pack(side='left', padx=6)

        row3 = tk.Frame(sec2, bg=self.SURFACE); row3.pack(fill='x', padx=16, pady=(4, 12))
        tk.Label(row3, text="Mode:",
                 font=(self.FONT, 10, "bold"), fg=self.FG, bg=self.SURFACE,
                 width=20, anchor='w').pack(side='left')
        mode_var = tk.StringVar(value=self.settings.time_conflict_mode)
        tk.Radiobutton(row3, text="🔧 Auto-fix (apply offset automatically)",
                       variable=mode_var, value=TIME_CONFLICT_MODE_AUTOFIX,
                       font=(self.FONT, 9), fg=self.MINT, bg=self.SURFACE,
                       activebackground=self.SURFACE, activeforeground=self.MINT,
                       selectcolor=self.SURFACE2, cursor='hand2'
                      ).pack(side='left', padx=6)
        tk.Radiobutton(row3, text="🚩 Flag only (do not modify)",
                       variable=mode_var, value=TIME_CONFLICT_MODE_FLAGONLY,
                       font=(self.FONT, 9), fg=self.CORAL, bg=self.SURFACE,
                       activebackground=self.SURFACE, activeforeground=self.CORAL,
                       selectcolor=self.SURFACE2, cursor='hand2'
                      ).pack(side='left', padx=6)

        sec3 = tk.Frame(body, bg=self.SURFACE)
        sec3.pack(fill='x', padx=20, pady=(0, 8))
        tk.Label(sec3, text="🕐  TIME NORMALIZATION",
                 font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE
                 ).pack(anchor='w', padx=16, pady=(12, 6))
        norm_var = tk.BooleanVar(value=self.settings.time_normalize_enabled)
        tk.Checkbutton(sec3,
            text="  Normalize all time values to canonical HH:MM",
            variable=norm_var, font=(self.FONT, 10, "bold"),
            fg=self.FG, bg=self.SURFACE, activebackground=self.SURFACE,
            activeforeground=self.SKY, selectcolor=self.SURFACE2,
            cursor='hand2', anchor='w'
        ).pack(anchor='w', padx=16, pady=(0, 4))
        conv12_var = tk.BooleanVar(value=self.settings.time_convert_12h)
        tk.Checkbutton(sec3,
            text="  Convert 12-hour (AM/PM) → 24-hour",
            variable=conv12_var, font=(self.FONT, 10, "bold"),
            fg=self.FG, bg=self.SURFACE, activebackground=self.SURFACE,
            activeforeground=self.SKY, selectcolor=self.SURFACE2,
            cursor='hand2', anchor='w'
        ).pack(anchor='w', padx=(48, 16), pady=(0, 12))

        sec4 = tk.Frame(body, bg=self.SURFACE)
        sec4.pack(fill='x', padx=20, pady=(0, 8))
        tk.Label(sec4, text="📋  PER-COLUMN ACTIONS",
                 font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE
                 ).pack(anchor='w', padx=16, pady=(12, 6))
        tk.Label(sec4,
            text="For each time column: KEEP / CLEAR / DELETE / OVERRIDE",
            font=(self.FONT, 9, "italic"), fg=self.MUTED, bg=self.SURFACE
        ).pack(anchor='w', padx=16, pady=(0, 6))

        col_rules = dict(self.settings.time_column_rules)
        row_widgets = {}
        for col, icon, display in TIME_COLUMNS:
            bg = self.SURFACE2
            row = tk.Frame(sec4, bg=bg); row.pack(fill='x', padx=16, pady=1)
            tk.Label(row, text=f"  {icon}  {display}",
                     font=(self.MONO, 10, "bold"), fg=self.SKY, bg=bg,
                     width=32, anchor='w').pack(side='left', padx=(4, 6), pady=8)
            rule = col_rules.get(col, {'action': 'keep', 'value': ''})
            av = tk.StringVar(value=rule.get('action', 'keep'))
            acb = ttk.Combobox(row, textvariable=av,
                                values=['keep', 'clear', 'delete', 'override'],
                                state='readonly', width=10, font=(self.FONT, 9))
            acb.pack(side='left', padx=4)
            vv = tk.StringVar(value=rule.get('value', '') or '')
            ve = tk.Entry(row, textvariable=vv, font=(self.FONT, 9),
                           bg=self.BORDER, fg=self.MUTED, insertbackground=self.SKY,
                           relief='flat', bd=0, width=22, state='disabled')
            ve.pack(side='left', padx=(4, 6), ipady=4, fill='x', expand=True)
            row_widgets[col] = {'a': av, 'v': vv, 'e': ve}
            def _upd(c=col, av=av, vv=vv, ve=ve):
                act = av.get()
                if act == 'override':
                    ve.config(state='normal', bg=self.SURFACE3, fg=self.FG)
                else:
                    ve.config(state='disabled', bg=self.BORDER, fg=self.MUTED)
                col_rules[c] = {'action': act,
                                 'value': vv.get() if act == 'override' else ''}
            acb.bind('<<ComboboxSelected>>', lambda e, f=_upd: f())
            ve.bind('<FocusOut>', lambda e, f=_upd: f())
            ve.bind('<Return>',   lambda e, f=_upd: f())
            _upd()

        sec5 = tk.Frame(body, bg=self.SURFACE2)
        sec5.pack(fill='x', padx=20, pady=(8, 8))
        tk.Label(sec5, text="🔎  LIVE PREVIEW — test the conflict rule",
                 font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE2
                 ).pack(anchor='w', padx=16, pady=(10, 4))
        prev_row = tk.Frame(sec5, bg=self.SURFACE2)
        prev_row.pack(fill='x', padx=16, pady=4)
        tk.Label(prev_row, text="pickup:", font=(self.FONT, 10, "bold"),
                 fg=self.FG, bg=self.SURFACE2).pack(side='left', padx=(0, 4))
        pv_var = tk.StringVar(value="07:15")
        tk.Entry(prev_row, textvariable=pv_var, font=(self.FONT, 11),
                 bg=self.SURFACE3, fg=self.FG, insertbackground=self.YELLOW,
                 relief='flat', bd=0, width=12).pack(side='left', ipady=5, padx=(0, 14))
        tk.Label(prev_row, text="dropoff:", font=(self.FONT, 10, "bold"),
                 fg=self.FG, bg=self.SURFACE2).pack(side='left', padx=(0, 4))
        dv_var = tk.StringVar(value="07:15")
        tk.Entry(prev_row, textvariable=dv_var, font=(self.FONT, 11),
                 bg=self.SURFACE3, fg=self.FG, insertbackground=self.YELLOW,
                 relief='flat', bd=0, width=12).pack(side='left', ipady=5)
        result_lbl = tk.Label(sec5, text="",
                               font=(self.FONT, 11, "bold"),
                               fg=self.MINT, bg=self.SURFACE2,
                               justify='left', anchor='w', wraplength=800)
        result_lbl.pack(anchor='w', padx=16, pady=(8, 12))

        def _preview():
            try: offset = int(offset_var.get())
            except Exception: offset = 30
            pv = to_str(pv_var.get()); dv = to_str(dv_var.get())
            if not pv or not dv:
                result_lbl.config(text="→ Enter both times", fg=self.MUTED); return
            if pv != dv:
                result_lbl.config(
                    text=f"✅ No conflict — '{pv}' ≠ '{dv}'",
                    fg=self.MINT); return
            target = target_var.get()
            new_t = offset_time_min(dv, offset)
            if new_t == pv: new_t = offset_time_min(dv, offset * 2)
            mode = mode_var.get()
            if mode == TIME_CONFLICT_MODE_AUTOFIX:
                result_lbl.config(
                    text=f"⚠ Conflict detected — AUTO-FIX: "
                         f"'{target}' will be offset by +{offset}min "
                         f"→ '{new_t}'",
                    fg=self.YELLOW)
            else:
                result_lbl.config(
                    text=f"🚩 Conflict detected — FLAG ONLY: row will be "
                         f"reported (suggested '{new_t}' on '{target}')",
                    fg=self.CORAL)
        pv_btn = self._make_btn(prev_row, "🕐 Test", _preview,
                                 self.YELLOW, 12, self.BG)
        pv_btn.pack(side='left', padx=(14, 0))
        _preview()

        foot = tk.Frame(d, bg=self.BG, height=60)
        foot.pack(fill='x', padx=20, pady=(0, 14)); foot.pack_propagate(False)

        def _reset():
            if not messagebox.askyesno("Reset Time Rules?",
                "Reset all Time Control Center settings to defaults?"): return
            self.settings.time_conflict_enabled = True
            self.settings.time_conflict_offset = DEFAULT_TIME_CONFLICT_OFFSET_MIN
            self.settings.time_conflict_target = DEFAULT_TIME_TARGET_COLUMN
            self.settings.time_conflict_mode = TIME_CONFLICT_MODE_AUTOFIX
            self.settings.time_normalize_enabled = True
            self.settings.time_convert_12h = True
            self.settings.time_column_rules = {}
            self.settings.save()
            self._refresh_time_pill()
            try: self._time_badge.config(text="🕐 Time ON", bg=self.YELLOW)
            except Exception: pass
            d.destroy()
            Toast(self.root, "Time rules reset to defaults", kind='info')

        def _apply():
            try: offset_val = int(offset_var.get())
            except Exception:
                messagebox.showerror("Invalid offset", "Offset must be an integer.")
                return
            self.settings.time_conflict_enabled = bool(enable_var.get())
            self.settings.time_conflict_offset = offset_val
            self.settings.time_conflict_target = target_var.get()
            self.settings.time_conflict_mode = mode_var.get()
            self.settings.time_normalize_enabled = bool(norm_var.get())
            self.settings.time_convert_12h = bool(conv12_var.get())
            final_rules = {}
            for c, w in row_widgets.items():
                act = w['a'].get()
                if act == 'keep': continue
                final_rules[c] = {'action': act,
                                   'value': w['v'].get() if act == 'override' else ''}
            self.settings.time_column_rules = final_rules
            self.settings.save()
            self._refresh_time_pill()
            try:
                self._time_badge.config(
                    text=f"🕐 Time {'ON' if self.settings.time_conflict_enabled else 'OFF'}",
                    bg=self.YELLOW if self.settings.time_conflict_enabled else self.MUTED)
            except Exception: pass
            self._set_status(
                f"🕐 Time rules applied — offset +{offset_val}min, "
                f"mode={mode_var.get()}", self.YELLOW)
            Toast(self.root, f"Time rules applied (offset +{offset_val}min)",
                  kind='success')
            d.destroy()

        self._make_btn(foot, "❌ Cancel", d.destroy,
                       self.SURFACE3, 14, self.FG).pack(side='right', padx=(6, 0), pady=12)
        self._make_btn(foot, "🔄 Reset Defaults", _reset,
                       self.SURFACE3, 14, self.FG).pack(side='right', padx=(6, 0), pady=12)
        self._make_btn(foot, "✔ Apply All", _apply,
                       self.YELLOW, 22, self.BG).pack(side='right', pady=12)

    def _show_time_preview(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        plan = self.analyzer.issues.get('time_conflicts', [])
        norm = self.analyzer.issues.get('time_normalizations', [])
        d = tk.Toplevel(self.root)
        d.title("👁 Time Preview")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(1100, sw - 80); h = min(700, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(860, 540)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="👁 Time Preview",
                 font=(self.FONT, 16, "bold"),
                 fg=self.YELLOW, bg=self.BG).pack(pady=(16,4), padx=20, anchor='w')
        tk.Label(d, text=f"⏰ {len(plan)} conflict(s)  ·  "
                          f"🕐 {len(norm)} normalization(s)  ·  "
                          f"mode={self.settings.time_conflict_mode}",
                 font=(self.FONT, 10, "italic"),
                 fg=self.MUTED, bg=self.BG).pack(padx=20, anchor='w')
        tree_wrap = tk.Frame(d, bg=self.BG)
        tree_wrap.pack(fill='both', expand=True, padx=20, pady=(12,10))
        cols = ('sheet','row','pickup','dropoff','target','suggested','mode')
        headings = {'sheet':'Sheet','row':'Row','pickup':'Pickup','dropoff':'Dropoff',
                    'target':'Target','suggested':'Suggested','mode':'Mode'}
        widths = {'sheet':120,'row':55,'pickup':90,'dropoff':90,
                  'target':180,'suggested':90,'mode':100}
        tree = ttk.Treeview(tree_wrap, columns=cols, show='headings',
                             style="Fixes.Treeview")
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=widths[c], anchor='w')
        vsb = ttk.Scrollbar(tree_wrap, orient='vertical',
                             command=tree.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        tree.configure(yscrollcommand=vsb.set)
        for p in plan:
            tree.insert('', 'end', values=(p['sheet'], p['row'],
                                            p['pickup'], p['dropoff'],
                                            p.get('target_col',''),
                                            p.get('suggested_dropoff',''),
                                            p.get('mode','')))
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 14, self.FG
                      ).pack(pady=(0,14))

    def _show_shift_engine_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("🌊 Shift Engine Configuration")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(920, sw - 80); h = min(740, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(720, 580)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        hdr = tk.Frame(d, bg=self.SURFACE, height=100)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="🌊", font=(self.FONT, 40),
                 fg=self.SKY, bg=self.SURFACE).pack(side='left', padx=(24,14), pady=22)
        tf = tk.Frame(hdr, bg=self.SURFACE); tf.pack(side='left', pady=26)
        tk.Label(tf, text="Shift Engine", font=(self.FONT, 20, "bold"),
                 fg=self.SKY, bg=self.SURFACE).pack(anchor='w')
        tk.Label(tf, text="Auto-upgrade bare shift patterns + normalize ordinals",
                 font=(self.FONT, 10, "italic"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor='w', pady=(2,0))
        rb = tk.Frame(d, bg=self.BG, height=4); rb.pack(fill='x')
        for c in (self.NAVY, self.PRIMARY, self.SKY, self.CYAN, self.TEAL):
            tk.Frame(rb, bg=c).pack(side='left', fill='both', expand=True)
        tgl_bar = tk.Frame(d, bg=self.SURFACE2); tgl_bar.pack(fill='x', padx=20, pady=(14, 10))
        enable_var = tk.BooleanVar(value=self.settings.shift_engine_enabled)
        tk.Checkbutton(tgl_bar, text="  🌊  Enable Shift Engine",
            variable=enable_var, font=(self.FONT, 11, "bold"),
            fg=self.MINT, bg=self.SURFACE2, activebackground=self.SURFACE2,
            activeforeground=self.SKY, selectcolor=self.SURFACE,
            cursor='hand2', anchor='w').pack(anchor='w', padx=16, pady=12)

        body_wrap = tk.Frame(d, bg=self.BG)
        body_wrap.pack(fill='both', expand=True)
        canvas = tk.Canvas(body_wrap, bg=self.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(body_wrap, orient='vertical', command=canvas.yview,
                             style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(canvas, bg=self.BG)
        win_id = canvas.create_window((0, 0), window=body, anchor='nw')
        def _on_cfg(e=None): canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_ccfg(e): canvas.itemconfigure(win_id, width=e.width)
        body.bind('<Configure>', _on_cfg)
        canvas.bind('<Configure>', _on_ccfg)
        def _wh(e): canvas.yview_scroll(int(-1*(e.delta/120)), 'units')
        canvas.bind('<MouseWheel>', _wh); body.bind('<MouseWheel>', _wh)

        tk.Label(body, text="📋  Active Base Patterns",
                 font=(self.FONT, 11, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(anchor='w', padx=20, pady=(8, 2))
        bases_frame = tk.Frame(body, bg=self.SURFACE); bases_frame.pack(fill='x', padx=20, pady=(0, 10))
        for base_display, triggers in SHIFT_BASE_PATTERNS.items():
            row = tk.Frame(bases_frame, bg=self.SURFACE); row.pack(fill='x', pady=1)
            tk.Label(row, text=f"  • {base_display:<18}",
                     font=(self.FONT, 10, "bold"), fg=self.SKY,
                     bg=self.SURFACE, width=22, anchor='w'
                     ).pack(side='left', padx=4, pady=6)
            tk.Label(row, text="matches: " + " | ".join(triggers[:6]) +
                     (" …" if len(triggers)>6 else ""),
                     font=(self.FONT, 9), fg=self.MUTED,
                     bg=self.SURFACE, anchor='w').pack(side='left', padx=6, pady=6)
        tk.Label(body, text="📋  Ordinal Mappings",
                 font=(self.FONT, 11, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(anchor='w', padx=20, pady=(8, 2))
        ord_frame = tk.Frame(body, bg=self.SURFACE); ord_frame.pack(fill='x', padx=20, pady=(0, 10))
        for keywords, canonical, short in SHIFT_ORDINALS:
            row = tk.Frame(ord_frame, bg=self.SURFACE); row.pack(fill='x', pady=1)
            tk.Label(row, text=f"  {canonical:<8} → '{short}'",
                     font=(self.FONT, 10, "bold"), fg=self.MINT,
                     bg=self.SURFACE, width=22, anchor='w'
                     ).pack(side='left', padx=4, pady=6)
            tk.Label(row, text="triggers: " + " | ".join(keywords),
                     font=(self.FONT, 9), fg=self.MUTED,
                     bg=self.SURFACE, anchor='w').pack(side='left', padx=6, pady=6)
        tk.Label(body, text="🔎  Live Preview — try it",
                 font=(self.FONT, 11, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(anchor='w', padx=20, pady=(10, 2))
        prev_frame = tk.Frame(body, bg=self.SURFACE)
        prev_frame.pack(fill='x', padx=20, pady=(0, 10))
        tk.Label(prev_frame, text="shift_name :",
                 font=(self.FONT, 10, "bold"), fg=self.FG, bg=self.SURFACE
                 ).grid(row=0, column=0, padx=(12,4), pady=8, sticky='w')
        sv_var = tk.StringVar(value="ورادي")
        tk.Entry(prev_frame, textvariable=sv_var, font=(self.FONT, 11),
                 bg=self.SURFACE2, fg=self.FG, insertbackground=self.SKY,
                 relief='flat', bd=0, width=32
                ).grid(row=0, column=1, padx=4, pady=8, ipady=5, sticky='w')
        tk.Label(prev_frame, text="schedule_name :",
                 font=(self.FONT, 10, "bold"), fg=self.FG, bg=self.SURFACE
                 ).grid(row=1, column=0, padx=(12,4), pady=8, sticky='w')
        sch_var = tk.StringVar(value="أولى ذهاب")
        tk.Entry(prev_frame, textvariable=sch_var, font=(self.FONT, 11),
                 bg=self.SURFACE2, fg=self.FG, insertbackground=self.SKY,
                 relief='flat', bd=0, width=32
                ).grid(row=1, column=1, padx=4, pady=8, ipady=5, sticky='w')
        result_lbl = tk.Label(prev_frame, text="", font=(self.FONT, 11, "bold"),
                              fg=self.MINT, bg=self.SURFACE,
                              justify='left', anchor='w', wraplength=500)
        result_lbl.grid(row=2, column=0, columnspan=3,
                        padx=12, pady=(6, 12), sticky='w')
        def _preview():
            engine = ShiftEngine(self.settings)
            res = engine.process(sv_var.get(), sch_var.get())
            if not res:
                result_lbl.config(text="→ No upgrade triggered", fg=self.MUTED)
            else:
                parts = []
                if res['new_shift']:
                    parts.append(f"shift_name  →  '{res['new_shift']}'")
                if res['new_schedule']:
                    parts.append(f"schedule    →  '{res['new_schedule']}'")
                result_lbl.config(text="🌊  " + "   ·   ".join(parts), fg=self.MINT)
        prev_btn = self._make_btn(prev_frame, "🌊 Preview", _preview, self.MINT, 14, self.BG)
        prev_btn.grid(row=0, column=2, rowspan=2, padx=8, pady=8)
        _preview()
        foot = tk.Frame(d, bg=self.BG)
        foot.pack(fill='x', padx=20, pady=(10, 16))
        def _apply():
            self.settings.shift_engine_enabled = bool(enable_var.get())
            self.settings.save()
            try:
                self._shift_badge.config(
                    text=f"🌊 Shift {'ON' if self.settings.shift_engine_enabled else 'OFF'}",
                    bg=self.MINT if self.settings.shift_engine_enabled else self.MUTED)
            except Exception: pass
            if 'shift' in self._sidebar_sections:
                self._sidebar_sections['shift'].set_badge(
                    "ON" if self.settings.shift_engine_enabled else "OFF",
                    self.MINT if self.settings.shift_engine_enabled else self.MUTED)
            d.destroy()
            Toast(self.root,
                  f"Shift Engine {'enabled' if self.settings.shift_engine_enabled else 'disabled'}",
                  kind='success')
        self._make_btn(foot, "❌ Cancel", d.destroy,
                       self.SURFACE3, 14, self.FG).pack(side='right', padx=(6,0))
        self._make_btn(foot, "✔ Apply", _apply, self.MINT, 22, self.BG).pack(side='right')

    def _show_shift_preview(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        plan = self.analyzer.issues.get('shift_upgrades', [])
        d = tk.Toplevel(self.root)
        d.title("👁 Shift Upgrade Preview")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(1100, sw - 80); h = min(680, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(860, 520)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="👁 Shift Upgrade Preview",
                 font=(self.FONT, 16, "bold"),
                 fg=self.SKY, bg=self.BG).pack(pady=(16,4), padx=20, anchor='w')
        tk.Label(d, text=f"{len(plan)} upgrade(s) planned",
                 font=(self.FONT, 10, "italic"),
                 fg=self.MUTED, bg=self.BG).pack(padx=20, anchor='w')
        tree_wrap = tk.Frame(d, bg=self.BG)
        tree_wrap.pack(fill='both', expand=True, padx=20, pady=(12,10))
        cols = ('sheet', 'row', 'old_s', 'new_s', 'old_sch', 'new_sch')
        tree = ttk.Treeview(tree_wrap, columns=cols, show='headings',
                             style="Fixes.Treeview")
        headings = {'sheet':'Sheet', 'row':'Row', 'old_s':'Old Shift',
                    'new_s':'→ New Shift', 'old_sch':'Old Schedule',
                    'new_sch':'→ New Schedule'}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=200, anchor='w')
        vsb = ttk.Scrollbar(tree_wrap, orient='vertical',
                             command=tree.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        tree.configure(yscrollcommand=vsb.set)
        for p in plan:
            tree.insert('', 'end', values=(p['sheet'], p['row'],
                                            p['old_shift'], p['new_shift'],
                                            p['old_schedule'], p['new_schedule']))
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 14, self.FG
                      ).pack(pady=(0,14))

    def _show_main_suppliers_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("🏢 Main Suppliers Manager")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(720, sw - 80); h = min(600, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(560, 460)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        hdr = tk.Frame(d, bg=self.SURFACE, height=88)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="🏢", font=(self.FONT, 32),
                 fg=self.VIOLET, bg=self.SURFACE
                 ).pack(side='left', padx=(20,12), pady=18)
        tf = tk.Frame(hdr, bg=self.SURFACE); tf.pack(side='left', pady=24)
        tk.Label(tf, text="Main Suppliers", font=(self.FONT, 17, "bold"),
                 fg=self.VIOLET, bg=self.SURFACE).pack(anchor='w')
        tk.Label(tf, text="Add unlimited suppliers",
                 font=(self.FONT, 9, "italic"),
                 fg=self.MUTED, bg=self.SURFACE).pack(anchor='w', pady=(2,0))
        rb = tk.Frame(d, bg=self.BG, height=4); rb.pack(fill='x')
        for c in (self.NAVY, self.PRIMARY, self.SKY, self.CYAN, self.TEAL):
            tk.Frame(rb, bg=c).pack(side='left', fill='both', expand=True)
        inp = tk.Frame(d, bg=self.BG); inp.pack(fill='x', padx=20, pady=(14, 6))
        tk.Label(inp, text="New supplier:",
                 font=(self.FONT, 10, "bold"),
                 fg=self.PRIMARY, bg=self.BG).pack(side='left', padx=(0,6))
        entry_var = tk.StringVar()
        entry = tk.Entry(inp, textvariable=entry_var, font=(self.FONT, 11),
                          bg=self.SURFACE2, fg=self.FG, insertbackground=self.PRIMARY,
                          relief='flat', bd=0)
        entry.pack(side='left', fill='x', expand=True, ipady=7, padx=(0,8))
        count_lbl = tk.Label(d, text="", font=(self.FONT, 10, "bold"),
                             fg=self.YELLOW, bg=self.BG)
        count_lbl.pack(anchor='w', padx=20, pady=(0, 6))
        list_wrap = tk.Frame(d, bg=self.SURFACE)
        list_wrap.pack(fill='both', expand=True, padx=20, pady=(4, 8))
        c = tk.Canvas(list_wrap, bg=self.SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(list_wrap, orient='vertical', command=c.yview,
                             style="Vertical.TScrollbar")
        c.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        c.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(c, bg=self.SURFACE)
        win_id = c.create_window((0, 0), window=inner, anchor='nw')
        def _resize(e=None): c.configure(scrollregion=c.bbox('all'))
        def _canvas_resize(e): c.itemconfigure(win_id, width=e.width)
        inner.bind('<Configure>', _resize); c.bind('<Configure>', _canvas_resize)
        def _wheel(e): c.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        c.bind('<MouseWheel>', _wheel); inner.bind('<MouseWheel>', _wheel)
        def _refresh():
            for w in inner.winfo_children(): w.destroy()
            supps = self.settings.get_main_suppliers()
            count_lbl.config(text=f"🌊 Total: {len(supps)} supplier(s)")
            if not supps:
                tk.Label(inner, text="(none)", font=(self.FONT, 10, "italic"),
                         fg=self.MUTED, bg=self.SURFACE).pack(pady=14); return
            for i, name in enumerate(supps):
                bg = self.SURFACE if i % 2 == 0 else self.SURFACE2
                row = tk.Frame(inner, bg=bg); row.pack(fill='x', pady=1)
                tk.Label(row, text=f"  {i+1:>3}.", font=(self.MONO, 10, "bold"),
                         fg=self.VIOLET, bg=bg, width=6, anchor='w'
                         ).pack(side='left', padx=(4,0), pady=6)
                tk.Label(row, text=name, font=(self.FONT, 11, "bold"),
                         fg=self.FG, bg=bg, anchor='w'
                         ).pack(side='left', fill='x', expand=True, pady=6)
                rem = tk.Label(row, text="  ✕ Remove  ",
                                font=(self.FONT, 9, "bold"),
                                fg=self.CORAL, bg=bg, cursor='hand2')
                rem.pack(side='right', padx=6)
                def _rm(n=name):
                    if messagebox.askyesno("Remove?", f"Remove '{n}'?"):
                        self.settings.remove(n); _refresh()
                        self._refresh_supplier_badge()
                rem.bind("<Button-1>", lambda e, f=_rm: f())
        def _add():
            name = entry_var.get().strip()
            if not name: return
            if self.settings.add(name):
                entry_var.set(''); _refresh(); self._refresh_supplier_badge()
                Toast(self.root, f"Added supplier '{name}'", kind='success')
            else:
                Toast(self.root, f"'{name}' already exists", kind='warning')
        def _reset():
            if messagebox.askyesno("Reset?", "Restore defaults?"):
                self.settings.reset(); _refresh(); self._refresh_supplier_badge()
                Toast(self.root, "Suppliers reset to defaults", kind='info')
        entry.bind('<Return>', lambda e: _add())
        foot = tk.Frame(d, bg=self.BG); foot.pack(fill='x', padx=20, pady=(0, 14))
        self._make_btn(foot, "➕ Add", _add, self.MINT, 14, self.BG).pack(side='left')
        self._make_btn(foot, "🔄 Reset", _reset, self.SURFACE3, 12, self.FG
                      ).pack(side='left', padx=(6,0))
        self._make_btn(foot, "✔ Close", d.destroy, self.PRIMARY, 16, self.FG
                      ).pack(side='right')
        _refresh(); entry.focus_set()

    def _refresh_supplier_badge(self):
        try:
            n = len(self.settings.get_main_suppliers())
            self._supplier_badge.config(text=f"🏢 {n}")
        except Exception: pass

    def _show_column_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("🎛️ Column Control")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(1100, sw - 80); h = min(720, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(880, 540)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        hdr = tk.Frame(d, bg=self.SURFACE, height=84)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="🎛️", font=(self.FONT, 30),
                 fg=self.VIOLET, bg=self.SURFACE).pack(side='left', padx=(18,10), pady=18)
        tf = tk.Frame(hdr, bg=self.SURFACE); tf.pack(side='left', pady=22)
        tk.Label(tf, text="Column Control", font=(self.FONT, 17, "bold"),
                 fg=self.VIOLET, bg=self.SURFACE).pack(anchor='w')
        tk.Label(tf, text="Keep / clear / delete / override",
                 font=(self.FONT, 9, "italic"), fg=self.MUTED, bg=self.SURFACE
                 ).pack(anchor='w', pady=(2,0))
        rbar = tk.Frame(d, bg=self.BG, height=4); rbar.pack(fill='x')
        for c in (self.NAVY, self.PRIMARY, self.SKY, self.CYAN, self.TEAL, self.MINT):
            tk.Frame(rbar, bg=c).pack(side='left', fill='both', expand=True)
        bar = tk.Frame(d, bg=self.SURFACE2); bar.pack(fill='x')
        tk.Label(bar, text="⚡ Preset:", font=(self.FONT, 10, "bold"),
                 fg=self.YELLOW, bg=self.SURFACE2
                 ).pack(side='left', padx=(14, 6), pady=10)
        preset_var = tk.StringVar(value='Keep all columns')
        presets = ['Keep all columns', 'ERP Upload (recommended)',
                   'ERP Minimal', 'Farm Frites (clear dropoff)']
        cb = ttk.Combobox(bar, textvariable=preset_var, values=presets,
                          state='readonly', width=32, font=(self.FONT, 10))
        cb.pack(side='left', padx=4, pady=10)
        self._dlg_erp_mode = tk.BooleanVar(value=self.column_controller.erp_mode)
        self._dlg_del_rejected = tk.BooleanVar(value=self.column_controller.delete_rejected)
        for txt_, var, col in [("🔒 ERP", self._dlg_erp_mode, self.YELLOW),
                                ("🗑 Auto-del", self._dlg_del_rejected, self.CORAL)]:
            tk.Checkbutton(bar, text=txt_, variable=var,
                           font=(self.FONT, 9, "bold"), fg=col, bg=self.SURFACE2,
                           activebackground=self.SURFACE2,
                           activeforeground=self.PRIMARY,
                           selectcolor=self.SURFACE, cursor='hand2'
                          ).pack(side='left', padx=(10, 4))
        list_wrap = tk.Frame(d, bg=self.BG)
        list_wrap.pack(fill='both', expand=True, padx=14, pady=(10, 8))
        cwrap = tk.Frame(list_wrap, bg=self.BG); cwrap.pack(fill='both', expand=True)
        c = tk.Canvas(cwrap, bg=self.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(cwrap, orient='vertical', command=c.yview,
                            style="Vertical.TScrollbar")
        c.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y'); c.pack(side='left', fill='both', expand=True)
        inner = tk.Frame(c, bg=self.BG)
        win = c.create_window((0, 0), window=inner, anchor='nw')
        def _rs(e=None): c.configure(scrollregion=c.bbox('all'))
        def _cw(e): c.itemconfigure(win, width=e.width)
        inner.bind('<Configure>', _rs); c.bind('<Configure>', _cw)
        def _wh(e): c.yview_scroll(int(-1*(e.delta/120)), 'units')
        c.bind('<MouseWheel>', _wh); inner.bind('<MouseWheel>', _wh)
        all_avail = set(ERP_COLUMN_SPEC.keys())
        if self.analyzer:
            fc = set()
            for info in self.analyzer.sheets_data.values():
                if info['skipped']: continue
                for k in info['cmap'].keys():
                    if not k.startswith('_'): fc.add(k)
            if fc: all_avail = fc | (all_avail & set(ERP_COLUMN_SPEC.keys()))
        row_widgets = {}
        def _mk_row(parent, col, idx):
            spec = ERP_COLUMN_SPEC.get(col, {'cat': 'unknown'})
            cat = spec.get('cat', 'unknown')
            req = spec.get('required', False)
            bg = self.SURFACE if idx % 2 == 0 else self.SURFACE2
            if req: bg = self.SURFACE3
            row = tk.Frame(parent, bg=bg, height=32)
            row.pack(fill='x', pady=1); row.pack_propagate(False)
            rule = self.column_controller.get(col)
            enabled_var = tk.BooleanVar(value=(rule['action'] != 'delete'))
            cb = tk.Checkbutton(row, variable=enabled_var, bg=bg,
                                 activebackground=bg, selectcolor=self.SURFACE,
                                 cursor='hand2')
            cb.pack(side='left', padx=(6, 0), pady=4)
            tk.Label(row, text=col, font=(self.MONO, 10, "bold"),
                     fg=(self.PRIMARY if req else self.FG), bg=bg, width=30, anchor='w'
                     ).pack(side='left', padx=(4, 2))
            ccol = {'core': self.PINK, 'driver': self.YELLOW, 'vehicle': self.CYAN,
                    'supplier': self.MINT, 'pricing': self.EMERALD,
                    'schedule': self.VIOLET, 'routing': self.BLUE,
                    'location': self.SKY, 'line': self.ORANGE,
                    'unknown': self.MUTED}.get(cat, self.MUTED)
            tk.Label(row, text=cat.upper(), font=(self.FONT, 8, "bold"),
                     fg=self.BG, bg=ccol, padx=6, pady=2, width=10
                     ).pack(side='left', padx=(0, 4))
            av = tk.StringVar(value=rule['action'])
            acb = ttk.Combobox(row, textvariable=av,
                                values=['keep', 'clear', 'override', 'delete'],
                                state='readonly', width=10, font=(self.FONT, 9))
            acb.pack(side='left', padx=(0, 4))
            vv = tk.StringVar(value=rule.get('value') or '')
            ve = tk.Entry(row, textvariable=vv, font=(self.FONT, 9),
                           bg=self.BORDER, fg=self.FG, insertbackground=self.PRIMARY,
                           relief='flat', width=22, bd=0)
            ve.pack(side='left', padx=(0, 6), ipady=4, fill='x', expand=True)
            if rule['action'] != 'override': ve.config(state='disabled')
            row_widgets[col] = {'a': av, 'v': vv, 'e': ve, 'en': enabled_var}
            def _rf(c=col):
                r = self.column_controller.get(c)
                w = row_widgets[c]; w['a'].set(r['action'])
                w['en'].set(r['action'] != 'delete')
                w['e'].config(state='normal' if r['action'] == 'override' else 'disabled',
                               bg=self.SURFACE3 if r['action'] == 'override' else self.BORDER)
            def _oa(c=col, v=av): self.column_controller.set_rule(c, v.get()); _rf()
            def _ot(c=col, v=enabled_var):
                if not v.get(): self.column_controller.set_rule(c, 'delete')
                elif self.column_controller.get(c)['action'] == 'delete':
                    self.column_controller.set_rule(c, 'keep')
                _rf()
            def _ov(c=col, v=vv):
                cur = self.column_controller.get(c)
                if cur['action'] == 'override':
                    self.column_controller.set_rule(c, 'override', v.get())
            acb.bind('<<ComboboxSelected>>', lambda e: _oa())
            cb.config(command=lambda: _ot())
            ve.bind('<FocusOut>', lambda e: _ov())
            ve.bind('<Return>', lambda e: _ov())
        def _rebuild():
            for w in inner.winfo_children(): w.destroy()
            row_widgets.clear()
            for i, col in enumerate(sorted(all_avail)):
                _mk_row(inner, col, i)
        _rebuild()
        def _apply_preset(e=None):
            mp = {'Keep all columns': 'keep_all',
                  'ERP Upload (recommended)': 'erp_upload',
                  'ERP Minimal': 'erp_minimal',
                  'Farm Frites (clear dropoff)': 'farm_frites'}
            k = mp.get(preset_var.get())
            if k:
                self.column_controller.apply_preset(k, list(all_avail))
                _rebuild()
        cb.bind('<<ComboboxSelected>>', _apply_preset)
        foot = tk.Frame(d, bg=self.BG)
        foot.pack(fill='x', padx=14, pady=(0, 12))
        def _reset():
            self.column_controller.reset(); _rebuild()
        def _apply_close():
            self.column_controller.erp_mode = bool(self._dlg_erp_mode.get())
            self.column_controller.delete_rejected = bool(self._dlg_del_rejected.get())
            d.destroy()
        self._make_btn(foot, "🔄 Reset", _reset, self.SURFACE3, 12, self.FG
                      ).pack(side='left')
        self._make_btn(foot, "✔ Apply", _apply_close, self.PRIMARY, 18, self.FG
                      ).pack(side='right')

    def _make_btn(self, parent, text, cmd, bg, padx=14, fg=None, size=10):
        outer = tk.Frame(parent, bg=bg, cursor='hand2')
        inner = tk.Frame(outer, bg=bg, cursor='hand2'); inner.pack()
        btn = tk.Label(inner, text=text, font=(self.FONT, size, "bold"),
                       bg=bg, fg=fg or self.BG, padx=padx, pady=6, cursor='hand2')
        btn.pack()
        hb = _lighten(bg, 0.28)
        def _en(_): outer.config(bg=hb); inner.config(bg=hb); btn.config(bg=hb)
        def _lv(_): outer.config(bg=bg); inner.config(bg=bg); btn.config(bg=bg)
        def _cl(_): cmd()
        for w in (outer, inner, btn):
            w.bind("<Enter>", _en); w.bind("<Leave>", _lv)
            w.bind("<Button-1>", _cl)
        return outer

    def _animate_logo(self):
        colors = [self.PRIMARY, self.SKY, self.CYAN, self.TEAL,
                  self.MINT, self.CYAN, self.SKY, self.PRIMARY]
        self._logo_ci = 0
        def _pulse():
            try:
                self._logo_lbl.config(fg=colors[self._logo_ci % len(colors)])
                self._logo_ci += 1
                self.root.after(600, _pulse)
            except Exception: pass
        _pulse()

    def _set_status(self, msg, color=None):
        c = color or self.SKY
        self._status_lbl.config(text=msg, fg=c)
        self._status_dot.config(fg=c)

    def _insert_lines(self, widget, lines):
        widget.config(state='normal'); widget.delete('1.0', 'end')
        use_shaper = HAS_SHAPER and self.arabic_shaping.get()
        for line, tag in lines:
            tags = []
            if tag: tags.append(tag)
            if tag == 'arabic_hdr' or is_rtl_line(line): tags.append('rtl')
            display = shape_for_display(line) if use_shaper else line
            widget.insert('end', display + "\n", tuple(tags))
        widget.config(state='disabled')

    def _reapply_shaping(self):
        if not self.analyzer: return
        report = self.analyzer.report
        idx = len(report)
        for i, (ln, _) in enumerate(report):
            if "EXECUTIVE SUMMARY" in ln or "Quality Score" in ln:
                idx = i; break
        self._insert_lines(self._txt_overview, report[idx:])
        self._insert_lines(self._txt_full,     report)

    def _maybe_open_file(self, path):
        if not os.path.exists(path): return
        if not messagebox.askyesno("📂 Open file?",
            f"Saved!\n\n{os.path.basename(path)}\n\nOpen now?"): return
        try:
            if sys.platform.startswith('win'): os.startfile(path)
            elif sys.platform == 'darwin': subprocess.Popen(['open', path])
            else: subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Cannot open", str(e))

    def browse_file(self):
        p = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("All supported", "*.xlsx *.xlsm *.csv *.tsv *.txt"),
                       ("Excel", "*.xlsx *.xlsm"),
                       ("CSV/TSV", "*.csv *.tsv *.txt"),
                       ("All files", "*.*")])
        if not p: return
        self.file_path = p
        name = os.path.basename(p); size = os.path.getsize(p)
        self._file_lbl.config(text=f"  {name}  ({size/1024:.1f} KB)", fg=self.FG)
        self._file_icon.config(text="📄", fg=self.MINT)
        self._set_status(f"✨ Loaded: {name}", self.CYAN)
        Toast(self.root, f"Loaded: {name}", kind='success')
        self._disable_exports()

    def analyze(self):
        if not self.file_path:
            Toast(self.root, "Select a file first", kind='warning'); return
        if self._running:
            Toast(self.root, "Analysis already running", kind='warning'); return
        self._clear_all_text()
        self._set_status("🌊 Analyzing… Time Control Center armed ✨", self.PRIMARY)
        self._disable_exports()
        self._pbar.pack(fill='x'); self._pbar.start(12)
        self._running = True
        cc = self.column_controller
        ms = self.settings.get_main_suppliers()
        st = self.settings
        def _worker():
            try:
                a = CodefyAnalyzer(self.file_path, column_controller=cc,
                                    main_suppliers=ms, settings=st)
                report, fixes = a.run()
                self._analysis_queue.put(('ok', a, report, fixes))
            except Exception as e:
                import traceback
                self._analysis_queue.put(('err', str(e), traceback.format_exc()))
        threading.Thread(target=_worker, daemon=True).start()
        self.root.after(150, self._poll_analysis)

    def _poll_analysis(self):
        try: result = self._analysis_queue.get_nowait()
        except queue.Empty:
            self.root.after(150, self._poll_analysis); return
        self._pbar.stop(); self._pbar.pack_forget(); self._running = False
        if result[0] == 'err':
            _, msg, tb = result
            messagebox.showerror("Analysis Error", f"{msg}\n\n{tb}")
            self._set_status("💥 Failed", self.RED)
            Toast(self.root, "Analysis failed — see error dialog", kind='error')
            return
        _, analyzer, report, fixes = result
        self.analyzer = analyzer
        idx = len(report)
        for i, (ln, _) in enumerate(report):
            if "EXECUTIVE SUMMARY" in ln or "Quality Score" in ln:
                idx = i; break
        self._insert_lines(self._txt_overview, report[idx:])
        self._insert_lines(self._txt_full,     report)
        self._n_err = sum(1 for _, t in self._filter_issues(report) if t == 'err')
        self._n_wrn = sum(1 for _, t in self._filter_issues(report) if t == 'warn')
        total_rows = sum(len(i['records']) for i in analyzer.sheets_data.values()
                         if not i['skipped'])
        expiry_n = len(analyzer.issues['expiry_alerts'])
        short_n = sum(1 for x in analyzer.issues['invalid_phones']
                      if x.get('kind') == 'short')
        shift_n = len(analyzer.issues['shift_upgrades'])
        tc_n = len(analyzer.issues['time_conflicts'])
        score = analyzer._compute_score()
        self._update_cards(score, total_rows, len(fixes),
                           self._n_err, self._n_wrn, expiry_n, short_n,
                           shift_n, tc_n)
        self._enable_exports(fixes)
        try:
            self._issue_store = analyzer.build_issue_list()
            self._selected_category = None
            self._refresh_issue_tree()
        except Exception:
            self._issue_store = []; self._refresh_issue_tree()
        grade = ("EXCELLENT 🎉" if score >= 90 else "GOOD 👍" if score >= 75 else
                 "FAIR 🙂" if score >= 60 else "POOR 😬" if score >= 40 else "CRITICAL 🚨")
        gc = self.MINT if score >= 75 else (self.YELLOW if score >= 60 else self.RED)
        ready = "READY ✨" if analyzer.upload_ready else f"🚩 {len(analyzer.red_flag_cells)} RED flags"
        self._set_status(
            f"🌊 Score: {score}/100 ({grade}) | {len(fixes)} fixes | "
            f"{shift_n} shift upgrades | {tc_n} time conflicts | {ready}", gc)
        Toast(self.root, f"Analysis complete — Score {score}/100", kind='success')
        self.nb.select(0)

    def _filter_issues(self, report):
        keep = {'err', 'warn', 'h2', 'arabic_hdr'}
        out = []
        for line, tag in report:
            if tag in keep: out.append((line, tag))
            elif line.strip() == '': out.append(('', None))
        cleaned, prev = [], False
        for ln, tg in out:
            b = (ln.strip() == '')
            if b and prev: continue
            cleaned.append((ln, tg)); prev = b
        return cleaned

    def _clear_all_text(self):
        for t in (self._txt_overview, self._txt_full):
            t.config(state='normal'); t.delete('1.0', 'end'); t.config(state='disabled')
        try:
            self._issue_tree.delete(*self._issue_tree.get_children())
            self._issue_store = []
            self._selected_category = None
            self._refresh_issue_tree()
        except Exception: pass

    def _clear_all(self):
        self._clear_all_text()
        for k in self._cards:
            v, c = self._cards[k]; v.config(text="—", fg=c)
        self._disable_exports()
        self._set_status("Cleared ✨", self.CYAN)
        self.analyzer = None
        Toast(self.root, "Results cleared", kind='info')

    def _disable_exports(self):
        for b in self._export_btns: self._set_btn_color(b, self.MUTED)

    def _enable_exports(self, fixes):
        for b in self._export_btns: self._set_btn_color(b, self.FG)
        self._set_btn_color(self._sb_fixed, self.MINT if fixes else self.MUTED)
        self._set_btn_color(self._sb_fixed_csv, self.CYAN)
        self._set_btn_color(self._sb_html, self.VIOLET)
        self._set_btn_color(self._sb_xlsx, self.YELLOW)
        self._set_btn_color(self._sb_csv, self.LIME)
        self._set_btn_color(self._sb_json, self.MINT)
        self._set_btn_color(self._sb_txt, self.MUTED)
        self._set_btn_color(self._sb_report, self.BLUE)
        self._set_btn_color(self._sb_wa, "#25D366")
        self._set_btn_color(self._sb_copy, self.MAGENTA)

    def _show_reorder_dialog(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        suppliers = self.analyzer.get_all_supplier_names()
        if not suppliers:
            Toast(self.root, "No suppliers found", kind='warning'); return
        d = tk.Toplevel(self.root)
        d.title("🎯 Supplier Reorder")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(700, sw - 80); h = min(660, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(560, 480)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="🎯 Reorder Rows by Supplier",
                 font=(self.FONT, 15, "bold"), fg=self.CYAN, bg=self.BG
                ).pack(pady=(18,4), padx=22, anchor='w')
        af = tk.Frame(d, bg=self.SURFACE); af.pack(fill='x', padx=22, pady=(14,6))
        tk.Label(af, text="Supplier:", font=(self.FONT, 10, "bold"),
                 fg=self.FG, bg=self.SURFACE).grid(row=0, column=0,
                                                   padx=(12,4), pady=12, sticky='w')
        sv = tk.StringVar(value=next(iter(suppliers)))
        ttk.Combobox(af, textvariable=sv, values=list(suppliers.keys()),
                     state='readonly', width=26, font=(self.FONT, 10)
                    ).grid(row=0, column=1, padx=4, pady=12, sticky='w')
        tk.Label(af, text="Position:", font=(self.FONT, 10, "bold"),
                 fg=self.FG, bg=self.SURFACE).grid(row=0, column=2,
                                                   padx=(12,4), pady=12, sticky='w')
        pv = tk.StringVar(value='bottom')
        ttk.Combobox(af, textvariable=pv, values=['top', 'bottom'],
                     state='readonly', width=10, font=(self.FONT, 10)
                    ).grid(row=0, column=3, padx=4, pady=12, sticky='w')
        lb_frame = tk.Frame(d, bg=self.SURFACE)
        lb_frame.pack(fill='both', expand=True, padx=22, pady=(8,10))
        lb = tk.Listbox(lb_frame, font=(self.MONO, 10), bg=self.SURFACE, fg=self.FG,
                        selectbackground=self.VIOLET, selectforeground=self.YELLOW,
                        relief='flat', bd=0, highlightthickness=0)
        lb.pack(side='left', fill='both', expand=True, padx=(10,0), pady=10)
        def _refresh():
            lb.delete(0, 'end')
            for i, r in enumerate(self.analyzer.custom_reorder_rules, 1):
                lb.insert('end', f"  {i}. '{r['supplier']}' → {r['position'].upper()}")
        def _add():
            n, p = sv.get().strip(), pv.get().strip()
            if not n: return
            self.analyzer.custom_reorder_rules = [
                r for r in self.analyzer.custom_reorder_rules
                if normalize_name(r['supplier']) != normalize_name(n)]
            self.analyzer.custom_reorder_rules.append({'supplier': n, 'position': p})
            _refresh()
        def _rm():
            s = lb.curselection()
            if s and s[0] < len(self.analyzer.custom_reorder_rules):
                del self.analyzer.custom_reorder_rules[s[0]]; _refresh()
        def _apply():
            self.analyzer._plan_reorder(log=False)
            d.destroy(); self._set_status("✨ Reorder applied", self.MINT)
            Toast(self.root, "Reorder rules applied", kind='success')
        row = tk.Frame(d, bg=self.BG); row.pack(fill='x', padx=22, pady=(0,14))
        self._make_btn(row, "➕ Add", _add, self.MINT, 12, self.BG).pack(side='left')
        self._make_btn(row, "🗑 Remove", _rm, self.SURFACE3, 12, self.FG
                      ).pack(side='left', padx=(6,0))
        self._make_btn(row, "✔ Apply", _apply, self.CYAN, 16, self.BG
                      ).pack(side='right')
        _refresh()

    def _show_auto_fix_log(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        d = tk.Toplevel(self.root)
        d.title("🔧 Auto-Fix Log")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(1200, sw - 80); h = min(740, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(900, 560)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="🔧 Auto-Fix Log", font=(self.FONT, 15, "bold"),
                 fg=self.MINT, bg=self.BG).pack(pady=(16,4), padx=18, anchor='w')
        tk.Label(d, text=f"{len(self.analyzer.fixes)} queued change(s)",
                 font=(self.FONT, 10, "bold"), fg=self.YELLOW, bg=self.BG
                ).pack(padx=18, anchor='w')
        tree_wrap = tk.Frame(d, bg=self.BG)
        tree_wrap.pack(fill='both', expand=True, padx=18, pady=(10,10))
        cols = ('id', 'sheet', 'row', 'col', 'old', 'new', 'reason')
        widths = {'id': 45, 'sheet': 110, 'row': 60, 'col': 200,
                  'old': 200, 'new': 200, 'reason': 400}
        tree = ttk.Treeview(tree_wrap, columns=cols, show='headings',
                             style="Fixes.Treeview")
        for c in cols:
            tree.heading(c, text=c.upper())
            tree.column(c, width=widths[c], anchor='w', stretch=(c == 'reason'))
        vsb = ttk.Scrollbar(tree_wrap, orient='vertical',
                             command=tree.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        tree.configure(yscrollcommand=vsb.set)
        for i, f in enumerate(self.analyzer.fixes, 1):
            tag = ()
            r = f['reason']
            if 'Shift Engine' in r: tag = ('shift',)
            elif 'offset' in r and '==' in r: tag = ('time',)
            tree.insert('', 'end', tags=tag,
                        values=(i, f['sheet'], f['row'], f['col'],
                                to_str(f['old'])[:50], to_str(f['new'])[:50], r))
        for i, (sheet, row, col, reason) in enumerate(
                self.analyzer.red_flag_cells, len(self.analyzer.fixes) + 1):
            tree.insert('', 'end', tags=('red',),
                        values=(i, sheet, row, col, '(unchanged)',
                                '🚩 RED FLAG', reason))
        tree.tag_configure('red', foreground=self.CORAL)
        tree.tag_configure('shift', foreground=self.SKY)
        tree.tag_configure('time', foreground=self.YELLOW)
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 14, self.FG
                      ).pack(pady=(0,14))

    def _show_kpi_popup(self, key):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        if key == 'auto_fixes':
            self._show_auto_fix_log(); return
        if key == 'shift_upgrades':
            self._show_shift_preview(); return
        if key == 'time_conflicts':
            self._show_time_preview(); return
        title, icon, color = {
            'quality_score':  ("Quality Score", "🎯", self.PRIMARY),
            'total_rows':     ("Data Rows", "📋", self.CYAN),
            'errors_count':   ("Errors", "✗", self.RED),
            'warnings_count': ("Warnings", "⚠", self.CORAL),
            'short_phones':   ("RED-flagged Phones", "🚩", self.PINK),
            'expiry_alerts':  ("Expiry Alerts", "📅", self.MINT),
        }.get(key, ("Details", "📊", self.CYAN))
        d = tk.Toplevel(self.root)
        d.title(f"{icon} {title}")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(820, sw - 80); h = min(620, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(600, 460)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text=f"{icon} {title}", font=(self.FONT, 15, "bold"),
                 fg=color, bg=self.BG).pack(pady=(16,4), padx=20, anchor='w')
        body = tk.Frame(d, bg=self.SURFACE); body.pack(fill='both', expand=True,
                                                       padx=20, pady=(0,14))
        txt = tk.Text(body, font=(self.MONO, 10), bg=self.SURFACE, fg=self.FG,
                      relief='flat', padx=16, pady=14, wrap='word', bd=0,
                      highlightthickness=0)
        txt.pack(side='left', fill='both', expand=True)
        vsb = ttk.Scrollbar(body, command=txt.yview, style="Vertical.TScrollbar")
        vsb.pack(side='right', fill='y'); txt.config(yscrollcommand=vsb.set)
        txt.tag_config('h', foreground=color, font=(self.FONT, 12, 'bold'))
        txt.tag_config('lbl', foreground=self.MUTED)
        txt.tag_config('val', foreground=self.CYAN)
        txt.tag_config('ok', foreground=self.MINT)
        txt.tag_config('warn', foreground=self.YELLOW)
        txt.tag_config('err', foreground=self.CORAL)
        txt.config(state='normal')
        a = self.analyzer
        def _l(t="", tag=None): txt.insert('end', t + "\n", tag or ())
        if key == 'quality_score':
            sc = a._compute_score()
            _l(f"  🌊 Score: {sc}/100", 'h'); _l()
            for label, pts, cnt, note in a.kpi_quality_breakdown():
                tag = 'err' if pts > 0 else 'ok'
                _l(f"  • {label:<42} count={cnt:<4} -{pts} pts", tag)
        elif key == 'total_rows':
            info = a.kpi_rows_breakdown()
            _l(f"  🌊 Total: {sum(info['per_sheet'].values()):,} rows", 'h'); _l()
            for sh, cnt in info['per_sheet'].items():
                _l(f"  • {sh:<40} {cnt:>6}", 'val')
        elif key == 'errors_count':
            errs = a.kpi_errors_breakdown()
            for label, items in [("Time conflicts", errs.get('time_conflicts', [])),
                                  ("Unparseable dates", errs.get('date_invalid', [])),
                                  ("Invalid phones", errs.get('invalid_phones', [])),
                                  ("Driver conflicts", errs.get('driver_conflicts', [])),
                                  ("Phone hard", errs.get('phone_hard', [])),
                                  ("Duplicate hard", errs.get('duplicate_hard', [])),
                                  ("Enum violations", errs.get('enum_violations', [])),
                                  ("ERP issues", errs.get('erp_issues', []))]:
                _l(f"  • {label:<36} {len(items):>5}",
                   'err' if items else 'ok')
        elif key == 'warnings_count':
            w = a.kpi_warnings_breakdown()
            for label, items in [("Short phones", w.get('phone_short', [])),
                                  ("Non-ISO dates", w.get('date_wrong_fmt', [])),
                                  ("Phone soft", w.get('phone_soft', [])),
                                  ("Duplicate soft", w.get('duplicate_soft', [])),
                                  ("Missing data", w.get('missing_data', [])),
                                  ("Expiry", w.get('expiry', [])),
                                  ("Shift upgrades", w.get('shift_upgrades', [])),
                                  ("Time normalizations",
                                   w.get('time_normalizations', [])),
                                  ("Main-supplier fixes",
                                   w.get('internal_supplier_fix', []))]:
                _l(f"  • {label:<36} {len(items):>5}",
                   'warn' if items else 'ok')
        elif key == 'short_phones':
            shorts = [x for x in a.issues['invalid_phones']
                      if x.get('kind') == 'short']
            _l(f"  🚩 {len(shorts)} RED-flagged phone(s)", 'h'); _l()
            _l("  These phones are NOT auto-fixed. Values stay as-is.", 'lbl')
            _l("  The cell will be painted RED on export for manual review.", 'lbl')
            _l()
            for i, s in enumerate(shorts, 1):
                _l(f"  #{i}  [{s['sheet']}] row {s['row']}  {s['col']}", 'val')
                _l(f"      value  : '{s['value']}'", 'err')
                _l(f"      reason : {s['reason']}", 'lbl'); _l()
        elif key == 'expiry_alerts':
            b = a.kpi_expiry_breakdown()
            for label, items in [("Driver EXPIRED", b['driver_expired']),
                                  ("Driver soon", b['driver_soon']),
                                  ("Vehicle EXPIRED", b['vehicle_expired']),
                                  ("Vehicle soon", b['vehicle_soon'])]:
                _l(f"  • {label:<30} {len(items):>5}",
                   'err' if 'EXPIRED' in label and items
                   else 'warn' if items else 'ok')
                for e in items[:20]:
                    _l(f"      {e['identifier'][:40]:<42} {e['date']} ({e['days']}d)",
                       'val')
        txt.config(state='disabled'); txt.see('1.0')
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 12, self.FG
                      ).pack(pady=(0,12))

    def _update_cards(self, score, total_rows, fixes, n_err, n_wrn, expiry,
                      short_phones=0, shift_upgrades=0, time_conflicts=0):
        cs = (self.MINT if score >= 75 else self.YELLOW if score >= 60 else self.RED)
        v, _ = self._cards["quality_score"]; v.config(text=f"{score}/100", fg=cs)
        v, _ = self._cards["total_rows"]; v.config(text=f"{total_rows:,}")
        v, _ = self._cards["auto_fixes"]
        v.config(text=str(fixes), fg=self.YELLOW if fixes else self.MINT)
        v, _ = self._cards["shift_upgrades"]
        v.config(text=str(shift_upgrades),
                 fg=self.SKY if shift_upgrades else self.MINT)
        v, _ = self._cards["time_conflicts"]
        v.config(text=str(time_conflicts),
                 fg=self.ORANGE if time_conflicts else self.MINT)
        v, _ = self._cards["errors_count"]
        v.config(text=str(n_err), fg=self.RED if n_err else self.MINT)
        v, _ = self._cards["short_phones"]
        v.config(text=str(short_phones),
                 fg=self.PINK if short_phones else self.MINT)
        v, _ = self._cards["expiry_alerts"]
        v.config(text=str(expiry), fg=self.YELLOW if expiry else self.MINT)

    def send_whatsapp(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        d = tk.Toplevel(self.root)
        d.title("📲 WhatsApp")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(560, sw - 80); h = min(620, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(480, 500)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="💬 Send via WhatsApp", font=(self.FONT, 14, "bold"),
                 fg="#25D366", bg=self.BG).pack(pady=(16,4), padx=20, anchor='w')
        pf = tk.Frame(d, bg=self.BG); pf.pack(fill='x', padx=20, pady=(8,4))
        tk.Label(pf, text="📞 Recipient:", font=(self.FONT, 10, "bold"),
                 fg=self.FG, bg=self.BG).pack(anchor='w')
        pv = tk.StringVar()
        tk.Entry(pf, textvariable=pv, font=(self.FONT, 12), bg=self.SURFACE2,
                 fg=self.FG, insertbackground=self.PRIMARY, relief='flat', bd=0
                ).pack(fill='x', ipady=7, pady=(4,0))
        txt_box = tk.Text(d, font=(self.MONO, 9), bg=self.SURFACE, fg=self.FG,
                           relief='flat', wrap='word', padx=10, pady=10,
                           bd=0, highlightthickness=0)
        txt_box.pack(fill='both', expand=True, padx=20, pady=10)
        msg = _build_whatsapp_message(self.analyzer,
                                       os.path.basename(self.file_path or "unknown"))
        txt_box.insert('1.0', msg); txt_box.config(state='disabled')
        row = tk.Frame(d, bg=self.BG); row.pack(fill='x', padx=20, pady=(0,12))
        def _send():
            phone = re.sub(r'\D', '', pv.get().strip())
            if not phone: return
            webbrowser.open(f"https://wa.me/{phone}?text=" + urllib.parse.quote(msg))
            d.destroy()
        self._make_btn(row, "📲 Send", _send, "#25D366", 16, self.FG
                      ).pack(side='left')
        self._make_btn(row, "📋 Copy",
                       lambda: (d.clipboard_clear(), d.clipboard_append(msg),
                                Toast(self.root, "Copied!", kind='success')),
                       self.SURFACE3, 12, self.FG).pack(side='left', padx=(6,0))
        self._make_btn(row, "✕ Close", d.destroy, self.SURFACE3, 12, self.FG
                      ).pack(side='right')

    def copy_summary(self):
        if not self.analyzer: return
        msg = _build_whatsapp_message(self.analyzer,
                                       os.path.basename(self.file_path or "unknown"))
        self.root.clipboard_clear(); self.root.clipboard_append(msg)
        self._set_status("✨ Copied summary", self.MINT)
        Toast(self.root, "Summary copied to clipboard", kind='success')

    def _base_name(self):
        return os.path.splitext(os.path.basename(self.file_path or "report"))[0]

    def _check_export_ready(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return False
        cc = self.column_controller
        has_rules = bool([c for c in cc.rules if cc.get(c)['action'] != 'keep'])
        has_time = bool([c for c, r in self.settings.time_column_rules.items()
                          if r.get('action', 'keep') != 'keep'])
        has = (self.analyzer.fixes or self.analyzer.red_flag_cells
               or any(v['top'] or v['bottom']
                      for v in self.analyzer.reorder_plan.values())
               or self.analyzer._any_dropoff_col() or has_rules or has_time)
        if not has:
            Toast(self.root, "No changes to apply", kind='info'); return False
        return True

    def export_fixed(self):
        if not self._check_export_ready(): return
        def _do_export():
            out = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=f"{self._base_name()}_FIXED.xlsx",
                filetypes=[("Excel", "*.xlsx")])
            if not out: return
            try: r = self.analyzer.export_fixed(out)
            except PermissionError:
                messagebox.showerror("File Locked", "Close Excel and retry."); return
            except Exception as e:
                messagebox.showerror("Export Error", str(e)); return
            messagebox.showinfo("🎉 Saved!",
                f"✨ Applied {r['applied_fixes']} fix(es)\n"
                f"🌊 Shift upgrades: {r['shift_upgrades']}\n"
                f"🕐 Time rules applied from Time Control Center\n"
                f"🚩 RED-flagged {r['red_flagged']} phone cell(s)\n"
                f"🎯 Reordered {r['reordered_rows']} row(s)\n\n{out}")
            self._set_status(f"✨ Saved: {os.path.basename(out)}", self.MINT)
            Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
            self._maybe_open_file(out)
        self._show_export_warning(_do_export, export_label="Fixed Excel")

    def export_fixed_csv(self):
        if not self._check_export_ready(): return
        def _do_export():
            out = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"{self._base_name()}_FIXED.csv",
                filetypes=[("CSV", "*.csv")])
            if not out: return
            try: r = self.analyzer.export_fixed_csv(out)
            except Exception as e:
                messagebox.showerror("Export Error", str(e)); return
            self._set_status(f"✨ Saved CSV: {os.path.basename(out)}", self.CYAN)
            Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
            self._maybe_open_file(out)
        self._show_export_warning(_do_export, export_label="Fixed CSV")

    def export_html(self):
        if not self.analyzer:
            Toast(self.root, "Run analysis first", kind='warning'); return
        out = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=f"{self._base_name()}_REPORT.html",
            filetypes=[("HTML", "*.html")])
        if not out: return
        try: self.analyzer.export_html_report(out)
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ HTML: {os.path.basename(out)}", self.VIOLET)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def export_issues_excel(self):
        if not self.analyzer: return
        out = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"{self._base_name()}_ISSUES.xlsx",
            filetypes=[("Excel", "*.xlsx")])
        if not out: return
        try: self.analyzer.export_issues_excel(out)
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ Issues XLSX: {os.path.basename(out)}", self.YELLOW)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def export_issues_csv(self):
        if not self.analyzer: return
        out = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{self._base_name()}_ISSUES.csv",
            filetypes=[("CSV", "*.csv")])
        if not out: return
        try: self.analyzer.export_issues_csv(out)
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ Issues CSV: {os.path.basename(out)}", self.LIME)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def export_issues_json(self):
        if not self.analyzer: return
        out = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{self._base_name()}_ISSUES.json",
            filetypes=[("JSON", "*.json")])
        if not out: return
        try: self.analyzer.export_issues_json(out)
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ Issues JSON: {os.path.basename(out)}", self.MINT)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def export_issues_txt(self):
        if not self.analyzer: return
        out = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{self._base_name()}_ISSUES.txt",
            filetypes=[("Text", "*.txt")])
        if not out: return
        try:
            with open(out, 'w', encoding='utf-8-sig') as f:
                f.write("🌊 CodefyERP v11.3.1 — Issues\n" + "="*60 + "\n\n")
                for ln, _ in self._filter_issues(self.analyzer.report):
                    f.write(ln + "\n")
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ Issues TXT: {os.path.basename(out)}", self.MUTED)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def export_full_txt(self):
        if not self.analyzer: return
        out = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{self._base_name()}_REPORT.txt",
            filetypes=[("Text", "*.txt")])
        if not out: return
        try:
            with open(out, 'w', encoding='utf-8-sig') as f:
                for ln, _ in self.analyzer.report:
                    f.write(ln + "\n")
        except Exception as e:
            messagebox.showerror("Export Error", str(e)); return
        self._set_status(f"✨ Report: {os.path.basename(out)}", self.BLUE)
        Toast(self.root, f"Saved {os.path.basename(out)}", kind='success')
        self._maybe_open_file(out)

    def _show_help(self):
        d = tk.Toplevel(self.root)
        d.title("📖 Quick Guide")
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        w = min(720, sw - 80); h = min(640, sh - 80)
        d.geometry(f"{w}x{h}"); d.minsize(560, 460)
        d.configure(bg=self.BG); d.transient(self.root); d.grab_set()
        tk.Label(d, text="📖 CodefyERP v11.3.1 — Quick Guide",
                 font=(self.FONT, 15, "bold"), fg=self.PRIMARY, bg=self.BG
                 ).pack(pady=(16,6), padx=20, anchor='w')
        body = tk.Frame(d, bg=self.SURFACE); body.pack(fill='both', expand=True,
                                                       padx=20, pady=(0,14))
        txt = tk.Text(body, font=(self.FONT, 10), bg=self.SURFACE, fg=self.FG,
                      relief='flat', padx=16, pady=14, wrap='word', bd=0,
                      highlightthickness=0)
        txt.pack(fill='both', expand=True)
        txt.tag_config('h', foreground=self.PRIMARY, font=(self.FONT, 12, 'bold'))
        txt.tag_config('k', foreground=self.CYAN, font=(self.FONT, 10, 'bold'))
        txt.tag_config('n', foreground=self.MINT)
        _w = lambda t, tag=None: txt.insert('end', t + "\n", tag or ())
        _w("1. Pick a file", 'h')
        _w("   File → Browse File…  (Ctrl+O)", 'k')
        _w("2. Run the analysis", 'h')
        _w("   Analyze → Analyze File  (F5)", 'k')
        _w("3. Review issues", 'h')
        _w("   Issues tab → filter by severity, click category cards.", 'n')
        _w("4. Apply fixes", 'h')
        _w("   Fix / Fix All, or open Auto-Fix Log to inspect.", 'n')
        _w("5. Configure (optional)", 'h')
        _w("   Configure → Column Control / Supplier Reorder.", 'n')
        _w("   Configure → Shift Engine / Time Control Center.", 'n')
        _w("6. Export", 'h')
        _w("   Export menu → any format. If unresolved issues remain,", 'n')
        _w("   an EXPORT GUARD window appears with a full detail list.", 'n')
        _w("")
        _w("Sidebar sections are collapsible — click any header to fold.", 'k')
        _w("Window resizes gracefully — KPI cards reflow 8→4→2 columns.", 'k')
        txt.config(state='disabled')
        self._make_btn(d, "✕ Close", d.destroy, self.VIOLET, 12, self.FG
                      ).pack(pady=(0,12))

    def _show_about(self):
        messagebox.showinfo(
            "About CodefyERP",
            "🌊 CodefyERP v11.3.1\n"
            "Sheets Analyzer · Time Control Center\n\n"
            "• Egyptian phone & Arabic name validation\n"
            "• Shift Engine with ordinal upgrade\n"
            "• Time conflict detection + offset engine\n"
            "• Auto-fix with full audit log\n"
            "• Export Guard with unresolved-issue report\n\n"
            "© 2026 · Powered by Python + Tkinter")

    def _on_close(self):
        self._running = False
        self.root.destroy()

# ═══════════════════════════════════════════════════════════════════════════════
#                                   MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()