$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $repoRoot '.env'

if (-not (Test-Path -LiteralPath $envFile)) {
    throw '.env was not found. Run .\scripts\setup-postgres.ps1 first or configure the database credentials.'
}

$psqlCommand = Get-Command psql.exe -ErrorAction SilentlyContinue
$psqlPath = if ($psqlCommand) { $psqlCommand.Source } else {
    $candidate = 'C:\Program Files\PostgreSQL\18\bin\psql.exe'
    if (Test-Path -LiteralPath $candidate) { $candidate } else { $null }
}
if (-not $psqlPath) { throw 'psql.exe was not found. Install PostgreSQL command-line tools or add its bin folder to PATH.' }

$settings = @{}
foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*([A-Z0-9_]+)=(.*)$') { $settings[$Matches[1]] = $Matches[2] }
}
if (-not $settings['CODEFY_MIGRATION_PASSWORD']) {
    throw '.env does not contain CODEFY_MIGRATION_PASSWORD. Restore the migration owner credentials before applying migrations.'
}

$env:PGPASSWORD = $settings['CODEFY_MIGRATION_PASSWORD']
$env:PGCLIENTENCODING = 'UTF8'
try {
    $migrationFiles = Get-ChildItem -LiteralPath (Join-Path $repoRoot 'database\migrations') -Filter '*.sql' | Sort-Object Name
    foreach ($migration in $migrationFiles) {
        & $psqlPath -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U codefy_owner -d codefy_guide -f $migration.FullName
        if ($LASTEXITCODE -ne 0) { throw "Migration $($migration.Name) failed. Its transaction was rolled back; fix the reported issue and rerun this script." }
    }
    Write-Host 'PostgreSQL migration applied successfully.' -ForegroundColor Green
    Write-Host 'Create the first admin with: .\scripts\create-admin.ps1'
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:PGCLIENTENCODING -ErrorAction SilentlyContinue
    $settings.Clear()
}
