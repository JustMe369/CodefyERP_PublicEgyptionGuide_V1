$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $repoRoot '.env'
if (Test-Path -LiteralPath $envFile) {
    throw '.env already exists. Keep it safe and configure PostgreSQL credentials there manually; this setup will not overwrite it.'
}

$psqlCommand = Get-Command psql.exe -ErrorAction SilentlyContinue
$psqlPath = if ($psqlCommand) { $psqlCommand.Source } else {
    $candidate = 'C:\Program Files\PostgreSQL\18\bin\psql.exe'
    if (Test-Path -LiteralPath $candidate) { $candidate } else { $null }
}
if (-not $psqlPath) { throw 'psql.exe was not found. Install PostgreSQL command-line tools or add its bin folder to PATH.' }

$securePassword = Read-Host 'Local PostgreSQL superuser password (postgres)' -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$ownerPassword = $null
$appPassword = $null
try {
    $postgresPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    $env:PGPASSWORD = $postgresPassword
    $existing = & $psqlPath -X -w -h 127.0.0.1 -p 5432 -U postgres -d postgres -Atqc "SELECT (SELECT count(*) FROM pg_database WHERE datname = 'codefy_guide') > 0 OR EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('codefy_owner', 'codefy_app'))" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Could not connect to the local PostgreSQL service: $existing" }
    if ($existing -match '^t') { throw 'A codefy_guide database or Codefy database role already exists. Setup stopped to protect existing data.' }

    function New-Secret {
        $bytes = New-Object byte[] 36
        $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
        try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
        return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
    }
    $ownerPassword = New-Secret
    $appPassword = New-Secret

    $setupSql = @'
SELECT format('CREATE ROLE codefy_owner LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'owner_password')
\gexec
CREATE DATABASE codefy_guide OWNER codefy_owner;
SELECT format('CREATE ROLE codefy_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password')
\gexec
GRANT CONNECT ON DATABASE codefy_guide TO codefy_app;
\connect codefy_guide
GRANT USAGE ON SCHEMA public TO codefy_app;
ALTER DEFAULT PRIVILEGES FOR ROLE codefy_owner IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO codefy_app;
ALTER DEFAULT PRIVILEGES FOR ROLE codefy_owner IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO codefy_app;
'@
    $setupSql | & $psqlPath -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U postgres -d postgres --set=owner_password=$ownerPassword --set=app_password=$appPassword
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL role/database setup failed. Review the error above before retrying.' }

    @(
        'PGHOST=127.0.0.1',
        'PGPORT=5432',
        'PGDATABASE=codefy_guide',
        'PGUSER=codefy_app',
        "PGPASSWORD=$appPassword",
        "CODEFY_DATABASE_DSN=pgsql:host=127.0.0.1;port=5432;dbname=codefy_guide",
        "CODEFY_MIGRATION_USER=codefy_owner",
        "CODEFY_MIGRATION_PASSWORD=$ownerPassword"
    ) | Set-Content -LiteralPath $envFile -Encoding ascii

    $env:PGPASSWORD = $ownerPassword
    $env:PGCLIENTENCODING = 'UTF8'
    $migrationFiles = Get-ChildItem -LiteralPath (Join-Path $repoRoot 'database\migrations') -Filter '*.sql' | Sort-Object Name
    foreach ($migration in $migrationFiles) {
        & $psqlPath -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U codefy_owner -d codefy_guide -f $migration.FullName
        if ($LASTEXITCODE -ne 0) { throw "Database and credentials are ready, but $($migration.Name) failed. Run .\scripts\migrate-postgres.ps1 to safely retry it." }
    }

    Write-Host 'PostgreSQL database and application role are ready. Credentials were saved to the ignored .env file.' -ForegroundColor Green
    Write-Host 'Create the first admin with: .\scripts\create-admin.ps1'
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:PGCLIENTENCODING -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    $postgresPassword = $null
    $ownerPassword = $null
    $appPassword = $null
}
