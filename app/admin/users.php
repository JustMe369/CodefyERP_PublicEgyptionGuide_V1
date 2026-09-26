<?php
require __DIR__ . '/_bootstrap.php';
$user = admin_require_permission('users.view');
$pdo = codefy_db();

$canAssignRole = static function (string $roleKey) use ($pdo, $user): bool {
    if (($user['role'] ?? '') === 'superuser') return true;
    if ($roleKey === 'superuser') return false;
    $active = $pdo->prepare('SELECT is_active FROM codefy_admin_roles WHERE role_key=:role');
    $active->execute(['role'=>$roleKey]);
    if (!codefy_bool($active->fetchColumn())) return false;
    $target = $pdo->prepare('SELECT p.permission_key FROM codefy_admin_role_permissions rp JOIN codefy_admin_permissions p USING (permission_key) JOIN codefy_admin_roles r USING (role_key) WHERE rp.role_key = :role AND r.is_active');
    $target->execute(['role' => $roleKey]);
    $actorPermissions = admin_user_permissions($user);
    foreach ($target->fetchAll(PDO::FETCH_COLUMN) as $permission) if (!isset($actorPermissions[$permission])) return false;
    return true;
};
$targetRoleWithinActor = static function (string $roleKey) use ($pdo, $user): bool {
    if (($user['role'] ?? '') === 'superuser') return true;
    $target = $pdo->prepare('SELECT permission_key FROM codefy_admin_role_permissions WHERE role_key=:role');
    $target->execute(['role'=>$roleKey]);
    $actorPermissions = admin_user_permissions($user);
    foreach ($target->fetchAll(PDO::FETCH_COLUMN) as $permission) if (!isset($actorPermissions[$permission])) return false;
    return true;
};

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_require_csrf();
    try {
        $action = (string)($_POST['action'] ?? '');
        if ($action === 'create_user') {
            admin_require_permission('users.create');
            $email = strtolower(trim((string)($_POST['email'] ?? '')));
            $name = trim((string)($_POST['display_name'] ?? ''));
            $password = (string)($_POST['password'] ?? '');
            $role = trim((string)($_POST['role'] ?? ''));
            if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 254 || $name === '' || strlen($name) > 120 || !codefy_password_is_valid($password)) {
                throw new InvalidArgumentException('تحقق من الاسم والبريد وكلمة المرور (14 حرفاً على الأقل وبحد 72 بايت).');
            }
            if (!$canAssignRole($role)) throw new InvalidArgumentException('لا يمكنك تعيين هذا الدور أو أنه غير نشط.');
            $pdo->beginTransaction();
            $insert = $pdo->prepare('INSERT INTO codefy_admin_users (email, password_hash, display_name, role) VALUES (:email, :hash, :name, :role) RETURNING id');
            $insert->execute(['email' => $email, 'hash' => password_hash($password, PASSWORD_DEFAULT), 'name' => $name, 'role' => $role]);
            $newId = (string)$insert->fetchColumn();
            codefy_admin_audit($pdo, (int)$user['id'], 'create', 'admin_user', $newId, ['email' => $email, 'role' => $role]);
            $pdo->commit();
            admin_flash('success', 'تم إنشاء الحساب وربطه بالدور المحدد.');
        } elseif ($action === 'update_user') {
            admin_require_permission('users.update');
            $targetId = filter_var($_POST['user_id'] ?? null, FILTER_VALIDATE_INT);
            $name = trim((string)($_POST['display_name'] ?? ''));
            $role = trim((string)($_POST['role'] ?? ''));
            $isActive = ($_POST['is_active'] ?? '0') === '1';
            $newPassword = (string)($_POST['new_password'] ?? '');
            if (!$targetId || $name === '' || strlen($name) > 120 || ($newPassword !== '' && !codefy_password_is_valid($newPassword))) {
                throw new InvalidArgumentException('تحقق من الاسم والدور وكلمة المرور الجديدة (14 حرفاً على الأقل وبحد 72 بايت).');
            }
            if ((int)$targetId === (int)$user['id'] && !$isActive) throw new InvalidArgumentException('لا يمكنك إيقاف حسابك الحالي.');
            if (!$canAssignRole($role)) throw new InvalidArgumentException('لا يمكنك تعيين هذا الدور أو أنه غير نشط.');

            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713249)');
            $lookup = $pdo->prepare('SELECT id, role, is_active FROM codefy_admin_users WHERE id = :id FOR UPDATE');
            $lookup->execute(['id' => $targetId]);
            $target = $lookup->fetch();
            if (!$target) throw new InvalidArgumentException('الحساب المطلوب غير موجود.');
            $actorIsSuperuser = ($user['role'] ?? '') === 'superuser';
            if ($target['role'] === 'superuser' && !$actorIsSuperuser) throw new InvalidArgumentException('حساب المستخدم الأعلى محمي ولا يستطيع تعديله إلا مستخدم أعلى آخر.');
            if (!$actorIsSuperuser && !$targetRoleWithinActor((string)$target['role'])) throw new InvalidArgumentException('لا تملك صلاحية تعديل حساب يحمل قدرات أعلى من دورك.');
            $losesLastSuperuser = $target['role'] === 'superuser' && ($role !== 'superuser' || !$isActive);
            $otherActiveSuperusers = $pdo->prepare("SELECT count(*) FROM codefy_admin_users WHERE role='superuser' AND is_active AND id<>:id");
            $otherActiveSuperusers->execute(['id'=>$targetId]);
            if ($losesLastSuperuser && (int)$otherActiveSuperusers->fetchColumn() < 1) {
                throw new InvalidArgumentException('يجب إبقاء مستخدم أعلى نشط واحد على الأقل.');
            }
            $changedAccess = $target['role'] !== $role || codefy_bool($target['is_active']) !== $isActive || $newPassword !== '';
            if ($newPassword !== '') {
                $save = $pdo->prepare('UPDATE codefy_admin_users SET display_name=:name, role=:role, is_active=:active, password_hash=:hash, session_version=session_version+:revoke, updated_at=now() WHERE id=:id');
                $save->execute(['name'=>$name,'role'=>$role,'active'=>$isActive,'hash'=>password_hash($newPassword,PASSWORD_DEFAULT),'revoke'=>$changedAccess?1:0,'id'=>$targetId]);
            } else {
                $save = $pdo->prepare('UPDATE codefy_admin_users SET display_name=:name, role=:role, is_active=:active, session_version=session_version+:revoke, updated_at=now() WHERE id=:id');
                $save->execute(['name'=>$name,'role'=>$role,'active'=>$isActive,'revoke'=>$changedAccess?1:0,'id'=>$targetId]);
            }
            codefy_admin_audit($pdo, (int)$user['id'], 'update', 'admin_user', (string)$targetId, ['role'=>$role,'is_active'=>$isActive,'password_reset'=>$newPassword!=='']);
            $pdo->commit();
            admin_flash('success', 'تم تحديث الحساب. أُبطلت الجلسات السابقة عند تغيير كلمة المرور أو الصلاحية.');
        } elseif ($action === 'delete_user') {
            admin_require_permission('users.delete');
            $targetId = filter_var($_POST['user_id'] ?? null, FILTER_VALIDATE_INT);
            if (!$targetId) throw new InvalidArgumentException('معرّف الحساب غير صالح.');
            if ((int)$targetId === (int)$user['id']) throw new InvalidArgumentException('لا يمكنك حذف الحساب الذي تستخدمه حالياً.');
            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713249)');
            $lookup = $pdo->prepare('SELECT id, email, role, is_active FROM codefy_admin_users WHERE id=:id FOR UPDATE');
            $lookup->execute(['id'=>$targetId]);
            $target = $lookup->fetch();
            if (!$target) throw new InvalidArgumentException('الحساب المطلوب غير موجود.');
            if ($target['role'] === 'superuser' && ($user['role'] ?? '') !== 'superuser') throw new InvalidArgumentException('حساب المستخدم الأعلى محمي.');
            if (($user['role'] ?? '') !== 'superuser' && !$targetRoleWithinActor((string)$target['role'])) throw new InvalidArgumentException('لا تملك صلاحية حذف حساب يحمل قدرات أعلى من دورك.');
            $otherActiveSuperusers = $pdo->prepare("SELECT count(*) FROM codefy_admin_users WHERE role='superuser' AND is_active AND id<>:id");
            $otherActiveSuperusers->execute(['id'=>$targetId]);
            if ($target['role'] === 'superuser' && (int)$otherActiveSuperusers->fetchColumn() < 1) {
                throw new InvalidArgumentException('يجب إبقاء مستخدم أعلى نشط واحد على الأقل.');
            }
            codefy_admin_audit($pdo, (int)$user['id'], 'delete', 'admin_user', (string)$targetId, ['email'=>$target['email'],'role'=>$target['role']]);
            $pdo->prepare('DELETE FROM codefy_admin_users WHERE id=:id')->execute(['id'=>$targetId]);
            $pdo->commit();
            admin_flash('success', 'تم حذف الحساب نهائياً.');
        } else {
            throw new InvalidArgumentException('الإجراء المطلوب غير معروف.');
        }
    } catch (Throwable $error) {
        if ($pdo->inTransaction()) $pdo->rollBack();
        error_log('Codefy user management failed: ' . $error->getMessage());
        $message = $error instanceof InvalidArgumentException ? $error->getMessage() : 'تعذر حفظ الحساب. تحقق من البريد أو قاعدة البيانات وحاول مرة أخرى.';
        if ($error instanceof PDOException && (str_contains($error->getMessage(), 'codefy_admin_users_email_key') || str_contains($error->getMessage(), 'codefy_admin_email_lower_idx'))) $message = 'يوجد حساب بهذا البريد الإلكتروني بالفعل.';
        admin_flash('error', $message);
    }
    header('Location: users.php');
    exit;
}

