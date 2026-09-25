$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $repoRoot '.env'

$psqlCommand = Get-Command psql.exe -ErrorAction SilentlyContinue
$psqlPath = if ($psqlCommand) { $psqlCommand.Source } else {
    $candidate = 'C:\Program Files\PostgreSQL\18\bin\psql.exe'
    if (Test-Path -LiteralPath $candidate) { $candidate } else { $null }
}
if (-not $psqlPath) { throw 'psql.exe was not found. Install PostgreSQL command-line tools or add its bin folder to PATH.' }

$securePassword = Read-Host 'Enter the NEW Supabase database password after rotating the exposed one' -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$adminPassword = $null
$appPassword = $null
try {
    $adminPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    $randomBytes = New-Object byte[] 36
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($randomBytes) } finally { $rng.Dispose() }
    $appPassword = [Convert]::ToBase64String($randomBytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')

    $env:PGPASSWORD = $adminPassword
    $env:PGCLIENTENCODING = 'UTF8'
    $env:PGSSLMODE = 'require'
    $env:CODEFY_NEW_APP_PASSWORD = $appPassword

    $hostName = 'aws-1-eu-west-1.pooler.supabase.com'
    $port = '6543'
    $database = 'postgres'
    $projectRef = 'mgdkjrbodyvjgkuaoocz'
    $adminRole = "postgres.$projectRef"
    $runtimePoolerUser = "codefy_app.$projectRef"
    $probe = & $psqlPath -X -w -h $hostName -p $port -U $adminRole -d $database -Atqc 'SELECT current_database()' 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Supabase connection failed: $probe" }
    if ($probe -ne 'postgres') { throw 'Connected to an unexpected database; setup stopped.' }

    $roleSql = @'
\getenv app_password CODEFY_NEW_APP_PASSWORD
-- Newly created PostgreSQL roles default to NOSUPERUSER, NOCREATEDB,
-- NOCREATEROLE, and NOBYPASSRLS. Supabase's postgres role cannot ALTER ROLE
-- with those attribute options, so leave the secure defaults implicit.
SELECT format('CREATE ROLE codefy_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codefy_app')
\gexec
SELECT format('ALTER ROLE codefy_app LOGIN PASSWORD %L', :'app_password')
\gexec
GRANT CONNECT ON DATABASE postgres TO codefy_app;
'@
    $roleSql | & $psqlPath -X -w -v ON_ERROR_STOP=1 -h $hostName -p $port -U $adminRole -d $database
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the restricted codefy_app database role.' }

    $migrationFiles = Get-ChildItem -LiteralPath (Join-Path $repoRoot 'database\migrations') -Filter '*.sql' | Sort-Object Name
    foreach ($migration in $migrationFiles) {
        Write-Host "Applying $($migration.Name)..."
        & $psqlPath -X -w -v ON_ERROR_STOP=1 -h $hostName -p $port -U $adminRole -d $database -f $migration.FullName
        if ($LASTEXITCODE -ne 0) { throw "Migration $($migration.Name) failed. Fix the reported issue and rerun this script." }
    }

    $verification = & $psqlPath -X -w -h $hostName -p $port -U $adminRole -d $database -Atqc "SELECT count(*) FROM codefy_schema_migrations WHERE version IN ('001_admin_foundation', '002_runtime_role_security', '003_visual_section_builder')" 2>&1
    if ($LASTEXITCODE -ne 0 -or $verification -ne '3') { throw "Migration verification failed: $verification" }
    $env:PGPASSWORD = $appPassword
    $runtimeCheck = $null
    for ($attempt = 1; $attempt -le 12; $attempt++) {
        $runtimeCheck = & $psqlPath -X -w -h $hostName -p $port -U $runtimePoolerUser -d $database -Atqc 'SELECT count(*) FROM codefy_guide_sections' 2>&1
        if ($LASTEXITCODE -eq 0 -and $runtimeCheck -eq '7') { break }
        if ($attempt -lt 12) {
            Write-Host "Supabase is refreshing the new role credentials; retrying verification ($attempt/12)..."
            Start-Sleep -Seconds 5
        }
    }
    if ($LASTEXITCODE -ne 0 -or $runtimeCheck -ne '7') { throw "Restricted application-role verification failed: $runtimeCheck" }
    $env:PGPASSWORD = $adminPassword

    $preserved = @()
    if (Test-Path -LiteralPath $envFile) {
        $databaseKeys = @('PGHOST','PGPORT','PGDATABASE','PGUSER','PGPASSWORD','PGSSLMODE','CODEFY_DATABASE_DSN','CODEFY_PDO_EMULATE_PREPARES','CODEFY_MIGRATION_USER','CODEFY_MIGRATION_PASSWORD')
        foreach ($line in Get-Content -LiteralPath $envFile) {
            if ($line -match '^\s*([A-Z0-9_]+)=') {
                if ($Matches[1] -notin $databaseKeys) { $preserved += $line }
            } else { $preserved += $line }
        }
    }
    $databaseConfig = @(
        "PGHOST=$hostName",
        "PGPORT=$port",
        "PGDATABASE=$database",
        "PGUSER=$runtimePoolerUser",
        "PGPASSWORD=$appPassword",
        'PGSSLMODE=require',
        "CODEFY_DATABASE_DSN=pgsql:host=$hostName;port=$port;dbname=$database;sslmode=require",
        'CODEFY_PDO_EMULATE_PREPARES=true'
    )
    @($preserved + $databaseConfig) | Set-Content -LiteralPath $envFile -Encoding ascii

    Write-Host 'Supabase migrations were applied and verified; the PHP app now uses the restricted codefy_app role.' -ForegroundColor Green
    Write-Host 'Create the first admin with: .\scripts\create-admin.ps1'
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:PGCLIENTENCODING -ErrorAction SilentlyContinue
    Remove-Item Env:PGSSLMODE -ErrorAction SilentlyContinue
    Remove-Item Env:CODEFY_NEW_APP_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    $adminPassword = $null
    $appPassword = $null
}
