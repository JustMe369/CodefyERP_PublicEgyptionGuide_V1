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

function codefy_accent_theme(string $accent): array {
    $themes = [
        'primary' => ['pill' => 'أولاً', 'pill_bg' => 'bg-primary-50', 'pill_text' => 'text-primary-700', 'gradient' => 'from-primary-500 to-primary-700', 'shadow' => 'shadow-primary-500/30', 'accent' => 'primary'],
        'indigo' => ['pill' => 'القسم', 'pill_bg' => 'bg-indigo-50', 'pill_text' => 'text-indigo-700', 'gradient' => 'from-indigo-500 to-purple-600', 'shadow' => 'shadow-indigo-500/30', 'accent' => 'indigo'],
        'emerald' => ['pill' => 'القسم', 'pill_bg' => 'bg-emerald-50', 'pill_text' => 'text-emerald-700', 'gradient' => 'from-emerald-500 to-teal-600', 'shadow' => 'shadow-emerald-500/30', 'accent' => 'emerald'],
        'amber' => ['pill' => 'القسم', 'pill_bg' => 'bg-amber-50', 'pill_text' => 'text-amber-700', 'gradient' => 'from-amber-500 to-orange-600', 'shadow' => 'shadow-amber-500/30', 'accent' => 'amber'],
        'violet' => ['pill' => 'القسم', 'pill_bg' => 'bg-violet-50', 'pill_text' => 'text-violet-700', 'gradient' => 'from-violet-500 to-fuchsia-600', 'shadow' => 'shadow-violet-500/30', 'accent' => 'violet'],
        'rose' => ['pill' => 'القسم', 'pill_bg' => 'bg-rose-50', 'pill_text' => 'text-rose-700', 'gradient' => 'from-rose-500 to-red-600', 'shadow' => 'shadow-rose-500/30', 'accent' => 'rose'],
        'cyan' => ['pill' => 'القسم', 'pill_bg' => 'bg-cyan-50', 'pill_text' => 'text-cyan-700', 'gradient' => 'from-cyan-500 to-teal-600', 'shadow' => 'shadow-cyan-500/30', 'accent' => 'cyan'],
    ];
    return $themes[$accent] ?? $themes['primary'];
}

function codefy_parse_database_url(string $url): array {
    $parts = parse_url($url);
    if (!is_array($parts) || !in_array(strtolower((string)($parts['scheme'] ?? '')), ['postgres', 'postgresql'], true)) {
        throw new RuntimeException('DATABASE_URL must be a PostgreSQL connection URL.');
    }
    $host = (string)($parts['host'] ?? '');
    $database = rawurldecode(ltrim((string)($parts['path'] ?? ''), '/'));
    $port = (int)($parts['port'] ?? 5432);
    $user = rawurldecode((string)($parts['user'] ?? ''));
    $password = rawurldecode((string)($parts['pass'] ?? ''));
    if ($host === '' || $database === '' || $user === '' || $password === '' || $port < 1 || $port > 65535
        || (!preg_match('/^(?=.{1,253}$)[A-Za-z0-9.-]+$/D', $host) && filter_var($host, FILTER_VALIDATE_IP) === false)
        || !preg_match('/^[A-Za-z0-9_.-]+$/D', $database)) {
        throw new RuntimeException('DATABASE_URL is missing valid PostgreSQL connection details.');
    }
    $query = [];
    parse_str((string)($parts['query'] ?? ''), $query);
    $sslMode = (string)($query['sslmode'] ?? 'require');
    if (!in_array($sslMode, ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'], true)) {
        throw new RuntimeException('DATABASE_URL contains an unsupported sslmode.');
    }
    return [
        'dsn' => 'pgsql:host=' . $host . ';port=' . $port . ';dbname=' . $database . ';sslmode=' . $sslMode,
        'user' => $user,
        'password' => $password,
        'emulate_prepares' => $port === 6543 && str_ends_with($host, '.pooler.supabase.com'),
    ];
}

function codefy_db(): PDO {
    static $pdo = null;
    if ($pdo instanceof PDO) return $pdo;

    $dsn = codefy_env('CODEFY_DATABASE_DSN');
    $connectionUser = codefy_env('PGUSER');
    $connectionPassword = codefy_env('PGPASSWORD');
    $emulatePreparesDefault = 'false';
    if (!$dsn && codefy_env('DATABASE_URL')) {
        $connection = codefy_parse_database_url((string)codefy_env('DATABASE_URL'));
        $dsn = $connection['dsn'];
        $connectionUser = $connection['user'];
        $connectionPassword = $connection['password'];
        $emulatePreparesDefault = $connection['emulate_prepares'] ? 'true' : 'false';
    }
    if (!$dsn) {
        $host = codefy_env('PGHOST', '127.0.0.1');
        $port = codefy_env('PGPORT', '5432');
        $database = codefy_env('PGDATABASE', 'codefy_guide');
        $dsn = 'pgsql:host=' . $host . ';port=' . $port . ';dbname=' . $database;
        $sslMode = codefy_env('PGSSLMODE');
        if ($sslMode) $dsn .= ';sslmode=' . $sslMode;
    }

    $pdo = new PDO($dsn, $connectionUser, $connectionPassword, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        // Supabase's transaction pooler does not retain named server-side prepares.
        PDO::ATTR_EMULATE_PREPARES => codefy_bool(codefy_env('CODEFY_PDO_EMULATE_PREPARES', $emulatePreparesDefault)),
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
        foreach ($pdo->query('SELECT slug, title, subtitle, icon, accent, content_mode, is_published, sort_order FROM codefy_guide_sections ORDER BY sort_order, slug') as $row) {
            $slug = $row['slug'];
            $section = $SECTIONS[$slug] ?? codefy_accent_theme((string)$row['accent']);
            $section['title'] = $row['title'];
            $section['subtitle'] = $row['subtitle'];
            $section['icon'] = $row['icon'];
            $section['accent'] = $row['accent'];
            $section['content_mode'] = $row['content_mode'];
            $section['published'] = codefy_bool($row['is_published']);
            $section['number'] = (int)$row['sort_order'];
            if (!isset($SECTIONS[$slug])) $section['pill'] .= ' ' . (int)$row['sort_order'];
            if (($SECTIONS[$slug]['accent'] ?? null) !== $row['accent']) {
                $theme = codefy_accent_theme((string)$row['accent']);
                foreach (['pill_bg', 'pill_text', 'gradient', 'shadow', 'accent'] as $key) $section[$key] = $theme[$key];
            }
            if ($section['published']) $orderedSections[$slug] = $section;
            elseif (codefy_current_slug() === $row['slug']) {
                http_response_code(404);
                exit('هذا القسم غير متاح حالياً.');
            }
        }
        if ($orderedSections) $SECTIONS = $orderedSections;

        $currentSlug = codefy_current_slug();
        if (isset($SECTIONS[$currentSlug]) && ($SECTIONS[$currentSlug]['content_mode'] ?? 'legacy') === 'builder') {
            $mermaid = $pdo->prepare("SELECT EXISTS (SELECT 1 FROM codefy_section_blocks WHERE section_slug = :slug AND block_type = 'mermaid')");
            $mermaid->execute(['slug' => $currentSlug]);
            if (codefy_bool($mermaid->fetchColumn())) $GLOBALS['page_needs_mermaid'] = true;
        }
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
