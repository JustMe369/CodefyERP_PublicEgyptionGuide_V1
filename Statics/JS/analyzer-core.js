// Enhanced Excel Data Validator for CodefyERP with Egyptian Business Logic

// Define column constants for Egyptian ERP system
const COL_DRIVER_NAME = 'driver_name';
const COL_DRIVER_PHONE = 'driver_phone';
const COL_SUPPLIER_NAME = 'supplier_name';
const COL_SUPPLIER_PHONE = 'supplier_phone';
const COL_PLATE = 'plate_number';
const COL_SHIFT = 'shift';
const COL_SCHEDULE = 'schedule';
const COL_ROUTE = 'route';
const COL_PICKUP_ARR = 'pickup_arrival';
const COL_PICKUP_DEP = 'pickup_departure';
const COL_DROPOFF_ARR = 'dropoff_arrival';
const COL_DROPOFF_TIME = 'dropoff_time';
const COL_WORKING_DAYS = 'working_days';
const COL_DIRECTION = 'direction';
const COL_EMP_TYPE = 'employee_type';
const COL_START_DATE = 'start_date';
const COL_END_DATE = 'end_date';
const COL_SERVICE_TYPE = 'service_type';
const COL_CAPACITY = 'capacity';
const COL_VEHICLE_TYPE = 'vehicle_type';
const COL_DRIVER_LICENSE = 'driver_license';
const COL_INSURANCE_EXPIRY = 'insurance_expiry';
const COL_MAINTENANCE_DATE = 'maintenance_date';
const COL_FUEL_TYPE = 'fuel_type';
const COL_VEHICLE_STATUS = 'vehicle_status';
const COL_COMPANY_NAME = 'company_name';
const COL_COMPANY_PHONE = 'company_phone';
const COL_COMPANY_ADDRESS = 'company_address';
const COL_COMPANY_EMAIL = 'company_email';
const COL_CONTACT_PERSON = 'contact_person';
const COL_TAX_ID = 'tax_id';
const COL_BANK_ACCOUNT = 'bank_account';
const COL_CREDIT_LIMIT = 'credit_limit';
const COL_PAYMENT_TERMS = 'payment_terms';
const COL_SUPPLIER_CATEGORY = 'supplier_category';
const COL_DELIVERY_TIME = 'delivery_time';
const COL_MIN_ORDER_VALUE = 'min_order_value';
const COL_DISCOUNT_RATE = 'discount_rate';

