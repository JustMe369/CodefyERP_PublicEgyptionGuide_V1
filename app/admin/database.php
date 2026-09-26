<?php
require __DIR__ . '/_bootstrap.php';
$user = admin_require_permission('database.view');
$pdo = codefy_db();

const CODEFY_DB_BACKUP_MAX_BYTES = 104857600;
const CODEFY_DB_BACKUP_CONFIRMATION = 'RESTORE DATABASE';

function codefy_db_ops_connection(string $envName): array {
    $url = codefy_env($envName);
    if (!$url) throw new RuntimeException('Database operation connection is not configured.');
    $parts = parse_url($url);
    if (!is_array($parts)) throw new RuntimeException('Database operation connection is invalid.');
    $parsed = codefy_parse_database_url($url);
    $host = (string)($parts['host'] ?? '');
    $port = (int)($parts['port'] ?? 5432);
    if ($port === 6543 && str_ends_with(strtolower($host), '.pooler.supabase.com')) $port = 5432;
    if ($port === 6543) throw new RuntimeException('استخدم اتصال Supabase المباشر أو session pooler على المنفذ 5432 لعمليات النسخ والاستعادة.');
    $database = rawurldecode(ltrim((string)($parts['path'] ?? ''), '/'));
    $query = [];
    parse_str((string)($parts['query'] ?? ''), $query);
    $env = [
        'PATH' => (string)(getenv('PATH') ?: '/usr/local/bin:/usr/bin:/bin'),
        'HOME' => sys_get_temp_dir(),
        'PGHOST' => $host,
        'PGPORT' => (string)$port,
        'PGDATABASE' => $database,
        'PGUSER' => rawurldecode((string)($parts['user'] ?? '')),
        'PGPASSWORD' => rawurldecode((string)($parts['pass'] ?? '')),
        'PGSSLMODE' => (string)($query['sslmode'] ?? 'require'),
        'PGCONNECT_TIMEOUT' => '12',
        'PGAPPNAME' => 'codefy-admin-database-ops',
    ];
    if (!$env['PGHOST'] || !$env['PGUSER'] || !$env['PGPASSWORD'] || !$env['PGDATABASE']) {
        throw new RuntimeException('Database operation connection is missing required fields.');
    }
    return ['env' => $env, 'database' => $database, 'host' => strtolower($host), 'user' => $env['PGUSER']];
}

function codefy_db_ops_runtime_backup_connection(): array {
    $dsn = (string)codefy_env('CODEFY_DATABASE_DSN', '');
    $url = codefy_env('DATABASE_URL');
    $host = (string)codefy_env('PGHOST', '');
    $database = (string)codefy_env('PGDATABASE', '');
    $username = (string)codefy_env('PGUSER', '');
    $password = (string)codefy_env('PGPASSWORD', '');
    $port = (int)codefy_env('PGPORT', '5432');
    $sslMode = (string)codefy_env('PGSSLMODE', 'require');
    if ($dsn !== '') {
        foreach (['host', 'port', 'dbname', 'sslmode'] as $field) {
            if (preg_match('/(?:^|[;:])' . $field . '=([^;]+)/i', $dsn, $match)) {
                if ($field === 'host') $host = $match[1];
                elseif ($field === 'port') $port = (int)$match[1];
                elseif ($field === 'dbname') $database = $match[1];
                else $sslMode = $match[1];
            }
        }
    } elseif ($url) {
        $parts = parse_url($url);
        if (!is_array($parts)) throw new RuntimeException('The application database URL is invalid.');
        $query = [];
        parse_str((string)($parts['query'] ?? ''), $query);
        $host = (string)($parts['host'] ?? '');
        $database = rawurldecode(ltrim((string)($parts['path'] ?? ''), '/'));
        $username = rawurldecode((string)($parts['user'] ?? ''));
        $password = rawurldecode((string)($parts['pass'] ?? ''));
        $port = (int)($parts['port'] ?? 5432);
        $sslMode = (string)($query['sslmode'] ?? 'require');
    }
    if ($port === 6543 && str_ends_with(strtolower($host), '.pooler.supabase.com')) $port = 5432;
    if ($port === 6543) throw new RuntimeException('The configured transaction pooler cannot run pg_dump. Set a session-mode backup URL on port 5432.');
    if (!$host || !$database || !$username || !$password || $port < 1 || $port > 65535) throw new RuntimeException('The current application connection cannot be used for database backup.');
    return [
        'env' => [
            'PATH' => (string)(getenv('PATH') ?: '/usr/local/bin:/usr/bin:/bin'), 'HOME' => sys_get_temp_dir(),
            'PGHOST' => $host, 'PGPORT' => (string)$port, 'PGDATABASE' => $database, 'PGUSER' => $username,
            'PGPASSWORD' => $password, 'PGSSLMODE' => $sslMode, 'PGCONNECT_TIMEOUT' => '12', 'PGAPPNAME' => 'codefy-admin-database-ops',
        ],
        'database' => $database, 'host' => strtolower($host), 'user' => $username,
    ];
}

