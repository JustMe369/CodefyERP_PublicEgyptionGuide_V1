/**
 * CodefyERP - Floating Water-Styled Footer Companion Script
 * Handles dock state, minimize/expand, smooth interactions, and Nile wave animations
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initFloatingFooter();
    });

    function initFloatingFooter() {
        const footer = document.getElementById('codefy-floating-footer');
        const minimizeToggle = document.getElementById('footer-minimize-btn');
        const scrollTopBtn = document.getElementById('footer-scroll-top');
        const helpBtn = document.getElementById('footer-help-btn');

        if (!footer) return;

        // Restore minimized preference if stored
        const isMinimized = localStorage.getItem('codefyFooterMinimized') === 'true';
        if (isMinimized) {
            footer.classList.add('is-minimized');
            document.body.classList.add('footer-minimized');
            if (minimizeToggle) {
                minimizeToggle.setAttribute('aria-expanded', 'false');
                minimizeToggle.setAttribute('title', 'توسيع شريط التنقل');
            }
        }

        // Minimize / Expand Toggle
        if (minimizeToggle) {
            minimizeToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const nowMinimized = footer.classList.toggle('is-minimized');
                document.body.classList.toggle('footer-minimized', nowMinimized);
                localStorage.setItem('codefyFooterMinimized', nowMinimized ? 'true' : 'false');
                minimizeToggle.setAttribute('aria-expanded', (!nowMinimized).toString());
                minimizeToggle.setAttribute('title', nowMinimized ? 'توسيع شريط التنقل' : 'تصغير شريط التنقل');
            });
        }

        // Quick Scroll to Top
        if (scrollTopBtn) {
            scrollTopBtn.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

        // Quick Help Trigger
        if (helpBtn) {
            helpBtn.addEventListener('click', function() {
                const floatHelp = document.getElementById('float-help');
                if (floatHelp) {
                    floatHelp.click();
                } else if (typeof showToast === 'function') {
                    showToast('فريق الدعم الفني في خدمتك دائماً عبر قنوات التواصل المباشرة 💬', 'info');
                }
            });
        }
    }

    // Expose helper globally
    window.initFloatingFooter = initFloatingFooter;
})();