// ERP column specifications with Egyptian business context
const ERP_COLUMN_SPEC = {
    [COL_DRIVER_NAME]: {'type': 'text', 'required': true},
    [COL_DRIVER_PHONE]: {'type': 'phone', 'required': true},
    [COL_SUPPLIER_NAME]: {'type': 'text', 'required': true},
    [COL_SUPPLIER_PHONE]: {'type': 'phone'},
    [COL_PLATE]: {'type': 'text', 'required': true},
    [COL_SHIFT]: {'type': 'text', 'required': true},
    [COL_SCHEDULE]: {'type': 'text', 'required': true},
    [COL_ROUTE]: {'type': 'text', 'required': true},
    [COL_PICKUP_ARR]: {'type': 'time'},
    [COL_PICKUP_DEP]: {'type': 'time'},
    [COL_DROPOFF_ARR]: {'type': 'time'},
    [COL_DROPOFF_TIME]: {'type': 'time'},
    [COL_WORKING_DAYS]: {'type': 'enum', 'enum': ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']},
    [COL_DIRECTION]: {'type': 'enum', 'enum': ['north', 'south', 'east', 'west', 'round_trip']},
    [COL_START_DATE]: {'type': 'date'},
    [COL_END_DATE]: {'type': 'date'},
    [COL_SERVICE_TYPE]: {'type': 'enum', 'enum': ['daily', 'weekly', 'monthly', 'event']},
    [COL_CAPACITY]: {'type': 'number'},
    [COL_VEHICLE_TYPE]: {'type': 'enum', 'enum': ['bus', 'van', 'truck', 'car']},
    [COL_DRIVER_LICENSE]: {'type': 'text'},
    [COL_INSURANCE_EXPIRY]: {'type': 'date'},
    [COL_MAINTENANCE_DATE]: {'type': 'date'},
    [COL_FUEL_TYPE]: {'type': 'enum', 'enum': ['gasoline', 'diesel', 'electric', 'hybrid']},
    [COL_VEHICLE_STATUS]: {'type': 'enum', 'enum': ['active', 'inactive', 'maintenance', 'decommissioned']},
    // Supplier-specific columns
    [COL_COMPANY_NAME]: {'type': 'text', 'required': true},
    [COL_COMPANY_PHONE]: {'type': 'phone', 'required': true},
    [COL_COMPANY_ADDRESS]: {'type': 'text', 'required': true},
    [COL_COMPANY_EMAIL]: {'type': 'email'},
    [COL_CONTACT_PERSON]: {'type': 'text', 'required': true},
    [COL_TAX_ID]: {'type': 'text'},  // Egyptian Tax ID format
    [COL_BANK_ACCOUNT]: {'type': 'text'},  // Bank account number
    [COL_CREDIT_LIMIT]: {'type': 'number'},
    [COL_PAYMENT_TERMS]: {'type': 'enum', 'enum': ['cash', 'credit', 'net_7', 'net_15', 'net_30', 'net_60']},
    [COL_SUPPLIER_CATEGORY]: {'type': 'enum', 'enum': ['raw_materials', 'services', 'equipment', 'maintenance', 'utilities', 'transportation']},
    [COL_DELIVERY_TIME]: {'type': 'number'},  // In days
    [COL_MIN_ORDER_VALUE]: {'type': 'number'},
    [COL_DISCOUNT_RATE]: {'type': 'number'},  // Percentage
};

// Day aliases for working days
const DAY_ALIAS_LOOKUP = {
    'sat': 'Saturday', 'saturday': 'Saturday', 'السبت': 'Saturday',
    'sun': 'Sunday', 'sunday': 'Sunday', 'الاحد': 'Sunday',
    'mon': 'Monday', 'monday': 'Monday', 'الاثنين': 'Monday',
    'tue': 'Tuesday', 'tuesday': 'Tuesday', 'الثلاثاء': 'Tuesday',
    'wed': 'Wednesday', 'wednesday': 'Wednesday', 'الاربعاء': 'Wednesday',
    'thu': 'Thursday', 'thursday': 'Thursday', 'الخميس': 'Thursday',
    'fri': 'Friday', 'friday': 'Friday', 'الجمعة': 'Friday'
};

const DAY_CANONICAL_ORDER = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

// Working days separators
const WORKING_DAYS_SEPARATORS = /[,\s\n\t;/\\|]+|و|and/gi;

// Shift patterns and ordinals
const SHIFT_BASE_PATTERNS = {
    'Morning': ['morning', 'صباحي', 'am', 'early', 'فجر'],
    'Evening': ['evening', 'مسائي', 'pm', 'late', 'مغرب'],
    'Night': ['night', 'ليلي', 'night', ' полночной'],
    'Day': ['day', 'نهار', 'normal', ' يومي'],
    'Special': ['special', 'خاصة', 'extra', ' مميز'],
    'Holiday': ['holiday', 'عطلة', 'weekend', ' عطلة'],
    'Weekend': ['weekend', 'نهاية الاسبوع', 'off', ' اسبوعية']
};

const SHIFT_ORDINALS = [
    [['first', 'primary', 'main', 'الاول', 'الرئيسي'], 'Primary', 'Pri'],
    [['second', 'secondary', 'الثاني', 'الفرعي'], 'Secondary', 'Sec'],
    [['third', 'tertiary', 'الثالث'], 'Tertiary', 'Ter'],
    [['round', 'both', '往返', 'both ways', '往返'], 'Round Trip', 'RT'],
    [['express', 'fast', 'سريع', ' express'], 'Express', 'Exp'],
    [['regular', 'normal', 'عادي', ' standard'], 'Regular', 'Reg'],
    [['vip', 'premium', ' vip', ' مميز'], 'VIP', 'VIP']
];

// Egyptian phone number patterns
const EGYPTIAN_PHONE_PATTERNS = [
    /^01[0-9]{9}$/,  // Egyptian mobile numbers
    /^\+201[0-9]{9}$/,  // International format
    /^201[0-9]{9}$/  // Without +
];

// Egyptian tax ID format (14 digits)
const EGYPTIAN_TAX_ID_PATTERN = /^\d{14}$/;

// Email validation pattern
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

function toStr(value) {
    /** Convert any value to string, handling null and undefined. */
    if (value === null || value === undefined) {
        return '';
    }
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        return String(value).toString().trim();
    }
    return String(value).trim();
}

function isArabic(text) {
    /** Check if text contains Arabic characters. */
    if (!text) {
        return false;
    }
    return /[\u0600-\u06FF]/.test(String(text));
}

function normalizeName(name) {
    /** Normalize names by removing extra spaces and standardizing format. */
    if (!name) {
        return '';
    }
    // Remove extra whitespace and standardize
    const normalized = String(name).replace(/\s+/g, ' ').trim();
    return normalized;
}

function isValidEgyptianPhone(phone) {
    /** Validate Egyptian phone number format. */
    if (!phone) {
        return false;
    }
    let phoneStr = String(phone).replace(/[-\s\(\)]/g, '');
    
    for (const pattern of EGYPTIAN_PHONE_PATTERNS) {
        if (pattern.test(phoneStr)) {
            return true;
        }
    }
    return false;
}

function normalizePhone(phone) {
    /** Normalize phone number to Egyptian standard format. */
    if (!phone) {
        return '';
    }
    
    let phoneStr = String(phone);
    let digits;
    if (phoneStr.startsWith('+')) {
        digits = '+' + phoneStr.substring(1).replace(/\D/g, '');
    } else {
        digits = phoneStr.replace(/\D/g, '');
    }
    
    // Convert to Egyptian format if applicable
    if (digits.length === 11 && digits.startsWith('01')) {
        return digits;  // Already in Egyptian format
    } else if (digits.length === 12 && digits.startsWith('201')) {
        return '0' + digits.substring(2);  // Convert from international to local
    } else if (digits.length === 13 && digits.startsWith('+201')) {
        return '0' + digits.substring(3);  // Convert from +international to local
    }
    
    return phoneStr;  // Return original if can't normalize
}