function codefy_db_ops_same_target(PDO $pdo, array $connection): bool {
    $runtime = $pdo->query('SELECT current_database() AS database, current_user AS username')->fetch();
    if (!is_array($runtime) || !hash_equals((string)$runtime['database'], $connection['database'])) return false;
    $runtimeUrl = codefy_env('DATABASE_URL');
    $runtimeHost = '';
    $runtimeDsn = codefy_env('CODEFY_DATABASE_DSN');
    if ($runtimeDsn && preg_match('/(?:^|[;:])host=([^;]+)/i', $runtimeDsn, $match)) {
        $runtimeHost = strtolower($match[1]);
    } elseif ($runtimeUrl) {
        $runtimeParts = parse_url($runtimeUrl);
        $runtimeHost = strtolower((string)($runtimeParts['host'] ?? ''));
    }
    if ($runtimeHost === '') $runtimeHost = strtolower((string)codefy_env('PGHOST', ''));
    $operationHost = $connection['host'];
    $runtimeIsSupabase = str_ends_with($runtimeHost, '.supabase.com') || str_ends_with($runtimeHost, '.supabase.co');
    $operationIsSupabase = str_ends_with($operationHost, '.supabase.com') || str_ends_with($operationHost, '.supabase.co');
    if ($runtimeIsSupabase && $operationIsSupabase) {
        $runtimeUsername = (string)codefy_env('PGUSER', '');
        if ($runtimeUsername === '' && $runtimeUrl) {
            $runtimeParts = parse_url($runtimeUrl);
            $runtimeUsername = rawurldecode((string)($runtimeParts['user'] ?? ''));
        }
        $runtimeProject = str_contains($runtimeUsername, '.') ? substr($runtimeUsername, strrpos($runtimeUsername, '.') + 1) : '';
        $operationProject = str_contains($connection['user'], '.') ? substr($connection['user'], strrpos($connection['user'], '.') + 1) : '';
        if ($runtimeProject === '' && preg_match('/^db\.([^.]+)\.supabase\.co$/', $runtimeHost, $match)) $runtimeProject = $match[1];
        if ($operationProject === '' && preg_match('/^db\.([^.]+)\.supabase\.co$/', $operationHost, $match)) $operationProject = $match[1];
        return $runtimeProject !== '' && hash_equals($runtimeProject, $operationProject);
    }
    return $runtimeHost !== '' && hash_equals($runtimeHost, $operationHost);
}

function codefy_db_ops_run(array $command, array $environment, string $workDir): array {
    if (!function_exists('proc_open')) throw new RuntimeException('Process execution is unavailable in this runtime.');
    $stdoutPath = $workDir . DIRECTORY_SEPARATOR . 'process.out';
    $stderrPath = $workDir . DIRECTORY_SEPARATOR . 'process.err';
    $process = proc_open($command, [
        0 => ['file', PHP_OS_FAMILY === 'Windows' ? 'NUL' : '/dev/null', 'r'],
        1 => ['file', $stdoutPath, 'w'],
        2 => ['file', $stderrPath, 'w'],
    ], $pipes, $workDir, $environment, ['bypass_shell' => true]);
    if (!is_resource($process)) throw new RuntimeException('Could not start the PostgreSQL utility.');
    $exitCode = proc_close($process);
    $stdout = is_file($stdoutPath) ? (string)file_get_contents($stdoutPath) : '';
    $stderr = is_file($stderrPath) ? (string)file_get_contents($stderrPath) : '';
    @unlink($stdoutPath);
    @unlink($stderrPath);
    return ['exit_code' => $exitCode, 'stdout' => $stdout, 'stderr' => $stderr];
}

