<?php
require_once __DIR__ . '/../includes/admin-db.php';

$secureCookie = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || codefy_env('CODEFY_SECURE_COOKIE') === 'true';
$adminCookiePath = str_replace('\\', '/', dirname(dirname($_SERVER['SCRIPT_NAME'] ?? '/admin/login.php')));
$adminCookiePath = rtrim($adminCookiePath, '/') ?: '/';
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_name('codefy_admin');
    session_set_cookie_params([
        'lifetime' => 0, 'path' => $adminCookiePath, 'secure' => $secureCookie,
        'httponly' => true, 'samesite' => 'Strict',
    ]);
    session_start();
}

function admin_csrf_token(): string {
    if (empty($_SESSION['admin_csrf'])) $_SESSION['admin_csrf'] = bin2hex(random_bytes(32));
    return $_SESSION['admin_csrf'];
}

function admin_require_csrf(): void {
    $submitted = $_POST['_csrf'] ?? '';
    if (!is_string($submitted) || !hash_equals(admin_csrf_token(), $submitted)) {
        http_response_code(419);
        exit('انتهت صلاحية النموذج. أعد تحميل الصفحة وحاول مرة أخرى.');
    }
}

function admin_current_user(): ?array {
    return isset($_SESSION['admin_user']) && is_array($_SESSION['admin_user']) ? $_SESSION['admin_user'] : null;
}

function admin_require_user(): array {
    $user = admin_current_user();
    if (!$user) {
        header('Location: login.php');
        exit;
    }
    $statement = codefy_db()->prepare("SELECT u.id, u.email, u.display_name, u.role, u.session_version FROM codefy_admin_users u JOIN codefy_admin_roles r ON r.role_key = u.role AND r.is_active WHERE u.id = :id AND u.is_active = true");
    $statement->execute(['id' => $user['id']]);
    $current = $statement->fetch();
    if (!$current || (int)($user['session_version'] ?? 0) !== (int)$current['session_version']) {
        $_SESSION = [];
        session_regenerate_id(true);
        header('Location: login.php');
        exit;
    }
    $_SESSION['admin_user'] = [
        'id' => (int)$current['id'], 'email' => $current['email'],
        'name' => $current['display_name'], 'role' => $current['role'],
        'session_version' => (int)$current['session_version'],
    ];
    $user = $_SESSION['admin_user'];
    return $user;
}

function admin_require_role(string $role): array {
    $user = admin_require_user();
    if ($role === 'admin' && !in_array(($user['role'] ?? ''), ['admin', 'superuser'], true)) {
        http_response_code(403);
        exit('ليست لديك صلاحية لتنفيذ هذا الإجراء.');
    }
    return $user;
}

function admin_user_permissions(?array $user = null): array {
    static $cache = [];
    $user ??= admin_current_user();
    if (!$user || !isset($user['role'])) return [];
    $role = (string)$user['role'];
    if (!array_key_exists($role, $cache)) {
        $statement = codefy_db()->prepare('SELECT rp.permission_key FROM codefy_admin_role_permissions rp JOIN codefy_admin_roles r ON r.role_key = rp.role_key AND r.is_active WHERE rp.role_key = :role ORDER BY rp.permission_key');
        $statement->execute(['role' => $role]);
        $cache[$role] = array_fill_keys($statement->fetchAll(PDO::FETCH_COLUMN), true);
    }
    return $cache[$role];
}

function admin_can(string $permission, ?array $user = null): bool {
    return isset(admin_user_permissions($user)[$permission]);
}

function admin_require_permission(string $permission): array {
    $user = admin_require_user();
    if (!admin_can($permission, $user)) {
        http_response_code(403);
        exit('ليست لديك صلاحية لتنفيذ هذا الإجراء.');
    }
    return $user;
}

function admin_require_any_permission(array $permissions): array {
    $user = admin_require_user();
    foreach ($permissions as $permission) {
        if (is_string($permission) && admin_can($permission, $user)) return $user;
    }
    http_response_code(403);
    exit('ليست لديك صلاحية لتنفيذ هذا الإجراء.');
}

function admin_role_name(?string $role): string {
    static $cache = [];
    $role = (string)$role;
    if (!array_key_exists($role, $cache)) {
        $statement = codefy_db()->prepare('SELECT name FROM codefy_admin_roles WHERE role_key=:role');
        $statement->execute(['role'=>$role]);
        $cache[$role] = (string)($statement->fetchColumn() ?: $role);
    }
    return $cache[$role];
}

function admin_flash(string $type, string $message): void {
    $_SESSION['admin_flash'] = ['type' => $type, 'message' => $message];
}

function admin_take_flash(): ?array {
    $flash = $_SESSION['admin_flash'] ?? null;
    unset($_SESSION['admin_flash']);
    return $flash;
}

function admin_e(?string $value): string {
    return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