function isValidDate(dateStr) {
    /** Validate date format and convert to standard format. */
    if (!dateStr) {
        return false;
    }
    
    dateStr = toStr(dateStr);
    
    // Try different date formats
    const formats = [
        '%Y-%m-%d',      // Standard: 2023-01-15
        '%d/%m/%Y',      // Egyptian: 15/01/2023
        '%m/%d/%Y',      // US: 01/15/2023
        '%d-%m-%Y',      // Egyptian: 15-01-2023
        '%m-%d-%Y',      // US: 01-15-2023
        '%d.%m.%Y',      // European: 15.01.2023
        '%Y/%m/%d',      // Alternative: 2023/01/15
    ];
    
    for (const fmt of formats) {
        try {
            const parsedDate = parseDateWithFormat(dateStr, fmt);
            if (parsedDate) {
                return true;
            }
        } catch (e) {
            continue;
        }
    }
    
    return false;
}

function normalizeDate(dateStr) {
    /** Normalize date to standard format YYYY-MM-DD. */
    if (!dateStr) {
        return '';
    }
    
    dateStr = toStr(dateStr);
    
    // Try different date formats
    const formats = [
        '%Y-%m-%d',      // Standard: 2023-01-15
        '%d/%m/%Y',      // Egyptian: 15/01/2023
        '%m/%d/%Y',      // US: 01/15/2023
        '%d-%m-%Y',      // Egyptian: 15-01-2023
        '%m-%d-%Y',      // US: 01-15-2023
        '%d.%m.%Y',      // European: 15.01.2023
        '%Y/%m/%d',      // Alternative: 2023/01/15
    ];
    
    for (const fmt of formats) {
        try {
            const parsedDate = parseDateWithFormat(dateStr, fmt);
            if (parsedDate) {
                return parsedDate.toISOString().split('T')[0]; // Return YYYY-MM-DD format
            }
        } catch (e) {
            continue;
        }
    }
    
    return dateStr;  // Return original if can't parse
}

function parseDateWithFormat(dateStr, format) {
    // Simple date parser for common formats
    const dateRegex = /(\d{4})-(\d{2})-(\d{2})/;
    const egyptianRegex = /(\d{1,2})\/(\d{1,2})\/(\d{4})/;
    const egyptianDashRegex = /(\d{1,2})-(\d{1,2})-(\d{4})/;
    
    if (format === '%Y-%m-%d' && dateRegex.test(dateStr)) {
        const [_, year, month, day] = dateRegex.exec(dateStr);
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    } else if (format === '%d/%m/%Y' && egyptianRegex.test(dateStr)) {
        const [_, day, month, year] = egyptianRegex.exec(dateStr);
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    } else if (format === '%m/%d/%Y') {
        // US format
        const [_, month, day, year] = dateStr.split(/[\/\-]/).map(Number);
        return new Date(year, month - 1, day);
    } else if (format === '%d-%m-%Y' && egyptianDashRegex.test(dateStr)) {
        const [_, day, month, year] = egyptianDashRegex.exec(dateStr);
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    } else if (format === '%m-%d-%Y') {
        // US format with dashes
        const [_, month, day, year] = dateStr.split(/[\/\-]/).map(Number);
        return new Date(year, month - 1, day);
    } else if (format === '%d.%m.%Y') {
        const [day, month, year] = dateStr.split('.').map(Number);
        return new Date(year, month - 1, day);
    } else if (format === '%Y/%m/%d') {
        const [year, month, day] = dateStr.split(/[\/\-]/).map(Number);
        return new Date(year, month - 1, day);
    }
    
    return null;
}

function isValidTime(timeStr) {
    /** Validate time format. */
    if (!timeStr) {
        return false;
    }
    
    timeStr = toStr(timeStr);
    
    // Try different time formats
    const formats = [
        '%H:%M',         // 24-hour: 14:30
        '%H:%M:%S',      // 24-hour with seconds: 14:30:00
        '%I:%M %p',      // 12-hour: 02:30 PM
        '%I:%M%p',       // 12-hour: 02:30PM
    ];
    
    for (const fmt of formats) {
        try {
            const parsedTime = parseTimeWithFormat(timeStr, fmt);
            if (parsedTime) {
                return true;
            }
        } catch (e) {
            continue;
        }
    }
    
    return false;
}

function parseTimeWithFormat(timeStr, format) {
    // Simple parser for time formats
    const timeRegex = /^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)?$/;
    const match = timeStr.trim().match(timeRegex);
    
    if (!match) return null;
    
    let [_, hours, minutes, seconds, period] = match;
    hours = parseInt(hours);
    minutes = parseInt(minutes);
    seconds = seconds ? parseInt(seconds) : 0;
    
    if (period && (period.toLowerCase() === 'pm' || period.toLowerCase() === 'am')) {
        if (period.toLowerCase() === 'pm' && hours !== 12) {
            hours += 12;
        } else if (period.toLowerCase() === 'am' && hours === 12) {
            hours = 0;
        }
    }
    
    if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59 || seconds < 0 || seconds > 59) {
        return null;
    }
    
    return { hours, minutes, seconds };
}

function normalizeWorkingDays(workingDaysStr) {
    /** Normalize working days string to canonical format. */
    if (!workingDaysStr) {
        return '';
    }
    
    // Split by various separators
    const days = String(workingDaysStr).split(WORKING_DAYS_SEPARATORS);
    const normalizedDays = [];
    
    for (const day of days) {
        const dayClean = day.trim().toLowerCase();
        if (DAY_ALIAS_LOOKUP[dayClean]) {
            const canonicalDay = DAY_ALIAS_LOOKUP[dayClean];
            if (!normalizedDays.includes(canonicalDay)) {
                normalizedDays.push(canonicalDay);
            }
        } else if (DAY_CANONICAL_ORDER.includes(dayClean.charAt(0).toUpperCase() + dayClean.slice(1))) {
            const canonicalDay = dayClean.charAt(0).toUpperCase() + dayClean.slice(1);
            if (!normalizedDays.includes(canonicalDay)) {
                normalizedDays.push(canonicalDay);
            }
        }
    }
    
    // Sort days according to Egyptian work week (Saturday is first)
    const sortedDays = [];
    for (const day of DAY_CANONICAL_ORDER) {
        if (normalizedDays.includes(day)) {
            sortedDays.push(day);
        }
    }
    
    return sortedDays.join(', ');
}

