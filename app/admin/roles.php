<?php
require __DIR__ . '/_bootstrap.php';
$user = admin_require_permission('roles.view');
$pdo = codefy_db();
$actorIsSuperuser = ($user['role'] ?? '') === 'superuser';

$permissionGroups = [];
foreach ($pdo->query('SELECT permission_key, group_key, label, description FROM codefy_admin_permissions ORDER BY sort_order') as $permission) {
    $group = (string)$permission['group_key'];
    if (!isset($permissionGroups[$group])) $permissionGroups[$group] = ['key'=>$group,'label'=>[
        'dashboard'=>'لوحة التحكم','sections'=>'إدارة الأقسام','settings'=>'إعدادات الموقع',
        'database'=>'قاعدة البيانات','users'=>'المستخدمون','roles'=>'الأدوار','audit'=>'سجل النشاط'
    ][$group] ?? $group,'permissions'=>[]];
    $permissionGroups[$group]['permissions'][] = ['key'=>$permission['permission_key'],'label'=>$permission['label'],'description'=>$permission['description']];
}
$permissionGroups = array_values($permissionGroups);
$knownPermissions = [];
foreach ($permissionGroups as $group) foreach ($group['permissions'] as $permission) $knownPermissions[$permission['key']] = true;
$actorPermissions = admin_user_permissions($user);
$canManageRoleKey = static function (string $roleKey) use ($actorIsSuperuser, $actorPermissions, $pdo): bool {
    if ($actorIsSuperuser) return true;
    $statement = $pdo->prepare('SELECT p.permission_key FROM codefy_admin_role_permissions rp JOIN codefy_admin_permissions p USING (permission_key) WHERE rp.role_key=:role');
    $statement->execute(['role'=>$roleKey]);
    foreach ($statement->fetchAll(PDO::FETCH_COLUMN) as $permission) if (!isset($actorPermissions[$permission])) return false;
    return true;
};

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_require_csrf();
    try {
        $action = (string)($_POST['action'] ?? '');
        if ($action === 'create_role') {
            admin_require_permission('roles.manage');
            $key = trim((string)($_POST['role_key'] ?? ''));
            $name = trim((string)($_POST['name'] ?? ''));
            $description = trim((string)($_POST['description'] ?? ''));
            $isActive = ($_POST['is_active'] ?? '0') === '1';
            $requested = $_POST['permissions'] ?? [];
            if (!preg_match('/^[a-z][a-z0-9_]{1,47}$/D', $key) || $name === '' || strlen($name) > 80 || strlen($description) > 240 || !is_array($requested) || count($requested) > count($knownPermissions)) {
                throw new InvalidArgumentException('تحقق من مفتاح الدور واسمه ووصفه والقدرات المختارة.');
            }
            $requested = array_values(array_unique(array_filter($requested, static fn($key) => is_string($key) && isset($knownPermissions[$key]))));
            if (!$actorIsSuperuser) foreach ($requested as $permission) if (!isset($actorPermissions[$permission])) throw new InvalidArgumentException('لا يمكنك منح صلاحيات غير موجودة في دورك الحالي.');
            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713250)');
            $pdo->prepare('INSERT INTO codefy_admin_roles(role_key,name,description,is_system,is_active) VALUES(:key,:name,:description,false,:active)')->execute(['key'=>$key,'name'=>$name,'description'=>$description,'active'=>$isActive]);
            $insert = $pdo->prepare('INSERT INTO codefy_admin_role_permissions(role_key,permission_key) VALUES(:role,:permission)');
            foreach ($requested as $permission) $insert->execute(['role'=>$key,'permission'=>$permission]);
            codefy_admin_audit($pdo,(int)$user['id'],'create','admin_role',$key,['permissions'=>$requested,'is_active'=>$isActive]);
            $pdo->commit();
            admin_flash('success','تم إنشاء الدور المخصص.');
        } elseif ($action === 'update_role') {
            admin_require_permission('roles.manage');
            $key = trim((string)($_POST['role_key'] ?? ''));
            if (!preg_match('/^[a-z][a-z0-9_]{1,47}$/D',$key)) throw new InvalidArgumentException('مفتاح الدور غير صالح.');
            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713250)');
            $lookup = $pdo->prepare('SELECT role_key,name,description,is_system,is_active FROM codefy_admin_roles WHERE role_key=:key FOR UPDATE');
            $lookup->execute(['key'=>$key]);
            $role = $lookup->fetch();
            if (!$role) throw new InvalidArgumentException('الدور المطلوب غير موجود.');
            if ($key === 'superuser') throw new InvalidArgumentException('دور المستخدم الأعلى ثابت ولا يمكن تعديله.');
            if (codefy_bool($role['is_system']) && !$actorIsSuperuser) throw new InvalidArgumentException('تعديل أدوار النظام متاح للمستخدم الأعلى فقط.');
            if (!$canManageRoleKey($key)) throw new InvalidArgumentException('لا يمكنك إدارة دور يمنح قدرات أعلى من دورك الحالي.');
            $name = codefy_bool($role['is_system']) ? (string)$role['name'] : trim((string)($_POST['name'] ?? ''));
            $description = codefy_bool($role['is_system']) ? (string)$role['description'] : trim((string)($_POST['description'] ?? ''));
            $isActive = ($_POST['is_active'] ?? '0') === '1';
            if ($name === '' || strlen($name) > 80 || strlen($description) > 500) throw new InvalidArgumentException('تحقق من اسم الدور ووصفه.');
            $memberCountQuery = $pdo->prepare('SELECT count(*) FROM codefy_admin_users WHERE role=:key');
            $memberCountQuery->execute(['key'=>$key]);
            $members = (int)$memberCountQuery->fetchColumn();
            if (!$isActive && $members > 0) throw new InvalidArgumentException('انقل الحسابات إلى دور نشط قبل إيقاف هذا الدور.');
            $requested = $_POST['permissions'] ?? [];
            if (!is_array($requested) || count($requested) > count($knownPermissions)) throw new InvalidArgumentException('قائمة القدرات غير صالحة.');
            $requested = array_values(array_unique(array_filter($requested,static fn($permission)=>is_string($permission)&&isset($knownPermissions[$permission]))));
            if (!$actorIsSuperuser) foreach ($requested as $permission) if (!isset($actorPermissions[$permission])) throw new InvalidArgumentException('لا يمكنك منح صلاحيات غير موجودة في دورك الحالي.');
            $oldPermissionsQuery = $pdo->prepare('SELECT permission_key FROM codefy_admin_role_permissions WHERE role_key=:key ORDER BY permission_key');
            $oldPermissionsQuery->execute(['key'=>$key]);
            $oldPermissions = $oldPermissionsQuery->fetchAll(PDO::FETCH_COLUMN);
            sort($requested, SORT_STRING);
            sort($oldPermissions, SORT_STRING);
            $pdo->prepare('UPDATE codefy_admin_roles SET name=:name,description=:description,is_active=:active,updated_at=now() WHERE role_key=:key')->execute(['name'=>$name,'description'=>$description,'active'=>$isActive,'key'=>$key]);
            $pdo->prepare('DELETE FROM codefy_admin_role_permissions WHERE role_key=:key')->execute(['key'=>$key]);
            $insert = $pdo->prepare('INSERT INTO codefy_admin_role_permissions(role_key,permission_key) VALUES(:role,:permission)');
            foreach ($requested as $permission) $insert->execute(['role'=>$key,'permission'=>$permission]);
            $permissionsChanged = $oldPermissions !== $requested;
            if ($permissionsChanged) $pdo->prepare('UPDATE codefy_admin_users SET session_version=session_version+1,updated_at=now() WHERE role=:key')->execute(['key'=>$key]);
            codefy_admin_audit($pdo,(int)$user['id'],'update','admin_role',$key,['permission_count'=>count($requested),'permissions_changed'=>$permissionsChanged,'is_active'=>$isActive]);
            $pdo->commit();
            admin_flash('success','تم تحديث الدور. أُبطلت الجلسات عند تغيير قائمة الصلاحيات.');
        } elseif ($action === 'delete_role') {
            admin_require_permission('roles.manage');
            $key = trim((string)($_POST['role_key'] ?? ''));
            if (!preg_match('/^[a-z][a-z0-9_]{1,47}$/D',$key)) throw new InvalidArgumentException('مفتاح الدور غير صالح.');
            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713250)');
            $lookup = $pdo->prepare('SELECT role_key,is_system FROM codefy_admin_roles WHERE role_key=:key FOR UPDATE');
            $lookup->execute(['key'=>$key]);
            $role = $lookup->fetch();
            if (!$role) throw new InvalidArgumentException('الدور المطلوب غير موجود.');
            if (codefy_bool($role['is_system'])) throw new InvalidArgumentException('لا يمكن حذف أدوار النظام.');
            if (!$canManageRoleKey($key)) throw new InvalidArgumentException('لا يمكنك حذف دور يمنح قدرات أعلى من دورك الحالي.');
            $memberCountQuery=$pdo->prepare('SELECT count(*) FROM codefy_admin_users WHERE role=:key');
            $memberCountQuery->execute(['key'=>$key]);
            if ((int)$memberCountQuery->fetchColumn() > 0) throw new InvalidArgumentException('لا يمكن حذف دور ما زالت حسابات تستخدمه.');
            codefy_admin_audit($pdo,(int)$user['id'],'delete','admin_role',$key);
            $pdo->prepare('DELETE FROM codefy_admin_roles WHERE role_key=:key')->execute(['key'=>$key]);
            $pdo->commit();
            admin_flash('success','تم حذف الدور المخصص.');
        } else {
            throw new InvalidArgumentException('الإجراء المطلوب غير معروف.');
        }
    } catch (Throwable $error) {
        if ($pdo->inTransaction()) $pdo->rollBack();
        error_log('Codefy role management failed: '.$error->getMessage());
        admin_flash('error',$error instanceof InvalidArgumentException ? $error->getMessage() : 'تعذر حفظ الدور. تحقق من المفتاح أو قاعدة البيانات وحاول مرة أخرى.');
    }
    header('Location: roles.php');
    exit;
}