$roles = $pdo->query("SELECT r.role_key, r.name, r.description, r.is_system, r.is_active, count(u.id)::int AS member_count FROM codefy_admin_roles r LEFT JOIN codefy_admin_users u ON u.role=r.role_key GROUP BY r.role_key ORDER BY r.is_system DESC, r.name")->fetchAll();
$users = $pdo->query('SELECT u.id,u.email,u.display_name,u.role,r.name AS role_name,u.is_active,u.last_login_at,u.created_at FROM codefy_admin_users u JOIN codefy_admin_roles r ON r.role_key=u.role ORDER BY u.created_at,u.id')->fetchAll();
$assignableRoleKeys = [];
foreach ($roles as $index => $role) {
    $roles[$index]['can_assign'] = codefy_bool($role['is_active']) && $canAssignRole((string)$role['role_key']);
    if ($roles[$index]['can_assign']) $assignableRoleKeys[(string)$role['role_key']] = true;
}
foreach ($users as $index => $account) {
    $users[$index]['can_manage'] = ($user['role'] ?? '') === 'superuser'
        || ($account['role'] !== 'superuser' && $targetRoleWithinActor((string)$account['role']));
}
$userStats = ['active'=>0,'inactive'=>0,'roles'=>count(array_filter($roles,static fn($role)=>codefy_bool($role['is_active'])))];
foreach ($users as $account) $userStats[codefy_bool($account['is_active'])?'active':'inactive']++;
$canAssignSuperuser = ($user['role'] ?? '') === 'superuser';
$canManageTargetSuperuser = $canAssignSuperuser;
$canCreateUsers = admin_can('users.create', $user);
$canUpdateUsers = admin_can('users.update', $user);
$canDeleteUsers = admin_can('users.delete', $user);
$currentRoleName = admin_role_name((string)($user['role'] ?? ''));
$flash = admin_take_flash();
$csrf = admin_csrf_token();
$activeNav = 'users';
require __DIR__ . '/users-view.php';
