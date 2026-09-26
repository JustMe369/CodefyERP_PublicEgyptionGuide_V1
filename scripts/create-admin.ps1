$ErrorActionPreference = 'Stop'
$email = Read-Host 'Administrator email'
$displayName = Read-Host 'Display name'
$role = Read-Host 'Role (superuser/admin/section_author/viewer, default superuser)'
if ([string]::IsNullOrWhiteSpace($role)) { $role = 'superuser' }
if ($role -notin @('superuser', 'admin', 'section_author', 'viewer')) { throw 'Role must be superuser, admin, section_author, or viewer.' }
$securePassword = Read-Host 'Password (14+ characters)' -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)

$phpCommand = Get-Command php.exe -ErrorAction SilentlyContinue
$phpPath = if ($phpCommand) { $phpCommand.Source } else {
    Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) 'php\php.exe'
}
if (-not (Test-Path -LiteralPath $phpPath)) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    throw 'PHP CLI was not found. Add XAMPP php.exe to PATH or run this script from the XAMPP project.'
}

try {
    $env:CODEFY_ADMIN_EMAIL = $email
    $env:CODEFY_ADMIN_NAME = $displayName
    $env:CODEFY_ADMIN_ROLE = $role
    $env:CODEFY_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    & $phpPath (Join-Path $PSScriptRoot 'create-admin.php')
    if ($LASTEXITCODE -ne 0) { throw "Admin account creation failed (exit $LASTEXITCODE)." }
}
finally {
    Remove-Item Env:CODEFY_ADMIN_EMAIL -ErrorAction SilentlyContinue
    Remove-Item Env:CODEFY_ADMIN_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:CODEFY_ADMIN_ROLE -ErrorAction SilentlyContinue
    Remove-Item Env:CODEFY_ADMIN_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
}
