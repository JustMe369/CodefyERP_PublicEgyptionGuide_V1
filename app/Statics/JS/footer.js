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
        if (!footer) return;

        const revealDistance = 200;
        let scheduled = false;
        function updateVisibility() {
            scheduled = false;
            const remaining = document.documentElement.scrollHeight - (window.scrollY + window.innerHeight);
            footer.classList.toggle('is-visible', remaining <= revealDistance);
        }
        function scheduleUpdate() {
            if (scheduled) return;
            scheduled = true;
            window.requestAnimationFrame(updateVisibility);
        }
        window.addEventListener('scroll', scheduleUpdate, { passive: true });
        window.addEventListener('resize', scheduleUpdate);
        scheduleUpdate();
    }

    // Expose helper globally
    window.initFloatingFooter = initFloatingFooter;
})();
