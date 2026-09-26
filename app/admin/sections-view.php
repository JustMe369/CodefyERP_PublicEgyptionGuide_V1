<?php
/** Presentational shell for the CMS section manager. The controller supplies the documented variables. */
$editing = is_array($editingSection ?? null) ? $editingSection : null;
$allSections = is_array($sections ?? null) ? $sections : [];
$availableMediaAssets = is_array($mediaAssets ?? null) ? $mediaAssets : [];
$currentBlocks = is_array($blocks ?? null) ? $blocks : [];
$token = (string)($csrf ?? '');
$isNew = $editing === null;
$isLegacyTemplate = (bool)($isLegacyTemplate ?? ($editing && ($editing['content_mode'] ?? '') === 'legacy'));
$hasLegacyTemplate = (bool)($hasLegacyTemplate ?? ($editing && ($editing['content_mode'] ?? '') === 'legacy'));
$status = $editing && !empty($editing['is_published']);
$fallbackPreview = $editing ? '../section.php?slug=' . rawurlencode((string)($editing['slug'] ?? '')) : '../index.php';
$previewCandidate = trim((string)($publicPreview ?? $fallbackPreview));
$previewParts = parse_url($previewCandidate);
$previewIsSameOrigin = is_array($previewParts) && !isset($previewParts['user'], $previewParts['pass'])
    && !str_contains($previewCandidate, '\\');
if ($previewIsSameOrigin && isset($previewParts['host'])) {
    $requestHost = strtolower((string)($_SERVER['HTTP_HOST'] ?? ''));
    $candidateHost = strtolower((string)$previewParts['host'] . (isset($previewParts['port']) ? ':' . $previewParts['port'] : ''));
    $requestScheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
    $previewIsSameOrigin = $candidateHost === $requestHost
        && (!isset($previewParts['scheme']) || strtolower((string)$previewParts['scheme']) === $requestScheme);
} elseif ($previewIsSameOrigin && isset($previewParts['scheme'])) {
    $previewIsSameOrigin = false;
} elseif ($previewIsSameOrigin && str_starts_with($previewCandidate, '//')) {
    $previewIsSameOrigin = false;
}
$publicPreview = $previewIsSameOrigin && $previewCandidate !== '' ? $previewCandidate : $fallbackPreview;
$blockJson = json_encode(array_values($currentBlocks), JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT);
if (!is_string($blockJson)) $blockJson = '[]';
$accentNames = ['primary'=>'أزرق أساسي','indigo'=>'نيلي','emerald'=>'زمردي','amber'=>'كهرماني','violet'=>'بنفسجي','rose'=>'وردي','cyan'=>'سماوي'];
$userName = (string)($user['name'] ?? $user['display_name'] ?? 'مدير النظام');
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="color-scheme" content="light">
    <title><?= $editing ? 'تحرير ' . admin_e((string)($editing['title'] ?? 'قسم')) : 'إنشاء قسم' ?> — إدارة كوديفاي</title>
    <link rel="stylesheet" href="admin.css"><link rel="stylesheet" href="sections.css">
    <script src="sections.js" defer></script>