function inferShiftFromSchedule(schedule) {
    /** Infer shift type from schedule description. */
    if (!schedule) {
        return '';
    }
    
    const scheduleLower = toStr(schedule).toLowerCase();
    
    // Look for shift indicators
    for (const [shiftType, keywords] of Object.entries(SHIFT_BASE_PATTERNS)) {
        for (const keyword of keywords) {
            if (scheduleLower.includes(keyword)) {
                return shiftType;
            }
        }
    }
    
    // Try to infer from time ranges in schedule
    const timeMatch = scheduleLower.match(/(\d{1,2}):(\d{2})/);
    if (timeMatch) {
        const hour = parseInt(timeMatch[1]);
        if (5 <= hour && hour <= 11) {
            return 'Morning';
        } else if (12 <= hour && hour <= 17) {
            return 'Afternoon';
        } else if (18 <= hour && hour <= 22) {
            return 'Evening';
        } else {
            return 'Night';
        }
    }
    
    return 'Day';
}

function analyzeShiftPatterns(shiftStr) {
    /** Analyze shift string for base type and ordinals. */
    if (!shiftStr) {
        return {'base': '', 'ordinals': []};
    }
    
    const shiftLower = toStr(shiftStr).toLowerCase();
    const result = {'base': '', 'ordinals': []};
    
    // Identify base shift type
    for (const [shiftType, keywords] of Object.entries(SHIFT_BASE_PATTERNS)) {
        for (const keyword of keywords) {
            if (shiftLower.includes(keyword)) {
                result['base'] = shiftType;
                break;
            }
        }
        if (result['base']) {
            break;
        }
    }
    
    // Identify ordinals
    for (const [ordinalGroup, fullName, abbr] of SHIFT_ORDINALS) {
        for (const keyword of ordinalGroup) {
            if (shiftLower.includes(keyword)) {
                result['ordinals'].push({'full': fullName, 'abbr': abbr});
                break;
            }
        }
    }
    
    return result;
}

function isValidTaxId(taxId) {
    /** Validate Egyptian tax ID format (14 digits). */
    if (!taxId) return false;
    taxId = toStr(taxId).replace(/[\s-]/g, '');
    return EGYPTIAN_TAX_ID_PATTERN.test(taxId);
}

function isValidEmail(email) {
    /** Validate email format. */
    if (!email) return false;
    email = toStr(email).trim().toLowerCase();
    return EMAIL_PATTERN.test(email);
}

/**
 * Advanced Shift Engine
 */
class ShiftEngine {
    constructor(settings = {}) {
        this.enabled = settings.enabled !== false; // Default to true
        this.settings = settings;
        this.basePatterns = { ...SHIFT_BASE_PATTERNS };
        this.ordinals = [...SHIFT_ORDINALS];
    }
    
    _detectBase(shiftValue) {
        const s = toStr(shiftValue);
        if (!s) return null;
        
        const sNorm = normalizeName(s).toLowerCase();
        
        // Check against all base patterns
        for (const [baseDisplay, triggers] of Object.entries(this.basePatterns)) {
            for (const trigger of triggers) {
                if (sNorm.includes(trigger.toLowerCase())) {
                    return baseDisplay;
                }
            }
        }
        
        return null;
    }

    _detectOrdinal(scheduleValue) {
        const s = toStr(scheduleValue);
        if (!s) return null;
        
        const firstWord = s.split(' ')[0] || s;
        const fwNorm = normalizeName(firstWord).toLowerCase();
        
        for (const [keywords, canonical, short] of this.ordinals) {
            for (const kw of keywords) {
                if (fwNorm === normalizeName(kw).toLowerCase()) {
                    return [canonical, short];
                }
            }
        }
        
        // If exact match didn't work, try partial match
        for (const [keywords, canonical, short] of this.ordinals) {
            for (const kw of keywords) {
                if (normalizeName(kw).toLowerCase().includes(fwNorm) || 
                    fwNorm.includes(normalizeName(kw).toLowerCase())) {
                    return [canonical, short];
                }
            }
        }
        
        return null;
    }

    _normalizeScheduleFirstWord(scheduleValue) {
        const s = toStr(scheduleValue);
        if (!s) return null;
        
        const parts = s.split(' ');
        if (parts.length === 0) return null;
        
        const first = parts[0];
        const rest = parts.slice(1).join(' ');
        
        for (const [keywords, canonical, _] of this.ordinals) {
            for (const kw of keywords) {
                if (normalizeName(first).toLowerCase() === normalizeName(kw).toLowerCase()) {
                    if (toStr(first).toLowerCase() === canonical.toLowerCase()) return null;
                    return canonical + (rest ? ' ' + rest : '');
                }
            }
        }
        
        return null;
    }
    
