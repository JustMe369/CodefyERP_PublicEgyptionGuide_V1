<?php
$slug    = codefy_current_slug();
$current = $slug !== 'index' ? ($SECTIONS[$slug] ?? null) : null;
$label   = $current ? ($current['icon'] . ' ' . $current['title']) : 'فهرس الدليل';
$asset   = $SITE['assets'];
?>
<body id="top" data-section="<?= e($slug) ?>" class="bg-slate-50 text-slate-800 antialiased selection:bg-primary-100 selection:text-primary-900">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:z-50">تخطي إلى المحتوى الرئيسي</a>

    <div id="scroll-progress" class="fixed top-0 start-0 z-[60] h-1 bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 shadow-sm shadow-primary-500/30 transition-all duration-300 ease-out" style="width: 0%; box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);"></div>

    <div id="mobile-header" class="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-md lg:hidden">
        <div class="flex items-center gap-2.5">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600 text-white shadow-md shadow-primary-600/20">
                <img src="<?= $asset ?>/img/CodefyLogo.png" alt="<?= e($SITE['name']) ?>" class="h-6 w-6 object-contain" onerror="this.src='<?= $asset ?>/img/login.png'">
            </div>
            <div>
                <span class="text-lg font-black text-slate-900"><?= e($SITE['name']) ?><span class="text-primary-600"><?= e($SITE['brand_suffix']) ?></span></span>
                <span id="mobile-current-section" class="block text-[11px] font-bold text-primary-600 truncate max-w-[170px]"><?= e($label) ?></span>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <button id="theme-toggle" type="button" aria-label="تبديل الثيم" class="codefy-theme-toggle p-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 transition-colors">
                <svg id="theme-icon" class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path id="sun-path" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    <path id="moon-path" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" class="hidden" />
                </svg>
            </button>
            <button id="mobile-menu-btn" type="button" aria-label="فتح القائمة" aria-controls="sidebar" aria-expanded="false" class="text-slate-600 hover:text-slate-900 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 transition-colors">
                <svg id="icon-menu" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
                <svg id="icon-close" class="h-6 w-6 hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
        </div>
    </div>
