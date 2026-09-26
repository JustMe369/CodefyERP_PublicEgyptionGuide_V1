<?php
/** Presentational shell for the PostgreSQL operations page. */
$dbStatus = is_array($databaseStatus ?? null) ? $databaseStatus : ['status' => $databaseStatus ?? null];
$dbMetrics = is_array($databaseMetrics ?? null) ? $databaseMetrics : [];
$dbTables = is_array($tables ?? null) ? $tables : [];
$dbFlash = is_array($flash ?? null) ? $flash : null;
$connectionValue = $dbStatus['connected'] ?? $dbStatus['healthy'] ?? $dbStatus['status'] ?? false;
$isConnected = is_bool($connectionValue)
    ? $connectionValue
    : in_array(strtolower(trim((string)$connectionValue)), ['1','true','connected','healthy','online','ok','متصل','سليم'], true);
$isAdmin = ($user['role'] ?? '') === 'admin';
$adminName = (string)($user['name'] ?? $user['display_name'] ?? 'مدير النظام');
$fmtBytes = static function ($value): string {
    if (!is_numeric($value) || (float)$value < 0) return '—';
    $size = (float)$value;
    if ($size < 1024) return number_format($size, 0) . ' بايت';
    foreach (['ك.بايت','م.بايت','ج.بايت','ت.بايت'] as $unit) {
        $size /= 1024;
        if ($size < 1024 || $unit === 'ت.بايت') return number_format($size, 1) . ' ' . $unit;
    }
    return '—';
};
$dbSize = $dbMetrics['size'] ?? $dbMetrics['database_size'] ?? $dbMetrics['size_bytes'] ?? null;
$dbSizeLabel = is_numeric($dbSize) ? $fmtBytes($dbSize) : (is_string($dbSize) && $dbSize !== '' ? $dbSize : 'غير متاح');
$dbProvider = (string)($dbMetrics['provider'] ?? $dbStatus['provider'] ?? 'PostgreSQL');
$dbEngine = (string)($dbMetrics['engine'] ?? $dbStatus['engine'] ?? 'PostgreSQL');
$tableCount = $dbMetrics['table_count'] ?? count($dbTables);
$token = (string)($csrf ?? '');
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>عمليات قاعدة البيانات — كوديفاي</title>
    <link rel="stylesheet" href="admin.css"><link rel="stylesheet" href="database.css">
