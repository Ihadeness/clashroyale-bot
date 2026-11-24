<#
.SYNOPSIS
    Installs Clash Royale Bot dependencies for 2.6 Hog Cycle on Windows.

.DESCRIPTION
    This script sets up the complete environment for running the Clash Royale bot:
    - Installs uv (fast Python package manager)
    - Creates virtual environment
    - Installs Python dependencies with DirectML support
    - Downloads and configures ADB (Android Debug Bridge)
    - Verifies BlueStacks installation

.NOTES
    Tested on: Windows 10/11, Ryzen 5 5500U (Vega 7 iGPU)
    Requires: PowerShell 5.1+, Administrator rights for ADB install
#>

param(
    [switch]$SkipVenv,
    [switch]$SkipAdb,
    [switch]$ForceReinstall,
    [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors for output
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Red = [ConsoleColor]::Red
$Cyan = [ConsoleColor]::Cyan

function Write-Log {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-Log "✓ $Message" $Green }
function Write-Warning { param([string]$Message) Write-Log "⚠ $Message" $Yellow }
function Write-Error { param([string]$Message) Write-Log "✗ $Message" $Red }
function Write-Info { param([string]$Message) Write-Log "$Message" $Cyan }

Write-Info "=== Clash Royale Bot Setup ==="
Write-Info "Target: 2.6 Hog Cycle on Ryzen 5500U (Vega 7 iGPU)"
Write-Info ""

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Error "PowerShell 5.1+ required. Current: $($PSVersionTable.PSVersion)"
    exit 1
}

# Check if running as Administrator (needed for ADB install to Program Files)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as Administrator. ADB install may fail if target is protected."
}

# 1. Install uv (fast Python package manager)
Write-Info "Step 1/5: Checking uv installation..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Success "uv already installed: $(uv --version)"
} else {
    Write-Info "Installing uv..."
    try {
        Invoke-WebRequest -Uri "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" -OutFile "$env:TEMP\uv.zip" -UseBasicParsing
        Expand-Archive -Path "$env:TEMP\uv.zip" -DestinationPath "$env:USERPROFILE\.local\bin" -Force
        $env:PATH += ";$env:USERPROFILE\.local\bin"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
        Write-Success "uv installed: $(uv --version)"
    } catch {
        Write-Error "Failed to install uv: $_"
        exit 1
    }
}

# 2. Create virtual environment
if (-not $SkipVenv) {
    Write-Info "Step 2/5: Creating virtual environment..."
    $venvPath = ".\.venv"
    if (Test-Path $venvPath -and -not $ForceReinstall) {
        Write-Warning "Virtual environment exists at $venvPath (use -ForceReinstall to recreate)"
    } else {
        if (Test-Path $venvPath) {
            Remove-Item -Recurse -Force $venvPath
        }
        uv venv --python $PythonVersion $venvPath
        Write-Success "Virtual environment created at $venvPath"
    }
}

# 3. Install Python dependencies
Write-Info "Step 3/5: Installing Python dependencies..."
$pip = if ($SkipVenv) { "uv pip" } else { ".\.venv\Scripts\uv.exe pip" }
$requirements = "requirements.txt"

if (-not (Test-Path $requirements)) {
    Write-Error "requirements.txt not found at $requirements"
    exit 1
}

try {
    & $pip install -r $requirements
    Write-Success "Python dependencies installed"
} catch {
    Write-Error "Failed to install dependencies: $_"
    exit 1
}

# 4. Download and configure ADB
if (-not $SkipAdb) {
    Write-Info "Step 4/5: Setting up ADB..."
    $adbDir = "platform-tools"
    $adbExe = "$adbDir\adb.exe"

    if (Test-Path $adbExe -and -not $ForceReinstall) {
        Write-Warning "ADB already exists at $adbExe (use -ForceReinstall to re-download)"
    } else {
        Write-Info "Downloading Android SDK Platform-Tools..."
        $url = "https://dl.google.com/android/repository/platform-tools_r34.0.5-windows.zip"
        $zipPath = "$env:TEMP\platform-tools.zip"

        try {
            Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
            if (Test-Path $adbDir) { Remove-Item -Recurse -Force $adbDir }
            Expand-Archive -Path $zipPath -DestinationPath "." -Force
            Write-Success "ADB installed at $adbExe"
        } catch {
            Write-Error "Failed to download ADB: $_"
            exit 1
        }
    }

    # Add ADB to PATH for current session
    $adbFullPath = Resolve-Path $adbDir
    $env:PATH += ";$adbFullPath"
    Write-Info "ADB added to PATH for this session"

    # Verify ADB works
    try {
        $output = & $adbExe version
        Write-Success "ADB version: $($output.Split("`n")[0])"
    } catch {
        Write-Warning "ADB verification failed (may need PATH restart): $_"
    }
}

# 5. Verify BlueStacks
Write-Info "Step 5/5: Verifying BlueStacks..."
$bluestacksPaths = @(
    "C:\Program Files\BlueStacks_nxt\HD-Player.exe",
    "C:\Program Files\BlueStacks\HD-Player.exe",
    "$env:LOCALAPPDATA\BlueStacks\nxt\HD-Player.exe",
    "$env:PROGRAMFILES\BlueStacks_nxt\HD-Player.exe"
)

$bluestacksFound = $false
foreach ($path in $bluestacksPaths) {
    if (Test-Path $path) {
        Write-Success "BlueStacks found at: $path"
        $bluestacksFound = $true
        break
    }
}

if (-not $bluestacksFound) {
    Write-Warning "BlueStacks not found in standard locations."
    Write-Info "Please install BlueStacks 5+ from https://www.bluestacks.com/"
    Write-Info "Then install Clash Royale from Play Store inside BlueStacks."
}

# Final summary
Write-Info ""
Write-Info "=== Setup Complete ==="
Write-Success "Virtual environment: .\.venv"
Write-Success "ADB: .\platform-tools\adb.exe"
Write-Success "Config: clashroyale_bot\config\hog_26.yaml"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Activate venv: .\.venv\Scripts\Activate.ps1"
Write-Info "2. Start BlueStacks and launch Clash Royale"
Write-Info "3. Start OneJev server: flide serve (in separate terminal)"
Write-Info "4. Run health check: python -m clashroyale_bot.setup.health_check"
Write-Info "5. Run bot: python -m clashroyale_bot.main --deck hog_26"
Write-Info ""
Write-Info "For DirectML on Vega 7: ensure Windows 10 1903+ and latest AMD drivers"

# Check if venv activation needed
if (-not $SkipVenv) {
    Write-Warning "Remember to activate the virtual environment in new terminals:"
    Write-Info "  .\.venv\Scripts\Activate.ps1"
}