<?php
$slug = codefy_current_slug();
$s    = $slug !== 'index' ? ($SECTIONS[$slug] ?? null) : null;
if (!$s) return;
?>
<div class="sticky top-2 z-30 mb-8 p-3.5 rounded-2xl bg-white/90 backdrop-blur-md border border-slate-200/80 shadow-sm flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center gap-2 text-xs sm:text-sm">
        <a href="index.php" class="text-slate-400 font-bold hover:text-primary-600 transition-colors">🏠 الفهرس</a>
        <span class="text-slate-300">/</span>
        <span class="font-black text-primary-700 flex items-center gap-1.5"><?= $s['icon'] ?> <?= e($s['title']) ?></span>
        <span class="ms-2 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[11px] font-black hidden sm:inline-block">
            القسم <?= (int)$s['number'] ?> من <?= count($SECTIONS) ?>
        </span>
    </div>
    <div class="flex items-center gap-1.5 bg-slate-100/80 p-1 rounded-xl border border-slate-200/60">
        <span class="text-xs font-bold text-slate-600 px-3 py-1"><?= e($s['subtitle']) ?></span>
    </div>
</div>