/**
 * CodefyERP Help System - Scripts
 * Enhanced for single-section view, smooth navigation, progress tracking, and Egyptian Arabic UX.
 * Updated to communicate with Python API for actual validation functionality.
 */

// Section Definitions
const SECTIONS = [
    { id: 'login', title: 'تسجيل الدخول', icon: '🔐', subtitle: 'الخطوة الأولى في النظام' },
    { id: 'bulk-import', title: 'رفع المشاريع بالجملة', icon: '📦', subtitle: 'ملف إكسيل واحد يخلصك' },
    { id: 'relationships', title: 'المورد والمركبة والسائق', icon: '🤝', subtitle: 'مين راكب إيه ومع مين' },
    { id: 'assignments', title: 'توزيع الشغل (الجداول)', icon: '📋', subtitle: 'توزيع النقلات ع الرجالة' },
    { id: 'pricing', title: 'حسبة التسعير', icon: '💰', subtitle: 'التكلفة والإيراد والمكسب' },
    { id: 'readiness', title: 'مراجعة الجاهزية', icon: '✅', subtitle: 'التأكيد قبل ما تدور العربية' }
];

// App State
let currentSectionIndex = 0;
let viewMode = 'single'; // 'single' (focused section only) or 'all' (continuous scroll)
let completedSections = new Set();
let currentFile = null;
let currentValidationResult = null;

document.addEventListener('DOMContentLoaded', function() {
    initApp();
    initializeValidationTool();
    initializeTabSwitching();
});

function initApp() {
    // Load saved progress from localStorage
    loadProgress();
    
    // Initialize Sidebar & Mobile Menu
    initSidebar();
    
    // Initialize View Mode & Section Navigation
    initSectionMode();
    
    // Initialize Search & Suggestions
    initSearch();
    
    // Initialize Lightbox Modal
    initLightbox();
    
    // Initialize Tabs inside sections
    initTabs();
    
    // Initialize Back to Top & Scroll Progress
    initScrollProgress();
    initBackToTop();
    
    // Initialize Floating Help
    initFloatingHelp();
    
    // Initialize Keyboard Shortcuts
    initKeyboardShortcuts();
    
    // Render initial progress
    updateProgressUI();
}

/**
 * Progress Management (localStorage)
 */
function loadProgress() {
    try {
        const saved = localStorage.getItem('codefy_completed_sections');
        if (saved) {
            completedSections = new Set(JSON.parse(saved));
        }
    } catch (e) {
        console.warn('Could not read completed sections from localStorage', e);
    }
}

function saveProgress() {
    try {
        localStorage.setItem('codefy_completed_sections', JSON.stringify([...completedSections]));
    } catch (e) {
        console.warn('Could not save completed sections to localStorage', e);
    }
}

function toggleSectionCompletion(sectionId) {
    if (completedSections.has(sectionId)) {
        completedSections.delete(sectionId);
        showToast('تم إلغاء تحديد إنجاز القسم 👍', 'info');
    } else {
        completedSections.add(sectionId);
        showToast('عاش يا بطل! تم تسجيل إنجاز القسم بنجاح 🎊', 'success');
    }
    saveProgress();
    updateProgressUI();
    updateStepperCompletionButton(sectionId);
}

function updateProgressUI() {
    const total = SECTIONS.length;
    const completed = completedSections.size;
    const percent = Math.round((completed / total) * 100);
    
    // Update sidebar progress widgets
    const percentElem = document.getElementById('progress-percent');
    const countElem = document.getElementById('progress-count');
    const fillElem = document.getElementById('progress-bar-fill');
    
    if (percentElem) percentElem.textContent = `${percent}%`;
    if (countElem) countElem.textContent = `${completed} من ${total}`;
    if (fillElem) fillElem.style.width = `${percent}%`;
    
    // Update check badges on all sidebar links
    SECTIONS.forEach(sec => {
        const badge = document.querySelector(`.section-check-badge[data-badge-section="${sec.id}"]`);
        if (badge) {
            if (completedSections.has(sec.id)) {
                badge.classList.add('is-done');
                badge.innerHTML = '✓';
                badge.title = 'تم إنجاز هذا القسم';
            } else {
                badge.classList.remove('is-done');
                badge.innerHTML = '○';
                badge.title = 'لم يتم الإنجاز بعد';
            }
        }
    });
}

/**
 * Section Switching & Single Section Focused Mode
 */