$roleQuery = $pdo->query("SELECT r.role_key,r.name,r.description,r.is_system,r.is_active,count(u.id)::int AS member_count,COALESCE((SELECT json_agg(rp.permission_key ORDER BY rp.permission_key)::text FROM codefy_admin_role_permissions rp WHERE rp.role_key=r.role_key),'[]') AS permission_keys FROM codefy_admin_roles r LEFT JOIN codefy_admin_users u ON u.role=r.role_key GROUP BY r.role_key ORDER BY CASE r.role_key WHEN 'superuser' THEN 0 WHEN 'admin' THEN 1 WHEN 'section_author' THEN 2 WHEN 'viewer' THEN 3 ELSE 4 END,r.name");
$roles = $roleQuery->fetchAll();
$editablePermissionsByRole = ['admin'=>$actorIsSuperuser];
$canDeleteRoleKeys = [];
$roleStats = ['roles'=>count($roles),'members'=>(int)$pdo->query('SELECT count(*) FROM codefy_admin_users')->fetchColumn(),'permissions'=>(int)$pdo->query('SELECT count(*) FROM codefy_admin_permissions')->fetchColumn()];
foreach ($roles as $role) {
    $roleKey = (string)$role['role_key'];
    $editablePermissionsByRole[$roleKey] = !codefy_bool($role['is_system']) || ($roleKey === 'admin' && $actorIsSuperuser);
    if (!codefy_bool($role['is_system']) && (int)$role['member_count'] === 0 && $canManageRoleKey((string)$role['role_key'])) $canDeleteRoleKeys[] = (string)$role['role_key'];
}
$canManageRoles = admin_can('roles.manage',$user);
$canModifySystemRoles = $actorIsSuperuser;
$flash = admin_take_flash();
$csrf = admin_csrf_token();
$activeNav = 'roles';
require __DIR__ . '/roles-view.php';
