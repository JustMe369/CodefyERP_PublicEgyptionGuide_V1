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
    $statement = codefy_db()->prepare('SELECT id, email, display_name, role, session_version FROM codefy_admin_users WHERE id = :id AND is_active = true');
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
    if ($role === 'admin' && ($user['role'] ?? '') !== 'admin') {
        http_response_code(403);
        exit('ليست لديك صلاحية لتنفيذ هذا الإجراء.');
    }
    return $user;
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