function initSectionMode() {
    // Read URL hash on load
    const hash = window.location.hash.replace('#', '');
    const foundIndex = SECTIONS.findIndex(s => s.id === hash);
    if (foundIndex !== -1) {
        currentSectionIndex = foundIndex;
    } else {
        currentSectionIndex = 0; // default to first section (login)
    }

    // Bind mode toggle buttons
    const modeSingleBtns = document.querySelectorAll('.btn-mode-single');
    const modeAllBtns = document.querySelectorAll('.btn-mode-all');

    modeSingleBtns.forEach(btn => {
        btn.addEventListener('click', () => setViewMode('single'));
    });

    modeAllBtns.forEach(btn => {
        btn.addEventListener('click', () => setViewMode('all'));
    });

    // Apply initial view mode
    applyViewMode();
    showCurrentSection(false);

    // Attach click handlers to all navigation links
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSecId = this.getAttribute('data-section');
            const targetIndex = SECTIONS.findIndex(s => s.id === targetSecId);
            if (targetIndex !== -1) {
                currentSectionIndex = targetIndex;
                showCurrentSection(true);
                if (window.innerWidth < 1024) {
                    closeSidebar();
                }
            }
        });
    });

    // Hash change event listener
    window.addEventListener('hashchange', function() {
        const newHash = window.location.hash.replace('#', '');
        const targetIndex = SECTIONS.findIndex(s => s.id === newHash);
        if (targetIndex !== -1 && targetIndex !== currentSectionIndex) {
            currentSectionIndex = targetIndex;
            showCurrentSection(false);
        }
    });
}

function setViewMode(mode) {
    if (viewMode === mode) return;
    viewMode = mode;
    applyViewMode();
    showCurrentSection(true);
    
    if (mode === 'single') {
        showToast('تم تفعيل وضع التركيز (عرض قسم بقسم) 🎯', 'info');
    } else {
        showToast('تم تفعيل وضع التصفح الكامل (كل الأقسام) 📜', 'info');
    }
}

function applyViewMode() {
    const mainContent = document.getElementById('main-content');
    const modeSingleBtns = document.querySelectorAll('.btn-mode-single');
    const modeAllBtns = document.querySelectorAll('.btn-mode-all');

    if (viewMode === 'single') {
        document.body.classList.add('single-section-mode');
        document.body.classList.remove('all-sections-mode');
        modeSingleBtns.forEach(b => b.classList.add('active'));
        modeAllBtns.forEach(b => b.classList.remove('active'));
    } else {
        document.body.classList.remove('single-section-mode');
        document.body.classList.add('all-sections-mode');
        modeSingleBtns.forEach(b => b.classList.remove('active'));
        modeAllBtns.forEach(b => b.classList.add('active'));
        
        // Ensure all sections are visible
        document.querySelectorAll('.section-content').forEach(sec => {
            sec.classList.remove('hidden');
        });
    }
}

function showCurrentSection(shouldScroll = true) {
    const currentSec = SECTIONS[currentSectionIndex];
    if (!currentSec) return;

    // Update active nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('data-section') === currentSec.id) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Update Top Breadcrumb & Mobile Header Title
    const breadcrumbElem = document.getElementById('active-section-breadcrumb');
    if (breadcrumbElem) {
        breadcrumbElem.textContent = `${currentSec.icon} ${currentSec.title}`;
    }
    const mobileHeaderPill = document.getElementById('mobile-current-section');
    if (mobileHeaderPill) {
        mobileHeaderPill.textContent = `${currentSec.icon} ${currentSec.title}`;
    }
    const sectionCounter = document.getElementById('section-counter');
    if (sectionCounter) {
        sectionCounter.textContent = `القسم ${currentSectionIndex + 1} من ${SECTIONS.length}`;
    }

    // Update URL hash safely without reload
    if (history.replaceState) {
        history.replaceState(null, null, `#${currentSec.id}`);
    } else {
        window.location.hash = `#${currentSec.id}`;
    }

    if (viewMode === 'single') {
        // Hide all sections, display only target section
        document.querySelectorAll('.section-content').forEach(sec => {
            if (sec.id === currentSec.id) {
                sec.classList.add('active-section');
                sec.classList.remove('hidden');
            } else {
                sec.classList.remove('active-section');
            }
        });
        
        // Update Bottom Stepper Footer inside active section
        updateSectionStepper(currentSec.id);
        
        if (shouldScroll) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    } else {
        // In All Sections mode, scroll to target section
        const targetElement = document.getElementById(currentSec.id);
        if (targetElement && shouldScroll) {
            const offset = 90;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
        }
    }

    // Trigger Mermaid rerender if needed
    if (window.mermaid) {
        try {
            mermaid.contentLoaded();
        } catch (e) {}
    }
}

