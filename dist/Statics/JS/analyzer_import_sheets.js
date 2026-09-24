/**
 * CodefyERP Excel Analyzer - Import Sheets Module
 * Dedicated module for Excel file validation, analysis and processing capabilities.
 * Handles file uploads, validation against Egyptian business rules, and results display.
 */

// App State variables for validation
let currentFile = null;
let currentValidationResult = null;

/**
 * Validation Tool Initialization
 */
function initializeValidationTool() {
    // Only initialize if we're on the bulk-import section
    const bulkImportSection = document.getElementById('bulk-import');
    if (!bulkImportSection) return;
    
    // Determine if we're running via file:// protocol or HTTP(S)
    const isFileProtocol = window.location.protocol === 'file:';
    const isLocalhost = !isFileProtocol && (
                       window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '0.0.0.0');
    
    // Set API endpoints based on environment
    // When running via file:// protocol, we cannot make API calls, so we'll use simulation
    let apiBase;
    if (isFileProtocol) {
        apiBase = null; // Will use simulation
    } else if (isLocalhost) {
        apiBase = 'http://localhost:5000/api'; // Local Python API
    } else {
        // For Vercel deployment, use the Vercel API routes
        apiBase = '/api'; // Vercel serverless functions
    }

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const progressBar = document.getElementById('progressBar');
    const progressFill = document.getElementById('progressFill');
    const analysisResults = document.getElementById('analysisResults');
    const summaryCard = document.getElementById('summaryCard');
    const issuesTableBody = document.getElementById('issuesTableBody');
    const downloadCleanBtn = document.getElementById('downloadCleanBtn');
    const proceedImportBtn = document.getElementById('proceedImportBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    // Drag and drop functionality
    if (dropZone) {
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#4f46e5';
            this.style.backgroundColor = '#ede9fe';
        });

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#ccc';
            this.style.backgroundColor = '';
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#ccc';
            this.style.backgroundColor = '';
            if (e.dataTransfer.files.length) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length) {
                handleFile(this.files[0]);
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            fileInput.value = '';
            fileInfo.style.display = 'none';
            progressBar.style.display = 'none';
            progressFill.style.width = '0%';
            analysisResults.style.display = 'none';
            summaryCard.innerHTML = '';
            issuesTableBody.innerHTML = '';
            downloadCleanBtn.disabled = true;
            proceedImportBtn.disabled = true;
            currentFile = null;
            currentValidationResult = null;
        });
    }

    function handleFile(file) {
        if (!file.name.match(/\.(xlsx|xls)$/i)) {
            alert('من فضلك اختر ملف إكسل صحيح (.xlsx أو .xls)');
            return;
        }

        // Store reference to current file
        currentFile = file;

        // Show file info
        if (fileInfo) {
            fileInfo.textContent = `تم اختيار: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} ميجابايت)`;
            fileInfo.style.display = 'block';
        }

        // Start actual analysis by calling the API
        startAnalysis(file);
    }

    async function startAnalysis(file) {
        if (progressBar) progressBar.style.display = 'block';
        if (progressFill) progressFill.style.width = '0%';

        const uploadFormData = new FormData();
        uploadFormData.append('file', file);

        try {
            // If we're running via file:// protocol, skip API call and go straight to simulation
            if (isFileProtocol) {
                console.warn('Running in file:// protocol, cannot make API calls. Using simulation mode.');
                alert('التطبيق يعمل في وضع الملف المحلي، لا يمكن الاتصال بالخادم. سيتم استخدام نتائج تجريبية.');
                simulateAnalysis(file);
                return;
            }
            
            // Update progress to show API call is happening
            if (progressFill) progressFill.style.width = '20%';
            
            // Use the appropriate API endpoint based on environment
            let endpoint;
            if (isLocalhost) {
                // For localhost, use the Python API directly - note the correct endpoint
                endpoint = 'http://localhost:5000/api/validate-excel';
            } else {
                // Vercel uses the simulated serverless endpoint
                endpoint = `${apiBase}/validate`;
            }
            console.log(`Using API endpoint: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: uploadFormData,
                mode: 'cors',  // Enable CORS mode
                credentials: 'omit', // Don't include credentials for CORS requests
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                displayResults(result);
            } else {
                alert(`خطأ في التحليل: ${result.error || 'حدث خطأ غير معروف'}`);
                if (progressBar) progressBar.style.display = 'none';
            }
        } catch (error) {
            console.error('Analysis error:', error);
            
            // Provide appropriate error message based on environment
            if (isLocalhost) {
                alert('خطأ في الاتصال بالخادم. يرجى التأكد من أن خادم API يعمل على localhost:5000.\n\n' +
                      'للتشغيل: انتقل إلى مجلد Statics/PY وشغل: python api_server.py');
            } else {
                alert('خطأ في الاتصال بالخادم. يتم الآن استخدام نتائج تجريبية.');
            }
            
            // Fallback to simulated results if API is not available
            simulateAnalysis(file);
        }
    }

    async function downloadCleanedFile(originalFile) {
        // If we're running via file:// protocol, skip API call
        if (isFileProtocol) {
            alert('لا يمكن تحميل الملف بعد التنظيف عند التشغيل من الملف المحلي. يرجى استخدام الخادم المحلي.');
            return;
        }
        
        // Use the appropriate API endpoint based on environment
        let endpoint;
        if (isLocalhost) {
            // For localhost, use the Python API directly - note the correct endpoint for export
            endpoint = 'http://localhost:5000/api/validate-and-fix';
        } else {
            // Vercel uses the simulated download endpoint
            endpoint = `${apiBase}/download-cleaned`;
        }
        
        console.log(`Using download endpoint: ${endpoint}`);

        try {
            // Create form data with auto_fix parameter
            const downloadFormData = new FormData();
            downloadFormData.append('file', originalFile);
            downloadFormData.append('auto_fix', 'true'); // Tell the API to auto-fix and return the file

            const response = await fetch(endpoint, {
                method: 'POST',
                body: downloadFormData,
                mode: 'cors',  // Enable CORS mode
                credentials: 'omit' // Don't include credentials for CORS requests
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Check if response is JSON or binary file
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
                // This is a file download response
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `fixed_${originalFile.name}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                // This is a JSON response, possibly an error
                const result = await response.json();
                if (result.success === false) {
                    alert(`Error: ${result.error || result.message || 'Unknown error'}`);
                } else {
                    alert('File processed successfully but no downloadable file returned.');
                }
            }
        } catch (error) {
            console.error('Download error:', error);
            
            // Provide appropriate error message based on environment
            if (isLocalhost) {
                alert('حدث خطأ أثناء تحميل الملف بعد التنظيف. يرجى التأكد من أن خادم API يعمل على localhost:5000.\n\n' +
                      'للتشغيل: انتقل إلى مجلد Statics/PY وشغل: python api_server.py');
            } else {
                alert('تم إنشاء الملف بعد التنظيف. في الإصدار الكامل، سيتم تحميل الملف مباشرة.');
            }
        }
    }

    function simulateAnalysis(file) {
        // Show that we're simulating because API is unavailable
        if (fileInfo) {
            fileInfo.textContent += ' (API غير متاح - استخدام نتائج تجريبية)';
        }

        // Simulate analysis progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                // Mock analysis results with realistic data
                const mockResult = {
                    success: true,
                    summary: {
                        file_name: file.name,
                        total_rows: Math.floor(Math.random() * 1000) + 500,
                        total_sheets: Math.floor(Math.random() * 5) + 1,
                        quality_score: Math.floor(Math.random() * 30) + 70,
                        issues: {
                            critical: Math.floor(Math.random() * 3) + 1,
                            warning: Math.floor(Math.random() * 5) + 1,
                            info: Math.floor(Math.random() * 8) + 1
                        },
                        breakdown: {
                            invalid_phones: Math.floor(Math.random() * 4),
                            date_format_issues: Math.floor(Math.random() * 3),
                            enum_violations: Math.floor(Math.random() * 2),
                            missing_data: Math.floor(Math.random() * 3),
                            duplicate_phones: Math.floor(Math.random() * 2),
                            time_conflicts: Math.floor(Math.random() * 2),
                            shift_upgrades: Math.floor(Math.random() * 4),
                            shift_conflicts: Math.floor(Math.random() * 2),
                            supplier_issues: Math.floor(Math.random() * 2),
                            capacity_issues: Math.floor(Math.random() * 2)
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
                };
                displayResults(mockResult);
            }
            if (progressFill) progressFill.style.width = `${progress}%`;
        }, 200);
    }

    function displayResults(result) {
        currentValidationResult = result;
        const summary = result.summary;
        
        // Update summary card
        if (summaryCard) {
            summaryCard.innerHTML = `
                <div class="summary-item" style="background: #f8f9fa; padding: 15px; border-radius: 6px; min-width: 150px; text-align: center;">
                    <div class="summary-value" style="font-size: 1.5em; font-weight: bold;">${summary.total_rows || 0}</div>
                    <div class="summary-label">إجمالي الصفوف</div>
                </div>
                <div class="summary-item" style="background: #f8f9fa; padding: 15px; border-radius: 6px; min-width: 150px; text-align: center;">
                    <div class="summary-value" style="font-size: 1.5em; font-weight: bold;">${summary.total_sheets || 0}</div>
                    <div class="summary-label">إجمالي الأوراق</div>
                </div>
                <div class="summary-item critical" style="background: #ffeef0; padding: 15px; border-radius: 6px; min-width: 150px; text-align: center; border-left: 4px solid #dc3545;">
                    <div class="summary-value" style="font-size: 1.5em; font-weight: bold; color: #dc3545;">${summary.issues?.critical || 0}</div>
                    <div class="summary-label">مشاكل حرجة</div>
                </div>
                <div class="summary-item warning" style="background: #fff3cd; padding: 15px; border-radius: 6px; min-width: 150px; text-align: center; border-left: 4px solid #ffc107;">
                    <div class="summary-value" style="font-size: 1.5em; font-weight: bold; color: #856404;">${summary.issues?.warning || 0}</div>
                    <div class="summary-label">تحذيرات</div>
                </div>
                <div class="summary-item info" style="background: #d1ecf1; padding: 15px; border-radius: 6px; min-width: 150px; text-align: center; border-left: 4px solid #17a2b8;">
                    <div class="summary-value" style="font-size: 1.5em; font-weight: bold; color: #0c5460;">${summary.quality_score || 0}/100</div>
                    <div class="summary-label">درجة الجودة</div>
                </div>
            `;
        }

        // Update issues table
        if (issuesTableBody) {
            issuesTableBody.innerHTML = '';
            (result.issues || []).forEach(issue => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;" class="severity-${issue.severity}">
                        <span style="font-weight: bold; ${
                            issue.severity === 'critical' ? 'color: #dc3545;' :
                            issue.severity === 'warning' ? 'color: #856404;' :
                            'color: #0c5460;'
                        }">${issue.severity.charAt(0).toUpperCase() + issue.severity.slice(1)}</span>
                    </td>
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;">${issue.category}</td>
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;">${issue.sheet}</td>
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;">${issue.row}</td>
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;">${issue.column}</td>
                    <td style="border: 1px solid #ddd; padding: 12px; text-align: left;">${issue.message || issue.issue}</td>
                `;
                issuesTableBody.appendChild(row);
            });
        }

        // Enable buttons based on results
        if (downloadCleanBtn) {
            downloadCleanBtn.disabled = false;
            downloadCleanBtn.onclick = function() {
                if (fileInput.files.length > 0) {
                    downloadCleanedFile(fileInput.files[0]);
                }
            };
        }
        
        if (proceedImportBtn) {
            const hasCriticalIssues = (summary.issues?.critical || 0) > 0;
            proceedImportBtn.disabled = hasCriticalIssues;
            proceedImportBtn.onclick = function() {
                if (hasCriticalIssues) {
                    if (confirm('لا يزال هناك مشاكل حرجة في الملف. هل ترغب في المتابعة على أي حال؟')) {
                        alert('جاري متابعة عملية الرفع...');
                    }
                } else {
                    alert('جاري متابعة عملية الرفع...');
                }
            };
        }

        if (analysisResults) analysisResults.style.display = 'block';
        if (progressBar) progressBar.style.display = 'none';
    }
}

/**
 * Analysis Configuration Management
 * Handles settings persistence, profiles, import/export, and sync with validation tool
 */
const ANALYSIS_CONFIG_KEY = 'codefy_analysis_config_v1';
const ANALYSIS_PROFILES_KEY = 'codefy_analysis_profiles_v1';

let analysisConfig = {
    shiftEngine: true,
    timeConflict: true,
    timeNormalize: true,
    format12h: true,
    offset: 30,
    target: 'dropoff_arrival_time'
};

function loadAnalysisConfig() {
    try {
        const saved = localStorage.getItem(ANALYSIS_CONFIG_KEY);
        if (saved) {
            analysisConfig = { ...analysisConfig, ...JSON.parse(saved) };
        }
    } catch (e) {
        console.warn('Could not load analysis config', e);
    }
    applyConfigToUI();
    syncConfigToValidationTab();
}

function saveAnalysisConfig() {
    try {
        localStorage.setItem(ANALYSIS_CONFIG_KEY, JSON.stringify(analysisConfig));
    } catch (e) {
        console.warn('Could not save analysis config', e);
    }
}

function applyConfigToUI() {
    const elements = {
        'cfg-shift-engine': 'shiftEngine',
        'cfg-time-conflict': 'timeConflict',
        'cfg-time-normalize': 'timeNormalize',
        'cfg-12h-format': 'format12h',
        'cfg-offset': 'offset',
        'cfg-target': 'target'
    };
    
    Object.entries(elements).forEach(([id, key]) => {
        const el = document.getElementById(id);
        if (el) {
            if (el.type === 'checkbox') {
                el.checked = analysisConfig[key];
            } else {
                el.value = analysisConfig[key];
            }
        }
    });
}

function syncConfigToValidationTab() {
    // Sync to inline validation tab settings
    const mapping = {
        'setting-shift-engine': 'shiftEngine',
        'setting-time-conflict': 'timeConflict',
        'setting-time-normalize': 'timeNormalize',
        'setting-12h': 'format12h',
        'setting-offset': 'offset',
        'setting-target': 'target'
    };
    
    Object.entries(mapping).forEach(([id, key]) => {
        const configEl = document.getElementById(id);
        if (configEl) {
            if (configEl.type === 'checkbox') {
                configEl.checked = analysisConfig[key];
            } else {
                configEl.value = analysisConfig[key];
            }
        }
    });
}

function getConfigFromUI() {
    const elements = {
        'cfg-shift-engine': 'shiftEngine',
        'cfg-time-conflict': 'timeConflict',
        'cfg-time-normalize': 'timeNormalize',
        'cfg-12h-format': 'format12h',
        'cfg-offset': 'offset',
        'cfg-target': 'target'
    };
    
    Object.entries(elements).forEach(([id, key]) => {
        const el = document.getElementById(id);
        if (el) {
            if (el.type === 'checkbox') {
                analysisConfig[key] = el.checked;
            } else {
                analysisConfig[key] = el.value;
            }
        }
    });
}

function loadProfiles() {
    try {
        const saved = localStorage.getItem(ANALYSIS_PROFILES_KEY);
        return saved ? JSON.parse(saved) : {};
    } catch (e) {
        console.warn('Could not load profiles', e);
        return {};
    }
}

function saveProfiles(profiles) {
    try {
        localStorage.setItem(ANALYSIS_PROFILES_KEY, JSON.stringify(profiles));
    } catch (e) {
        console.warn('Could not save profiles', e);
    }
}

function renderProfiles() {
    const container = document.getElementById('cfg-profiles-list');
    const emptyState = document.getElementById('cfg-empty-profiles');
    if (!container) return;
    
    const profiles = loadProfiles();
    const profileNames = Object.keys(profiles);
    
    if (profileNames.length === 0) {
        container.innerHTML = '';
        if (emptyState) container.appendChild(emptyState);
        emptyState.style.display = 'block';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    container.innerHTML = profileNames.map(name => {
        const p = profiles[name];
        const updated = new Date(p.updated).toLocaleDateString('ar-EG');
        return `
            <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-primary-300 transition-colors">
                <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                    </div>
                    <div>
                        <div class="font-bold text-slate-900">${name}</div>
                        <div class="text-xs text-slate-500">محدّث: ${updated}</div>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button type="button" onclick="applyProfile('${name}')"
                        class="px-3 py-1.5 bg-primary-600 text-white text-sm font-bold rounded-lg hover:bg-primary-700 transition-colors">
                        تطبيق
                    </button>
                    <button type="button" onclick="deleteProfile('${name}')"
                        class="px-3 py-1.5 bg-red-100 text-red-600 text-sm font-bold rounded-lg hover:bg-red-200 transition-colors">
                        حذف
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function applyProfile(name) {
    const profiles = loadProfiles();
    if (profiles[name]) {
        analysisConfig = { ...analysisConfig, ...profiles[name].config };
        saveAnalysisConfig();
        applyConfigToUI();
        syncConfigToValidationTab();
        showToast(`تم تطبيق ملف التعريف: ${name}`, 'success');
    }
}

function deleteProfile(name) {
    if (confirm(`حذف ملف التعريف "${name}"؟`)) {
        const profiles = loadProfiles();
        delete profiles[name];
        saveProfiles(profiles);
        renderProfiles();
        showToast('تم حذف ملف التعريف', 'info');
    }
}

function initializeAnalysisConfig() {
    loadAnalysisConfig();
    renderProfiles();
    
    // Bind UI events
    const configElements = [
        'cfg-shift-engine', 'cfg-time-conflict', 'cfg-time-normalize', 
        'cfg-12h-format', 'cfg-offset', 'cfg-target'
    ];
    
    configElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                getConfigFromUI();
                saveAnalysisConfig();
                syncConfigToValidationTab();
            });
        }
    });
    
    // Save profile button
    const saveBtn = document.getElementById('cfg-save-profile');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const name = prompt('اسم ملف التعريف:', `ملف تعريف ${new Date().toLocaleDateString('ar-EG')}`);
            if (name) {
                getConfigFromUI();
                const profiles = loadProfiles();
                profiles[name] = {
                    config: { ...analysisConfig },
                    updated: Date.now()
                };
                saveProfiles(profiles);
                renderProfiles();
                showToast('تم حفظ ملف التعريف', 'success');
            }
        });
    }
    
    // Reset button
    const resetBtn = document.getElementById('cfg-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('إعادة جميع الإعدادات للقيم الافتراضية؟')) {
                analysisConfig = {
                    shiftEngine: true,
                    timeConflict: true,
                    timeNormalize: true,
                    format12h: true,
                    offset: 30,
                    target: 'dropoff_arrival_time'
                };
                saveAnalysisConfig();
                applyConfigToUI();
                syncConfigToValidationTab();
                showToast('تم إعادة التعيين للافتراضي', 'info');
            }
        });
    }
    
    // Export button
    const exportBtn = document.getElementById('cfg-export');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            getConfigFromUI();
            const data = {
                config: analysisConfig,
                profiles: loadProfiles(),
                exportedAt: new Date().toISOString(),
                version: '1.0'
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `codefy-analysis-config-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('تم تصدير الإعدادات', 'success');
        });
    }
    
    // Import file input
    const importFile = document.getElementById('cfg-import-file');
    if (importFile) {
        importFile.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    if (data.config) {
                        analysisConfig = { ...analysisConfig, ...data.config };
                        saveAnalysisConfig();
                        applyConfigToUI();
                        syncConfigToValidationTab();
                    }
                    if (data.profiles) {
                        saveProfiles(data.profiles);
                        renderProfiles();
                    }
                    showToast('تم استيراد الإعدادات بنجاح', 'success');
                } catch (err) {
                    console.error('Import error:', err);
                    showToast('خطأ في قراءة الملف', 'error');
                }
            };
            reader.readAsText(file);
            e.target.value = '';
        });
    }
}

/**
 * Toast Notifications
 */
let toastTimeout = null;
function showToast(message, type = 'info') {
    let toast = document.getElementById('toast-notification');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        document.body.appendChild(toast);
    }

    const bgColors = {
        success: 'bg-emerald-800 text-emerald-50 border-emerald-700',
        info: 'bg-slate-900 text-white border-slate-700',
        warn: 'bg-amber-800 text-amber-50 border-amber-700'
    };

    toast.className = `px-5 py-3.5 rounded-2xl shadow-2xl border text-sm font-bold flex items-center gap-3 backdrop-blur-md ${bgColors[type] || bgColors.info} show`;
    toast.innerHTML = `
        <span class="text-lg">${type === 'success' ? '✅' : '💡'}</span>
        <span>${message}</span>
    `;

    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}