function codefy_db_ops_temp_dir(): string {
    $path = rtrim(sys_get_temp_dir(), DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . 'codefy-db-' . bin2hex(random_bytes(16));
    if (!mkdir($path, 0700)) throw new RuntimeException('Could not create a temporary backup workspace.');
    return $path;
}

function codefy_db_ops_remove_dir(string $path): void {
    if (!is_dir($path) || is_link($path)) return;
    foreach (scandir($path) ?: [] as $item) {
        if ($item === '.' || $item === '..') continue;
        $child = $path . DIRECTORY_SEPARATOR . $item;
        if (is_dir($child) && !is_link($child)) codefy_db_ops_remove_dir($child);
        else @unlink($child);
    }
    @rmdir($path);
}

function codefy_db_ops_signing_key(): string {
    $key = codefy_env('CODEFY_BACKUP_SIGNING_KEY');
    if (!$key || strlen($key) < 32) throw new RuntimeException('A backup signing key of at least 32 characters is required.');
    return $key;
}

function codefy_db_ops_signed_manifest(array $manifest, string $key): string {
    $payload = json_encode($manifest, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    $manifest['signature'] = hash_hmac('sha256', $payload, $key);
    return json_encode($manifest, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
}

function codefy_db_ops_tool(string $name): string {
    $configured = codefy_env(strtoupper(str_replace('-', '_', $name)) . '_BIN');
    return $configured ?: $name;
}

function codefy_db_ops_require_tools(): void {
    foreach (['pg_dump', 'pg_restore', 'tar'] as $tool) {
        $path = codefy_db_ops_tool($tool);
        if (str_contains($path, DIRECTORY_SEPARATOR) ? !is_file($path) : !is_executable('/usr/bin/' . $path) && !is_executable('/usr/local/bin/' . $path) && !is_executable('/bin/' . $path)) {
            throw new RuntimeException('Required PostgreSQL backup utilities are not installed on the server.');
        }
    }
}

function codefy_db_ops_flash_redirect(string $type, string $message): never {
    admin_flash($type, $message);
    header('Location: database.php');
    exit;
}

function codefy_db_ops_backup(PDO $pdo, array $user): never {
    $connection = codefy_env('CODEFY_BACKUP_DATABASE_URL')
        ? codefy_db_ops_connection('CODEFY_BACKUP_DATABASE_URL')
        : codefy_db_ops_runtime_backup_connection();
    if (!codefy_db_ops_same_target($pdo, $connection)) throw new InvalidArgumentException('The backup connection must point to the same database project configured for this application.');
    $key = codefy_db_ops_signing_key();
    codefy_db_ops_require_tools();
    $workDir = codefy_db_ops_temp_dir();
    try {
        set_time_limit(300);
        $dumpPath = $workDir . DIRECTORY_SEPARATOR . 'database.dump';
        $result = codefy_db_ops_run([
            codefy_db_ops_tool('pg_dump'), '--format=custom', '--no-owner', '--no-acl', '--no-comments',
            '--table=public.codefy_*', '--file=' . $dumpPath,
        ], $connection['env'], $workDir);
        if ($result['exit_code'] !== 0 || !is_file($dumpPath) || filesize($dumpPath) < 1) {
            $stderr = trim($result['stderr']);
            error_log('Codefy database backup failed (pg_dump): ' . $stderr);
            if (preg_match('/permission denied/i', $stderr)) throw new RuntimeException('حساب النسخ الاحتياطي لا يملك صلاحية قراءة كل جداول Codefy. امنحه SELECT على public.codefy_* أو اضبط CODEFY_BACKUP_DATABASE_URL على اتصال مناسب بصلاحية القراءة.');
            if (preg_match('/password authentication failed|no password supplied/i', $stderr)) throw new RuntimeException('فشل التحقق من كلمة مرور اتصال النسخ الاحتياطي. حدّث CODEFY_BACKUP_DATABASE_URL ببيانات Supabase الصحيحة على الخادم.');
            if (preg_match('/timeout expired|could not connect|connection refused|could not translate host name|name or service not known|SSL error/i', $stderr)) throw new RuntimeException('تعذر اتصال pg_dump بقاعدة البيانات. استخدم اتصال Supabase المباشر أو session pooler على المنفذ 5432 وتحقق من إعدادات الشبكة.');
            throw new RuntimeException('تعذر إنشاء النسخة باستخدام pg_dump. راجع سجل الخادم لمعرفة فئة الخطأ المسجلة.');
        }
        if (filesize($dumpPath) > CODEFY_DB_BACKUP_MAX_BYTES) throw new RuntimeException('This backup is larger than the 100 MB download limit for the admin page.');
        $manifest = [
            'format' => 'codefy-postgres-backup-v1',
            'database' => $connection['database'],
            'created_at' => gmdate('Y-m-d\TH:i:s\Z'),
            'scope' => 'public.codefy_*',
            'sha256' => hash_file('sha256', $dumpPath),
        ];
        file_put_contents($workDir . DIRECTORY_SEPARATOR . 'manifest.json', codefy_db_ops_signed_manifest($manifest, $key), LOCK_EX);
        $archivePath = $workDir . DIRECTORY_SEPARATOR . 'codefy-backup.tar.gz';
        $packed = codefy_db_ops_run([codefy_db_ops_tool('tar'), '-czf', $archivePath, '-C', $workDir, 'database.dump', 'manifest.json'], $connection['env'], $workDir);
        if ($packed['exit_code'] !== 0 || !is_file($archivePath)) {
            error_log('Codefy database backup archive failed: ' . trim($packed['stderr']));
            throw new RuntimeException('تعذر تجميع الحزمة الموقعة. تحقق من المساحة المؤقتة وأدوات الأرشفة على الخادم.');
        }
        codefy_admin_audit($pdo, (int)$user['id'], 'backup', 'database', $connection['database'], ['scope' => 'public.codefy_*', 'sha256' => $manifest['sha256'], 'bytes' => filesize($archivePath)]);
        header('Content-Type: application/gzip');
        header('Content-Length: ' . filesize($archivePath));
        header('Content-Disposition: attachment; filename="codefy-backup-' . gmdate('Ymd-His') . '.tar.gz"');
        header('Cache-Control: private, no-store, max-age=0');
        readfile($archivePath);
    } finally {
        codefy_db_ops_remove_dir($workDir);
    }
    exit;
}

function codefy_db_ops_restore(PDO $pdo, array $user): never {
    $url = codefy_env('CODEFY_RESTORE_DATABASE_URL');
    if (!$url) throw new RuntimeException('Configure CODEFY_RESTORE_DATABASE_URL in the hosting environment.');
    if (!hash_equals(CODEFY_DB_BACKUP_CONFIRMATION, (string)($_POST['confirmation'] ?? ''))) {
        throw new InvalidArgumentException('Type RESTORE DATABASE exactly to confirm the restore.');
    }
    $upload = $_FILES['backup_file'] ?? null;
    if (!is_array($upload) || ($upload['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK || !is_uploaded_file((string)($upload['tmp_name'] ?? ''))) {
        throw new InvalidArgumentException('Choose a valid Codefy backup bundle before restoring.');
    }
    if ((int)$upload['size'] < 1 || (int)$upload['size'] > CODEFY_DB_BACKUP_MAX_BYTES) throw new InvalidArgumentException('The backup package must be between 1 byte and 100 MB.');
    $connection = codefy_db_ops_connection('CODEFY_RESTORE_DATABASE_URL');
    $key = codefy_db_ops_signing_key();
    codefy_db_ops_require_tools();
    $currentDatabase = (string)$pdo->query('SELECT current_database()')->fetchColumn();
    if (!hash_equals($currentDatabase, $connection['database']) || !codefy_db_ops_same_target($pdo, $connection)) throw new InvalidArgumentException('Restore target must match the currently connected application database project.');
    $workDir = codefy_db_ops_temp_dir();
    try {
        set_time_limit(600);
        $bundle = $workDir . DIRECTORY_SEPARATOR . 'upload.tar.gz';
        if (!move_uploaded_file((string)$upload['tmp_name'], $bundle)) throw new RuntimeException('Could not stage the uploaded backup package.');
        $listing = codefy_db_ops_run([codefy_db_ops_tool('tar'), '-tzf', $bundle], $connection['env'], $workDir);
        if ($listing['exit_code'] !== 0) throw new InvalidArgumentException('The uploaded file is not a valid Codefy backup bundle.');
        $members = [];
        foreach (preg_split('/\r?\n/', $listing['stdout']) ?: [] as $member) {
            $member = trim($member);
            if ($member === '') continue;
            if (str_starts_with($member, './')) $member = substr($member, 2);
            if (!in_array($member, ['database.dump', 'manifest.json'], true)) throw new InvalidArgumentException('The backup bundle contains an unexpected file path.');
            $members[] = $member;
        }
        sort($members, SORT_STRING);
        if ($members !== ['database.dump', 'manifest.json']) throw new InvalidArgumentException('The bundle must contain only the signed database dump and its manifest.');
        $extracted = codefy_db_ops_run([codefy_db_ops_tool('tar'), '-xzf', $bundle, '-C', $workDir], $connection['env'], $workDir);
        if ($extracted['exit_code'] !== 0) throw new InvalidArgumentException('The backup bundle could not be extracted.');
        $manifestRaw = file_get_contents($workDir . DIRECTORY_SEPARATOR . 'manifest.json');
        $manifest = is_string($manifestRaw) ? json_decode($manifestRaw, true) : null;
        if (!is_array($manifest) || ($manifest['format'] ?? '') !== 'codefy-postgres-backup-v1' || ($manifest['scope'] ?? '') !== 'public.codefy_*' || !is_string($manifest['signature'] ?? null)) {
            throw new InvalidArgumentException('This is not a supported Codefy signed backup.');
        }
        $signature = $manifest['signature'];
        unset($manifest['signature']);
        $expected = hash_hmac('sha256', json_encode($manifest, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR), $key);
        if (!hash_equals($expected, $signature) || !hash_equals($connection['database'], (string)($manifest['database'] ?? ''))) throw new InvalidArgumentException('Backup signature or database identity does not match this restore target.');
        $dumpPath = $workDir . DIRECTORY_SEPARATOR . 'database.dump';
        $sha = hash_file('sha256', $dumpPath);
        if (!is_string($sha) || !hash_equals((string)($manifest['sha256'] ?? ''), $sha)) throw new InvalidArgumentException('The backup dump failed its integrity check.');
        codefy_admin_audit($pdo, (int)$user['id'], 'restore_started', 'database', $connection['database'], ['scope' => 'public.codefy_*', 'sha256' => $sha]);
        $restore = codefy_db_ops_run([
            codefy_db_ops_tool('pg_restore'), '--clean', '--if-exists', '--single-transaction', '--no-owner', '--no-acl', '--exit-on-error', $dumpPath,
        ], $connection['env'], $workDir);
        if ($restore['exit_code'] !== 0) {
            error_log('Codefy database restore failed: ' . trim($restore['stderr']));
            throw new RuntimeException('Restore failed and PostgreSQL rolled back the transaction. Check the server logs and target permissions.');
        }
        try {
            codefy_admin_audit($pdo, (int)$user['id'], 'restore_completed', 'database', $connection['database'], ['scope' => 'public.codefy_*', 'sha256' => $sha]);
        } catch (Throwable $auditError) {
            error_log('Codefy restore completed but post-restore audit entry could not be written: ' . $auditError->getMessage());
        }
    } finally {
        codefy_db_ops_remove_dir($workDir);
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    admin_require_csrf();
    try {
        $action = (string)($_POST['action'] ?? '');
        if ($action === 'create_backup') { admin_require_permission('database.backup'); codefy_db_ops_backup($pdo, $user); }
        if ($action === 'restore_backup') {
            admin_require_permission('database.restore');
            codefy_db_ops_restore($pdo, $user);
            codefy_db_ops_flash_redirect('success', 'تمت استعادة نسخة Codefy والتحقق من تكامل المعاملة.');
        }
        throw new InvalidArgumentException('الإجراء المطلوب غير معروف.');
    } catch (Throwable $error) {
        error_log('Codefy database operation failed: ' . $error->getMessage());
        $message = $error instanceof InvalidArgumentException ? $error->getMessage() : 'تعذر تنفيذ العملية. راجع إعدادات عمليات قاعدة البيانات وسجل الخادم.';
        codefy_db_ops_flash_redirect('error', $message);
    }
}

$databaseStatus = ['connected' => false, 'message' => 'تعذر الوصول إلى قاعدة البيانات'];
$databaseMetrics = [];
$tables = [];
try {
    $overview = $pdo->query("SELECT current_database() AS database, current_user AS role, current_setting('server_version') AS server_version, pg_database_size(current_database()) AS size")->fetch();
    $databaseStatus = ['connected' => true, 'message' => 'اتصال PostgreSQL الحالي يعمل'];
    $databaseMetrics = [
        'database' => (string)$overview['database'], 'role' => (string)$overview['role'],
        'engine' => 'PostgreSQL ' . (string)$overview['server_version'], 'size' => (int)$overview['size'],
        'provider' => 'PostgreSQL مستضاف', 'checked_at' => gmdate('Y-m-d H:i:s') . ' UTC',
    ];
    $adminUrl = codefy_env('CODEFY_BACKUP_DATABASE_URL') ?: codefy_env('DATABASE_URL') ?: '';
    $host = '';
    if ($adminUrl !== '') { $parts = parse_url($adminUrl); $host = strtolower((string)($parts['host'] ?? '')); }
    if ($host === '') $host = strtolower((string)codefy_env('PGHOST', ''));
    if (str_ends_with($host, '.supabase.com') || str_ends_with($host, '.supabase.co')) $databaseMetrics['provider'] = 'Supabase';
    $tables = $pdo->query("SELECT st.schemaname AS schema, st.relname AS table, GREATEST(c.reltuples, 0)::bigint AS estimated_rows, pg_total_relation_size(st.relid)::bigint AS approximate_bytes FROM pg_stat_user_tables st JOIN pg_class c ON c.oid=st.relid ORDER BY pg_total_relation_size(st.relid) DESC, st.schemaname, st.relname LIMIT 300")->fetchAll();
    $databaseMetrics['table_count'] = count($tables);
} catch (Throwable $error) {
    error_log('Codefy database operations inventory unavailable: ' . $error->getMessage());
}

$backupEnabled = false;
$restoreEnabled = false;
$backupNotice = '';
$restoreNotice = '';
$flash = admin_take_flash();
$operationsReady = true;
try {
    codefy_db_ops_signing_key();
    codefy_db_ops_require_tools();
} catch (Throwable $error) {
    $operationsReady = false;
    $backupNotice = $error->getMessage();
    $restoreNotice = $error->getMessage();
}
if ($operationsReady && !codefy_env('CODEFY_BACKUP_DATABASE_URL')) $backupNotice = 'أضف CODEFY_BACKUP_DATABASE_URL كمتغير سري في Vercel ثم أعد النشر.';
if ($operationsReady && !codefy_env('CODEFY_RESTORE_DATABASE_URL')) $restoreNotice = 'أضف CODEFY_RESTORE_DATABASE_URL بصلاحية مالك جداول التطبيق، ثم أعد النشر.';
if ($operationsReady && codefy_env('CODEFY_BACKUP_DATABASE_URL')) {
    try {
        $backupConnection = codefy_db_ops_connection('CODEFY_BACKUP_DATABASE_URL');
        $backupEnabled = codefy_db_ops_same_target($pdo, $backupConnection);
        if (!$backupEnabled) $backupNotice = 'اتصال النسخ الاحتياطي لا يشير إلى مشروع قاعدة البيانات المرتبط بالتطبيق.';
    } catch (Throwable $error) { $backupNotice = $error->getMessage(); }
} elseif ($operationsReady) {
    try {
        $backupConnection = codefy_db_ops_runtime_backup_connection();
        $backupEnabled = codefy_db_ops_same_target($pdo, $backupConnection);
        if (!$backupEnabled) $backupNotice = 'اتصال النسخ الاحتياطي لا يشير إلى مشروع قاعدة البيانات المرتبط بالتطبيق.';
        else $backupNotice = 'سيُستخدم اتصال التطبيق للقراءة فقط لإنشاء نسخة موقعة من public.codefy_*، بحد أقصى 100 ميغابايت.';
    } catch (Throwable $error) { $backupNotice = $error->getMessage(); }
}
if ($operationsReady && codefy_env('CODEFY_RESTORE_DATABASE_URL')) {
    try {
        $restoreConnection = codefy_db_ops_connection('CODEFY_RESTORE_DATABASE_URL');
        $restoreEnabled = $backupEnabled && codefy_db_ops_same_target($pdo, $restoreConnection);
        if (!$restoreEnabled) $restoreNotice = 'الاستعادة تتطلب اتصال مالك إلى قاعدة البيانات نفسها واتصال نسخ احتياطي صالحاً.';
    } catch (Throwable $error) { $restoreNotice = $error->getMessage(); }
}
if ($backupEnabled) $backupNotice = 'نسخة موقعة من جداول public.codefy_*، بحد أقصى 100 ميغابايت.';
if ($restoreEnabled) $restoreNotice = 'تُقبل النسخ الموقعة التي أنشأتها هذه الصفحة فقط، وتُستعاد داخل معاملة واحدة.';
$csrf = admin_csrf_token();
require __DIR__ . '/database-view.php';