function updateSectionStepper(sectionId) {
    const stepperContainer = document.getElementById('section-stepper-container');
    if (!stepperContainer) return;

    const prevSec = currentSectionIndex > 0 ? SECTIONS[currentSectionIndex - 1] : null;
    const nextSec = currentSectionIndex < SECTIONS.length - 1 ? SECTIONS[currentSectionIndex + 1] : null;
    const isDone = completedSections.has(sectionId);

    stepperContainer.innerHTML = `
        <div class="mt-16 pt-8 border-t border-slate-200">
            <!-- Mark as Done Toggle -->
            <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-gradient-to-r from-blue-50/70 via-indigo-50/50 to-white border border-blue-100 mb-8">
                <div class="flex items-center gap-3">
                    <span class="text-3xl">${isDone ? '🎉' : '✨'}</span>
                    <div>
                        <div class="font-black text-slate-900 text-sm">
                            ${isDone ? 'الله ينور! خلصت القسم ده' : 'خلصت قراءة القسم وفهمت المطلوب؟'}
                        </div>
                        <p class="text-xs text-slate-500 m-0">علّم عليه عشان تتابع تقدمك خطوة بخطوة في القائمة الجانبية.</p>
                    </div>
                </div>
                <button type="button" id="btn-toggle-done" class="px-5 py-2.5 rounded-xl font-black text-sm flex items-center gap-2 transition-all shadow-sm ${
                    isDone 
                        ? 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-emerald-600/20' 
                        : 'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50'
                }">
                    <span>${isDone ? '✓ تم الإنجاز' : '○ علّم كمنجز'}</span>
                </button>
            </div>

            <!-- Stepper Prev / Next Buttons -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                ${prevSec ? `
                    <button type="button" id="btn-prev-section" class="section-stepper-card text-start">
                        <span class="text-xs font-bold text-slate-400 mb-1 flex items-center gap-1">
                            <span>➔</span> القسم السابق
                        </span>
                        <span class="text-base font-black text-slate-800 flex items-center gap-2">
                            <span>${prevSec.icon}</span>
                            <span>${prevSec.title}</span>
                        </span>
                    </button>
                ` : `<div></div>`}

                ${nextSec ? `
                    <button type="button" id="btn-next-section" class="section-stepper-card text-end sm:text-end">
                        <span class="text-xs font-bold text-primary-600 mb-1 flex items-center justify-end gap-1">
                            القسم التالي <span>←</span>
                        </span>
                        <span class="text-base font-black text-slate-900 flex items-center justify-end gap-2">
                            <span>${nextSec.title}</span>
                            <span>${nextSec.icon}</span>
                        </span>
                    </button>
                ` : `
                    <button type="button" id="btn-finish-guide" class="section-stepper-card text-end bg-gradient-to-l from-emerald-50 to-white border-emerald-200 hover:border-emerald-400">
                        <span class="text-xs font-bold text-emerald-600 mb-1 flex items-center justify-end gap-1">
                            مبروك! <span>🎉</span>
                        </span>
                        <span class="text-base font-black text-emerald-900 flex items-center justify-end gap-2">
                            <span>تم الانتهاء من الدليل بالكامل</span>
                        </span>
                    </button>
                `}
            </div>
        </div>
    `;

    // Bind Stepper events
    const doneBtn = document.getElementById('btn-toggle-done');
    if (doneBtn) {
        doneBtn.addEventListener('click', () => {
            toggleSectionCompletion(sectionId);
        });
    }

    const prevBtn = document.getElementById('btn-prev-section');
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentSectionIndex > 0) {
                currentSectionIndex--;
                showCurrentSection(true);
            }
        });
    }

    const nextBtn = document.getElementById('btn-next-section');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentSectionIndex < SECTIONS.length - 1) {
                currentSectionIndex++;
                showCurrentSection(true);
            }
        });
    }

    const finishBtn = document.getElementById('btn-finish-guide');
    if (finishBtn) {
        finishBtn.addEventListener('click', () => {
            showToast('مبروك يا بطل! كده انت جاهز تدير شغلك بكل ثقة 🚀', 'success');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

function updateStepperCompletionButton(sectionId) {
    updateSectionStepper(sectionId);
}

/**
 * Sidebar Navigation & Mobile Drawer
 */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const iconMenu = document.getElementById('icon-menu');
    const iconClose = document.getElementById('icon-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            if (sidebar.classList.contains('translate-x-full')) {
                openSidebar();
            } else {
                closeSidebar();
            }
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const iconMenu = document.getElementById('icon-menu');
    const iconClose = document.getElementById('icon-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');

    if (sidebar) {
        sidebar.classList.remove('translate-x-full');
        sidebar.classList.add('translate-x-0');
    }
    if (iconMenu) iconMenu.classList.add('hidden');
    if (iconClose) iconClose.classList.remove('hidden');
    if (sidebarOverlay) sidebarOverlay.classList.remove('hidden');
    if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const iconMenu = document.getElementById('icon-menu');
    const iconClose = document.getElementById('icon-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');

    if (sidebar) {
        sidebar.classList.add('translate-x-full');
        sidebar.classList.remove('translate-x-0');
    }
    if (iconMenu) iconMenu.classList.remove('hidden');
    if (iconClose) iconClose.classList.add('hidden');
    if (sidebarOverlay) sidebarOverlay.classList.add('hidden');
    if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
}

/**
 * Search Functionality with live suggestion dropdown
 */
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchSuggestions = document.getElementById('search-suggestions');
    const suggestionsList = document.getElementById('suggestions-list');

    if (!searchInput || !searchSuggestions || !suggestionsList) return;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        if (!query) {
            searchSuggestions.classList.add('hidden');
            return;
        }

        // Search through sections
        const matches = SECTIONS.filter(s => 
            s.title.toLowerCase().includes(query) || 
            s.subtitle.toLowerCase().includes(query) ||
            s.id.toLowerCase().includes(query)
        );

        if (matches.length > 0) {
            suggestionsList.innerHTML = matches.map(m => `
                <li class="px-4 py-2.5 hover:bg-primary-50 cursor-pointer flex items-center justify-between border-b border-slate-100 last:border-none" data-search-target="${m.id}">
                    <div class="flex items-center gap-2.5">
                        <span class="text-xl">${m.icon}</span>
                        <div>
                            <div class="font-bold text-slate-800 text-sm">${m.title}</div>
                            <div class="text-xs text-slate-500">${m.subtitle}</div>
                        </div>
                    </div>
                    <span class="text-xs font-bold text-primary-600">فتح ↵</span>
                </li>
            `).join('');

            suggestionsList.querySelectorAll('li').forEach(li => {
                li.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-search-target');
                    const targetIndex = SECTIONS.findIndex(s => s.id === targetId);
                    if (targetIndex !== -1) {
                        currentSectionIndex = targetIndex;
                        showCurrentSection(true);
                        searchInput.value = '';
                        searchSuggestions.classList.add('hidden');
                        if (window.innerWidth < 1024) closeSidebar();
                    }
                });
            });

            searchSuggestions.classList.remove('hidden');
        } else {
            suggestionsList.innerHTML = `
                <li class="px-4 py-3 text-center text-xs text-slate-500">
                    ملقناش حاجة مطابقة لكلمة "${query}". جرب كلمة تانية زي "تسجيل" أو "تسعير".
                </li>
            `;
            searchSuggestions.classList.remove('hidden');
        }
    });

    // Close on click outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.classList.add('hidden');
        }
    });
}

