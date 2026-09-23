/**
 * Navbar standalone companion script
 * Works cleanly whether loaded as standalone navbar component or alongside scripts.js
 */
document.addEventListener('DOMContentLoaded', function() {
    // If scripts.js is already running and handling the app, avoid redundant double initialization
    if (window.codefyAppLoaded || window.codefyNavbarLoaded) return;
    window.codefyAppLoaded = true;
    window.codefyNavbarLoaded = true;

    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const iconMenu = document.getElementById('icon-menu');
    const iconClose = document.getElementById('icon-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function() {
            const isClosed = sidebar.classList.contains('translate-x-full');
            if (isClosed) {
                sidebar.classList.remove('translate-x-full');
                sidebar.classList.add('translate-x-0');
                if (iconMenu) iconMenu.classList.add('hidden');
                if (iconClose) iconClose.classList.remove('hidden');
                if (sidebarOverlay) sidebarOverlay.classList.remove('hidden');
            } else {
                sidebar.classList.add('translate-x-full');
                sidebar.classList.remove('translate-x-0');
                if (iconMenu) iconMenu.classList.remove('hidden');
                if (iconClose) iconClose.classList.add('hidden');
                if (sidebarOverlay) sidebarOverlay.classList.add('hidden');
            }
        });
    }

    if (sidebarOverlay && sidebar) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.add('translate-x-full');
            sidebar.classList.remove('translate-x-0');
            if (iconMenu) iconMenu.classList.remove('hidden');
            if (iconClose) iconClose.classList.add('hidden');
            sidebarOverlay.classList.add('hidden');
        });
    }
});