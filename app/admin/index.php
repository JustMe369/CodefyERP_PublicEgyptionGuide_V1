<?php
require __DIR__ . '/_bootstrap.php';
$user = admin_require_user();
$pdo = codefy_db();
$allowedSettings = ['name', 'brand_suffix', 'subtitle', 'copyright', 'version', 'home_eyebrow', 'home_title', 'home_intro', 'navigation_label', 'search_placeholder'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_require_csrf();
    $action = (string)($_POST['action'] ?? '');
    try {
        if ($action === 'logout') {
            codefy_admin_audit($pdo, (int)$user['id'], 'logout', 'admin_user', (string)$user['id']);
            $_SESSION = [];
            session_regenerate_id(true);
            header('Location: login.php'); exit;
        }
        if ($action === 'save_settings') {
            admin_require_permission('settings.manage');
            $posted = $_POST['settings'] ?? [];
            $limits = ['name' => 100, 'brand_suffix' => 16, 'subtitle' => 180, 'copyright' => 220, 'version' => 32, 'home_eyebrow' => 180, 'home_title' => 180, 'home_intro' => 1000, 'navigation_label' => 80, 'search_placeholder' => 120];
            $values = [];
            foreach ($allowedSettings as $key) {
                $value = trim((string)($posted[$key] ?? ''));
                if ($value === '' || strlen($value) > $limits[$key]) throw new InvalidArgumentException('راجع الحقول المطلوبة. بعض النصوص فارغة أو أطول من الحد المسموح.');
                $values[$key] = $value;
            }
            $pdo->beginTransaction();
            $statement = $pdo->prepare('INSERT INTO codefy_site_settings (setting_key, setting_value, updated_at, updated_by) VALUES (:key, :value, now(), :admin_id) ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = now(), updated_by = EXCLUDED.updated_by');
            foreach ($values as $key => $value) $statement->execute(['key' => $key, 'value' => $value, 'admin_id' => $user['id']]);
            codefy_admin_audit($pdo, (int)$user['id'], 'update', 'site_settings', null, ['keys' => array_keys($values)]);
            $pdo->commit();
            admin_flash('success', 'تم حفظ إعدادات الموقع.');
        } elseif ($action === 'save_sections') {
            admin_require_permission('sections.edit');
            admin_require_permission('sections.publish');
            $posted = $_POST['sections'] ?? [];
            $current = $pdo->query('SELECT slug FROM codefy_guide_sections ORDER BY sort_order')->fetchAll(PDO::FETCH_COLUMN);
            if (count($posted) !== count($current)) throw new InvalidArgumentException('لم تصل بيانات جميع الأقسام. أعد تحميل الصفحة وحاول مرة أخرى.');
            $values = [];
            $orders = [];
            foreach ($current as $slug) {
                if (!isset($posted[$slug]) || !is_array($posted[$slug])) throw new InvalidArgumentException('بيانات الأقسام غير مكتملة.');
                $row = $posted[$slug];
                $title = trim((string)($row['title'] ?? ''));
                $subtitle = trim((string)($row['subtitle'] ?? ''));
                $icon = trim((string)($row['icon'] ?? ''));
                $order = filter_var($row['sort_order'] ?? null, FILTER_VALIDATE_INT);
                if ($title === '' || strlen($title) > 160 || strlen($subtitle) > 240 || $icon === '' || strlen($icon) > 32 || $order === false || $order < 1 || $order > count($current)) {
                    throw new InvalidArgumentException('راجع عنوان ووصف ورمز وترتيب كل قسم.');
                }
                $orders[] = $order;
                $values[$slug] = ['title' => $title, 'subtitle' => $subtitle, 'icon' => $icon, 'sort_order' => $order, 'is_published' => isset($row['is_published']) && $row['is_published'] === '1'];
            }
            if (count(array_unique($orders)) !== count($current)) throw new InvalidArgumentException('يجب أن يكون ترتيب الأقسام فريداً من 1 إلى ' . count($current) . '.');
            if (count(array_filter($values, static fn($row) => $row['is_published'])) === 0) throw new InvalidArgumentException('يجب إبقاء قسم واحد على الأقل منشوراً.');
            $pdo->beginTransaction();
            $pdo->exec('UPDATE codefy_guide_sections SET sort_order = sort_order + 100');
            $statement = $pdo->prepare('UPDATE codefy_guide_sections SET title = :title, subtitle = :subtitle, icon = :icon, sort_order = :sort_order, is_published = CAST(:published AS boolean), updated_at = now(), updated_by = :admin_id WHERE slug = :slug');
            foreach ($values as $slug => $row) {
                $statement->execute([
                    'title' => $row['title'], 'subtitle' => $row['subtitle'], 'icon' => $row['icon'],
                    'sort_order' => $row['sort_order'], 'published' => $row['is_published'] ? 'true' : 'false',
                    'admin_id' => $user['id'], 'slug' => $slug,
                ]);
            }
            codefy_admin_audit($pdo, (int)$user['id'], 'update', 'guide_sections', null, ['slugs' => array_keys($values)]);
            $pdo->commit();
            admin_flash('success', 'تم حفظ الأقسام وترتيبها.');
        } else {
            throw new InvalidArgumentException('الإجراء المطلوب غير معروف.');
        }
    } catch (Throwable $exception) {
        if ($pdo->inTransaction()) $pdo->rollBack();
        error_log('Codefy admin action failed: ' . $exception->getMessage());
        admin_flash('error', $exception instanceof InvalidArgumentException ? $exception->getMessage() : 'تعذر حفظ التغييرات. تحقق من قاعدة البيانات ثم حاول مرة أخرى.');
    }
    header('Location: index.php'); exit;
}