/**
 * Lightbox Modal for Large Images
 */
function initLightbox() {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.getElementById('lightbox-close');
    const triggers = document.querySelectorAll('.lightbox-trigger');

    if (!lightbox || !lightboxImg || !lightboxClose) return;

    triggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const src = this.src || this.getAttribute('data-large-src');
            if (src) {
                lightboxImg.src = src;
                lightbox.classList.remove('hidden');
                setTimeout(() => lightbox.classList.remove('opacity-0'), 10);
                document.body.style.overflow = 'hidden';
            }
        });
    });

    const closeHandler = () => {
        lightbox.classList.add('opacity-0');
        setTimeout(() => {
            lightbox.classList.add('hidden');
            document.body.style.overflow = '';
        }, 300);
    };

    lightboxClose.addEventListener('click', closeHandler);
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) closeHandler();
    });
}

/**
 * Inner Tabs in Sections
 */
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (!tabBtns.length || !tabContents.length) return;

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            if (!tabName) return;

            tabBtns.forEach(b => {
                b.classList.remove('active');
            });

            tabContents.forEach(content => {
                content.classList.add('hidden');
            });

            this.classList.add('active');
            document.querySelector(`.tab-content[data-content="${tabName}"]`).classList.remove('hidden');
        });
    });
}

/**
 * Tab Switching Functionality for Bulk Import
 */
function initializeTabSwitching() {
    // Add event listeners for bulk import tabs
    const tabButtons = document.querySelectorAll('#bulk-import .tab-btn');
    if (!tabButtons.length) return;

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and content
            document.querySelectorAll('#bulk-import .tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.querySelectorAll('#bulk-import .tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.querySelector(`#bulk-import .tab-content[data-content="${tabName}"]`).classList.remove('hidden');
        });
    });
}

/**
 * Back to Top & Scroll Progress
 */
