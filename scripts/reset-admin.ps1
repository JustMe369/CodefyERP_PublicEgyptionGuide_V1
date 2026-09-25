$ErrorActionPreference = 'Stop'
$email = Read-Host 'Existing administrator email'
$securePassword = Read-Host 'New administrator password (14+ characters)' -AsSecureString
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
    $env:CODEFY_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    & $phpPath (Join-Path $PSScriptRoot 'reset-admin.php')
    if ($LASTEXITCODE -ne 0) { throw "Admin password reset failed (exit $LASTEXITCODE)." }
}
finally {
    Remove-Item Env:CODEFY_ADMIN_EMAIL -ErrorAction SilentlyContinue
    Remove-Item Env:CODEFY_ADMIN_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
}