admin_require_permission('dashboard.view');

$settings = [];
if (admin_can('settings.manage')) foreach ($pdo->query('SELECT setting_key, setting_value FROM codefy_site_settings') as $row) $settings[$row['setting_key']] = $row['setting_value'];
$sections = admin_can('sections.view') ? $pdo->query('SELECT slug, title, subtitle, icon, sort_order, is_published FROM codefy_guide_sections ORDER BY sort_order')->fetchAll() : [];
$audit = admin_can('audit.view') ? $pdo->query('SELECT a.action, a.entity_type, a.created_at, u.display_name FROM codefy_admin_audit_log a LEFT JOIN codefy_admin_users u ON u.id = a.admin_id ORDER BY a.created_at DESC LIMIT 8')->fetchAll() : [];
$flash = admin_take_flash();
$roleDisplay = admin_role_name((string)($user['role'] ?? ''));
$userInitial = 'م';
if (preg_match('/^./us', (string)$user['name'], $initialMatch)) $userInitial = $initialMatch[0];
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>لوحة التحكم — كوديفاي</title><link rel="stylesheet" href="admin.css">
</head>
<body>
<div class="admin-shell">
    <aside class="admin-sidebar">
        <a class="admin-brand" href="index.php"><span class="brand-mark">ك</span><span><strong>كوديفاي</strong><small>لوحة الإدارة</small></span></a>
        <?php $activeNav = 'dashboard'; require __DIR__ . '/_navigation.php'; ?>
        <a class="public-link" href="../index.php">↗ عرض الدليل العام</a>
    </aside>

    <main class="admin-main">
        <header class="topbar">
            <div><span class="eyebrow">مساحة العمل / الإدارة</span><h1>لوحة التحكم</h1></div>
            <div class="account-box"><span class="avatar"><?= admin_e($userInitial) ?></span><span><strong><?= admin_e($user['name']) ?></strong><small><?= admin_e($roleDisplay) ?></small></span>
                <form method="post"><input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>"><input type="hidden" name="action" value="logout"><button class="button light" type="submit">خروج</button></form>
            </div>
        </header>

        <?php if ($flash): ?><div class="notice <?= admin_e($flash['type']) ?>" role="status"><?= admin_e($flash['message']) ?></div><?php endif; ?>

        <section id="overview" class="welcome-card">
            <div><span class="eyebrow">مرحباً <?= admin_e($user['name']) ?></span><h2>إدارة دليل كوديفاي من مكان واحد</h2><p>تحكم في هوية الموقع، أنشئ أقساماً، وابنِ محتوى الصفحات من محرر الكتل المرئي.</p><?php if (admin_can('sections.view')): ?><a class="button light" href="sections.php">فتح محرر الأقسام</a><?php endif; ?></div>
            <div class="welcome-symbol" aria-hidden="true">✦</div>
        </section>

        <section class="stat-grid" aria-label="ملخص المشروع">
            <article class="stat-card"><span class="stat-icon blue">▤</span><div><span class="stat-label">إجمالي الأقسام</span><strong><?= count($sections) ?></strong></div></article>
            <article class="stat-card"><span class="stat-icon green">●</span><div><span class="stat-label">أقسام منشورة</span><strong><?= count(array_filter($sections, static fn($s) => codefy_bool($s['is_published']))) ?></strong></div></article>
            <article class="stat-card"><span class="stat-icon violet">♙</span><div><span class="stat-label">حالة الحساب</span><strong class="small-value"><?= admin_e($roleDisplay) ?></strong></div></article>
        </section>

        <section id="sections" class="panel">
            <div class="panel-heading"><div><span class="eyebrow">المحتوى المنشور</span><h2>إدارة أقسام الدليل</h2><p>عدّل العناوين والوصف والأيقونة وترتيب العرض، أو أوقف نشر قسم مؤقتاً.</p></div><span class="panel-count"><?= count($sections) ?> أقسام</span></div>
            <?php if (admin_can('sections.edit') && admin_can('sections.publish')): ?><form method="post">
                <input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>"><input type="hidden" name="action" value="save_sections">
                <div class="table-wrap"><table><thead><tr><th>الترتيب</th><th>القسم</th><th>العنوان</th><th>الوصف المختصر</th><th>الرمز</th><th>النشر</th></tr></thead><tbody>
                <?php foreach ($sections as $section): $slug = $section['slug']; ?>
                    <tr>
                        <td><input class="order-input" type="number" min="1" max="<?= count($sections) ?>" name="sections[<?= admin_e($slug) ?>][sort_order]" value="<?= (int)$section['sort_order'] ?>" aria-label="ترتيب <?= admin_e($section['title']) ?>"></td>
                        <td><span class="slug-label"><?= admin_e($slug) ?></span></td>
                        <td><input type="text" maxlength="160" name="sections[<?= admin_e($slug) ?>][title]" value="<?= admin_e($section['title']) ?>" required></td>
                        <td><input type="text" maxlength="240" name="sections[<?= admin_e($slug) ?>][subtitle]" value="<?= admin_e($section['subtitle']) ?>"></td>
                        <td><input class="icon-input" type="text" maxlength="12" name="sections[<?= admin_e($slug) ?>][icon]" value="<?= admin_e($section['icon']) ?>" required aria-label="رمز <?= admin_e($section['title']) ?>"></td>
                        <td><label class="switch"><input type="hidden" name="sections[<?= admin_e($slug) ?>][is_published]" value="0"><input type="checkbox" name="sections[<?= admin_e($slug) ?>][is_published]" value="1" <?= codefy_bool($section['is_published']) ? 'checked' : '' ?>><span></span><span class="switch-label">منشور</span></label></td>
                    </tr>
                <?php endforeach; ?>
                </tbody></table></div>
                <div class="form-actions"><p class="muted">لتحرير محتوى أي صفحة تفصيلياً، افتح محرر الأقسام واختر القسم.</p><button class="button primary" type="submit">حفظ الأقسام</button></div>
            </form><?php else: ?><div class="table-wrap"><table><thead><tr><th>الترتيب</th><th>المعرّف</th><th>القسم</th><th>الوصف</th><th>الحالة</th></tr></thead><tbody><?php foreach ($sections as $section): ?><tr><td><?= (int)$section['sort_order'] ?></td><td><span class="slug-label"><?= admin_e($section['slug']) ?></span></td><td><?= admin_e($section['title']) ?></td><td><?= admin_e($section['subtitle']) ?></td><td><?= codefy_bool($section['is_published']) ? 'منشور' : 'مسودة' ?></td></tr><?php endforeach; ?></tbody></table></div><?php endif; ?>
        </section>

        <section id="settings" class="panel">
            <div class="panel-heading"><div><span class="eyebrow">هوية الدليل</span><h2>إعدادات الموقع</h2><p>هذه القيم تظهر في ترويسة الموقع وعنوان الصفحة وتذييلها.</p></div></div>
            <?php if (admin_can('settings.manage')): ?>
            <form method="post" class="settings-form">
                <input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>"><input type="hidden" name="action" value="save_settings">
                <label>اسم الموقع<input name="settings[name]" maxlength="100" value="<?= admin_e($settings['name'] ?? '') ?>" required></label>
                <label>لاحقة العلامة التجارية<input name="settings[brand_suffix]" maxlength="16" value="<?= admin_e($settings['brand_suffix'] ?? '') ?>" required></label>
                <label>الوصف التعريفي<input name="settings[subtitle]" maxlength="180" value="<?= admin_e($settings['subtitle'] ?? '') ?>" required></label>
                <label>بيان حقوق النشر<input name="settings[copyright]" maxlength="220" value="<?= admin_e($settings['copyright'] ?? '') ?>" required></label>
                <label>إصدار الدليل<input name="settings[version]" maxlength="32" value="<?= admin_e($settings['version'] ?? '') ?>" required></label>
                <label>عبارة أعلى الصفحة الرئيسية<input name="settings[home_eyebrow]" maxlength="180" value="<?= admin_e($settings['home_eyebrow'] ?? '') ?>" required></label>
                <label>عنوان الصفحة الرئيسية<input name="settings[home_title]" maxlength="180" value="<?= admin_e($settings['home_title'] ?? '') ?>" required></label>
                <label class="field-wide">مقدمة الصفحة الرئيسية<textarea name="settings[home_intro]" maxlength="1000" rows="3" required><?= admin_e($settings['home_intro'] ?? '') ?></textarea></label>
                <label>عنوان قائمة التنقل<input name="settings[navigation_label]" maxlength="80" value="<?= admin_e($settings['navigation_label'] ?? '') ?>" required></label>
                <label>نص حقل البحث<input name="settings[search_placeholder]" maxlength="120" value="<?= admin_e($settings['search_placeholder'] ?? '') ?>" required></label>
                <div class="form-actions"><span></span><button class="button primary" type="submit">حفظ الإعدادات</button></div>
            </form>
            <?php else: ?><div class="notice">يمكن لمدير النظام فقط تعديل إعدادات الموقع العامة.</div><?php endif; ?>
        </section>

        <?php if (false): ?>
        <section id="users" class="panel">
            <div class="panel-heading"><div><span class="eyebrow">الصلاحيات والدخول</span><h2>حسابات لوحة الإدارة</h2><p>أنشئ حسابات مدير أو محرر، وغيّر صلاحياتها أو أوقفها. تُحفظ كلمات المرور بعد تشفيرها.</p></div></div>
            <form method="post" class="user-create-form">
                <input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>"><input type="hidden" name="action" value="create_user">
                <label>الاسم<input name="display_name" maxlength="120" required></label>
                <label>البريد الإلكتروني<input name="email" type="email" maxlength="254" required></label>
                <label>الدور<select name="role"><option value="editor">محرر</option><option value="admin">مدير النظام</option></select></label>
                <label>كلمة مرور مؤقتة<input name="password" type="password" minlength="14" autocomplete="new-password" required></label>
                <button class="button primary" type="submit">إنشاء الحساب</button>
            </form>
            <div class="user-row-forms"><?php foreach ($adminUsers as $account): ?><form id="user-save-<?= (int)$account['id'] ?>" method="post"><input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>"><input type="hidden" name="action" value="update_user"><input type="hidden" name="user_id" value="<?= (int)$account['id'] ?>"></form><?php endforeach; ?></div>
            <div class="table-wrap user-table-wrap"><table><thead><tr><th>الحساب</th><th>الاسم</th><th>الدور</th><th>كلمة مرور جديدة (اختياري)</th><th>الحالة</th><th>آخر دخول</th><th></th></tr></thead><tbody>
            <?php foreach ($adminUsers as $account): $formId = 'user-save-' . (int)$account['id']; ?>
                <tr>
                    <td><span class="email-label"><?= admin_e($account['email']) ?></span></td>
                    <td><input form="<?= $formId ?>" class="user-name-input" name="display_name" maxlength="120" value="<?= admin_e($account['display_name']) ?>" required></td>
                    <td><select form="<?= $formId ?>" name="role"><option value="editor" <?= $account['role'] === 'editor' ? 'selected' : '' ?>>محرر</option><option value="admin" <?= $account['role'] === 'admin' ? 'selected' : '' ?>>مدير</option></select></td>
                    <td><input form="<?= $formId ?>" type="password" name="new_password" minlength="14" autocomplete="new-password" placeholder="اتركها فارغة للإبقاء عليها"></td>
                    <td><label class="switch"><input form="<?= $formId ?>" type="hidden" name="is_active" value="0"><input form="<?= $formId ?>" type="checkbox" name="is_active" value="1" <?= codefy_bool($account['is_active']) ? 'checked' : '' ?> <?= (int)$account['id'] === (int)$user['id'] ? 'disabled' : '' ?>><span></span><span class="switch-label"><?= codefy_bool($account['is_active']) ? 'نشط' : 'موقوف' ?></span></label><?php if ((int)$account['id'] === (int)$user['id']): ?><input form="<?= $formId ?>" type="hidden" name="is_active" value="1"><?php endif; ?></td>
                    <td><span class="last-login"><?= $account['last_login_at'] ? admin_e(date('Y-m-d H:i', strtotime($account['last_login_at']))) : 'لم يسجل الدخول' ?></span></td>
                    <td><button class="button light" form="<?= $formId ?>" type="submit">حفظ</button></td>
                </tr>
            <?php endforeach; ?>
            </tbody></table></div>
        </section>
        <?php endif; ?>

        <?php if (admin_can('audit.view')): ?><section id="activity" class="panel">
            <div class="panel-heading"><div><span class="eyebrow">المتابعة والأمان</span><h2>آخر النشاطات</h2><p>سجل تغييرات لوحة الإدارة وتوقيت تنفيذها.</p></div></div>
            <?php if ($audit): ?><div class="activity-list">
                <?php foreach ($audit as $event): ?>
                <div class="activity-row"><span class="activity-dot"></span><div><strong><?= admin_e($event['display_name'] ?? 'حساب محذوف') ?></strong><span><?= admin_e($event['action']) ?> · <?= admin_e($event['entity_type']) ?></span></div><time><?= admin_e(date('Y-m-d H:i', strtotime($event['created_at']))) ?></time></div>
                <?php endforeach; ?>
            </div><?php else: ?><p class="muted">لا توجد نشاطات مسجلة حتى الآن.</p><?php endif; ?>
        </section><?php endif; ?>
        <footer class="admin-footer">كوديفاي · لوحة الإدارة</footer>
    </main>
</div>
</body>
</html>
