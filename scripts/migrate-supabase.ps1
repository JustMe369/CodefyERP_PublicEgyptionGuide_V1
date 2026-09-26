$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent

$psqlCommand = Get-Command psql.exe -ErrorAction SilentlyContinue
$psqlPath = if ($psqlCommand) { $psqlCommand.Source } else {
    $candidate = 'C:\Program Files\PostgreSQL\18\bin\psql.exe'
    if (Test-Path -LiteralPath $candidate) { $candidate } else { $null }
}
if (-not $psqlPath) { throw 'psql.exe was not found. Install PostgreSQL command-line tools or add its bin folder to PATH.' }

$securePassword = Read-Host 'Supabase postgres database password' -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$databasePassword = $null
try {
    $databasePassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    $env:PGPASSWORD = $databasePassword
    $env:PGCLIENTENCODING = 'UTF8'
    $hostName = if ($env:CODEFY_SUPABASE_DB_HOST) { $env:CODEFY_SUPABASE_DB_HOST } else { 'aws-1-eu-west-1.pooler.supabase.com' }
    $port = if ($env:CODEFY_SUPABASE_DB_PORT) { $env:CODEFY_SUPABASE_DB_PORT } else { '6543' }
    $database = if ($env:CODEFY_SUPABASE_DB_NAME) { $env:CODEFY_SUPABASE_DB_NAME } else { 'postgres' }
    $projectRef = 'mgdkjrbodyvjgkuaoocz'
    $databaseRole = "postgres.$projectRef"

    $probe = & $psqlPath -X -w -h $hostName -p $port -U $databaseRole -d $database -Atqc 'SELECT current_database()' 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Supabase connection failed: $probe" }
    if ($probe -ne 'postgres') { throw 'Connected to an unexpected Supabase database; migration stopped.' }

    $migrationFiles = Get-ChildItem -LiteralPath (Join-Path $repoRoot 'database\migrations') -Filter '*.sql' | Sort-Object Name
    foreach ($migration in $migrationFiles) {
        Write-Host "Applying $($migration.Name)..."
        & $psqlPath -X -w -v ON_ERROR_STOP=1 -h $hostName -p $port -U $databaseRole -d $database -f $migration.FullName
        if ($LASTEXITCODE -ne 0) { throw "Migration $($migration.Name) failed. Review its error, correct it, then rerun this script." }
    }

    $verification = & $psqlPath -X -w -h $hostName -p $port -U $databaseRole -d $database -Atqc "SELECT (SELECT count(*) FROM codefy_schema_migrations WHERE version IN ('001_admin_foundation','002_runtime_role_security','003_visual_section_builder','004_admin_roles_and_draft_sections')) || '|' || (SELECT count(*) FROM codefy_admin_roles) || '|' || (SELECT count(*) FROM codefy_admin_permissions) || '|' || has_table_privilege('codefy_app','public.codefy_schema_migrations','SELECT')" 2>&1
    if ($LASTEXITCODE -ne 0 -or $verification -ne '4|4|18|t') { throw "Supabase role and migration verification failed: $verification" }
    Write-Host 'Supabase migrations and application-role grants were verified. The existing codefy_app password was not changed.' -ForegroundColor Green
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:PGCLIENTENCODING -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    $databasePassword = $null
}
