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
    const sunPathElement = document.getElementById('sun-path');
    const moonPathElement = document.getElementById('moon-path');
    const smartThemeButton = document.getElementById('smart-theme-toggle');
    const smartSunPath = document.getElementById('smart-sun-path');
    const smartMoonPath = document.getElementById('smart-moon-path');
    const themeButtons = [themeToggleButton, smartThemeButton].filter(Boolean);
    const iconPairs = [
        [sunPathElement, moonPathElement],
        [smartSunPath, smartMoonPath]
    ];

    function applyTheme(theme) {
        const isDark = theme === 'dark-blue';
        document.documentElement.setAttribute('data-theme', isDark ? 'dark-blue' : 'light');
        localStorage.setItem('theme', isDark ? 'dark-blue' : 'light');

        iconPairs.forEach(function(pair) {
            if (!pair[0] || !pair[1]) return;
            pair[0].classList.toggle('hidden', isDark);
            pair[1].classList.toggle('hidden', !isDark);
        });

        themeButtons.forEach(function(button) {
            button.setAttribute('aria-pressed', String(isDark));
            button.setAttribute('aria-label', isDark ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن');
            button.setAttribute('title', isDark ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن');
        });
    }

    function toggleTheme() {
        const nextTheme = document.documentElement.getAttribute('data-theme') === 'dark-blue'
            ? 'light'
            : 'dark-blue';
        applyTheme(nextTheme);
    }

    applyTheme(localStorage.getItem('theme') === 'dark-blue' ? 'dark-blue' : 'light');
    themeButtons.forEach(function(button) {
        button.addEventListener('click', toggleTheme);
    });

    window.codefyThemeController = { applyTheme: applyTheme, toggleTheme: toggleTheme };
}

function initApp() {
    // Initialize viewMode to single by default if not set
    if (typeof viewMode === 'undefined' || !viewMode) {
        viewMode = 'single';
    }
    
    // Load saved progress from localStorage
    loadProgress();
    
    // Initialize View Mode & Section Navigation
    initSectionMode();
    
    // Initialize View Mode Toggle Buttons
    initViewModeToggle();
    
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
 * Initialize View Mode Toggle Buttons
 */
function initViewModeToggle() {
    const singleModeBtns = document.querySelectorAll('.btn-mode-single');
    const allModeBtns = document.querySelectorAll('.btn-mode-all');
    
    // Set initial active state based on current viewMode
    if (viewMode === 'single') {
        singleModeBtns.forEach(btn => btn.classList.add('active'));
        allModeBtns.forEach(btn => btn.classList.remove('active'));
    } else {
        singleModeBtns.forEach(btn => btn.classList.remove('active'));
        allModeBtns.forEach(btn => btn.classList.add('active'));
    }
    
    // Add event listeners to single mode buttons
    singleModeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            setViewMode('single');
            
            // Update active states
            singleModeBtns.forEach(b => b.classList.add('active'));
            allModeBtns.forEach(b => b.classList.remove('active'));
        });
    });
    
    // Add event listeners to all mode buttons
    allModeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            setViewMode('all');
            
            // Update active states
            singleModeBtns.forEach(b => b.classList.remove('active'));
            allModeBtns.forEach(b => b.classList.add('active'));
        });
    });
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
    const footerFill = document.getElementById('footer-progress-fill');
    
    if (percentElem) percentElem.textContent = `${percent}%`;
    if (countElem) countElem.textContent = `${completed} من ${total}`;
    if (fillElem) fillElem.style.width = `${percent}%`;
    if (footerFill) footerFill.style.width = `${percent}%`;
    
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

    const currentSec = SECTIONS[currentSectionIndex] || { title: '', icon: '📄' };
    const prevSec = currentSectionIndex > 0 ? SECTIONS[currentSectionIndex - 1] : null;
    const nextSec = currentSectionIndex < SECTIONS.length - 1 ? SECTIONS[currentSectionIndex + 1] : null;
    const isDone = completedSections.has(sectionId);
    const progressPct = Math.round((completedSections.size / SECTIONS.length) * 100);

    stepperContainer.innerHTML = `
        <div class="stepper-dock-row">
            <!-- Stepper Prev Button -->
            ${prevSec ? `
                <button type="button" id="btn-prev-section" class="stepper-nav-btn text-start" title="العودة إلى: ${prevSec.title}">
                    <span aria-hidden="true" class="text-base">➔</span>
                    <span class="flex items-center gap-1.5">
                        <span>${prevSec.icon}</span>
                        <span class="font-bold">${prevSec.title}</span>
                    </span>
                </button>
            ` : `
                <button type="button" class="stepper-nav-btn disabled" disabled aria-disabled="true">
                    <span aria-hidden="true">➔</span>
                    <span class="text-xs text-slate-400">بداية الدليل</span>
                </button>
            `}

            <!-- Stepper Center Capsule -->
            <div class="stepper-center-capsule">
                <div class="stepper-section-badge" title="القسم الحالي: ${currentSec.title}">
                    <span class="water-droplet-dot" aria-hidden="true"></span>
                    <span class="truncate">${currentSec.icon} ${currentSec.title}</span>
                </div>

                <button type="button" id="btn-toggle-done" class="btn-toggle-done-pill ${isDone ? 'is-done' : ''}" title="${isDone ? 'إلغاء تعليم الإنجاز' : 'علّم هذا القسم كمنجز'}">
                    <span>${isDone ? '✓ تم الإنجاز' : '○ علّم كمنجز'}</span>
                </button>

                <div class="water-progress-track" title="إجمالي إنجاز الدليل: ${progressPct}%" aria-hidden="true">
                    <div id="footer-progress-fill" class="water-progress-fill" style="width: ${progressPct}%;"></div>
                </div>
            </div>

            <!-- Stepper Next Button / Finish -->
            ${nextSec ? `
                <button type="button" id="btn-next-section" class="stepper-nav-btn primary text-end" title="الانتقال إلى: ${nextSec.title}">
                    <span class="flex items-center gap-1.5">
                        <span class="font-bold">${nextSec.title}</span>
                        <span>${nextSec.icon}</span>
                    </span>
                    <span aria-hidden="true" class="text-base">←</span>
                </button>
            ` : `
                <button type="button" id="btn-finish-guide" class="stepper-nav-btn finish text-end" title="إنهاء الدليل بالكامل">
                    <span class="flex items-center gap-1.5 font-black">
                        <span>تم الانتهاء!</span>
                        <span>🎉</span>
                    </span>
                    <span aria-hidden="true" class="text-base">✓</span>
                </button>
            `}
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

    // Set default view mode to 'single' if not already set
    if (!viewMode) {
        viewMode = 'single';
    }

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
        
        // Make sure only the current section is visible in single mode
        if (typeof showCurrentSection === 'function') {
            setTimeout(() => {
                showCurrentSection(false);
            }, 0);
        }
    } else {
        document.body.classList.remove('single-section-mode');
        document.body.classList.add('all-sections-mode');
        modeSingleBtns.forEach(b => b.classList.remove('active'));
        modeAllBtns.forEach(b => b.classList.add('active'));
        
        // Ensure all sections are visible in all mode
        document.querySelectorAll('.section-content').forEach(sec => {
            sec.classList.remove('hidden');
            sec.classList.remove('active-section');
            sec.style.display = 'block';
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
        // Hide all sections first
        document.querySelectorAll('.section-content').forEach(sec => {
            sec.classList.add('hidden');
            sec.classList.remove('active-section');
        });
        
        // Then show only the current section
        const targetSection = document.getElementById(currentSec.id);
        if (targetSection) {
            targetSection.classList.remove('hidden');
            targetSection.classList.add('active-section');
            
            // Make sure it's visible by removing any potential conflicting classes
            targetSection.style.display = 'block';
        }
        
        // Update Bottom Stepper Footer inside active section
        updateSectionStepper(currentSec.id);
        
        if (shouldScroll) {
            // Use a slight delay to ensure DOM updates are complete before scrolling
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 50);
        }
    } else {
        // In All Sections mode, show all sections and scroll to target section
        document.querySelectorAll('.section-content').forEach(sec => {
            sec.classList.remove('hidden');
            sec.classList.remove('active-section');
            sec.style.display = 'block';
        });
        
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
                if (typeof mermaid.run === 'function') {
                    mermaid.run({ querySelector: '#' + currentSec.id + ' .mermaid' });
                } else if (typeof mermaid.init === 'function') {
                    mermaid.init(undefined, document.querySelectorAll('#' + currentSec.id + ' .mermaid'));
                } else if (typeof mermaid.contentLoaded === 'function') {
                    mermaid.contentLoaded();
                }
            } catch (e) {
                console.warn('Mermaid re-render failed:', e);
            }
        }
}

/**
 * Sidebar Navigation & Mobile Drawer
 */
function initializeCollapsibleSidebar() {
    // Sidebar click handlers are managed by the inline script in
    // index.html for comprehensive toggle handling (overlay opacity,
    // icon switching, body scroll). This function handles navigation only.

    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (!sidebar || !sidebarOverlay) return;

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
                setTimeout(() => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }, 100);
                if (window.innerWidth < 1024 && typeof closeSidebar === 'function') {
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
 * Amazing Sidebar Collapse Button - Dynamic Animations & Interactions
 */
function initializeCollapseButton() {
    console.log('[CollapseButton] Initializing...');
    const collapseBtn = document.getElementById('sidebar-collapse-toggle');
    const sidebar = document.getElementById('sidebar');
    const body = document.body;
    
    if (!collapseBtn || !sidebar) {
        console.error('[CollapseButton] Missing elements:', { collapseBtn: !!collapseBtn, sidebar: !!sidebar });
        return;
    }
    
    console.log('[CollapseButton] Elements found, attaching listeners');
    
    const particlesContainer = collapseBtn.querySelector('.collapse-particles');
    
    // Particle burst on click
    function createParticleBurst() {
        if (!particlesContainer) return;
        
        const particleCount = 12;
        const particles = [];
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'collapse-particle';
            
            // Random angle for particle spread
            const angle = (i / particleCount) * Math.PI * 2;
            const distance = 40 + Math.random() * 30;
            const tx = Math.cos(angle) * distance;
            const ty = Math.sin(angle) * distance;
            
            particle.style.setProperty('--tx', `${tx}px`);
            particle.style.setProperty('--ty', `${ty}px`);
            
            // Random color variation
            const hue = 200 + Math.random() * 80; // Blue to purple range
            particle.style.background = `hsl(${hue}, 80%, 60%)`;
            
            // Random size
            const size = 4 + Math.random() * 6;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            particlesContainer.appendChild(particle);
            particles.push(particle);
        }
        
        // Clean up particles after animation
        setTimeout(() => {
            particles.forEach(p => p.remove());
        }, 800);
    }
    
    // Ripple effect on click
    function createRipple(event) {
        const ripple = document.createElement('div');
        ripple.className = 'collapse-ripple';
        
        const rect = collapseBtn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        
        collapseBtn.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 500);
    }
    
    // Apply collapsed state with smooth transitions
    function applyCollapsedState(isCollapsed) {
        // Enable hardware acceleration for smoother animations
        sidebar.style.willChange = 'transform, width';
        collapseBtn.style.willChange = 'transform';
        
        // Update ARIA attributes and core classes
        collapseBtn.setAttribute('aria-expanded', String(!isCollapsed));
        body.classList.toggle('sidebar-is-collapsed', isCollapsed);
        sidebar.classList.toggle('sidebar-collapsed', isCollapsed);
        
        // Get icon elements
        const expandedIcon = collapseBtn.querySelector('.collapse-icon-expanded');
        const collapsedIcon = collapseBtn.querySelector('.collapse-icon-collapsed');
        const glowRing = collapseBtn.querySelector('.collapse-glow-ring');
        const pulseRing = collapseBtn.querySelector('.collapse-pulse-ring');
        
        // Update icons with extremely smooth transitions
        if (expandedIcon && collapsedIcon) {
            // Force GPU acceleration for icon animations
            expandedIcon.style.willChange = 'opacity, transform';
            collapsedIcon.style.willChange = 'opacity, transform';
            
            if (isCollapsed) {
                // Sidebar is collapsed: show collapsed icon (chevron left), hide expanded icon
                expandedIcon.style.opacity = '0';
                expandedIcon.style.transform = 'translate(-50%, -50%) scale(0.5) rotate(-90deg)';
                collapsedIcon.style.opacity = '1';
                collapsedIcon.style.transform = 'translate(-50%, -50%) scale(1) rotate(0deg)';
            } else {
                // Sidebar is expanded: show expanded icon (chevron right), hide collapsed icon
                expandedIcon.style.opacity = '1';
                expandedIcon.style.transform = 'translate(-50%, -50%) scale(1) rotate(0deg)';
                collapsedIcon.style.opacity = '0';
                collapsedIcon.style.transform = 'translate(-50%, -50%) scale(0.5) rotate(90deg)';
            }
            
            // Clean up willChange after animations complete
            setTimeout(() => {
                expandedIcon.style.willChange = 'auto';
                collapsedIcon.style.willChange = 'auto';
            }, 600);
        }
        
        // Trigger enhanced glow and pulse effects
        if (glowRing) {
            glowRing.style.opacity = '1';
            glowRing.style.transform = 'scale(1.1)';
            setTimeout(() => {
                glowRing.style.opacity = '0';
                glowRing.style.transform = 'scale(1)';
            }, 500);
        }
        if (pulseRing) {
            pulseRing.style.opacity = '1';
            pulseRing.style.transform = 'scale(1.2)';
            setTimeout(() => {
                pulseRing.style.opacity = '0';
                pulseRing.style.transform = 'scale(1)';
            }, 700);
        }
        
        // Update tooltip text and position with smooth transition
        const tooltip = collapseBtn.querySelector('.collapse-tooltip');
        if (tooltip) {
            // Fade out tooltip first
            tooltip.style.opacity = '0';
            setTimeout(() => {
                tooltip.textContent = isCollapsed ? 'توسيع الشريط الجانبي' : 'طي الشريط الجانبي';
                // Update tooltip position for RTL
                if (isCollapsed) {
                    tooltip.style.transform = 'translateY(-50%) translateX(0)';
                } else {
                    tooltip.style.transform = 'translateY(-50%) translateX(8px)';
                }
                // Fade tooltip back in
                tooltip.style.opacity = '1';
            }, 150);
        }
        
        // Clean up willChange after all sidebar animations complete
        setTimeout(() => {
            sidebar.style.willChange = 'auto';
            collapseBtn.style.willChange = 'auto';
        }, 400);
        
        // Save to localStorage
        localStorage.setItem('sidebar-collapsed', String(isCollapsed));
        console.log('[CollapseButton] State changed smoothly:', isCollapsed);
    }
    
    // Main click handler
    collapseBtn.addEventListener('click', function(event) {
        console.log('[CollapseButton] Clicked!');
        const isCurrentlyCollapsed = body.classList.contains('sidebar-is-collapsed');
        const newState = !isCurrentlyCollapsed;
        
        // Create particle burst
        createParticleBurst();
        
        // Create ripple
        createRipple(event);
        
        // Apply new state
        applyCollapsedState(newState);
        
        // Add haptic feedback via vibration API if available
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
        
        // Show toast notification
        const message = newState ? 'تم طي الشريط الجانبي ←' : 'تم توسيع الشريط الجانبي →';
        if (typeof showToast === 'function') {
            showToast(message, 'info');
        }
    });
    
    // Keyboard accessibility
    collapseBtn.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.click();
        }
    });
    
    // Initialize tooltip
    collapseBtn.addEventListener('mouseenter', function() {
        const tooltip = this.querySelector('.collapse-tooltip');
        if (tooltip) {
            tooltip.style.opacity = '1';
            tooltip.style.visibility = 'visible';
            tooltip.style.transform = 'translateY(-50%) translateX(0)';
        }
    });
    
    collapseBtn.addEventListener('mouseleave', function() {
        const tooltip = this.querySelector('.collapse-tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
            tooltip.style.transform = 'translateY(-50%) translateX(8px)';
        }
    });
    
    // Load saved state from localStorage
    const savedState = localStorage.getItem('sidebar-collapsed');
    if (savedState === 'true') {
        console.log('[CollapseButton] Loading saved state: collapsed');
        applyCollapsedState(true);
    }
    
    console.log('[CollapseButton] Initialization complete');
}

// Initialize collapse button when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCollapseButton);
} else {
    initializeCollapseButton();
}

// Also expose for debugging
window.codefyCollapseButton = {
    toggle: () => document.getElementById('sidebar-collapse-toggle')?.click(),
    getState: () => document.body.classList.contains('sidebar-is-collapsed')
};

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
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const lightboxClose = document.getElementById('lightbox-close');

    if (!lightbox || !lightboxImg) return;

    function open(src, caption) {
        lightboxImg.src = src;
        if (lightboxCaption && caption) lightboxCaption.textContent = caption;
        lightbox.classList.remove('hidden', 'opacity-0');
        lightbox.classList.add('flex', 'opacity-100');
        lightboxImg.classList.remove('scale-95');
        lightboxImg.classList.add('scale-100');
    }

    function close() {
        lightboxImg.classList.add('scale-95');
        lightboxImg.classList.remove('scale-100');
        lightbox.classList.add('opacity-0');
        lightbox.classList.remove('opacity-100');
        setTimeout(() => {
            lightbox.classList.add('hidden');
            lightbox.classList.remove('flex', 'opacity-0');
        }, 300);
    }

    // Initialize lightbox triggers
    const triggers = document.querySelectorAll('.lightbox-trigger');
    triggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const imgSrc = this.src || this.getAttribute('href') || (this.querySelector('img') && this.querySelector('img').src) || '';
            const caption = (this.querySelector('figcaption') && this.querySelector('figcaption').textContent) || this.title || this.alt || '';
            if (imgSrc) open(imgSrc, caption);
        });
    });

    // Close lightbox
    if (lightboxClose) {
        lightboxClose.addEventListener('click', close);
    }

    // Close on clicking the backdrop
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) close();
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !lightbox.classList.contains('hidden')) {
            close();
        }
    });
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

            // Re-render mermaid diagrams in the newly shown tab content
            if (window.mermaid) {
                try {
                    if (typeof mermaid.run === 'function') {
                        mermaid.run({ querySelector: '.tab-content[data-content="' + tabName + '"] .mermaid' });
                    } else if (typeof mermaid.init === 'function') {
                        mermaid.init(undefined, document.querySelectorAll('.tab-content[data-content="' + tabName + '"] .mermaid'));
                    }
                } catch (e) {
                    console.warn('Mermaid re-render failed:', e);
                }
            }
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
            
            // Re-render mermaid diagrams in the newly shown tab content
            if (window.mermaid) {
                try {
                    if (typeof mermaid.run === 'function') {
                        mermaid.run({ querySelector: '#bulk-import .tab-content[data-content="' + tabName + '"] .mermaid' });
                    } else if (typeof mermaid.init === 'function') {
                        mermaid.init(undefined, document.querySelectorAll('#bulk-import .tab-content[data-content="' + tabName + '"] .mermaid'));
                    }
                } catch (e) {
                    console.warn('Mermaid re-render failed:', e);
                }
            }
        });
    });
}

/**
 * Back to Top & Scroll Progress
 */
function initScrollProgress() {
    const progress = document.getElementById('scroll-progress');
    if (!progress) return;

    // Throttled scroll handler for better performance
    let ticking = false;
    
    function updateScrollProgress() {
        if (viewMode === 'all') {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = height ? (winScroll / height) * 100 : 0;
            
            // Animate the width with smoother transitions
            progress.style.width = scrolled + '%';
            
            // Add opacity effect based on scroll amount for more visual interest
            const opacity = Math.min(1, scrolled / 20); // Start fading in at 20% scroll
            progress.style.opacity = opacity > 0.2 ? 1 : 0.2 + (opacity * 0.8);
        } else {
            // In single section mode, calculate based on section index
            const pct = ((currentSectionIndex + 1) / SECTIONS.length) * 100;
            progress.style.width = pct + '%';
            progress.style.opacity = 1;
        }
        ticking = false;
    }

    function requestScrollUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateScrollProgress);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestScrollUpdate, { passive: true });
    
    // Also update when view mode changes
    // Note: This assumes there's a mechanism to call updateScrollProgress when viewMode changes
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