</head>
<body class="sections-admin-page">
<div class="admin-shell">
    <aside class="admin-sidebar">
        <a class="admin-brand" href="index.php"><span class="brand-mark">ك</span><span><strong>كوديفاي</strong><small>لوحة الإدارة</small></span></a>
        <nav aria-label="أقسام الإدارة">
            <a class="side-link" href="index.php">◈ <span>نظرة عامة</span></a>
            <a class="side-link active" href="sections.php" aria-current="page">▤ <span>محرر الأقسام</span></a>
            <a class="side-link" href="database.php">▣ <span>قاعدة البيانات</span></a>
            <a class="side-link" href="index.php#settings">⚙ <span>إعدادات الموقع</span></a>
            <a class="side-link" href="index.php#users">♙ <span>حسابات الإدارة</span></a>
            <a class="side-link" href="index.php#activity">◷ <span>سجل النشاط</span></a>
        </nav>
        <a class="public-link" href="../index.php">↗ عرض الدليل العام</a>
    </aside>
    <main class="admin-main cms-main">
        <header class="topbar">
            <div><span class="eyebrow">مساحة العمل / المحتوى</span><h1>محرر أقسام الدليل</h1></div>
            <div class="account-box"><span class="avatar" aria-hidden="true">ك</span><span><strong><?= admin_e($userName) ?></strong><small>إدارة المحتوى</small></span><a class="button light" href="index.php">لوحة التحكم</a></div>
        </header>
        <?php if (!empty($flash) && is_array($flash)): ?><div class="notice <?= admin_e((string)($flash['type'] ?? '')) ?>" role="status" aria-live="polite"><?= admin_e((string)($flash['message'] ?? '')) ?></div><?php endif; ?>

        <section class="cms-intro" aria-labelledby="cms-title">
            <div><span class="eyebrow">استوديو النشر</span><h2 id="cms-title">كل فكرة تبدأ بقسم</h2><p>رتّب محتوى الدليل بكتل واضحة، وعاين النتيجة قبل حفظها.</p></div>
            <a class="button primary" href="sections.php">＋ قسم جديد</a>
            <div class="intro-mark" aria-hidden="true">01<span>—</span>∞</div>
        </section>

        <div class="cms-layout">
            <aside class="section-rail" aria-label="أقسام الدليل">
                <div class="rail-heading"><div><span class="eyebrow">مكتبة المحتوى</span><h2>الأقسام <span><?= count($allSections) ?></span></h2></div><a href="sections.php" class="rail-add" aria-label="إنشاء قسم جديد">＋</a></div>
                <div class="rail-stats" aria-label="ملخص الأقسام">
                    <span><strong><?= (int)($sectionStats['published'] ?? 0) ?></strong><small>منشور</small></span>
                    <span><strong><?= (int)($sectionStats['drafts'] ?? 0) ?></strong><small>مسودة</small></span>
                    <span><strong><?= (int)($sectionStats['blocks'] ?? 0) ?></strong><small>كتلة محتوى</small></span>
                </div>
                <?php if ($allSections): ?><div class="section-filters">
                    <label class="section-search"><span class="sr-only">ابحث في الأقسام</span><span aria-hidden="true">⌕</span><input type="search" data-section-search placeholder="ابحث بالاسم أو الرابط" autocomplete="off"></label>
                    <label class="sr-only" for="section-status-filter">تصفية حسب حالة النشر</label><select id="section-status-filter" data-section-status><option value="all">كل الحالات</option><option value="published">المنشورة</option><option value="draft">المسودات</option></select>
                    <p class="section-filter-count" data-section-filter-count aria-live="polite"><?= count($allSections) ?> أقسام</p>
                </div><?php endif; ?>
                <?php if ($allSections): ?><ol class="section-list">
                    <?php foreach ($allSections as $row): $slug = (string)($row['slug'] ?? ''); $active = $editing && $slug === (string)($editing['slug'] ?? ''); $rowPreview = (string)($row['public_url'] ?? ('../section.php?slug=' . rawurlencode($slug))); ?>
                    <li data-section-row data-title="<?= admin_e((string)($row['title'] ?? '')) ?>" data-slug="<?= admin_e($slug) ?>" data-status="<?= !empty($row['is_published']) ? 'published' : 'draft' ?>"><a class="section-item<?= $active ? ' selected' : '' ?>" href="sections.php?edit=<?= rawurlencode($slug) ?>"<?= $active ? ' aria-current="page"' : '' ?>>
                        <span class="section-order"><?= sprintf('%02d', (int)($row['sort_order'] ?? 0)) ?></span><span class="section-icon"><?= admin_e((string)($row['icon'] ?? '▤')) ?></span>
                        <span class="section-copy"><strong><?= admin_e((string)($row['title'] ?? 'قسم بلا عنوان')) ?></strong><small dir="ltr"><?= admin_e($slug) ?></small></span>
                        <span class="publish-dot<?= !empty($row['is_published']) ? ' is-live' : '' ?>" title="<?= !empty($row['is_published']) ? 'منشور' : 'مسودة' ?>"></span>
                    </a><a class="section-row-preview" href="<?= admin_e($rowPreview) ?>" target="_blank" rel="noopener" aria-label="معاينة <?= admin_e((string)($row['title'] ?? 'القسم')) ?>">↗</a></li>
                    <?php endforeach; ?>
                </ol><div class="rail-empty filter-empty" data-filter-empty hidden><strong>لا توجد نتائج مطابقة</strong><p>غيّر كلمات البحث أو حالة النشر.</p></div><?php else: ?><div class="rail-empty"><span aria-hidden="true">▤</span><strong>لا توجد أقسام بعد</strong><p>ابدأ بإنشاء أول قسم للدليل.</p></div><?php endif; ?>
                <div class="rail-legend"><span class="publish-dot is-live"></span> منشور <span class="publish-dot"></span> مسودة</div>
            </aside>

            <section class="editor-panel" aria-labelledby="editor-title">
                <div class="editor-heading"><div><span class="eyebrow"><?= $isNew ? 'مسودة جديدة' : 'تحرير القسم' ?></span><h2 id="editor-title"><?= $isNew ? 'إنشاء قسم جديد' : 'تفاصيل القسم' ?></h2></div>
                    <?php if ($editing): ?><a class="preview-link" href="<?= admin_e($publicPreview) ?>" target="_blank" rel="noopener">معاينة الصفحة <span aria-hidden="true">↗</span></a><?php endif; ?>
                </div>
                <?php if ($editing && $hasLegacyTemplate): ?>
                <section class="legacy-source" aria-labelledby="legacy-source-title" data-source-panel="legacy" <?= !$isLegacyTemplate ? 'hidden' : '' ?>>
                    <header class="legacy-source-heading"><span class="legacy-source-icon" aria-hidden="true">▣</span><div><span class="legacy-status">قالب الصفحة الحالي</span><h3 id="legacy-source-title">المحتوى محفوظ في ملف الصفحة الأصلي</h3><p>يعرض هذا القسم محتوى قالب PHP الحالي كما يظهر للزوار. تعديل الكتل المرئية لا يغيّر القالب حتى تختار «المحرر المرئي» من مصدر المحتوى.</p></div></header>
                    <div class="legacy-preview-toolbar"><span><span class="source-live-dot" aria-hidden="true"></span> معاينة آمنة للصفحة المنشورة</span><a class="preview-link" href="<?= admin_e($publicPreview) ?>" target="_blank" rel="noopener">فتح الصفحة العامة <span aria-hidden="true">↗</span></a></div>
                    <div class="legacy-frame-wrap"><iframe class="legacy-frame" src="<?= admin_e($publicPreview) ?>" title="معاينة الصفحة العامة للقسم <?= admin_e((string)($editing['title'] ?? '')) ?>" loading="lazy" referrerpolicy="no-referrer" sandbox="allow-same-origin"></iframe></div>
                    <p class="legacy-frame-note">المعاينة معزولة داخل إطار بلا صلاحية تشغيل JavaScript أو إرسال النماذج. استخدم رابط الصفحة العامة للتفاعل الكامل.</p>
                </section>
                <?php elseif ($editing): ?>
                <div class="builder-source-status" role="status" aria-live="polite" data-source-panel="builder" <?= $isLegacyTemplate ? 'hidden' : '' ?>><span aria-hidden="true">✦</span><div><strong>مصدر المحتوى: المحرر المرئي</strong><small>الكتل أدناه هي مصدر محتوى هذه الصفحة.</small></div></div>
                <?php endif; ?>
                <form method="post" class="section-form" id="section-form" data-section-form>
                    <input type="hidden" name="_csrf" value="<?= admin_e($token) ?>"><input type="hidden" name="action" value="save_section">
                    <input type="hidden" name="original_slug" value="<?= admin_e((string)($editing['slug'] ?? '')) ?>">
                    <input type="hidden" name="blocks_json" id="blocks-json" value="<?= admin_e($blockJson) ?>">
                    <section class="meta-fields" aria-labelledby="meta-title"><div class="subsection-heading"><span class="step-index">1</span><div><h3 id="meta-title">هوية القسم</h3><p>الاسم والرابط والمظهر العام.</p></div></div>
                        <div class="fields-grid">
                            <label class="field field-title">عنوان القسم <span class="required-mark">*</span><input name="title" maxlength="160" value="<?= admin_e((string)($editing['title'] ?? '')) ?>" placeholder="مثال: إدارة الفواتير" required></label>
                            <label class="field">معرّف الرابط <span class="required-mark">*</span><input name="slug" dir="ltr" maxlength="80" pattern="[a-z0-9]+(?:-[a-z0-9]+)*" value="<?= admin_e((string)($editing['slug'] ?? '')) ?>" placeholder="invoice-management" required><small>أحرف إنجليزية صغيرة وأرقام وواصلات فقط.</small></label>
                            <label class="field field-wide">وصف مختصر<input name="subtitle" maxlength="240" value="<?= admin_e((string)($editing['subtitle'] ?? '')) ?>" placeholder="جملة واحدة توضّح ما سيتعلمه القارئ"></label>
                            <label class="field">الأيقونة أو الرمز التعبيري<input name="icon" maxlength="32" value="<?= admin_e((string)($editing['icon'] ?? '📘')) ?>" placeholder="📘" required></label>
                            <label class="field">لون التمييز<select name="accent"><?php foreach ($accentNames as $value=>$label): ?><option value="<?= admin_e($value) ?>" <?= ($editing['accent'] ?? 'primary') === $value ? 'selected' : '' ?>><?= admin_e($label) ?></option><?php endforeach; ?></select></label>
                            <label class="field">ترتيب العرض<input name="sort_order" type="number" min="1" step="1" value="<?= (int)($editing['sort_order'] ?? (count($allSections) + 1)) ?>" required></label>
                            <label class="field">مصدر المحتوى<select name="content_mode"><option value="builder" <?= ($editing['content_mode'] ?? 'builder') === 'builder' ? 'selected' : '' ?>>المحرر المرئي</option><option value="legacy" <?= ($editing['content_mode'] ?? '') === 'legacy' ? 'selected' : '' ?>>قالب الصفحة الحالي</option></select><small>القالب الحالي يحافظ على صفحة الشرح الموجودة.</small></label>
                        </div>
                        <label class="publish-control"><input type="checkbox" name="is_published" value="1" <?= $status ? 'checked' : '' ?>><span class="toggle-track" aria-hidden="true"></span><span><strong>نشر القسم</strong><small>سيظهر القسم للزوار في الدليل العام.</small></span></label>
                    </section>

                    <section class="composer" aria-labelledby="composer-title" data-composer>
                        <div class="subsection-heading"><span class="step-index">2</span><div><h3 id="composer-title">محتوى الصفحة</h3><p>أضف الكتل، اسحبها لترتيبها، واضبط عرضها ومكانها.</p></div><span class="block-count" data-block-count>0 كتل</span></div>
                        <div class="composer-toolbar"><span class="toolbar-label">إضافة كتلة</span><div class="block-tools" role="group" aria-label="أنواع كتل المحتوى">
                            <button type="button" data-add="heading"><b>H</b> عنوان</button><button type="button" data-add="paragraph"><b>¶</b> فقرة</button><button type="button" data-add="list"><b>☷</b> قائمة</button><button type="button" data-add="steps"><b>↗</b> خطوات</button><button type="button" data-add="callout"><b>✦</b> تنبيه</button><button type="button" data-add="image"><b>▧</b> صورة</button><button type="button" data-add="table"><b>▦</b> جدول</button><button type="button" data-add="code"><b>&lt;/&gt;</b> كود</button><button type="button" data-add="mermaid"><b>◇</b> مخطط</button><button type="button" data-add="link"><b>↗</b> رابط</button><button type="button" data-add="divider"><b>—</b> فاصل</button>
                        </div></div>
                        <div class="composer-workspace"><div class="block-stack" data-block-stack aria-live="polite"></div>
                            <div class="composer-empty" data-empty-state><span class="empty-glyph" aria-hidden="true">＋</span><h4>ابدأ ببناء الصفحة</h4><p>اختر نوع كتلة من الشريط أعلاه. يمكنك نقل كل كتلة أو تكرارها أو حذفها.</p></div>
                            <aside class="live-preview" aria-label="معاينة تخطيط المحتوى"><div class="preview-head"><span class="preview-light"></span><span class="preview-light"></span><span class="preview-light"></span><b>لوحة التخطيط</b></div><div class="preview-body preview-canvas" data-preview><span class="preview-placeholder">ستظهر هنا لمحة عن ترتيب المحتوى.</span></div><p class="canvas-guidance">تتبع اللوحة ترتيب الكتل وعرضها. على الشاشات الصغيرة تتراص الكتل بعرض كامل.</p></aside>
                        </div>
                    </section>
                    <footer class="save-dock"><div class="save-state"><span class="save-indicator" data-save-indicator></span><span data-save-label>كل التعديلات محفوظة في النموذج</span></div><div class="save-actions">
                        <?php $coreSlugs = ['login','bulk-import','relationships','assignments','pricing','readiness','analysis-config']; $canDelete = $editing && !in_array((string)$editing['slug'], $coreSlugs, true); ?>
                        <?php if ($canDelete): ?><button class="button danger" type="submit" form="delete-section-form">حذف القسم</button><?php endif; ?>
                        <a class="button light" href="sections.php">إلغاء</a><button class="button primary" type="submit"><span aria-hidden="true">✓</span> <?= $status ? 'حفظ التغييرات' : 'حفظ القسم' ?></button></div></footer>
                </form>
                <?php if ($canDelete): ?><form id="delete-section-form" class="delete-form" method="post"><input type="hidden" name="_csrf" value="<?= admin_e($token) ?>"><input type="hidden" name="action" value="delete_section"><input type="hidden" name="original_slug" value="<?= admin_e((string)$editing['slug']) ?>"></form><?php endif; ?>
                <datalist id="cms-media-assets">
                    <?php foreach ($availableMediaAssets as $asset): if (!is_string($asset)) continue; ?><option value="<?= admin_e($asset) ?>"></option><?php endforeach; ?>
                </datalist>
            </section>
        </div>
        <footer class="admin-footer">كوديفاي · مساحة تحرير الدليل</footer>
    </main>
</div>
<script type="application/json" id="initial-blocks"><?= $blockJson ?></script>
</body>
</html>
