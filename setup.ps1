# Function to check if a command exists in the Windows PATH
function Test-CommandExists {
    param([string]$command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# 1. Copy .env.template to .env if it exists
if (Test-Path ".\.env.template") {
    if (-not (Test-Path ".\.env")) {
        Copy-Item ".\.env.template" ".\.env"
        Write-Host "Created .env from template." -ForegroundColor Cyan
    }
} else {
    Write-Host "Warning: .env.template not found." -ForegroundColor Yellow
}

# 2. User verification step
Write-Host "`nKindly verify the entries in '.env' file in the project directory." -ForegroundColor Yellow
Write-Host "Press any key to continue..." -NoNewline
$null = [Console]::ReadKey($true)
Write-Host "`n"

# 3. Execution Logic
if (Test-CommandExists "mise") {
    Write-Host "Mise detected. Proceeding with installation..." -ForegroundColor Green
    & mise install
    & mise run setup
    Write-Host "All setup complete" -ForegroundColor Green
}
else {
    Write-Host "Error: Neither 'nix' nor 'mise' was found in your PATH." -ForegroundColor Red
    Write-Host "Please install mise (https://mise.jdx.dev) to continue." -ForegroundColor Yellow
    exit 1
}