<?php
$accessUsers = is_array($users ?? null) ? $users : [];
$accessRoles = is_array($roles ?? null) ? $roles : [];
$stats = is_array($userStats ?? null) ? $userStats : [];
$mayManageSuperuser = (bool)($canManageTargetSuperuser ?? false);
$mayAssignSuperuser = (bool)($canAssignSuperuser ?? false);
$mayCreateUsers = (bool)($canCreateUsers ?? false);
$mayUpdateUsers = (bool)($canUpdateUsers ?? false);
$mayDeleteUsers = (bool)($canDeleteUsers ?? false);
$accessFlash = is_array($flash ?? null) ? $flash : null;
$accessToken = (string)($csrf ?? '');
$accessBool = static fn($value): bool => $value === true || $value === 1 || in_array(strtolower((string)$value), ['1','t','true','yes','on'], true);
$accountName = (string)($user['name'] ?? $user['display_name'] ?? 'مدير النظام');
$activeCount = (int)($stats['active'] ?? $stats['active_users'] ?? count(array_filter($accessUsers, static fn($row) => $accessBool($row['is_active'] ?? false))));
$inactiveCount = (int)($stats['inactive'] ?? $stats['inactive_users'] ?? count($accessUsers) - $activeCount);
$roleCount = (int)($stats['roles'] ?? $stats['role_count'] ?? count($accessRoles));
$assignableRoleKeys = is_array($assignableRoleKeys ?? null) ? $assignableRoleKeys : [];
$assignableRoles = array_values(array_filter($accessRoles, static fn($role) => is_array($role) && !empty($assignableRoleKeys[(string)($role['role_key'] ?? '')]) && (($role['role_key'] ?? '') !== 'superuser' || $mayAssignSuperuser)));
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>حسابات المستخدمين — كوديفاي</title><link rel="stylesheet" href="admin.css"><link rel="stylesheet" href="access-control.css"></head>
<body class="access-page users-page">
<div class="admin-shell">
    <aside class="admin-sidebar"><a class="admin-brand" href="index.php"><span class="brand-mark">ك</span><span><strong>كوديفاي</strong><small>لوحة الإدارة</small></span></a>
        <?php $activeNav = 'users'; require __DIR__ . '/_navigation.php'; ?>
        <a class="public-link" href="../index.php">↗ عرض الدليل العام</a>
    </aside>
    <main class="admin-main access-main">
        <header class="topbar"><div><span class="eyebrow">مساحة العمل / التحكم بالوصول</span><h1>حسابات المستخدمين</h1></div><div class="account-box"><span class="avatar" aria-hidden="true">ك</span><span><strong><?= admin_e($accountName) ?></strong><small><?= admin_e(admin_role_name((string)($user['role'] ?? ''))) ?></small></span><form method="post" action="index.php"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="logout"><button class="button light" type="submit">خروج</button></form></div></header>
        <?php if ($accessFlash): ?><div class="notice <?= admin_e((string)($accessFlash['type'] ?? '')) ?>" role="status" aria-live="polite"><?= admin_e((string)($accessFlash['message'] ?? '')) ?></div><?php endif; ?>
        <section class="access-intro"><div><span class="eyebrow">إدارة دورة حياة الحساب</span><h2>من لديه حق الدخول؟</h2><p>أنشئ حسابات موثوقة، حدّث أدوارها، وأوقف الجلسات عند الحاجة.</p></div><?php if ($mayCreateUsers): ?><a class="access-jump" href="#create-user">＋ حساب جديد</a><?php endif; ?></section>
        <section class="access-stats" aria-label="ملخص المستخدمين"><article><span class="access-stat-icon active-icon" aria-hidden="true">●</span><span><small>حسابات نشطة</small><strong><?= number_format($activeCount) ?></strong></span></article><article><span class="access-stat-icon inactive-icon" aria-hidden="true">◌</span><span><small>حسابات موقوفة</small><strong><?= number_format($inactiveCount) ?></strong></span></article><article><span class="access-stat-icon roles-icon" aria-hidden="true">▦</span><span><small>الأدوار المتاحة</small><strong><?= number_format($roleCount) ?></strong></span></article></section>

        <?php if ($mayCreateUsers): ?><section class="access-panel create-panel" id="create-user" aria-labelledby="create-user-title"><header class="access-panel-heading"><div><span class="eyebrow">إضافة وصول جديد</span><h2 id="create-user-title">إنشاء حساب</h2><p>أرسل بيانات دخول أولية للمستخدم الجديد.</p></div><span class="panel-mark" aria-hidden="true">＋</span></header>
            <form method="post" action="users.php" class="access-form user-create-form"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="create_user">
                <label class="access-field">الاسم المعروض<input name="display_name" maxlength="120" autocomplete="name" required></label>
                <label class="access-field">البريد الإلكتروني<input name="email" type="email" maxlength="254" autocomplete="email" dir="ltr" required></label>
                <label class="access-field">الدور<select name="role" required><?php if (!$assignableRoles): ?><option value="" disabled selected>لا توجد أدوار قابلة للتعيين</option><?php endif; ?><?php foreach ($assignableRoles as $role): ?><option value="<?= admin_e((string)$role['role_key']) ?>"><?= admin_e((string)$role['name']) ?><?= ($role['role_key'] ?? '') === 'superuser' ? ' · فائق الصلاحية' : '' ?></option><?php endforeach; ?></select></label>
                <label class="access-field">كلمة المرور الأولية<input name="password" type="password" minlength="14" maxlength="72" autocomplete="new-password" required><small>14 حرفاً على الأقل، وبحد أقصى 72 بايت.</small></label>
                <button class="button primary" type="submit" <?= !$assignableRoles ? 'disabled' : '' ?>>إنشاء الحساب</button>
            </form>
        </section><?php endif; ?>

        <section class="access-panel directory-panel" aria-labelledby="users-list-title"><header class="access-panel-heading directory-heading"><div><span class="eyebrow">دليل الوصول</span><h2 id="users-list-title">الحسابات المسجلة</h2><p>عدّل بيانات الحساب أو صلاحياته. إعادة تعيين كلمة المرور تنهي الجلسات الحالية.</p></div><span class="directory-count"><?= count($accessUsers) ?> حساب</span></header>
            <div class="directory-tools"><label class="directory-search"><span aria-hidden="true">⌕</span><span class="sr-only">ابحث بالاسم أو البريد</span><input type="search" data-user-search placeholder="ابحث بالاسم أو البريد الإلكتروني" autocomplete="off"></label><label class="sr-only" for="user-state-filter">تصفية حالة الحساب</label><select id="user-state-filter" data-user-state><option value="all">كل الحالات</option><option value="active">نشط</option><option value="inactive">موقوف</option></select><span data-user-result aria-live="polite"><?= count($accessUsers) ?> حساب</span></div>
            <?php if ($accessUsers): ?><div class="access-table-wrap"><table class="access-table"><caption class="sr-only">حسابات لوحة الإدارة</caption><thead><tr><th scope="col">المستخدم</th><th scope="col">الدور</th><th scope="col">الحالة</th><th scope="col">آخر تسجيل دخول</th><th scope="col">إجراءات الحساب</th></tr></thead><tbody>
                <?php foreach ($accessUsers as $account): if (!is_array($account)) continue; $targetSuperuser = ($account['role'] ?? '') === 'superuser'; $readOnly = ($targetSuperuser && !$mayManageSuperuser) || empty($account['can_manage']); $isActive = $accessBool($account['is_active'] ?? false); $formId = 'user-update-' . (int)($account['id'] ?? 0); $displayName=(string)($account['display_name'] ?? $account['email'] ?? 'م'); $initial='م'; if (preg_match('/^./us',$displayName,$initialMatch)) $initial=$initialMatch[0]; ?>
                <tr data-user-row data-search-text="<?= admin_e((string)($account['display_name'] ?? '') . ' ' . (string)($account['email'] ?? '')) ?>" data-user-state="<?= $isActive ? 'active' : 'inactive' ?>">
                    <td class="identity-cell"><span class="user-avatar" aria-hidden="true"><?= admin_e($initial) ?></span><span><strong><?= admin_e((string)($account['display_name'] ?? 'بدون اسم')) ?><?php if ($targetSuperuser): ?><span class="superuser-badge">فائق الصلاحية</span><?php endif; ?></strong><small dir="ltr"><?= admin_e((string)($account['email'] ?? '')) ?></small></span></td>
                    <td><?php if ($readOnly): ?><span class="role-pill <?= $targetSuperuser ? 'superuser-role' : '' ?>"><?= admin_e((string)($account['role_name'] ?? '')) ?></span><?php elseif ($mayUpdateUsers): ?><select form="<?= admin_e($formId) ?>" name="role" aria-label="دور <?= admin_e((string)($account['display_name'] ?? 'المستخدم')) ?>"><?php if (!isset($assignableRoleKeys[(string)($account['role'] ?? '')])): ?><option value="<?= admin_e((string)$account['role']) ?>" selected disabled><?= admin_e((string)($account['role_name'] ?? $account['role'])) ?> — غير قابل للتعيين</option><?php endif; ?><?php foreach ($assignableRoles as $role): ?><option value="<?= admin_e((string)$role['role_key']) ?>" <?= ($account['role'] ?? '') === ($role['role_key'] ?? '') ? 'selected' : '' ?>><?= admin_e((string)$role['name']) ?></option><?php endforeach; ?></select><?php else: ?><span class="role-pill"><?= admin_e((string)($account['role_name'] ?? '')) ?></span><?php endif; ?></td>
                    <td><span class="state-pill <?= $isActive ? 'state-active' : 'state-inactive' ?>"><span></span><?= $isActive ? 'نشط' : 'موقوف' ?></span></td>
                    <td class="last-login-cell"><?= !empty($account['last_login_at']) ? admin_e(date('Y-m-d H:i', strtotime((string)$account['last_login_at']))) : 'لم يسجل الدخول بعد' ?></td>
                    <td class="user-actions-cell">
                        <?php if ($readOnly): ?><span class="read-only-note">حساب محمي للقراءة فقط</span><?php else: ?>
                        <?php if ($mayUpdateUsers): ?>
                        <form id="<?= admin_e($formId) ?>" method="post" action="users.php" class="user-update-form"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="update_user"><input type="hidden" name="user_id" value="<?= (int)($account['id'] ?? 0) ?>">
                            <input name="display_name" maxlength="120" value="<?= admin_e((string)($account['display_name'] ?? '')) ?>" aria-label="اسم <?= admin_e((string)($account['email'] ?? 'المستخدم')) ?>" required>
                            <input name="new_password" type="password" minlength="14" maxlength="72" autocomplete="new-password" placeholder="إعادة تعيين كلمة المرور" aria-label="كلمة مرور جديدة لـ <?= admin_e((string)($account['email'] ?? 'المستخدم')) ?>">
                            <input type="hidden" name="is_active" value="0"><label class="state-toggle"><input name="is_active" type="checkbox" value="1" <?= $isActive ? 'checked' : '' ?>><span>نشط</span></label>
                            <button class="button light" type="submit">حفظ</button>
                        </form>
                        <?php endif; ?>
                        <?php if ($mayDeleteUsers): ?><form method="post" action="users.php" class="user-delete-form" data-access-confirm="حذف هذا الحساب نهائياً؟ لن يتمكن صاحبه من تسجيل الدخول."><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="delete_user"><input type="hidden" name="user_id" value="<?= (int)($account['id'] ?? 0) ?>"><button class="button quiet-danger" type="submit">حذف</button></form><?php endif; ?>
                        <?php endif; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody></table></div><div class="directory-empty" data-users-empty hidden><strong>لا توجد حسابات مطابقة</strong><p>غيّر كلمات البحث أو حالة الحساب.</p></div>
            <?php else: ?><div class="access-empty"><span aria-hidden="true">♙</span><strong>لا توجد حسابات بعد</strong><p>أنشئ أول حساب من النموذج أعلاه.</p></div><?php endif; ?>
        </section>
        <aside class="access-note"><span aria-hidden="true">i</span><p><strong>حماية الجلسات:</strong> تغيير كلمة المرور يزيد رقم إصدار الجلسة، فيطلب من جميع الأجهزة تسجيل الدخول مرة أخرى.</p></aside>
        <footer class="admin-footer">كوديفاي · إدارة الحسابات</footer>
    </main>
</div>
<script>
(()=>{const search=document.querySelector('[data-user-search]'),state=document.querySelector('[data-user-state]'),rows=[...document.querySelectorAll('[data-user-row]')],empty=document.querySelector('[data-users-empty]'),result=document.querySelector('[data-user-result]');const filter=()=>{const q=(search?.value||'').trim().toLocaleLowerCase();const mode=state?.value||'all';let shown=0;rows.forEach(row=>{const visible=(row.dataset.searchText||'').toLocaleLowerCase().includes(q)&&(mode==='all'||row.dataset.userState===mode);row.hidden=!visible;if(visible)shown++;});if(empty)empty.hidden=shown!==0;if(result)result.textContent=`عرض ${shown} من ${rows.length} حساب`;};search?.addEventListener('input',filter);state?.addEventListener('change',filter);document.querySelectorAll('[data-access-confirm]').forEach(form=>form.addEventListener('submit',event=>{if(!window.confirm(form.dataset.accessConfirm))event.preventDefault();}));})();
</script>
</body></html>
