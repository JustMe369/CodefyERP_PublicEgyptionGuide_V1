<?php
$asset = $SITE['assets'];
$currentSlug = codefy_current_slug();
?>
<div class="flex">
    <aside id="sidebar" aria-label="التنقل الرئيسي" class="sidebar-shell fixed inset-y-0 start-0 z-50 flex w-72 translate-x-full transform flex-col overflow-y-auto pt-5 pb-6 transition-all duration-300 ease-in-out lg:translate-x-0 shadow-xl backdrop-blur-2xl border-e">

        <div class="relative z-10 px-4 mb-5">
            <div id="brand-container" class="collapsible-brand-container flex items-center gap-3 flex-1 min-w-0">
                <div class="logo-container flex items-center justify-center flex-shrink-0">
                    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-blue-600 text-white shadow-md shadow-primary-500/25 ring-1 ring-white/08">
                        <img src="<?= $asset ?>/img/CodefyLogo.png" alt="شعار كوديفاي" class="h-6 w-6 object-contain" onerror="this.src='<?= $asset ?>/img/login.png'">
                    </div>
                </div>
                <div class="full-brand flex flex-col flex-1 min-w-0 transition-opacity duration-300" style="opacity: 1;">
                    <span class="brand-text text-lg font-extrabold text-white tracking-tight truncate"><?= e($SITE['name']) ?><span class="text-primary-400"><?= e($SITE['brand_suffix']) ?></span></span>
                    <span class="brand-subtitle block text-[10px] font-medium text-slate-500 truncate"><?= e($SITE['subtitle']) ?></span>
                </div>
                <button id="smart-theme-toggle" type="button" aria-label="تفعيل الوضع الداكن" aria-pressed="false" title="تفعيل الوضع الداكن" class="sidebar-icon-button theme-control flex-shrink-0" style="opacity: 1;">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" id="smart-sun-path" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" class="hidden" id="smart-moon-path" />
                    </svg>
                </button>
                <button id="sidebar-collapse-toggle" type="button" aria-label="طي الشريط الجانبي" aria-controls="sidebar" aria-expanded="true" title="طي الشريط الجانبي" class="sidebar-collapse-button" data-collapse-toggle>
                    <div class="collapse-particles absolute inset-0 pointer-events-none overflow-hidden rounded-full" aria-hidden="true"></div>
                    <div class="collapse-icon-wrapper relative flex h-full w-full items-center justify-center">
                        <svg class="collapse-icon-expanded absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-5 w-5 text-white transition-all duration-500 ease-out" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" /></svg>
                        <svg class="collapse-icon-collapsed absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-5 w-5 text-white opacity-0 scale-50 transition-all duration-500 ease-out" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" /></svg>
                        <div class="collapse-glow-ring absolute inset-0 rounded-full border-2 border-primary-400/50 opacity-0 transition-all duration-500"></div>
                        <div class="collapse-pulse-ring absolute -inset-1 rounded-full border-2 border-primary-500/30 opacity-0 transition-all duration-700"></div>
                    </div>
                    <span class="collapse-tooltip absolute -right-10 top-1/2 -translate-y-1/2 px-3 py-1.5 text-[11px] font-medium text-white bg-slate-900 rounded-lg shadow-lg opacity-0 invisible translate-x-2 transition-all duration-300 whitespace-nowrap pointer-events-none">طي الشريط الجانبي</span>
                </button>
            </div>
        </div>

        <div class="search-container relative z-10 px-4 mb-5 transition-opacity duration-300">
            <div class="relative">
                <input type="text" id="search-input" placeholder="ابحث في الدليل... (Ctrl+K)" autocomplete="off"
                    class="w-full py-2.5 ps-10 pe-4 rounded-xl border border-white/[0.05] bg-white/[0.02] focus:bg-white/[0.05] focus:outline-none focus:ring-1 focus:ring-primary-500/40 focus:border-primary-500/20 text-xs font-medium text-white placeholder-slate-600 transition-all duration-300 backdrop-blur-xl">
                <div class="absolute inset-y-0 start-0 flex items-center ps-3.5 pointer-events-none text-slate-600">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                </div>
            </div>
            <div id="search-suggestions" class="absolute z-30 mt-2 start-4 end-4 bg-slate-900/98 backdrop-blur-2xl border border-white/[0.05] rounded-xl shadow-2xl hidden overflow-hidden">
                <ul id="suggestions-list" class="py-2 max-h-64 overflow-y-auto divide-y divide-white/[0.03]"></ul>
            </div>
        </div>

        <div class="relative z-10 px-4 flex-1">
            <div class="navigation-header text-[10px] font-black text-slate-600 uppercase tracking-[0.15em] mb-4 px-2 transition-opacity duration-300">دليلك</div>
            <ul id="navigation-links" class="space-y-1.5">
                <?php foreach ($SECTIONS as $slug => $s): ?>
                    <li>
                        <a href="<?= e($slug) ?>.php" data-section="<?= e($slug) ?>"
                           class="collapsible-nav-item nav-link flex items-center justify-between rounded-2xl px-4 py-3.5 text-slate-300 hover:bg-white/10 hover:text-white transition-all duration-300 group border border-transparent hover:border-white/10">
                            <div class="collapsible-nav-content flex items-center gap-4">
                                <span class="collapsible-nav-icon text-2xl flex-shrink-0 group-hover:scale-125 transition-transform duration-300"><?= e($s['icon']) ?></span>
                                <div>
                                    <div class="nav-text font-bold text-sm text-slate-100 group-hover:text-primary-300 transition-opacity duration-300" style="opacity:1;"><?= e($s['title']) ?></div>
                                    <div class="nav-subtitle text-[11px] text-slate-500 group-hover:text-slate-400 transition-opacity duration-300" style="opacity:1;"><?= e($s['subtitle']) ?></div>
                                </div>
                            </div>
                            <span class="nav-badge section-check-badge text-slate-500 group-hover:text-primary-400 transition-colors" data-badge-section="<?= e($slug) ?>">○</span>
                        </a>
                    </li>
                <?php endforeach; ?>
            </ul>
        </div>

        <div class="footer-content relative z-10 px-5 pt-5 mt-auto border-t border-white/10 text-center transition-opacity duration-300">
            <p class="text-[11px] text-slate-500 m-0"><?= e($SITE['copyright']) ?></p>
        </div>
    </aside>

    <div id="sidebar-overlay" class="fixed inset-0 z-40 hidden bg-slate-950/70 backdrop-blur-md transition-all duration-500 lg:hidden opacity-0"></div>

    <script>
    (function () {
        'use strict';
        function boot() {
            var sidebar = document.getElementById('sidebar');
            var sidebarOverlay = document.getElementById('sidebar-overlay');
            var mobileMenuBtn = document.getElementById('mobile-menu-btn');
            var iconMenu = document.getElementById('icon-menu');
            var iconClose = document.getElementById('icon-close');
            if (!sidebar) return;
            var navLinks = document.querySelectorAll('.nav-link[data-section]');
            var currentSection = document.body.getAttribute('data-section');

            navLinks.forEach(function (link) {
                if (link.getAttribute('data-section') === currentSection) {
                    link.classList.add('active', 'bg-primary-500/20', 'border-primary-500/50', 'shadow-lg', 'shadow-primary-500/30');
                    link.style.boxShadow = '0 0 30px rgba(59, 130, 246, 0.4), inset 0 0 20px rgba(59, 130, 246, 0.1)';
                }
            });

            function openMobileSidebar() {
                sidebar.classList.remove('translate-x-full'); sidebar.classList.add('translate-x-0');
                if (sidebarOverlay) { sidebarOverlay.classList.remove('hidden', 'opacity-0'); sidebarOverlay.classList.add('opacity-100'); }
                if (iconMenu) iconMenu.classList.add('hidden');
                if (iconClose) iconClose.classList.remove('hidden');
                if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'true');
                document.body.style.overflow = 'hidden';
            }
            function closeMobileSidebar() {
                sidebar.classList.add('translate-x-full'); sidebar.classList.remove('translate-x-0');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('opacity-100'); sidebarOverlay.classList.add('opacity-0');
                    setTimeout(function () { sidebarOverlay.classList.add('hidden'); }, 300);
                }
                if (iconMenu) iconMenu.classList.remove('hidden');
                if (iconClose) iconClose.classList.add('hidden');
                if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }

            if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', function () {
                if (sidebar.classList.contains('translate-x-full')) openMobileSidebar();
                else closeMobileSidebar();
            });
            if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeMobileSidebar);
            navLinks.forEach(function (link) {
                link.addEventListener('click', function () { if (window.innerWidth < 1024) closeMobileSidebar(); });
            });
            window.addEventListener('resize', function () {
                if (window.innerWidth >= 1024) {
                    if (sidebarOverlay) { sidebarOverlay.classList.remove('opacity-100'); sidebarOverlay.classList.add('hidden', 'opacity-0'); }
                    document.body.style.overflow = '';
                    if (iconMenu) iconMenu.classList.remove('hidden');
                    if (iconClose) iconClose.classList.add('hidden');
                    if (mobileMenuBtn) mobileMenuBtn.setAttribute('aria-expanded', 'false');
                }
            });
        }
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
        else boot();
    })();
    </script>
