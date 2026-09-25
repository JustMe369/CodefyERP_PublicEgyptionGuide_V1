<?php
require __DIR__ . '/../app/includes/admin-db.php';

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

$email = trim((string)codefy_env('CODEFY_ADMIN_EMAIL'));
$password = (string)codefy_env('CODEFY_ADMIN_PASSWORD');
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || !codefy_password_is_valid($password)) {
    fwrite(STDERR, "Provide a valid administrator email and a password of at least 14 characters (maximum 72 UTF-8 bytes).\n");
    exit(2);
}

try {
    $pdo = codefy_db();
    $pdo->beginTransaction();
    $statement = $pdo->prepare("UPDATE codefy_admin_users SET password_hash = :password_hash, session_version = session_version + 1, updated_at = now() WHERE lower(email) = lower(:email) AND role = 'admin' AND is_active = true RETURNING id, email");
    $statement->execute(['password_hash' => password_hash($password, PASSWORD_DEFAULT), 'email' => $email]);
    $account = $statement->fetch();
    if (!$account) {
        $pdo->rollBack();
        throw new RuntimeException('No active administrator account matched that email. Password was not changed.');
    }
    codefy_admin_audit($pdo, null, 'password_reset', 'admin_user', (string)$account['id'], ['email' => $account['email'], 'source' => 'cli']);
    $pdo->commit();
    fwrite(STDOUT, "Reset password for active administrator {$account['email']}. Existing admin sessions were revoked.\n");
} catch (Throwable $error) {
    if (isset($pdo) && $pdo instanceof PDO && $pdo->inTransaction()) $pdo->rollBack();
    fwrite(STDERR, 'Could not reset admin password: ' . $error->getMessage() . "\n");
    exit(1);
}
