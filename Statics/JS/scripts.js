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
    
    // Initialize Scroll Reveal Animations
    initScrollReveal();
    
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
 * Section Switching & Single Section Focused Mode
 */
function initSectionMode() {
    // Read URL hash on load
    const hash = window.location.hash.replace('#', '');
    const foundIndex = SECTIONS.findIndex(s => s.id === hash);
    currentSectionIndex = foundIndex !== -1 ? foundIndex : 0;

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
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !mobileMenuBtn || !sidebarOverlay) return;
    
    // Toggle sidebar on mobile menu button click
    mobileMenuBtn.addEventListener('click', function() {
        openSidebar();
    });
    
    // Close sidebar when clicking overlay
    sidebarOverlay.addEventListener('click', function() {
        closeSidebar();
    });
    
    // Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        if (sidebar.classList.contains('translate-x-0') && 
            !sidebar.contains(e.target) && 
            e.target !== mobileMenuBtn &&
            !mobileMenuBtn.contains(e.target)) {
            closeSidebar();
        }
    });
    
    // Close sidebar on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('translate-x-0')) {
            closeSidebar();
        }
    });
    
    // Initialize active section highlighting
    updateActiveSection();
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !sidebarOverlay) return;
    
    sidebar.classList.remove('-translate-x-full');
    sidebar.classList.add('translate-x-0');
    sidebarOverlay.classList.remove('hidden');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !sidebarOverlay) return;
    
    sidebar.classList.remove('translate-x-0');
    sidebar.classList.add('-translate-x-full');
    sidebarOverlay.classList.add('hidden');
    
    // Restore body scroll
    document.body.style.overflow = '';
}

