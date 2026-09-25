<?php
require __DIR__ . '/includes/config.php';
$page_title = $SITE['home_title'];
$page_description = $SITE['home_intro'];
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">

    <header class="relative mb-8 rounded-2xl overflow-hidden hero-gradient bg-grid border border-slate-200/70 p-6 sm:p-10">
        <div class="inline-flex items-center gap-2 rounded-full bg-white/80 backdrop-blur px-3 py-1 text-xs font-bold text-primary-700 mb-3 border border-primary-100 shadow-sm">
            <span>🇪🇬</span> <?= e($SITE['home_eyebrow']) ?>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mb-3">
            <?= e($SITE['home_title']) ?>
        </h1>
        <p class="text-sm sm:text-base text-slate-600 leading-relaxed max-w-3xl">
            <?= e($SITE['home_intro']) ?>
        </p>
    </header>

    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <?php foreach ($SECTIONS as $slug => $s): ?>
            <a href="<?= e(codefy_section_url($slug)) ?>"
               class="group bg-white rounded-2xl border border-slate-200 p-6 hover-lift hover:border-<?= e($s['accent']) ?>-300 hover:shadow-xl transition-all">
                <div class="flex items-start gap-4">
                    <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>">
                        <?= e($s['icon']) ?>
                    </div>
                    <div class="flex-1">
                        <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                        <h2 class="text-lg font-black text-slate-900 mb-1"><?= e($s['title']) ?></h2>
                        <p class="text-xs text-slate-500 leading-relaxed"><?= e($s['subtitle']) ?></p>
                        <span class="inline-flex items-center gap-1 text-xs font-bold text-<?= e($s['accent']) ?>-600 mt-3 group-hover:gap-2 transition-all">
                            ابدأ الآن <span aria-hidden="true">←</span>
                        </span>
                    </div>
                </div>
            </a>
        <?php endforeach; ?>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
