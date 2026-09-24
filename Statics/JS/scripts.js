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
    { id: 'readiness', title: 'مراجعة الجاهزية', icon: '✅', subtitle: 'التأكيد قبل ما تدور العربية' },
    { id: 'analysis-config', title: 'إعدادات تحليل الإكسل', icon: '⚙️', subtitle: 'تخصيص قواعد التحقق والمعالجة' }
];

// App State
let currentSectionIndex = 0;
let viewMode = 'single'; // 'single' (focused section only) or 'all' (continuous scroll)
let completedSections = new Set();

// Prevent companion scripts from initializing the application twice.
window.codefyAppLoaded = true;

// Clear the safety timeout from index.html so .reveal elements stay animated
if (window.__jsReadyTimer) {
    clearTimeout(window.__jsReadyTimer);
}

document.addEventListener('DOMContentLoaded', function() {
    initApp();
    initializeValidationTool();  // This function is now in analyzer_import_sheets.js
    initializeTabSwitching();
    // Initialize theme functionality with unique names to avoid conflicts
    initializeCodefyThemeSystem();
    // Initialize collapsible sidebar functionality
    initializeCollapsibleSidebar();
});


// Theme Management System with unique function names to avoid conflicts
function initializeCodefyThemeSystem() {
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeIconElement = document.getElementById('theme-icon');
    const sunPathElement = document.getElementById('sun-path');
    const moonPathElement = document.getElementById('moon-path');
    
    // Desktop theme toggle elements
    const desktopThemeButton = document.getElementById('desktop-theme-toggle');
    const desktopThemeIcon = document.getElementById('desktop-theme-icon');
    const desktopSunPath = document.getElementById('desktop-sun-path');
    const desktopMoonPath = document.getElementById('desktop-moon-path');
    
    // Check for saved theme preference or respect OS preference
    const currentThemePref = localStorage.getItem('theme') || 
                         (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-blue' : 'light');
    
    // Apply the saved theme on page load
    if (currentThemePref === 'dark-blue') {
        document.documentElement.setAttribute('data-theme', 'dark-blue');
        // Update mobile theme icon
        if (sunPathElement && moonPathElement) {
            sunPathElement.classList.add('hidden');
            moonPathElement.classList.remove('hidden');
        }
        // Update desktop theme icon
        if (desktopSunPath && desktopMoonPath) {
            desktopSunPath.classList.add('hidden');
            desktopMoonPath.classList.remove('hidden');
        }
    } else if (currentThemePref === 'sunny-light') {
        document.documentElement.setAttribute('data-theme', 'sunny-light');
        // Update mobile theme icon
        if (sunPathElement && moonPathElement) {
            sunPathElement.classList.remove('hidden');
            moonPathElement.classList.add('hidden');
        }
        // Update desktop theme icon
        if (desktopSunPath && desktopMoonPath) {
            desktopSunPath.classList.remove('hidden');
            desktopMoonPath.classList.add('hidden');
        }
    } else {
        document.documentElement.removeAttribute('data-theme');
        // Update mobile theme icon
        if (sunPathElement && moonPathElement) {
            sunPathElement.classList.remove('hidden');
            moonPathElement.classList.add('hidden');
        }
        // Update desktop theme icon
        if (desktopSunPath && desktopMoonPath) {
            desktopSunPath.classList.remove('hidden');
            desktopMoonPath.classList.add('hidden');
        }
    }
    
    // Function to update theme elements
    function updateThemeDisplay(isDark) {
        if (isDark) {
            // Dark theme active
            if (sunPathElement && moonPathElement) {
                sunPathElement.classList.add('hidden');
                moonPathElement.classList.remove('hidden');
            }
            if (desktopSunPath && desktopMoonPath) {
                desktopSunPath.classList.add('hidden');
                desktopMoonPath.classList.remove('hidden');
            }
        } else {
            // Light theme active
            if (sunPathElement && moonPathElement) {
                sunPathElement.classList.remove('hidden');
                moonPathElement.classList.add('hidden');
            }
            if (desktopSunPath && desktopMoonPath) {
                desktopSunPath.classList.remove('hidden');
                desktopMoonPath.classList.add('hidden');
            }
        }
    }
    
    // Function to update theme display for sunny theme
    function updateThemeDisplaySunny() {
        // Light theme active (same as regular light)
        if (sunPathElement && moonPathElement) {
            sunPathElement.classList.remove('hidden');
            moonPathElement.classList.add('hidden');
        }
        if (desktopSunPath && desktopMoonPath) {
            desktopSunPath.classList.remove('hidden');
            desktopMoonPath.classList.add('hidden');
        }
    }
    
    // Toggle theme when mobile button is clicked
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', function() {
            toggleCodefyTheme();
        });
    }
    
    // Toggle theme when desktop button is clicked
    if (desktopThemeButton) {
        desktopThemeButton.addEventListener('click', function() {
            toggleCodefyTheme();
        });
    }
    
    // Common toggle function with unique name
    function toggleCodefyTheme() {
        const currentThemeAttribute = document.documentElement.getAttribute('data-theme');
        
        if (currentThemeAttribute === 'dark-blue') {
            // Switch to sunny light theme
            document.documentElement.setAttribute('data-theme', 'sunny-light');
            localStorage.setItem('theme', 'sunny-light');
            updateThemeDisplaySunny();
        } else if (currentThemeAttribute === 'sunny-light') {
            // Switch to regular light theme
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            updateThemeDisplay(false);
        } else {
            // Switch to dark blue theme
            document.documentElement.setAttribute('data-theme', 'dark-blue');
            localStorage.setItem('theme', 'dark-blue');
            updateThemeDisplay(true);
        }
        
        // Optional: Add a subtle transition effect
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    }
}