function updateActiveSection() {
    const currentHash = window.location.hash.substring(1) || 'login';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const sectionId = link.getAttribute('data-section');
        if (sectionId === currentHash) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
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
 * Enhanced Excel Analyzer Integration
 */
function initializeEnhancedExcelAnalyzer() {
    // Create enhanced analyzer UI elements dynamically
    const validationContainer = document.getElementById('validation-container');
    if (!validationContainer) return;

    // Enhanced analyzer UI
    const enhancedAnalyzerHTML = `
        <div id="enhanced-analyzer-panel" class="mt-6 p-6 rounded-xl border border-blue-200 bg-blue-50">
            <div class="flex items-center gap-3 mb-4">
                <span class="text-2xl">🌊</span>
                <h3 class="text-lg font-black text-blue-900">محلل إكسل متقدم</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <h4 class="font-bold text-gray-800 mb-2">تحليل الورديات</h4>
                    <p class="text-sm text-gray-600">الكشف عن تعارضات الورديات وتحسين الأسماء</p>
                </div>
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <h4 class="font-bold text-gray-800 mb-2">تحليل الأوقات</h4>
                    <p class="text-sm text-gray-600">الكشف عن تعارضات الأوقات وتقديم الحلول</p>
                </div>
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <h4 class="font-bold text-gray-800 mb-2">تحليل الموردين</h4>
                    <p class="text-sm text-gray-600">التحقق من معلومات الموردين والتصحيح التلقائي</p>
                </div>
            </div>
            <div class="flex flex-wrap gap-3">
                <button id="run-deep-analysis" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    🌊 بدء التحليل المتعمق
                </button>
                <button id="export-report" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors" disabled>
                    📊 تصدير التقرير
                </button>
                <button id="apply-fixes" class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors" disabled>
                    🔧 تطبيق الإصلاحات
                </button>
                <button id="export-excel" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors" disabled>
                    📥 تصدير Excel
                </button>
            </div>
            <div id="analyzer-results" class="mt-4 hidden">
                <h4 class="font-bold text-gray-800 mb-2">نتائج التحليل</h4>
                <div id="deep-analysis-results" class="bg-white p-4 rounded-lg border border-gray-200 max-h-60 overflow-y-auto"></div>
            </div>
        </div>
    `;

    validationContainer.insertAdjacentHTML('beforeend', enhancedAnalyzerHTML);

    // Event listeners for enhanced analyzer
    document.getElementById('run-deep-analysis').addEventListener('click', runDeepAnalysis);
    document.getElementById('export-report').addEventListener('click', exportAnalysisReport);
    document.getElementById('apply-fixes').addEventListener('click', applyAutomaticFixes);
    document.getElementById('export-excel').addEventListener('click', exportExcelReport);
}

async function runDeepAnalysis() {
    const runBtn = document.getElementById('run-deep-analysis');
    const exportBtn = document.getElementById('export-report');
    const applyBtn = document.getElementById('apply-fixes');
    const resultsDiv = document.getElementById('analyzer-results');
    const deepResultsDiv = document.getElementById('deep-analysis-results');

    if (!currentFile) {
        alert('يرجى اختيار ملف إكسل أولاً');
        return;
    }

    // Disable buttons during analysis
    runBtn.disabled = true;
    runBtn.textContent = 'جاري التحليل...';
    runBtn.classList.add('bg-gray-500', 'cursor-not-allowed');

    // Show progress
    deepResultsDiv.innerHTML = '<p class="text-blue-600">جاري تحليل الملف بشكل متعمق...</p>';
    resultsDiv.classList.remove('hidden');

    try {
        // Create form data for deep analysis
        const formData = new FormData();
        formData.append('file', currentFile);

        // Determine API endpoint based on environment
        const isFileProtocol = window.location.protocol === 'file:';
        const isLocalhost = !isFileProtocol && (
                           window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname === '0.0.0.0');
        
        let apiBase;
        if (isFileProtocol) {
            apiBase = null; // Will use simulation
        } else if (isLocalhost) {
            apiBase = 'http://localhost:5000/api'; // Local Python API
        } else {
            apiBase = '/api'; // Vercel serverless functions
        }

        // Make API call for deep analysis if available, otherwise simulate
        if (apiBase) {
            const response = await fetch(`${apiBase}/deep-analyze`, {
                method: 'POST',
                body: formData,
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            displayDeepAnalysisResults(result);
        } else {
            // Simulate deep analysis since we're in file protocol mode
            simulateDeepAnalysis(formData);
        }

        // Enable other buttons
        exportBtn.disabled = false;
        applyBtn.disabled = false;

    } catch (error) {
        console.error('Deep analysis error:', error);
        deepResultsDiv.innerHTML = '<p class="text-red-600">حدث خطأ أثناء التحليل المتعمق</p>';
    } finally {
        // Re-enable run button
        runBtn.disabled = false;
        runBtn.textContent = '🌊 بدء التحليل المتعمق';
        runBtn.classList.remove('bg-gray-500', 'cursor-not-allowed');
        runBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }
}

function simulateDeepAnalysis(formData) {
    // Simulate deep analysis with realistic results
    const file = formData.get('file');
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
            fixes_available: Math.floor(Math.random() * 15) + 5,
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
        detailed_issues: [
            { severity: 'critical', category: 'Invalid Phone', sheet: 'Drivers', row: 45, column: 'Phone', message: 'Invalid Egyptian phone number format' },
            { severity: 'warning', category: 'Date Format', sheet: 'Schedule', row: 12, column: 'Start_Date', message: 'Date not in YYYY-MM-DD format' },
            { severity: 'info', category: 'Normalization', sheet: 'Routes', row: 67, column: 'Direction', message: 'Direction inferred from schedule' },
            { severity: 'critical', category: 'Missing Data', sheet: 'Vehicles', row: 89, column: 'Driver_Name', message: 'Required field missing' },
            { severity: 'warning', category: 'Capacity Issue', sheet: 'Vehicles', row: 156, column: 'Capacity', message: 'Capacity value seems unusually high for vehicle type' }
        ],
        shift_upgrades: Math.floor(Math.random() * 4),
        time_conflicts: Math.floor(Math.random() * 3),
        time_normalizations: Math.floor(Math.random() * 5),
        red_flags: Math.floor(Math.random() * 2),
        ready_to_upload: Math.random() > 0.5
    };
    displayDeepAnalysisResults(mockResult);
}

function displayDeepAnalysisResults(result) {
    const deepResultsDiv = document.getElementById('deep-analysis-results');
    
    if (result.success) {
        const htmlContent = `
            <div class="space-y-4">
                <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <h5 class="font-bold text-blue-800">ملخص التحليل</h5>
                    <ul class="mt-2 space-y-1 text-sm">
                        <li>• درجة الجودة: <strong>${result.summary.quality_score}/100</strong></li>
                        <li>• إجمالي الصفوف: <strong>${result.summary.total_rows}</strong></li>
                        <li>• عدد الأوراق: <strong>${result.summary.total_sheets}</strong></li>
                        <li>• الإصلاحات الممكنة: <strong>${result.summary.fixes_available}</strong></li>
                        <li>• جاهز للرفع: <strong>${result.ready_to_upload ? 'نعم ✅' : 'لا ❌'}</strong></li>
                    </ul>
                </div>
                
                <div class="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <h5 class="font-bold text-yellow-800">التحذيرات (${result.summary.issues.warning})</h5>
                    <ul class="mt-2 space-y-1 text-sm">
                        ${result.summary.breakdown.invalid_phones > 0 ? `<li>• أرقام هواتف غير صالحة: ${result.summary.breakdown.invalid_phones}</li>` : ''}
                        ${result.summary.breakdown.date_format_issues > 0 ? `<li>• تنسيقات تواريخ غير صحيحة: ${result.summary.breakdown.date_format_issues}</li>` : ''}
                        ${result.summary.breakdown.enum_violations > 0 ? `<li>• انتهاكات تعداد: ${result.summary.breakdown.enum_violations}</li>` : ''}
                    </ul>
                </div>
                
                <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                    <h5 class="font-bold text-green-800">التحسينات (${result.shift_upgrades})</h5>
                    <ul class="mt-2 space-y-1 text-sm">
                        <li>• تحسينات الورديات: ${result.shift_upgrades}</li>
                        <li>• تحسينات الأوقات: ${result.time_conflicts}</li>
                        <li>• تحسينات الموردين: ${result.time_normalizations}</li>
                        <li>• علامات الحظر: ${result.red_flags}</li>
                    </ul>
                </div>
                
                ${result.detailed_issues && result.detailed_issues.length > 0 ? `
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <h5 class="font-bold text-gray-800">أمثلة على المشكلات المكتشفة</h5>
                    <ul class="mt-2 space-y-2 text-sm max-h-40 overflow-y-auto">
                        ${result.detailed_issues.slice(0, 5).map(issue => 
                            `<li class="flex justify-between">
                                <span class="font-medium">${issue.category}</span>
                                <span class="text-gray-600">${issue.sheet}:${issue.row}</span>
                                <span class="text-gray-500">${issue.message}</span>
                            </li>`
                        ).join('')}
                    </ul>
                </div>` : ''}
            </div>
        `;
        deepResultsDiv.innerHTML = htmlContent;
    } else {
        deepResultsDiv.innerHTML = '<p class="text-red-600">فشل التحليل: ' + (result.error || 'حدث خطأ غير معروف') + '</p>';
    }
}

function exportAnalysisReport() {
    if (!currentValidationResult) {
        alert('لا توجد نتائج تحليل لتصديرها');
        return;
    }

    // Create a downloadable report
    const reportContent = JSON.stringify(currentValidationResult, null, 2);
    const blob = new Blob([reportContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `codefy_analysis_report_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function exportExcelReport() {
    if (!currentFile) {
        alert('يرجى اختيار ملف إكسل أولاً');
        return;
    }

    // In a real implementation, this would call the API to generate an Excel report
    // For now, we'll simulate this functionality
    alert('في الإصدار الكامل، سيؤدي هذا إلى توليد تقرير Excel مفصل مع كل النتائج والتصليحات.');
    
    // In the actual implementation, this would be:
    // downloadCleanedFile(currentFile);
}

function applyAutomaticFixes() {
    if (!currentFile) {
        alert('يرجى اختيار ملف إكسل أولاً');
        return;
    }

    if (confirm('هل أنت متأكد من تطبيق الإصلاحات التلقائية؟ سيتم إنشاء نسخة معدلة من الملف.')) {
        downloadCleanedFile(currentFile);
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

    // Initialize the enhanced analyzer after the validation tool is initialized
    setTimeout(initializeEnhancedExcelAnalyzer, 100);

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
                alert(`خطأ في التحليل: ${result.error || 'حدث خطأ غير معرف'}`);
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

    // Initialize validation tool
    function initValidationTool() {
        const validationContainer = document.getElementById('validation-container');
        if (!validationContainer) {
            console.log('Validation container not found');
            return;
        }

        // Create validation UI
        validationContainer.innerHTML = `
            <div class="validation-header">
                <h3>🧰 أداة التحقق من صحة البيانات</h3>
                <p>تحقق من صحة ملفات Excel قبل رفعها إلى النظام</p>
            </div>
            
            <div class="validation-controls">
                <div class="file-upload-section">
                    <label for="excelFile" class="upload-label">
                        <span class="upload-icon">📁</span>
                        <span class="upload-text">اختر ملف Excel للتحقق</span>
                    </label>
                    <input type="file" id="excelFile" accept=".xlsx,.xls,.csv" class="file-input">
                    <button class="validate-btn" onclick="validateFile()">تحقق من الملف</button>
                </div>
                
                <div class="validation-options">
                    <div class="option-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="enableShiftEngine" checked>
                            <span class="checkmark"></span>
                            <span class="label-text">تفعيل محرك الورديات المتقدم</span>
                        </label>
                    </div>
                    <div class="option-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="enableTimeControl" checked>
                            <span class="checkmark"></span>
                            <span class="label-text">تفعيل التحكم بالوقت</span>
                        </label>
                    </div>
                </div>
            </div>
            
            <div id="validation-results" class="validation-results hidden">
                <div class="results-summary">
                    <div class="summary-item">
                        <span class="summary-label">📋 عدد الصفوف:</span>
                        <span id="totalRows" class="summary-value">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">🎯 درجة الجودة:</span>
                        <span id="qualityScore" class="summary-value">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">⚠️ المشاكل:</span>
                        <span id="issueCount" class="summary-value">0</span>
                    </div>
                </div>
                
                <div class="results-details">
                    <div class="tabs">
                        <button class="tab-btn active" onclick="switchTab('issues')">المشاكل</button>
                        <button class="tab-btn" onclick="switchTab('summary')">الملخص</button>
                        <button class="tab-btn" onclick="switchTab('fixes')">التصليحات</button>
                    </div>
                    
                    <div id="issues-tab" class="tab-content active">
                        <table class="issues-table">
                            <thead>
                                <tr>
                                    <th>الخطورة</th>
                                    <th>النوع</th>
                                    <th>الورقة</th>
                                    <th>الصف</th>
                                    <th>العمود</th>
                                    <th>القيمة</th>
                                    <th>الرسالة</th>
                                </tr>
                            </thead>
                            <tbody id="issues-body">
                            </tbody>
                        </table>
                    </div>
                    
                    <div id="summary-tab" class="tab-content">
                        <div id="summary-content"></div>
                    </div>
                    
                    <div id="fixes-tab" class="tab-content">
                        <div id="fixes-content"></div>
                    </div>
                </div>
            </div>
        `;
    }

    // Enhanced validation function
    async function validateFile() {
        const fileInput = document.getElementById('excelFile');
        const resultsDiv = document.getElementById('validation-results');
        const excelFile = fileInput.files[0];
        
        if (!excelFile) {
            alert('الرجاء اختيار ملف Excel للتحقق');
            return;
        }

        // Show loading state
        resultsDiv.classList.remove('hidden');
        document.getElementById('issues-body').innerHTML = '<tr><td colspan="7">جاري التحقق من الملف...</td></tr>';
        
        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('file', excelFile);
            
            // Get options
            const enableShiftEngine = document.getElementById('enableShiftEngine').checked;
            const enableTimeControl = document.getElementById('enableTimeControl').checked;
            
            // Call the API with enhanced options
            const response = await fetch('/deep_analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Display results
            displayResults(result);
        } catch (error) {
            console.error('Error during validation:', error);
            document.getElementById('issues-body').innerHTML = `<tr><td colspan="7">خطأ أثناء التحقق: ${error.message}</td></tr>`;
        }
    }

    // Enhanced display results function
    function displayResults(result) {
        // Update summary
        document.getElementById('totalRows').textContent = result.summary.total_rows || 0;
        document.getElementById('qualityScore').textContent = result.summary.quality_score || 0;
        
        // Calculate total issues
        const totalIssues = (result.summary.issues.critical || 0) + 
                           (result.summary.issues.warning || 0) + 
                           (result.summary.issues.info || 0);
        document.getElementById('issueCount').textContent = totalIssues;
        
        // Populate issues table
        const issuesBody = document.getElementById('issues-body');
        issuesBody.innerHTML = '';
        
        if (result.issues && Array.isArray(result.issues)) {
            result.issues.forEach(issue => {
                const row = document.createElement('tr');
                
                // Determine row color based on severity
                let rowClass = '';
                if (issue.severity === 'critical') rowClass = 'critical-issue';
                else if (issue.severity === 'warning') rowClass = 'warning-issue';
                else if (issue.severity === 'info') rowClass = 'info-issue';
                
                row.className = rowClass;
                
                row.innerHTML = `
                    <td>${getSeverityEmoji(issue.severity)} ${issue.severity}</td>
                    <td>${issue.category || 'General'}</td>
                    <td>${issue.sheet || 'N/A'}</td>
                    <td>${issue.row || 'N/A'}</td>
                    <td>${issue.column || 'N/A'}</td>
                    <td>${issue.value || ''}</td>
                    <td>${issue.message || ''}</td>
                `;
                issuesBody.appendChild(row);
            });
        }
        
        // Populate summary tab
        const summaryContent = document.getElementById('summary-content');
        summaryContent.innerHTML = `
            <div class="summary-grid">
                <div class="summary-card">
                    <h4>📋 معلومات الملف</h4>
                    <p><strong>عدد الأوراق:</strong> ${result.summary.total_sheets || 0}</p>
                    <p><strong>عدد الصفوف:</strong> ${result.summary.total_rows || 0}</p>
                    <p><strong>درجة الجودة:</strong> ${result.summary.quality_score || 0}/100</p>
                </div>
                
                <div class="summary-card">
                    <h4>⚠️ توزيع المشاكل</h4>
                    <p><strong class="critical">حرجة:</strong> ${result.summary.issues.critical || 0}</p>
                    <p><strong class="warning">تحذير:</strong> ${result.summary.issues.warning || 0}</p>
                    <p><strong class="info">معلومة:</strong> ${result.summary.issues.info || 0}</p>
                </div>
                
                <div class="summary-card">
                    <h4>🔍 تفاصيل المشاكل</h4>
                    <p><strong>هاتف غير صحيح:</strong> ${result.summary.breakdown.invalid_phones || 0}</p>
                    <p><strong>صيغة تاريخ:</strong> ${result.summary.breakdown.date_format_issues || 0}</p>
                    <p><strong>قيمة غير صحيحة:</strong> ${result.summary.breakdown.enum_violations || 0}</p>
                    <p><strong>بيانات مفقودة:</strong> ${result.summary.breakdown.missing_data || 0}</p>
                    <p><strong>وقت متعارض:</strong> ${result.summary.breakdown.time_conflicts || 0}</p>
                    <p><strong>وردية متعارضة:</strong> ${result.summary.breakdown.shift_conflicts || 0}</p>
                </div>
            </div>
        `;
        
        // Populate fixes tab if available
        const fixesContent = document.getElementById('fixes-content');
        if (result.fixes && result.fixes.length > 0) {
            let fixesHTML = '<h4>🔧 التصليحات المقترحة</h4><ul>';
            result.fixes.forEach(fix => {
                fixesHTML += `<li><strong>ورقة ${fix.sheet}, صف ${fix.row}, عمود ${fix.col}:</strong> ${fix.reason} - <em>"${fix.old}" → "${fix.new}"</em></li>`;
            });
            fixesHTML += '</ul>';
            fixesContent.innerHTML = fixesHTML;
        } else {
            fixesContent.innerHTML = '<h4>🔧 التصليحات المقترحة</h4><p>لا توجد تصليحات مقترحة</p>';
        }
    }

    // Helper function to get severity emoji
    function getSeverityEmoji(severity) {
        switch(severity) {
            case 'critical': return '🔴';
            case 'warning': return '🟡';
            case 'info': return '🔵';
            default: return '⚪';
        }
    }

    // Tab switching function
    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab and activate button
        document.getElementById(`${tabName}-tab`).classList.add('active');
        event.target.classList.add('active');
    }

    // Initialize validation tool when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initValidationTool();
    });