</head>
<body>
<div class="admin-shell">
    <aside class="admin-sidebar">
        <a class="admin-brand" href="index.php"><span class="brand-mark">ك</span><span><strong>كوديفاي</strong><small>لوحة الإدارة</small></span></a>
        <nav aria-label="أقسام الإدارة">
            <a class="side-link" href="index.php">◈ <span>نظرة عامة</span></a>
            <a class="side-link" href="sections.php">▤ <span>محرر الأقسام</span></a>
            <a class="side-link" href="index.php#settings">⚙ <span>إعدادات الموقع</span></a>
            <?php if ($isAdmin): ?><a class="side-link" href="index.php#users">♙ <span>حسابات الإدارة</span></a><?php endif; ?>
            <a class="side-link active" href="database.php" aria-current="page">▣ <span>قاعدة البيانات</span></a>
            <a class="side-link" href="index.php#activity">◷ <span>سجل النشاط</span></a>
        </nav>
        <a class="public-link" href="../index.php">↗ عرض الدليل العام</a>
    </aside>
    <main class="admin-main db-main">
        <header class="topbar">
            <div><span class="eyebrow">مساحة العمل / البنية التحتية</span><h1>عمليات قاعدة البيانات</h1></div>
            <div class="account-box"><span class="avatar" aria-hidden="true">ك</span><span><strong><?= admin_e($adminName) ?></strong><small><?= $isAdmin ? 'مدير النظام' : 'محرر' ?></small></span>
                <form method="post" action="index.php"><input type="hidden" name="_csrf" value="<?= admin_e($token) ?>"><input type="hidden" name="action" value="logout"><button class="button light" type="submit">خروج</button></form>
            </div>
        </header>
        <?php if ($dbFlash): ?><div class="notice <?= admin_e((string)($dbFlash['type'] ?? '')) ?>" role="status" aria-live="polite"><?= admin_e((string)($dbFlash['message'] ?? '')) ?></div><?php endif; ?>

        <section class="db-intro" aria-labelledby="db-title">
            <div class="db-intro-copy"><span class="eyebrow">لوحة تشغيل آمنة</span><h2 id="db-title">حالة قاعدة بيانات الدليل</h2><p>راقب اتصال PostgreSQL، واستعرض الجداول، وأنشئ نسخة موقعة لجداول تطبيق Codefy أو استعدها.</p>
                <p class="credentials-note"><span aria-hidden="true">⌑</span> بيانات الاتصال مضبوطة على الخادم ولا تُعرض في هذه الصفحة.</p>
            </div>
            <div class="connection-stamp<?= $isConnected ? ' is-online' : ' is-offline' ?>"><span class="connection-pulse" aria-hidden="true"></span><span><strong><?= $isConnected ? 'الاتصال سليم' : 'تعذر الاتصال' ?></strong><small><?= admin_e((string)($dbStatus['message'] ?? ($isConnected ? 'تم الوصول إلى قاعدة البيانات' : 'تحقق من اتصال الخادم')) ) ?></small></span></div>
        </section>

        <section class="db-metrics" aria-label="ملخص قاعدة البيانات">
            <article class="db-metric connection-metric"><span class="metric-symbol" aria-hidden="true">◉</span><div><small>حالة الاتصال</small><strong class="<?= $isConnected ? 'tone-good' : 'tone-bad' ?>"><?= $isConnected ? 'متصل' : 'غير متصل' ?></strong></div><span class="metric-foot"><?= admin_e((string)($dbMetrics['checked_at'] ?? 'فحص الحالة الحالية')) ?></span></article>
            <article class="db-metric"><span class="metric-symbol blue-symbol" aria-hidden="true">▧</span><div><small>المزوّد والمحرك</small><strong><?= admin_e($dbProvider) ?></strong><span><?= admin_e($dbEngine) ?></span></div></article>
            <article class="db-metric"><span class="metric-symbol teal-symbol" aria-hidden="true">◫</span><div><small>حجم قاعدة البيانات</small><strong><?= admin_e($dbSizeLabel) ?></strong><span><?= admin_e((string)($dbMetrics['database'] ?? $dbMetrics['database_name'] ?? 'قاعدة البيانات المهيأة')) ?></span></div></article>
            <article class="db-metric"><span class="metric-symbol amber-symbol" aria-hidden="true">▤</span><div><small>الجداول المرصودة</small><strong><?= is_numeric($tableCount) ? number_format((int)$tableCount) : '—' ?></strong><span>ضمن المخطط المسموح</span></div></article>
        </section>

        <section class="db-panel inventory-panel" aria-labelledby="inventory-title">
            <div class="db-panel-heading"><div><span class="eyebrow">قراءة فقط</span><h2 id="inventory-title">جرد الجداول</h2><p>تفاصيل تقريبية للجداول التي يستطيع حساب التطبيق رؤيتها.</p></div><span class="inventory-count"><?= count($dbTables) ?> جدول</span></div>
            <?php if (!$isConnected): ?><div class="db-empty db-error" role="status"><span aria-hidden="true">!</span><div><strong>تعذر تحميل الجرد</strong><p>أعد المحاولة بعد استعادة اتصال الخادم بقاعدة البيانات.</p></div></div>
            <?php elseif ($dbTables): ?><div class="db-table-wrap"><table class="db-table"><caption class="sr-only">مخطط وأسماء الجداول وتقدير الصفوف والحجم</caption><thead><tr><th scope="col">المخطط</th><th scope="col">اسم الجدول</th><th scope="col">الصفوف المقدّرة</th><th scope="col">الحجم التقريبي</th></tr></thead><tbody>
                <?php foreach ($dbTables as $table): if (!is_array($table)) continue; $bytes = $table['approximate_bytes'] ?? $table['size_bytes'] ?? null; ?>
                <tr><td><span class="schema-name" dir="ltr"><?= admin_e((string)($table['schema'] ?? 'public')) ?></span></td><th scope="row"><span class="table-name" dir="ltr"><?= admin_e((string)($table['table'] ?? $table['name'] ?? '')) ?></span></th><td><?= is_numeric($table['estimated_rows'] ?? null) ? number_format((int)$table['estimated_rows']) : '—' ?></td><td><?= admin_e(is_numeric($bytes) ? $fmtBytes($bytes) : (string)($table['approximate_size'] ?? '—')) ?></td></tr>
                <?php endforeach; ?>
            </tbody></table></div>
            <?php else: ?><div class="db-empty"><span aria-hidden="true">▤</span><div><strong>لا توجد جداول متاحة للعرض</strong><p>سيظهر جرد الجداول هنا عند توفر بيانات من وحدة التحكم.</p></div></div><?php endif; ?>
        </section>

        <section class="operations-section" aria-labelledby="operations-title">
            <div class="operations-heading"><div><span class="eyebrow">نسخ واستعادة</span><h2 id="operations-title">عمليات قاعدة البيانات</h2><p>اختر إجراءً واضحاً على الهدف المضبوط حالياً على الخادم.</p></div><span class="ops-lock" aria-label="عمليات محمية">⌑ آمن</span></div>
            <div class="operations-grid">
                <article class="operation-card backup-card">
                    <div class="operation-icon backup-icon" aria-hidden="true">↓</div><div class="operation-copy"><span class="operation-kicker">نسخة قابلة للتنزيل</span><h3>نسخ جداول Codefy</h3><p>نزّل ملفاً موقّعاً لجداول التطبيق في مخطط public، مع فحص سلامة المحتوى قبل أي استعادة.</p></div>
                    <?php if (!empty($backupNotice)): ?><div class="operation-notice <?= !empty($backupEnabled) ? '' : 'notice-muted' ?>" role="status"><?= admin_e((string)$backupNotice) ?></div><?php endif; ?>
                    <form method="post" action="database.php" class="operation-form"><input type="hidden" name="_csrf" value="<?= admin_e($token) ?>"><input type="hidden" name="action" value="create_backup">
                        <button class="button primary" type="submit" <?= empty($backupEnabled) || !$isConnected ? 'disabled' : '' ?>>إنشاء وتنزيل النسخة <span aria-hidden="true">↓</span></button>
                        <?php if (empty($backupEnabled)): ?><small class="form-hint">إنشاء النسخ الاحتياطية غير متاح حالياً.</small><?php endif; ?>
                    </form>
                </article>
                <article class="operation-card restore-card">
                    <div class="restore-risk"><span aria-hidden="true">!</span> إجراء يستبدل بيانات التطبيق الحالية</div>
                    <div class="operation-icon restore-icon" aria-hidden="true">↑</div><div class="operation-copy"><span class="operation-kicker">استعادة من ملف موثوق</span><h3>استعادة جداول Codefy</h3><p>سيتم استبدال جداول Codefy في قاعدة التطبيق من ملف موقّع صادر عن هذه الصفحة. لا يمكن التراجع عن ذلك من هنا.</p></div>
                    <?php if (!empty($restoreNotice)): ?><div class="operation-notice <?= !empty($restoreEnabled) ? 'notice-risk' : 'notice-muted' ?>" role="status"><?= admin_e((string)$restoreNotice) ?></div><?php endif; ?>
                    <form method="post" action="database.php" enctype="multipart/form-data" class="operation-form restore-form">
                        <input type="hidden" name="_csrf" value="<?= admin_e($token) ?>"><input type="hidden" name="action" value="restore_backup">
                        <label class="file-field">حزمة Codefy بصيغة .tar.gz<input type="file" name="backup_file" accept=".tar.gz,application/gzip,application/x-gzip" required <?= empty($restoreEnabled) || !$isConnected ? 'disabled' : '' ?>></label>
                        <label class="confirmation-field">للتأكيد، اكتب العبارة التالية كما هي <span dir="ltr">RESTORE DATABASE</span><input type="text" name="confirmation" dir="ltr" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="RESTORE DATABASE" pattern="RESTORE DATABASE" required <?= empty($restoreEnabled) || !$isConnected ? 'disabled' : '' ?>></label>
                        <button class="button restore-button" type="submit" <?= empty($restoreEnabled) || !$isConnected ? 'disabled' : '' ?>>استعادة قاعدة البيانات</button>
                        <?php if (empty($restoreEnabled)): ?><small class="form-hint">الاستعادة غير متاحة حالياً.</small><?php endif; ?>
                    </form>
                </article>
            </div>
        </section>

        <aside class="provider-note" aria-labelledby="provider-note-title"><span class="provider-note-icon" aria-hidden="true">i</span><div><h2 id="provider-note-title">الاتصال السحابي وإدارة Supabase</h2><p>لربط مزوّد PostgreSQL أو مشروع آخر، حدّث أسرار الاتصال في إعدادات بيئة Vercel ثم أعد النشر؛ لا نخزن كلمات المرور داخل لوحة الإدارة. إنشاء مشروع Supabase جديد واللقطات والاستعادة الزمنية تتم من لوحة Supabase. هذه الصفحة تعمل على هدف التطبيق المهيأ فقط.</p></div><div class="provider-links"><a href="https://supabase.com/dashboard" target="_blank" rel="noopener">لوحة Supabase ↗</a><a href="https://vercel.com/dashboard" target="_blank" rel="noopener">إعدادات Vercel ↗</a></div></aside>
        <footer class="admin-footer">كوديفاي · عمليات قاعدة البيانات</footer>
    </main>
</div>
</body>
</html>