    process(shiftValue, scheduleValue) {
        if (!this.enabled) return null;
        
        const base = this._detectBase(shiftValue);
        const ordinal = this._detectOrdinal(scheduleValue) ? this._detectOrdinal(scheduleValue) : null;
        
        let newShift = null;
        let newSchedule = null;
        const reasons = [];
        
        if (base && ordinal) {
            const [canonical, short] = ordinal;
            newShift = `${base} - ${short}`;
            reasons.push(`shift '${base}' + ordinal '${short}' → '${newShift}'`);
        }
        
        const normalizedSchedule = this._normalizeScheduleFirstWord(scheduleValue);
        if (normalizedSchedule && normalizedSchedule !== toStr(scheduleValue)) {
            newSchedule = normalizedSchedule;
            reasons.push('schedule first-word normalized');
        }
        
        if (!newShift && !newSchedule) return null;
        
        return {
            'new_shift': newShift, 
            'new_schedule': newSchedule,
            'reason': reasons.join(' · '), 
            'base': base,
            'ordinal': ordinal ? ordinal[0] : null
        };
    }
}

/**
 * Time Control System
 */
class TimeControlSystem {
    constructor(settings = {}) {
        this.enabled = settings.enabled !== false;
        this.offset = settings.offset || 30; // Default 30 minute offset
        this.target = settings.target || COL_DROPOFF_TIME; // Default target column
        this.mode = settings.mode || 'normalize'; // normalize, flag_only, etc.
        this.settings = settings;
    }
    
    detectConflicts(records, pickupColumn = COL_PICKUP_DEP, dropoffColumn = COL_DROPOFF_TIME) {
        if (!this.enabled) return [];
        
        const conflicts = [];
        
        for (let i = 0; i < records.length; i++) {
            const record = records[i];
            const pickup = record[pickupColumn];
            const dropoff = record[dropoffColumn];
            
            if (pickup && dropoff) {
                // Parse times
                const pickupParsed = parseTimeWithFormat(toStr(pickup), '%H:%M');
                const dropoffParsed = parseTimeWithFormat(toStr(dropoff), '%H:%M');
                
                if (pickupParsed && dropoffParsed) {
                    // Convert to minutes from midnight for comparison
                    const pickupMinutes = pickupParsed.hours * 60 + pickupParsed.minutes;
                    const dropoffMinutes = dropoffParsed.hours * 60 + dropoffParsed.minutes;
                    
                    // Check if times are equal or very close (potential conflict)
                    if (Math.abs(pickupMinutes - dropoffMinutes) <= 1) { // Within 1 minute tolerance
                        const suggested = this._calculateSuggestedTime(dropoffMinutes);
                        
                        conflicts.push({
                            'row_index': i,
                            'pickup_col': pickupColumn,
                            'dropoff_col': dropoffColumn,
                            'pickup': pickup,
                            'dropoff': dropoff,
                            'suggested_dropoff': suggested,
                            'offset': this.offset
                        });
                    }
                }
            }
        }
        
        return conflicts;
    }
    
    _calculateSuggestedTime(dropoffMinutes) {
        // Add offset to the dropoff time
        let newMinutes = dropoffMinutes + this.offset;
        
        // Handle day overflow
        if (newMinutes >= 24 * 60) {
            newMinutes = newMinutes % (24 * 60);
        }
        
        const newHours = Math.floor(newMinutes / 60);
        const newMins = newMinutes % 60;
        
        return `${String(newHours).padStart(2, '0')}:${String(newMins).padStart(2, '0')}`;
    }
}

/**
 * Main Analyzer Class
 */
class CodefyAnalyzer {
    constructor(settings = {}) {
        this.issues = {
            'invalid_phones': [],
            'date_format_issues': [],
            'enum_violations': [],
            'missing_data': [],
            'duplicate_phones': [],
            'time_conflicts': [],
            'shift_conflicts': [],
            'supplier_issues': [],
            'capacity_issues': [],
            'insurance_expiry_issues': [],
            'expiry_alerts': [],      // For upcoming expiries
            'shift_upgrades': [],     // For shift improvements
            'tax_id_issues': [],      // For supplier tax ID issues
            'email_issues': [],       // For email validation issues
            'vehicle_type_issues': [], // For vehicle type issues
            'schedule_conflicts': [],  // For schedule conflicts
            'invalid_plates': [],      // For invalid plate numbers
            'duplicate_plates': []     // For duplicate plate numbers
        };
        
        this.fixes = [];
        this.analysisSummary = {};
        
        // Initialize engines
        this.shiftEngine = new ShiftEngine(settings.shiftEngine);
        this.timeControlSystem = new TimeControlSystem(settings.timeControl);
    }
    
