<?php
require __DIR__ . '/../app/includes/admin-db.php';

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
$email = trim((string)codefy_env('CODEFY_ADMIN_EMAIL'));
$name = trim((string)codefy_env('CODEFY_ADMIN_NAME'));
$role = (string)codefy_env('CODEFY_ADMIN_ROLE', 'superuser');
$password = (string)codefy_env('CODEFY_ADMIN_PASSWORD');
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || $name === '' || strlen($name) > 120 || !codefy_password_is_valid($password) || !in_array($role, ['superuser', 'admin', 'section_author', 'viewer'], true)) {
    fwrite(STDERR, "Set a valid admin email and name, a password between 14 characters and 72 bytes, and a role of superuser, admin, section_author, or viewer.\n");
    exit(2);
}

try {
    $pdo = codefy_db();
    if ($role !== 'superuser' && (int)$pdo->query("SELECT count(*) FROM codefy_admin_users WHERE role = 'superuser' AND is_active = true")->fetchColumn() === 0) {
        throw new RuntimeException('Create an active superuser account before creating additional accounts.');
    }
    $statement = $pdo->prepare('INSERT INTO codefy_admin_users (email, password_hash, display_name, role) VALUES (:email, :password_hash, :display_name, :role) RETURNING id');
    $statement->execute(['email' => $email, 'password_hash' => password_hash($password, PASSWORD_DEFAULT), 'display_name' => $name, 'role' => $role]);
    fwrite(STDOUT, 'Created ' . $role . ' account #' . $statement->fetchColumn() . " for {$email}.\n");
} catch (Throwable $error) {
    fwrite(STDERR, 'Could not create admin account: ' . $error->getMessage() . "\n");
    exit(1);
}
