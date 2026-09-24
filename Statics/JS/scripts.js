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
let currentFile = null;
let currentValidationResult = null;

// Prevent companion scripts from initializing the application twice.
window.codefyAppLoaded = true;

// Clear the safety timeout from index.html so .reveal elements stay animated
if (window.__jsReadyTimer) {
    clearTimeout(window.__jsReadyTimer);
}

document.addEventListener('DOMContentLoaded', function() {
    initApp();
    initializeValidationTool();
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
    
    // Initialize Analysis Configuration
    initializeAnalysisConfig();
    
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
        showToast('🎉 مبروك! خلصت كل الدليل بالكامل!', 'success');
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
            showToast('مبروك يا بطل! كده انت جاهز تدير شغلك بكل ثقة 🚀', 'success');
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
        showToast('تم تفعيل وضع التركيز (عرض قسم بقسم) 🎯', 'info');
    } else {
        showToast('تم تفعيل وضع التصفح الكامل (كل الأقسام) 📜', 'info');
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
        showToast('يا هلا بيك! لو محتاج أي استفسار فريق دعم كوديفاي في خدمتك دايماً 💬', 'info');
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
            const endpoint = `${apiBase}/validate`;
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
        
        const downloadFormData = new FormData();
        downloadFormData.append('file', originalFile);

        // Use the appropriate API endpoint based on environment
        const endpoint = `${apiBase}/download-cleaned`;
        console.log(`Using download endpoint: ${endpoint}`);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: downloadFormData,
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