function initScrollProgress() {
    const progress = document.getElementById('scroll-progress');
    if (!progress) return;

    window.addEventListener('scroll', () => {
        if (viewMode === 'all') {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progress.style.width = scrolled + '%';
        } else {
            const pct = ((currentSectionIndex + 1) / SECTIONS.length) * 100;
            progress.style.width = pct + '%';
        }
    }, { passive: true });
}

function initBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            btn.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-3');
        } else {
            btn.classList.add('opacity-0', 'pointer-events-none', 'translate-y-3');
        }
    }, { passive: true });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Floating Help Alert
 */
function initFloatingHelp() {
    const btn = document.getElementById('float-help');
    if (!btn) return;

    btn.addEventListener('click', function() {
        showToast('يا هلا بيك! لو محتاج أي استفسار فريق دعم كوديفاي في خدمتك دايماً 💬', 'info');
    });
}

/**
 * Keyboard Shortcuts (Arrow keys & Ctrl+K)
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                if (window.innerWidth < 1024) openSidebar();
                searchInput.focus();
            }
        }
        // Escape closes sidebar / lightbox
        if (e.key === 'Escape') {
            closeSidebar();
            const lightbox = document.getElementById('lightbox');
            if (lightbox && !lightbox.classList.contains('hidden')) {
                lightbox.classList.add('opacity-0');
                setTimeout(() => lightbox.classList.add('hidden'), 300);
            }
        }
        // In single mode: ArrowLeft moves to next section in RTL
        if (viewMode === 'single' && !['input', 'textarea'].includes(document.activeElement.tagName.toLowerCase())) {
            if (e.key === 'ArrowLeft') {
                if (currentSectionIndex < SECTIONS.length - 1) {
                    currentSectionIndex++;
                    showCurrentSection(true);
                }
            } else if (e.key === 'ArrowRight') {
                if (currentSectionIndex > 0) {
                    currentSectionIndex--;
                    showCurrentSection(true);
                }
            }
        }
    });
}

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

        const formData = new FormData();
        formData.append('file', file);

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
            const endpoint = `${apiBase}/validate`;
            console.log(`Using API endpoint: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
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
                if (progressBar) progressBar.style.style = 'none';
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
        
        const formData = new FormData();
        formData.append('file', originalFile);
        
        // Use the appropriate API endpoint based on environment
        const endpoint = `${apiBase}/download-cleaned`;
        console.log(`Using download endpoint: ${endpoint}`);

        const formData = new FormData();
        formData.append('file', originalFile);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
                mode: 'cors',  // Enable CORS mode
                credentials: 'omit' // Don't include credentials for CORS requests
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Create a blob from the response and trigger download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `cleaned_${originalFile.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
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

    async function downloadCleanedFile(originalFile) {
        const formData = new FormData();
        formData.append('file', originalFile);

        try {
            // Try multiple API endpoints as fallbacks for download
            const apiEndpoints = [
                'http://localhost:5000/api/download-cleaned',
                'http://127.0.0.1:5000/api/download-cleaned',
                'http://0.0.0.0:5000/api/download-cleaned',
                '/api/download-cleaned' // Relative path as final fallback
            ];
            
            let response = null;
            let lastError = null;
            let retryCount = 3;
            
            for (const endpoint of apiEndpoints) {
                for (let i = 0; i < retryCount; i++) {
                    try {
                        console.log(`Trying download endpoint: ${endpoint} (attempt ${i+1}/${retryCount})`);
                        response = await fetch(endpoint, {
                            method: 'POST',
                            body: formData,
                            mode: 'cors',
                            cache: 'no-cache'
                        });
                        
                        if (response.ok) {
                            break; // Success, exit retry loop
                        } else {
                            console.warn(`Download endpoint failed: ${endpoint}, status: ${response.status}`);
                            lastError = `HTTP error! status: ${response.status}`;
                            // Wait before retrying
                            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                        }
                    } catch (error) {
                        console.warn(`Download endpoint failed: ${endpoint}, error: ${error.message}`);
                        lastError = error.message;
                        // Wait before retrying
                        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                    }
                }
                
                if (response && response.ok) break; // Exit endpoint loop if successful
            }
            
            if (!response || !response.ok) {
                throw new Error(lastError || 'All download endpoints failed after retries');
            }

            // Create a blob from the response and trigger download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `cleaned_${originalFile.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download error:', error);
            alert('حدث خطأ أثناء تحميل الملف بعد التنظيف. يرجى التأكد من أن خادم API يعمل على localhost:5000.\n\n' +
                  'للتشغيل: انتقل إلى مجلد Statics/PY وشغل: python api_server.py');
        }
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