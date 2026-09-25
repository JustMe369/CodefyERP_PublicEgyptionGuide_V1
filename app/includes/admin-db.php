<?php
/** Minimal PostgreSQL access shared by the public guide and admin panel. */
function codefy_load_local_environment(): void {
    static $loaded = false;
    if ($loaded) return;
    $loaded = true;
    $path = dirname(__DIR__, 2) . DIRECTORY_SEPARATOR . '.env';
    if (!is_readable($path)) return;
    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [] as $line) {
        $line = trim($line);
        if ($line === '' || $line[0] === '#' || strpos($line, '=') === false) continue;
        [$key, $value] = explode('=', $line, 2);
        $key = trim($key);
        $value = trim($value);
        if (!preg_match('/^[A-Z][A-Z0-9_]*$/', $key) || getenv($key) !== false) continue;
        if (strlen($value) >= 2 && (($value[0] === '"' && substr($value, -1) === '"') || ($value[0] === "'" && substr($value, -1) === "'"))) {
            $value = substr($value, 1, -1);
        }
        putenv($key . '=' . $value);
        $_ENV[$key] = $value;
    }
}

function codefy_env(string $name, ?string $default = null): ?string {
    codefy_load_local_environment();
    $value = getenv($name);
    if ($value === false || $value === '') $value = $_SERVER[$name] ?? $_ENV[$name] ?? null;
    return ($value === null || $value === '') ? $default : (string)$value;
}

function codefy_password_is_valid(string $password): bool {
    $characters = preg_match_all('/./us', $password);
    return $characters !== false && $characters >= 14 && strlen($password) <= 72;
}

function codefy_bool($value): bool {
    if (is_bool($value)) return $value;
    return in_array(strtolower((string)$value), ['1', 't', 'true', 'yes', 'on'], true);
}

function codefy_db(): PDO {
    static $pdo = null;
    if ($pdo instanceof PDO) return $pdo;

    $dsn = codefy_env('CODEFY_DATABASE_DSN');
    if (!$dsn) {
        $host = codefy_env('PGHOST', '127.0.0.1');
        $port = codefy_env('PGPORT', '5432');
        $database = codefy_env('PGDATABASE', 'codefy_guide');
        $dsn = 'pgsql:host=' . $host . ';port=' . $port . ';dbname=' . $database;
        $sslMode = codefy_env('PGSSLMODE');
        if ($sslMode) $dsn .= ';sslmode=' . $sslMode;
    }

    $pdo = new PDO($dsn, codefy_env('PGUSER'), codefy_env('PGPASSWORD'), [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
        PDO::ATTR_PERSISTENT => false,
    ]);
    return $pdo;
}

function codefy_apply_database_content(): void {
    global $SITE, $SECTIONS;
    try {
        $pdo = codefy_db();
        foreach ($pdo->query('SELECT setting_key, setting_value FROM codefy_site_settings') as $row) {
            if (array_key_exists($row['setting_key'], $SITE)) $SITE[$row['setting_key']] = $row['setting_value'];
        }
        $orderedSections = [];
        foreach ($pdo->query('SELECT slug, title, subtitle, icon, is_published, sort_order FROM codefy_guide_sections ORDER BY sort_order, slug') as $row) {
            if (!isset($SECTIONS[$row['slug']])) continue;
            $SECTIONS[$row['slug']]['title'] = $row['title'];
            $SECTIONS[$row['slug']]['subtitle'] = $row['subtitle'];
            $SECTIONS[$row['slug']]['icon'] = $row['icon'];
            $SECTIONS[$row['slug']]['published'] = codefy_bool($row['is_published']);
            $SECTIONS[$row['slug']]['number'] = (int)$row['sort_order'];
            if ($SECTIONS[$row['slug']]['published']) $orderedSections[$row['slug']] = $SECTIONS[$row['slug']];
            elseif (codefy_current_slug() === $row['slug']) {
                http_response_code(404);
                exit('هذا القسم غير متاح حالياً.');
            }
        }
        if ($orderedSections) $SECTIONS = $orderedSections;
    } catch (Throwable $error) {
        // Public guide pages stay available when the optional admin database is offline.
        error_log('Codefy content database unavailable: ' . $error->getMessage());
    }
}

function codefy_admin_audit(PDO $pdo, ?int $adminId, string $action, string $entity, ?string $entityId = null, array $details = []): void {
    $statement = $pdo->prepare(
        'INSERT INTO codefy_admin_audit_log (admin_id, action, entity_type, entity_id, details, ip_address) VALUES (:admin_id, :action, :entity_type, :entity_id, CAST(:details AS jsonb), CAST(:ip AS inet))'
    );
    $statement->execute([
        'admin_id' => $adminId, 'action' => $action, 'entity_type' => $entity,
        'entity_id' => $entityId, 'details' => json_encode($details, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR),
        'ip' => $_SERVER['REMOTE_ADDR'] ?? null,
    ]);
}
