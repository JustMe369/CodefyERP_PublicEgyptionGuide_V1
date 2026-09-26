<?php
require __DIR__ . '/_bootstrap.php';
if (admin_current_user()) { header('Location: index.php'); exit; }

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_require_csrf();
    try {
        $pdo = codefy_db();
        $ipHash = hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? 'unknown'));
        $limit = $pdo->prepare('SELECT blocked_until > now() AS is_blocked FROM codefy_admin_login_throttle WHERE ip_hash = :ip_hash');
        $limit->execute(['ip_hash' => $ipHash]);
        if (codefy_bool($limit->fetchColumn())) {
            $error = 'محاولات كثيرة. انتظر 15 دقيقة ثم حاول مرة أخرى.';
        } else {
            $statement = $pdo->prepare('SELECT u.id, u.email, u.display_name, u.role, u.password_hash, u.session_version FROM codefy_admin_users u JOIN codefy_admin_roles r ON r.role_key=u.role AND r.is_active WHERE lower(u.email) = lower(:email) AND u.is_active = true LIMIT 1');
            $statement->execute(['email' => trim((string)($_POST['email'] ?? ''))]);
            $account = $statement->fetch();
            if ($account && password_verify((string)($_POST['password'] ?? ''), $account['password_hash'])) {
                session_regenerate_id(true);
                unset($_SESSION['admin_csrf']);
                $_SESSION['admin_user'] = ['id' => (int)$account['id'], 'email' => $account['email'], 'name' => $account['display_name'], 'role' => $account['role'], 'session_version' => (int)$account['session_version']];
                $pdo->prepare('DELETE FROM codefy_admin_login_throttle WHERE ip_hash = :ip_hash')->execute(['ip_hash' => $ipHash]);
                $pdo->prepare('UPDATE codefy_admin_users SET last_login_at = now() WHERE id = :id')->execute(['id' => $account['id']]);
                codefy_admin_audit($pdo, (int)$account['id'], 'login', 'admin_user', (string)$account['id']);
                header('Location: index.php');
                exit;
            }
            $throttle = $pdo->prepare("INSERT INTO codefy_admin_login_throttle (ip_hash, failed_attempts, window_started_at, updated_at) VALUES (:ip_hash, 1, now(), now()) ON CONFLICT (ip_hash) DO UPDATE SET failed_attempts = CASE WHEN codefy_admin_login_throttle.window_started_at < now() - interval '15 minutes' THEN 1 ELSE codefy_admin_login_throttle.failed_attempts + 1 END, window_started_at = CASE WHEN codefy_admin_login_throttle.window_started_at < now() - interval '15 minutes' THEN now() ELSE codefy_admin_login_throttle.window_started_at END, blocked_until = CASE WHEN codefy_admin_login_throttle.window_started_at < now() - interval '15 minutes' THEN NULL WHEN codefy_admin_login_throttle.failed_attempts + 1 >= 8 THEN now() + interval '15 minutes' ELSE codefy_admin_login_throttle.blocked_until END, updated_at = now()");
            $throttle->execute(['ip_hash' => $ipHash]);
            $pdo->exec("DELETE FROM codefy_admin_login_throttle WHERE updated_at < now() - interval '30 days'");
            $error = 'بيانات الدخول غير صحيحة.';
        }
    } catch (Throwable $exception) {
        error_log('Codefy admin login failed: ' . $exception->getMessage());
        $error = 'تعذر الاتصال بقاعدة البيانات. راجع إعدادات PostgreSQL ودليل التشغيل.';
    }
}
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>دخول الإدارة — كوديفاي</title><link rel="stylesheet" href="admin.css">
</head>
<body class="admin-login-page">
    <main class="login-card">
        <div class="admin-brand"><span class="brand-mark">ك</span><div><strong>كوديفاي</strong><small>مركز إدارة الدليل</small></div></div>
        <h1>تسجيل دخول الإدارة</h1><p class="muted">أدخل بيانات حساب الإدارة للمتابعة.</p>
        <?php if ($error): ?><div class="notice error" role="alert"><?= admin_e($error) ?></div><?php endif; ?>
        <form method="post" autocomplete="on">
            <input type="hidden" name="_csrf" value="<?= admin_e(admin_csrf_token()) ?>">
            <label for="email">البريد الإلكتروني</label>
            <input id="email" name="email" type="email" required autocomplete="username" autofocus>
            <label for="password">كلمة المرور</label>
            <input id="password" name="password" type="password" required autocomplete="current-password">
            <button class="button primary full" type="submit">دخول آمن</button>
        </form>
        <a class="back-link" href="../index.php">العودة إلى الدليل</a>
    </main>
</body>
</html>