    validateCell(value, colName, sheetName, row_num) {
        const issues = [];
        const spec = ERP_COLUMN_SPEC[colName] || {};
        
        // Check for required fields
        if (spec.required && (value === null || toStr(value) === '')) {
            issues.push({
                'sheet': sheetName,
                'row': row_num,
                'col': colName,
                'value': toStr(value),
                'issue': `Required field ${colName} is missing`,
                'severity': 'critical'
            });
            return issues; // Don't continue with other validations if required field is missing
        }
        
        // Skip validation if value is empty and not required
        if (value === null || toStr(value) === '') {
            return issues;
        }
        
        // Validate based on type
        const colType = spec.type || 'text';
        
        if (colType === 'phone') {
            if (!isValidEgyptianPhone(value)) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': 'Invalid Egyptian phone number format',
                    'severity': 'critical'
                });
            }
        } else if (colType === 'date') {
            if (!isValidDate(value)) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': 'Invalid date format (expected YYYY-MM-DD)',
                    'severity': 'warning'
                });
            }
        } else if (colType === 'time') {
            if (!isValidTime(value)) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': 'Invalid time format (expected HH:MM)',
                    'severity': 'warning'
                });
            }
        } else if (colType === 'enum') {
            const allowedValues = spec.enum || [];
            if (!allowedValues.some(v => v.toLowerCase() === toStr(value).toLowerCase())) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': `Invalid value. Expected one of: ${allowedValues.join(', ')}`,
                    'severity': 'warning'
                });
            }
        } else if (colType === 'number') {
            if (isNaN(parseFloat(toStr(value)))) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': 'Expected a numeric value',
                    'severity': 'critical'
                });
            }
        } else if (colType === 'email') {
            if (!isValidEmail(value)) {
                issues.push({
                    'sheet': sheetName,
                    'row': row_num,
                    'col': colName,
                    'value': toStr(value),
                    'issue': 'Invalid email format',
                    'severity': 'warning'
                });
            }
        }
        
        return issues;
    }
    
    normalizeCellValue(value, colName) {
        /** Normalize a cell value and return the normalized value with a reason. */
        if (value === null || toStr(value) === '') {
            return [value, 'no_normalization_needed'];
        }
        
        const spec = ERP_COLUMN_SPEC[colName] || {};
        const colType = spec.type || 'text';
        
        if (colType === 'phone') {
            const normalized = normalizePhone(value);
            if (normalized !== toStr(value)) {
                return [normalized, 'normalized_to_standard_format'];
            }
        } else if (colType === 'date') {
            const normalized = normalizeDate(value);
            if (normalized !== toStr(value)) {
                return [normalized, 'normalized_to_standard_date_format'];
            }
        } else if (colType === 'text') {
            if (colName === COL_WORKING_DAYS) {
                const normalized = normalizeWorkingDays(value);
                if (normalized !== toStr(value)) {
                    return [normalized, 'normalized_working_days_format'];
                }
            }
        } else if (colName === COL_SHIFT) {
            // Analyze and potentially upgrade shift descriptions
            const shiftAnalysis = analyzeShiftPatterns(toStr(value));
            if (shiftAnalysis.ordinals.length > 0) {  // If there are ordinals to improve
                // Create improved shift name
                const baseShift = shiftAnalysis.base || 'Day';
                const ordinals = shiftAnalysis.ordinals.map(o => o.abbr);
                const improvedName = ordinals.length > 0 ? `${baseShift} (${ordinals.join('-')})` : baseShift;
                if (improvedName.toLowerCase() !== toStr(value).toLowerCase()) {
                    return [improvedName, 'improved_shift_description_with_ordinals'];
                }
            }
        }
        
        return [value, 'no_normalization_needed'];
    }
    
    _findDuplicates(data, colName, sheetName) {
        /** Find duplicates in a specific column. */
        if (!data || data.length === 0) return;
        
        const values = data.map(row => row[colName]).filter(val => val !== null && toStr(val) !== '');
        const seen = new Set();
        const duplicates = new Set();
        
        for (const value of values) {
            if (seen.has(toStr(value))) {
                duplicates.add(toStr(value));
            } else {
                seen.add(toStr(value));
            }
        }
        
        // Find rows with duplicate values
        for (let i = 0; i < data.length; i++) {
            const row = data[i];
            if (duplicates.has(toStr(row[colName]))) {
                this.issues['duplicate_phones'].push({
                    'sheet': sheetName,
                    'row': i + 2,  // +2 because of header row and 0-indexing
                    'col': colName,
                    'value': toStr(row[colName]),
                    'issue': `Duplicate value found in ${colName}`
                });
            }
        }
    }
    
    _processShiftUpgrades(data, sheetName) {
        /** Process shift upgrades using the shift engine. */
        for (let i = 0; i < data.length; i++) {
            const row = data[i];
            if (row[COL_SHIFT] && row[COL_SCHEDULE]) {
                const result = this.shiftEngine.process(row[COL_SHIFT], row[COL_SCHEDULE]);
                
                if (result) {
                    if (result.new_shift) {
                        this.fixes.push({
                            'sheet': sheetName,
                            'row': i + 2, // +2 because of header row and 0-indexing
                            'col': COL_SHIFT,
                            'old': row[COL_SHIFT],
                            'new': result.new_shift,
                            'reason': `Shift Engine — ${result.reason}`
                        });
                    }
                    
                    if (result.new_schedule) {
                        this.fixes.push({
                            'sheet': sheetName,
                            'row': i + 2,
                            'col': COL_SCHEDULE,
                            'old': row[COL_SCHEDULE],
                            'new': result.new_schedule,
                            'reason': 'Shift Engine — normalized schedule_name'
                        });
                    }
                    
                    this.issues['shift_upgrades'].push({
                        'sheet': sheetName,
                        'row': i + 2,
                        'old_shift': toStr(row[COL_SHIFT]),
                        'new_shift': result.new_shift || toStr(row[COL_SHIFT]),
                        'old_schedule': toStr(row[COL_SCHEDULE]),
                        'new_schedule': result.new_schedule || toStr(row[COL_SCHEDULE]),
                        'reason': result.reason
                    });
                }
            }
        }
    }
    
    analyze(workbook) {
        try {
            let totalRows = 0;
            
            for (const [sheetName, data] of Object.entries(workbook)) {
                if (!Array.isArray(data) || data.length === 0) {
                    continue;
                }
                
                totalRows += data.length;
                
                // Validate each cell in the data
                for (let i = 0; i < data.length; i++) {
                    const row = data[i];
                    const rowNum = i + 2; // +2 because of header row and 0-indexing
                    
                    for (const [colName, value] of Object.entries(row)) {
                        if (ERP_COLUMN_SPEC[colName]) { // Only validate known columns
                            const cellIssues = this.validateCell(value, colName, sheetName, rowNum);
                            for (const issue of cellIssues) {
                                // Map severity to the appropriate issue category
                                const issueType = `${issue.severity}_issues`;
                                if (this.issues[issueType]) {
                                    this.issues[issueType].push(issue);
                                } else {
                                    this.issues['enum_violations'].push(issue); // Default to enum violations
                                }
                            }
                        }
                    }
                }
                
                // Check for duplicate phones
                this._findDuplicates(data, COL_DRIVER_PHONE, sheetName);
                this._findDuplicates(data, COL_SUPPLIER_PHONE, sheetName);
                
                // Run shift engine if enabled
                if (this.shiftEngine.enabled) {
                    this._processShiftUpgrades(data, sheetName);
                }
                
                // Run time control system if enabled
                if (this.timeControlSystem.enabled) {
                    const timeConflicts = this.timeControlSystem.detectConflicts(data);
                    for (const conflict of timeConflicts) {
                        this.issues.time_conflicts.push({
                            'sheet': sheetName,
                            'row': conflict.row_index + 2,
                            'col': `${conflict.pickup_col} vs ${conflict.dropoff_col}`,
                            'value': `${conflict.pickup} vs ${conflict.dropoff}`,
                            'issue': `Time conflict: ${conflict.pickup} == ${conflict.dropoff}, suggested: ${conflict.suggested_dropoff}`,
                            'severity': 'warning'
                        });
                    }
                }
            }
            
            // Generate analysis summary
            this.analysisSummary = {
                'total_sheets': Object.keys(workbook).length,
                'total_rows': totalRows,
                'quality_score': this._computeScore(),
                'issues': {
                    'critical': this.issues.invalid_phones.length + 
                               this.issues.missing_data.length + 
                               this.issues.capacity_issues.length + 
                               this.issues.insurance_expiry_issues.length,
                    'warning': this.issues.date_format_issues.length + 
                              this.issues.enum_violations.length + 
                              this.issues.time_conflicts.length + 
                              this.issues.shift_conflicts.length + 
                              this.issues.expiry_alerts.length + 
                              this.issues.supplier_issues.length,
                    'info': this.issues.shift_upgrades.length + 
                           this.issues.duplicate_phones.length
                },
                'breakdown': {
                    'invalid_phones': this.issues.invalid_phones.length,
                    'date_format_issues': this.issues.date_format_issues.length,
                    'enum_violations': this.issues.enum_violations.length,
                    'missing_data': this.issues.missing_data.length,
                    'duplicate_phones': this.issues.duplicate_phones.length,
                    'time_conflicts': this.issues.time_conflicts.length,
                    'shift_conflicts': this.issues.shift_conflicts.length,
                    'supplier_issues': this.issues.supplier_issues.length,
                    'capacity_issues': this.issues.capacity_issues.length,
                    'insurance_expiry_issues': this.issues.insurance_expiry_issues.length,
                    'expiry_alerts': this.issues.expiry_alerts.length,
                    'shift_upgrades': this.issues.shift_upgrades.length
                }
            };
            
            return true;
        } catch (e) {
            console.error('Error analyzing workbook:', e);
            return false;
        }
    }
    
    _allIssues() {
        const out = [];
        
        // Invalid phones
        for (const ip of this.issues.invalid_phones) {
            out.push({
                'severity': 'critical',
                'category': 'Invalid Phone',
                'sheet': ip.sheet,
                'row': ip.row,
                'column': ip.col,
                'value': String(ip.value),
                'message': ip.issue
            });
        }
        
        // Date format issues
        for (const dfi of this.issues.date_format_issues) {
            out.push({
                'severity': 'warning',
                'category': 'Date Format',
                'sheet': dfi.sheet,
                'row': dfi.row,
                'column': dfi.col,
                'value': String(dfi.value),
                'message': dfi.issue
            });
        }
        
        // Enum violations
        for (const ev of this.issues.enum_violations) {
            out.push({
                'severity': 'warning',
                'category': 'Enum Violation',
                'sheet': ev.sheet,
                'row': ev.row,
                'column': ev.col,
                'value': String(ev.value),
                'message': ev.issue
            });
        }
        
        // Missing data
        for (const md of this.issues.missing_data) {
            out.push({
                'severity': 'critical',
                'category': 'Missing Data',
                'sheet': md.sheet,
                'row': md.row,
                'column': md.col,
                'value': String(md.value),
                'message': md.issue
            });
        }
        
        // Duplicate phones
        for (const dp of this.issues.duplicate_phones) {
            out.push({
                'severity': 'warning',
                'category': 'Duplicate Value',
                'sheet': dp.sheet,
                'row': dp.row,
                'column': dp.col,
                'value': String(dp.value),
                'message': dp.issue
            });
        }
        
        // Time conflicts
        for (const tc of this.issues.time_conflicts) {
            out.push({
                'severity': 'warning',
                'category': 'Time Conflict',
                'sheet': tc.sheet,
                'row': tc.row,
                'column': tc.col,
                'value': String(tc.value),
                'message': tc.issue
            });
        }
        
        // Shift conflicts
        for (const sc of this.issues.shift_conflicts) {
            out.push({
                'severity': 'warning',
                'category': 'Shift Conflict',
                'sheet': sc.sheet,
                'row': sc.row,
                'column': sc.col,
                'value': String(sc.value),
                'message': sc.issue
            });
        }
        
        // Supplier issues
        for (const si of this.issues.supplier_issues) {
            out.push({
                'severity': si.severity || 'warning',
                'category': 'Supplier Issue',
                'sheet': si.sheet,
                'row': si.row,
                'column': si.col,
                'value': String(si.value),
                'message': si.issue
            });
        }
        
        // Capacity issues
        for (const ci of this.issues.capacity_issues) {
            out.push({
                'severity': 'critical',
                'category': 'Capacity Issue',
                'sheet': ci.sheet,
                'row': ci.row,
                'column': ci.col,
                'value': String(ci.value),
                'message': ci.issue
            });
        }
        
        // Insurance expiry issues
        for (const ie of this.issues.insurance_expiry_issues) {
            out.push({
                'severity': 'critical',
                'category': 'Insurance Expired',
                'sheet': ie.sheet,
                'row': ie.row,
                'column': ie.col,
                'value': ie.value,
                'message': `Expired ${ie.days_overdue} days ago`
            });
        }
        
        // Expiry alerts
        for (const ea of this.issues.expiry_alerts) {
            out.push({
                'severity': 'warning',
                'category': 'Expiry Alert',
                'sheet': ea.sheet,
                'row': ea.row,
                'column': ea.col,
                'value': ea.value,
                'message': `Expires in ${ea.days_until_expiry} days`
            });
        }
        
        // Shift upgrades
        for (const su of this.issues.shift_upgrades) {
            out.push({
                'severity': 'info',
                'category': 'Shift Upgrade',
                'sheet': su.sheet,
                'row': su.row,
                'column': 'shift',
                'value': su.old_shift,
                'message': `Upgraded from "${su.old_shift}" to "${su.new_shift}"`
            });
        }
        
        return out;
    }
    
    _computeScore() {
        /** Compute quality score based on issues. */
        let totalPoints = 100;
        let issuePoints = 0;
        
        // Deduct points for various issues
        issuePoints += this.issues.invalid_phones.length * 3;  // 3 points per invalid phone
        issuePoints += this.issues.missing_data.length * 5;   // 5 points per missing data
        issuePoints += this.issues.enum_violations.length * 2; // 2 points per enum violation
        issuePoints += this.issues.time_conflicts.length * 4;  // 4 points per time conflict
        issuePoints += this.issues.date_format_issues.length * 1; // 1 point per date issue
        issuePoints += this.issues.capacity_issues.length * 3; // 3 points per capacity issue
        issuePoints += this.issues.insurance_expiry_issues.length * 5; // 5 points per expired insurance
        issuePoints += this.issues.shift_conflicts.length * 2; // 2 points per shift conflict
        issuePoints += this.issues.supplier_issues.length * 2; // 2 points per supplier issue
        
        // Bonus points for good practices (up to 10 bonus points)
        const bonusPoints = Math.min(this.issues.shift_upgrades.length * 0.5, 10);
        
        const totalDeduction = Math.min(issuePoints, 95);  // Cap at 95 points deducted
        let finalScore = Math.max(5, Math.min(100, 100 - totalDeduction + bonusPoints));  // Minimum score is 5, max is 100
        
        return Math.round(finalScore);
    }
    
    getAnalysisSummary() {
        return this.analysisSummary;
    }
}

