<?php
$slug = codefy_current_slug();
if (!isset($SECTIONS[$slug])) return;
$nav = codefy_neighbors($SECTIONS, $slug);
?>
<nav class="section-pager flex flex-wrap items-center justify-between gap-4 mt-12 pt-6 border-t border-slate-200">
    <?php if ($nav['prev']): $p = $SECTIONS[$nav['prev']]; ?>
        <a href="<?= e($nav['prev']) ?>.php" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-colors">
            <span aria-hidden="true">→</span> السابق: <?= e($p['title']) ?>
        </a>
    <?php else: ?>
        <a href="index.php" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-colors">🏠 الفهرس</a>
    <?php endif; ?>

    <a href="index.php" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-colors">🏠 الفهرس</a>

    <?php if ($nav['next']): $n = $SECTIONS[$nav['next']]; ?>
        <a href="<?= e($nav['next']) ?>.php" class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/20">
            التالي: <?= e($n['title']) ?> <span aria-hidden="true">←</span>
        </a>
    <?php else: ?>
        <a href="index.php" class="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-600/20">
            العودة للفهرس <span aria-hidden="true">←</span>
        </a>
    <?php endif; ?>
</nav>