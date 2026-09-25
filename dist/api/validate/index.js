/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 619:
/***/ ((module) => {

/* eslint-disable no-undef */
/* Vercel Serverless API - Validate Endpoint */
/* Handles POST /api/validate for Excel file validation */

module.exports = async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: `Method ${req.method} not allowed` });
    return;
  }

  try {
    // Return simulated validation results
    // In production, this would process the uploaded Excel file using Python/NumPy/Pandas
    res.status(200).json({
      success: true,
      summary: {
        file_name: 'sample_data.xlsx',
        total_rows: 500,
        total_sheets: 3,
        quality_score: 85,
        issues: {
          critical: 2,
          warning: 5,
          info: 8
        },
        breakdown: {
          invalid_phones: 1,
          date_format_issues: 2,
          enum_violations: 1,
          missing_data: 2,
          duplicate_phones: 1,
          time_conflicts: 1,
          shift_conflicts: 1,
          supplier_issues: 2,
          capacity_issues: 1,
          shift_upgrades: 3
        }
      },
      issues: [
        { severity: 'critical', category: 'Invalid Phone', sheet: 'Drivers', row: 45, column: 'Phone', message: 'Invalid Egyptian phone number format' },
        { severity: 'warning', category: 'Date Format', sheet: 'Schedule', row: 12, column: 'Start_Date', message: 'Date not in YYYY-MM-DD format' },
        { severity: 'info', category: 'Normalization', sheet: 'Routes', row: 67, column: 'Direction', message: 'Direction inferred from schedule' },
        { severity: 'critical', category: 'Missing Data', sheet: 'Vehicles', row: 89, column: 'Driver_Name', message: 'Required field missing' },
        { severity: 'warning', category: 'Capacity Issue', sheet: 'Vehicles', row: 156, column: 'Capacity', message: 'Capacity value seems unusually high for vehicle type' },
        { severity: 'warning', category: 'Shift Conflict', sheet: 'Schedule', row: 23, column: 'Shift', message: 'Shift type conflicts with scheduled times' },
        { severity: 'warning', category: 'Supplier Issue', sheet: 'Suppliers', row: 78, column: 'Tax_ID', message: 'Invalid Egyptian tax ID format' }
      ]
    });
  } catch (error) {
    console.error('Validation API Error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
}


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = __nccwpck_require__(619);
/******/ 	module.exports = __webpack_exports__;
/******/ 	
/******/ })()
;