// Export the classes and functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CodefyAnalyzer,
        ShiftEngine,
        TimeControlSystem,
        toStr,
        normalizeName,
        normalizePhone,
        isValidEgyptianPhone,
        normalizeDate,
        isValidDate,
        isValidTime,
        normalizeWorkingDays,
        inferShiftFromSchedule,
        analyzeShiftPatterns,
        isValidTaxId,
        isValidEmail,
        parseTimeWithFormat,
        ERP_COLUMN_SPEC,
        COL_DRIVER_NAME,
        COL_DRIVER_PHONE,
        COL_SUPPLIER_NAME,
        COL_SUPPLIER_PHONE,
        COL_PLATE,
        COL_SHIFT,
        COL_SCHEDULE,
        COL_ROUTE,
        COL_PICKUP_ARR,
        COL_PICKUP_DEP,
        COL_DROPOFF_ARR,
        COL_DROPOFF_TIME,
        COL_WORKING_DAYS,
        COL_DIRECTION,
        COL_EMP_TYPE,
        COL_START_DATE,
        COL_END_DATE,
        COL_SERVICE_TYPE,
        COL_CAPACITY,
        COL_VEHICLE_TYPE,
        COL_DRIVER_LICENSE,
        COL_INSURANCE_EXPIRY,
        COL_MAINTENANCE_DATE,
        COL_FUEL_TYPE,
        COL_VEHICLE_STATUS,
        COL_COMPANY_NAME,
        COL_COMPANY_PHONE,
        COL_COMPANY_ADDRESS,
        COL_COMPANY_EMAIL,
        COL_CONTACT_PERSON,
        COL_TAX_ID,
        COL_BANK_ACCOUNT,
        COL_CREDIT_LIMIT,
        COL_PAYMENT_TERMS,
        COL_SUPPLIER_CATEGORY,
        COL_DELIVERY_TIME,
        COL_MIN_ORDER_VALUE,
        COL_DISCOUNT_RATE
    };
}