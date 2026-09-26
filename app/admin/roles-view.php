<?php
$accessRoles = is_array($roles ?? null) ? $roles : [];
$permissionGroups = is_array($permissionGroups ?? null) ? $permissionGroups : [];
$editableByRole = is_array($editablePermissionsByRole ?? null) ? $editablePermissionsByRole : [];
$deletableKeys = is_array($canDeleteRoleKeys ?? null) ? $canDeleteRoleKeys : [];
$stats = is_array($roleStats ?? null) ? $roleStats : [];
$accessFlash = is_array($flash ?? null) ? $flash : null;
$accessToken = (string)($csrf ?? '');
$accessBool = static fn($value): bool => $value === true || $value === 1 || in_array(strtolower((string)$value), ['1','t','true','yes','on'], true);
$mayManageRoles = $accessBool($canManageRoles ?? true);
$mayModifySystemRoles = $accessBool($canModifySystemRoles ?? false);
$accountName = (string)($user['name'] ?? $user['display_name'] ?? 'مدير النظام');
$roleCount = (int)($stats['roles'] ?? $stats['role_count'] ?? count($accessRoles));
$memberCount = (int)($stats['members'] ?? $stats['assigned_users'] ?? array_sum(array_map(static fn($r) => (int)($r['member_count'] ?? 0), array_filter($accessRoles, 'is_array'))));
$permissionCount = (int)($stats['permissions'] ?? $stats['permission_count'] ?? array_sum(array_map(static fn($g) => count(is_array($g['permissions'] ?? null) ? $g['permissions'] : []), array_filter($permissionGroups, 'is_array'))));
$isDeletable = static function (string $key) use ($deletableKeys): bool { return array_is_list($deletableKeys) ? in_array($key, $deletableKeys, true) : !empty($deletableKeys[$key]); };
$permKeys = static function ($role): array { $keys = $role['permission_keys'] ?? []; if (is_string($keys)) { $decoded = json_decode($keys, true); $keys = is_array($decoded) ? $decoded : []; } return is_array($keys) ? array_values(array_filter($keys, 'is_string')) : []; };
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>الأدوار والصلاحيات — كوديفاي</title><link rel="stylesheet" href="admin.css"><link rel="stylesheet" href="access-control.css"></head>
<body class="access-page roles-page">
<div class="admin-shell">
    <aside class="admin-sidebar"><a class="admin-brand" href="index.php"><span class="brand-mark">ك</span><span><strong>كوديفاي</strong><small>لوحة الإدارة</small></span></a>
        <?php $activeNav = 'roles'; require __DIR__ . '/_navigation.php'; ?>
        <a class="public-link" href="../index.php">↗ عرض الدليل العام</a>
    </aside>
    <main class="admin-main access-main">
        <header class="topbar"><div><span class="eyebrow">مساحة العمل / التحكم بالوصول</span><h1>الأدوار والصلاحيات</h1></div><div class="account-box"><span class="avatar" aria-hidden="true">ك</span><span><strong><?= admin_e($accountName) ?></strong><small><?= admin_e(admin_role_name((string)($user['role'] ?? ''))) ?></small></span><form method="post" action="index.php"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="logout"><button class="button light" type="submit">خروج</button></form></div></header>
        <?php if ($accessFlash): ?><div class="notice <?= admin_e((string)($accessFlash['type'] ?? '')) ?>" role="status" aria-live="polite"><?= admin_e((string)($accessFlash['message'] ?? '')) ?></div><?php endif; ?>
        <section class="access-intro role-intro"><div><span class="eyebrow">مصفوفة التحكم</span><h2>الصلاحية المناسبة لكل مهمة</h2><p>كوّن أدواراً بحسب القدرات المطلوبة، ثم عيّنها للحسابات.</p></div><?php if ($mayManageRoles): ?><a class="access-jump" href="#create-role">＋ دور مخصص</a><?php endif; ?></section>
        <section class="access-stats role-stats" aria-label="ملخص الأدوار"><article><span class="access-stat-icon roles-icon" aria-hidden="true">▦</span><span><small>إجمالي الأدوار</small><strong><?= number_format($roleCount) ?></strong></span></article><article><span class="access-stat-icon active-icon" aria-hidden="true">♙</span><span><small>حسابات مرتبطة</small><strong><?= number_format($memberCount) ?></strong></span></article><article><span class="access-stat-icon permissions-icon" aria-hidden="true">✓</span><span><small>قدرات معرفة</small><strong><?= number_format($permissionCount) ?></strong></span></article></section>

        <section class="access-panel role-directory" aria-labelledby="role-directory-title"><header class="access-panel-heading"><div><span class="eyebrow">أدوار البيئة</span><h2 id="role-directory-title">الأدوار الحالية</h2><p>استعرض مفاتيح الأدوار وحالتها وعدد الحسابات والقدرات المرتبطة بها.</p></div><span class="directory-count"><?= count($accessRoles) ?> دور</span></header>
            <?php if ($accessRoles): ?><div class="role-list">
                <?php foreach ($accessRoles as $role): if (!is_array($role)) continue; $key=(string)($role['role_key'] ?? ''); $system=$accessBool($role['is_system'] ?? false); $superuser=$key==='superuser'; $enabled=$accessBool($role['is_active'] ?? false); $canEditPermissions=$mayManageRoles && !$superuser && (!$system || $accessBool($editableByRole[$key] ?? false)); $canSaveRole=$mayManageRoles && !$superuser && (!$system || $mayModifySystemRoles); $permissions=$permKeys($role); $formId='role-update-' . substr(hash('sha256',$key),0,12); ?>
                <article class="role-record<?= $superuser ? ' superuser-record' : '' ?>">
                    <header class="role-record-head"><span class="role-symbol<?= $superuser ? ' super-symbol' : '' ?>" aria-hidden="true"><?= $superuser ? '✦' : ($system ? '▣' : '▦') ?></span><div class="role-identity"><h3><?= admin_e((string)($role['name'] ?? $key)) ?><?php if ($system): ?><span class="system-badge">دور نظام</span><?php else: ?><span class="custom-badge">مخصص</span><?php endif; ?></h3><code dir="ltr"><?= admin_e($key) ?></code><p><?= admin_e((string)($role['description'] ?? 'لا يوجد وصف لهذا الدور.')) ?></p></div><div class="role-facts"><span class="state-pill <?= $enabled ? 'state-active' : 'state-inactive' ?>"><span></span><?= $enabled ? 'نشط' : 'موقوف' ?></span><small><?= number_format((int)($role['member_count'] ?? 0)) ?> حسابات</small><small><?= $superuser ? 'وصول كامل' : number_format(count($permissions)) . ' قدرات' ?></small></div></header>
                    <?php if ($superuser): ?><div class="full-access-callout"><span aria-hidden="true">✦</span><p><strong>صلاحية فائقة كاملة</strong> — هذا الدور يملك وصولاً كاملاً للنظام. لا يمكن تعديل هويته أو قائمة قدراته من هذه الشاشة.</p></div><?php endif; ?>
                    <details class="role-editor-details"><summary><?= $system ? 'عرض إعدادات الدور' : 'تحرير الدور والقدرات' ?><span aria-hidden="true">⌄</span></summary>
                        <form id="<?= admin_e($formId) ?>" method="post" action="roles.php" class="role-edit-form"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="update_role"><input type="hidden" name="role_key" value="<?= admin_e($key) ?>">
                            <div class="role-identity-fields"><label class="access-field">اسم الدور<input name="name" maxlength="100" value="<?= admin_e((string)($role['name'] ?? '')) ?>" <?= ($system || !$mayManageRoles) ? 'disabled' : 'required' ?>></label><label class="access-field">مفتاح الدور<input dir="ltr" value="<?= admin_e($key) ?>" disabled><small>المفتاح ثابت بعد إنشاء الدور.</small></label><label class="access-field field-span">وصف مختصر<textarea name="description" maxlength="240" rows="2" <?= ($system || !$mayManageRoles) ? 'disabled' : '' ?>><?= admin_e((string)($role['description'] ?? '')) ?></textarea></label><?php if (!$superuser): ?><label class="state-toggle active-role-toggle"><input type="checkbox" name="is_active" value="1" <?= $enabled ? 'checked' : '' ?> <?= (!$mayManageRoles || ($system && !$mayModifySystemRoles)) ? 'disabled' : '' ?>><span>الدور نشط</span></label><?php endif; ?></div>
                            <?php if ($superuser): ?><p class="locked-permissions">قائمة القدرات محمية، والوصول الكامل موروث من دور النظام.</p>
                            <?php else: ?><div class="permission-matrix"><div class="matrix-heading"><div><h4>مصفوفة القدرات</h4><p><?= $canEditPermissions ? 'اختر القدرات التي يحتاجها هذا الدور.' : 'قدرات دور النظام للعرض فقط.' ?></p></div><span><?= count($permissions) ?> مفعلة</span></div>
                                <?php if (!$canEditPermissions): foreach ($permissions as $lockedPermission): ?><input type="hidden" name="permissions[]" value="<?= admin_e($lockedPermission) ?>"><?php endforeach; endif; ?>
                                <?php foreach ($permissionGroups as $group): if (!is_array($group)) continue; $groupItems=is_array($group['permissions'] ?? null)?$group['permissions']:[]; if (!$groupItems) continue; ?>
                                <fieldset class="permission-group"><legend><?= admin_e((string)($group['label'] ?? 'قدرات')) ?></legend><div class="permission-options">
                                    <?php foreach ($groupItems as $permission): if (!is_array($permission)) continue; $permissionKey=(string)($permission['key'] ?? ''); if ($permissionKey==='') continue; ?>
                                    <label class="permission-option"><input type="checkbox" name="permissions[]" value="<?= admin_e($permissionKey) ?>" <?= in_array($permissionKey,$permissions,true) ? 'checked' : '' ?> <?= $canEditPermissions ? '' : 'disabled' ?>><span class="permission-check" aria-hidden="true"></span><span><strong><?= admin_e((string)($permission['label'] ?? $permissionKey)) ?></strong><small><?= admin_e((string)($permission['description'] ?? '')) ?></small></span><code dir="ltr"><?= admin_e($permissionKey) ?></code></label>
                                    <?php endforeach; ?>
                                </div></fieldset><?php endforeach; ?>
                            </div><?php endif; ?>
                            <footer class="role-edit-actions"><span class="muted-access"><?php if ($superuser): ?>الدور فائق الصلاحية للعرض فقط.<?php elseif ($system && !$mayModifySystemRoles): ?>تعديل دور النظام غير متاح لحسابك.<?php elseif (!$mayManageRoles): ?>ليس لديك صلاحية إدارة الأدوار.<?php else: ?>تغييرات الصلاحية تُطبّق على الحسابات المرتبطة بهذا الدور.<?php endif; ?></span><?php if ($canSaveRole): ?><button class="button primary" type="submit">حفظ الدور</button><?php elseif ($system && !$superuser && $mayManageRoles): ?><button class="button light" type="button" disabled>حفظ دور النظام غير متاح</button><?php endif; ?></footer>
                        </form>
                    </details>
                    <?php if ($mayManageRoles && !$superuser && $isDeletable($key)): ?><form method="post" action="roles.php" class="role-delete-form" data-access-confirm="حذف هذا الدور؟ تأكد أولاً من عدم وجود حسابات تعتمد عليه."><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="delete_role"><input type="hidden" name="role_key" value="<?= admin_e($key) ?>"><button class="button quiet-danger" type="submit">حذف الدور</button></form><?php endif; ?>
                </article>
                <?php endforeach; ?>
            </div><?php else: ?><div class="access-empty"><span aria-hidden="true">▦</span><strong>لا توجد أدوار معرفة</strong><p>أنشئ دوراً مخصصاً من النموذج أدناه.</p></div><?php endif; ?>
        </section>

        <section class="access-panel create-role-panel" id="create-role" aria-labelledby="create-role-title"><header class="access-panel-heading"><div><span class="eyebrow">دور جديد</span><h2 id="create-role-title">إنشاء دور مخصص</h2><p>امنح أقل مجموعة قدرات لازمة لإنجاز العمل.</p></div><span class="panel-mark" aria-hidden="true">＋</span></header>
            <?php if ($mayManageRoles): ?><form method="post" action="roles.php" class="role-create-form"><input type="hidden" name="_csrf" value="<?= admin_e($accessToken) ?>"><input type="hidden" name="action" value="create_role">
                <div class="role-identity-fields"><label class="access-field">اسم الدور<input name="name" maxlength="100" required></label><label class="access-field">مفتاح الدور<input name="role_key" dir="ltr" maxlength="64" pattern="[a-z][a-z0-9_]*" placeholder="content_editor" required><small>أحرف صغيرة وأرقام وشرطة سفلية.</small></label><label class="access-field field-span">وصف مختصر<textarea name="description" maxlength="240" rows="2" placeholder="المهام التي يسمح بها هذا الدور"></textarea></label><label class="state-toggle active-role-toggle"><input type="checkbox" name="is_active" value="1" checked><span>الدور نشط</span></label></div>
                <div class="permission-matrix"><div class="matrix-heading"><div><h4>اختر القدرات</h4><p>يمكنك تحديث هذه الاختيارات لاحقاً.</p></div><span><?= $permissionCount ?> متاحة</span></div>
                    <?php foreach ($permissionGroups as $group): if (!is_array($group)) continue; $groupItems=is_array($group['permissions'] ?? null)?$group['permissions']:[]; if (!$groupItems) continue; ?>
                    <fieldset class="permission-group"><legend><?= admin_e((string)($group['label'] ?? 'قدرات')) ?></legend><div class="permission-options">
                        <?php foreach ($groupItems as $permission): if (!is_array($permission)) continue; $permissionKey=(string)($permission['key'] ?? ''); if ($permissionKey==='') continue; ?>
                        <label class="permission-option"><input type="checkbox" name="permissions[]" value="<?= admin_e($permissionKey) ?>"><span class="permission-check" aria-hidden="true"></span><span><strong><?= admin_e((string)($permission['label'] ?? $permissionKey)) ?></strong><small><?= admin_e((string)($permission['description'] ?? '')) ?></small></span><code dir="ltr"><?= admin_e($permissionKey) ?></code></label>
                        <?php endforeach; ?>
                    </div></fieldset><?php endforeach; ?>
                </div><footer class="role-edit-actions"><span class="muted-access">ابدأ بأقل صلاحية لازمة.</span><button class="button primary" type="submit">إنشاء الدور</button></footer>
            </form><?php else: ?><p class="role-access-denied" role="status">ليس لديك صلاحية إنشاء أدوار أو تعديلها.</p><?php endif; ?>
        </section>
        <footer class="admin-footer">كوديفاي · استوديو الأدوار</footer>
    </main>
</div>
<script>document.querySelectorAll('[data-access-confirm]').forEach(form=>form.addEventListener('submit',event=>{if(!window.confirm(form.dataset.accessConfirm))event.preventDefault();}));</script>
</body></html>