function initApp() {
    // Load saved progress from localStorage
    loadProgress();
    
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
    
    // Initialize Scroll Reveal Animations
    initScrollReveal();
    
    // Initialize Analysis Configuration (now in separate module)
    initializeAnalysisConfig();  // This function is now in analyzer_import_sheets.js
    
    // Render initial progress
    updateProgressUI();
    updateFinalCTAVisibility();
}

/**
 * Scroll Reveal Animation Observer
 * Elements with .reveal class start hidden (opacity:0) and fade in when scrolled into view
 */
function initScrollReveal() {
    const revealElements = document.querySelectorAll('.reveal');
    if (!revealElements.length) return;

    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    revealObserver.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.08,
            rootMargin: '0px 0px -40px 0px',
        }
    );

    revealElements.forEach((el) => revealObserver.observe(el));
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
    } else {
        completedSections.add(sectionId);
    }
    saveProgress();
    updateProgressUI();
    updateSectionStepper(sectionId);
    updateFinalCTAVisibility();
}

/**
 * Final CTA Visibility — shows the celebration message only after all 6 sections are completed
 */
function updateFinalCTAVisibility() {
    const finalCta = document.querySelector('[data-final-cta]');
    if (!finalCta) return;

    const allCompleted = completedSections.size === SECTIONS.length;
    if (allCompleted) {
        finalCta.classList.remove('hidden');
        finalCta.classList.add('is-visible');
        showToast('🎉 مبروك! خلصت كل الدليل بالكامل!', 'success');  // This function is now in analyzer_import_sheets.js
    } else {
        finalCta.classList.add('hidden');
        finalCta.classList.remove('is-visible');
    }
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
                // Ensure scroll to top happens after showing the section
                setTimeout(() => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 100);
            }
        });
    }

    const nextBtn = document.getElementById('btn-next-section');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentSectionIndex < SECTIONS.length - 1) {
                currentSectionIndex++;
                showCurrentSection(true);
                // Ensure scroll to top happens after showing the section
                setTimeout(() => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 100);
            }
        });
    }

    const finishBtn = document.getElementById('btn-finish-guide');
    if (finishBtn) {
        finishBtn.addEventListener('click', () => {
            showToast('مبروك يا بطل! كده انت جاهز تدير شغلك بكل ثقة 🚀', 'success');  // This function is now in analyzer_import_sheets.js
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

function updateStepperCompletionButton(sectionId) {
    updateSectionStepper(sectionId);
}

/**
 * Section Switching & Single Section Focused Mode
 */
function initSectionMode() {
    // Read URL hash on load
    const hash = window.location.hash.replace('#', '');
    const foundIndex = SECTIONS.findIndex(s => s.id === hash);
    currentSectionIndex = foundIndex !== -1 ? foundIndex : 0;


    // Apply initial view mode
    applyViewMode();
    showCurrentSection(false);


    // Hash change event listener
    window.addEventListener('hashchange', function() {
        const newHash = window.location.hash.replace('#', '');
        const targetIndex = SECTIONS.findIndex(s => s.id === newHash);
        if (targetIndex !== -1 && targetIndex !== currentSectionIndex) {
            currentSectionIndex = targetIndex;
            showCurrentSection(true);
            // Ensure scroll to top happens after showing the section
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
        }
    });
}

function setViewMode(mode) {
    if (viewMode === mode) return;
    viewMode = mode;
    applyViewMode();
    showCurrentSection(true);
    
    // Always scroll to top when changing view mode
    setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
    
    if (mode === 'single') {
        showToast('تم تفعيل وضع التركيز (عرض قسم بقسم) 🎯', 'info');  // This function is now in analyzer_import_sheets.js
    } else {
        showToast('تم تفعيل وضع التصفح الكامل (كل الأقسام) 📜', 'info');  // This function is now in analyzer_import_sheets.js
    }
}

function applyViewMode() {
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

/**
 * Sidebar Navigation & Mobile Drawer
 */
function initializeCollapsibleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (!sidebar || !sidebarToggle || !sidebarOverlay) return;

    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('open');
    });

    sidebarOverlay.addEventListener('click', function() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    });

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
                // Ensure scroll to top happens after showing the section
                setTimeout(() => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 100); // Small delay to ensure section is rendered
                if (window.innerWidth < 1024) {
                    closeSidebar();
                }
            }
        });
    });
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (sidebar) sidebar.classList.remove('open');
    if (sidebarOverlay) sidebarOverlay.classList.remove('open');
}

/**
 * Search Functionality
 */
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-suggestions');
    const allContent = document.querySelector('main');
    
    if (!searchInput || !searchResults || !allContent) return;
    
    // Sample search suggestions
    const suggestions = [
        { text: 'تسجيل الدخول', section: 'login' },
        { text: 'رفع المشاريع', section: 'bulk-import' },
        { text: 'المورد والمركبة', section: 'relationships' },
        { text: 'توزيع الشغل', section: 'assignments' },
        { text: 'التسعير', section: 'pricing' },
        { text: 'مراجعة الجاهزية', section: 'readiness' }
    ];
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        
        if (query === '') {
            searchResults.classList.add('hidden');
            return;
        }
        
        // Filter suggestions based on query
        const filtered = suggestions.filter(item => 
            item.text.toLowerCase().includes(query) || 
            item.section.toLowerCase().includes(query)
        );
        
        if (filtered.length > 0) {
            searchResults.innerHTML = '';
            filtered.forEach(item => {
                const li = document.createElement('li');
                li.className = 'px-4 py-3 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-b-0';
                li.innerHTML = `
                    <div class="font-bold text-slate-900">${item.text}</div>
                    <div class="text-xs text-slate-500 mt-1">القسم: ${SECTIONS.find(s => s.id === item.section)?.title || item.section}</div>
                `;
                li.addEventListener('click', function() {
                    // Navigate to section
                    if (viewMode === 'single') {
                        const sectionIndex = SECTIONS.findIndex(s => s.id === item.section);
                        if (sectionIndex !== -1) {
                            currentSectionIndex = sectionIndex;
                            showCurrentSection();
                        }
                    } else {
                        window.location.hash = item.section;
                    }
                    
                    // Clear search and hide results
                    searchInput.value = '';
                    searchResults.classList.add('hidden');
                    
                    // Close mobile sidebar if open
                    closeSidebar();
                });
                searchResults.appendChild(li);
            });
            searchResults.classList.remove('hidden');
        } else {
            searchResults.innerHTML = '<li class="px-4 py-3 text-center text-slate-500">لا توجد نتائج</li>';
            searchResults.classList.remove('hidden');
        }
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
    
    // Keyboard shortcuts for search
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
        }
        
        // Escape to clear search
        if (e.key === 'Escape' && searchInput === document.activeElement) {
            searchInput.value = '';
            searchResults.classList.add('hidden');
        }
    });
}

/**
 * Lightbox Modal for Images
 */
function initLightbox() {
    // Initialize lightbox triggers
    const triggers = document.querySelectorAll('.lightbox-trigger');
    
    triggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            
            const imgSrc = this.src || this.getAttribute('href') || this.querySelector('img')?.src;
            const caption = this.querySelector('figcaption')?.textContent || this.title || this.alt || '';
            
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            const lightboxCaption = document.getElementById('lightbox-caption');
            
            if (lightbox && lightboxImg) {
                lightboxImg.src = imgSrc;
                if (lightboxCaption) lightboxCaption.textContent = caption;
                
                // Show lightbox with fade-in effect
                lightbox.classList.remove('hidden');
                setTimeout(() => lightbox.classList.remove('opacity-0'), 10);
            }
        });
    });
    
    // Close lightbox
    const lightboxClose = document.getElementById('lightbox-close');
    const lightbox = document.getElementById('lightbox');
    
    if (lightboxClose && lightbox) {
        lightboxClose.addEventListener('click', function() {
            lightbox.classList.add('opacity-0');
            setTimeout(() => lightbox.classList.add('hidden'), 300);
        });
        
        // Close on clicking the backdrop
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
                lightbox.classList.add('opacity-0');
                setTimeout(() => lightbox.classList.add('hidden'), 300);
            }
        });
    }
}

/**
 * Tab Switching Functionality
 */
function initTabs() {
    // Initialize any generic tabs on the page
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabBtns.length === 0 || tabContents.length === 0) return;
    
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
        showToast('يا هلا بيك! لو محتاج أي استفسار فريق دعم كوديفاي في خدمتك دايماً 💬', 'info');  // This function is now in analyzer_import_sheets.js
    });
}

/**
 * Keyboard Shortcuts (Arrow keys & Ctrl+K)
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Arrow keys for navigation
        if (e.key === 'ArrowLeft' && currentSectionIndex > 0) {
            e.preventDefault();
            currentSectionIndex--;
            showCurrentSection();
        } else if (e.key === 'ArrowRight' && currentSectionIndex < SECTIONS.length - 1) {
            e.preventDefault();
            currentSectionIndex++;
            showCurrentSection();
        }
    });
}

// Note: Analysis Configuration functions have been moved to analyzer_import_sheets.js
// Functions like loadAnalysisConfig, saveAnalysisConfig, applyConfigToUI, etc.