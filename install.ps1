# Install script for Windows (PowerShell)
# Mirrors install.sh behaviour: prereq checks, .env setup, hosts entry, docker compose start, health checks

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Colors
$Green = "`e[32m"; $Red = "`e[31m"; $Yellow = "`e[33m"; $Cyan = "`e[36m"; $NC = "`e[0m"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LogFile = Join-Path $ScriptDir "install-windows.log"
$ProjectName = 'APS Scheduler'
$ProjectUrl = 'http://aps-schedule.local'
$ProjectUrlFallback = 'http://localhost'
$MinDockerVersion = '20.10'
$MinComposeVersion = '1.29'

function Log([string]$msg){ Write-Host "${Cyan}[INFO]${NC} $msg"; Add-Content -Path $LogFile -Value "[INFO] $msg" }
function Success([string]$msg){ Write-Host "${Green}[✓]${NC} $msg"; Add-Content -Path $LogFile -Value "[OK] $msg" }
function ErrorMsg([string]$msg){ Write-Host "${Red}[✗]${NC} $msg"; Add-Content -Path $LogFile -Value "[ERR] $msg" }
function Warn([string]$msg){ Write-Host "${Yellow}[!]${NC} $msg"; Add-Content -Path $LogFile -Value "[WARN] $msg" }

function Test-CommandExists([string]$name){ return (Get-Command $name -ErrorAction SilentlyContinue) -ne $null }

function Read-Input([string]$prompt,[string]$default=''){
    if ($default -ne ''){
        $resp = Read-Host "$prompt [$default]"
        if ([string]::IsNullOrWhiteSpace($resp)) { return $default } else { return $resp }
    } else {
        return Read-Host $prompt
    }
}

function Ensure-Prereqs{
    Log "Checking prerequisites..."

    $missing = @()

    if (-not (Test-CommandExists docker)){
        ErrorMsg "Docker not found"
        $missing += 'docker'
    } else {
        try { $dv = (& docker --version) -replace 'Docker version ','',0 -replace ',.*','' } catch { $dv = '' }
        if ($dv -and [version]$dv -ge [version]$MinDockerVersion) { Success "Docker $dv" } else { Warn "Docker version seems older than $MinDockerVersion ($dv)" }
    }

    # docker compose (v2) or docker-compose
    $hasDockerCompose = Test-CommandExists 'docker-compose'
    $hasDockerComposeV2 = $false
    try { if ((Get-Command 'docker' -ErrorAction SilentlyContinue)) { $out = & docker compose version 2>&1; if ($out -and -not ($out -match 'command not found')) { $hasDockerComposeV2 = $true } } } catch {}
    if (-not ($hasDockerCompose -or $hasDockerComposeV2)){
        ErrorMsg "Docker Compose not found (docker compose or docker-compose)"
        $missing += 'docker-compose'
    }

    # Docker daemon
    try { & docker info >$null 2>&1; Success 'Docker daemon is running' } catch { ErrorMsg 'Docker daemon not running'; $missing += 'docker-daemon' }

    if (-not (Test-Path (Join-Path $ScriptDir 'docker-compose.yaml'))){ ErrorMsg 'docker-compose.yaml missing'; $missing += 'compose-file' } else { Success 'docker-compose.yaml found' }

    if ($missing.Count -gt 0){ ErrorMsg "$($missing.Count) prerequisites missing: $($missing -join ', ')"; throw 'Missing prerequisites' }
    Success 'All prerequisites satisfied'
}

function Setup-Env{
    Log 'Setting up .env file'
    $envFile = Join-Path $ScriptDir '.env'
    $envExample = Join-Path $ScriptDir '.env.example'

    if (-not (Test-Path $envExample)){ ErrorMsg '.env.example not found'; throw 'Missing .env.example' }

    if (Test-Path $envFile){ $overwrite = Read-Input 'Overwrite existing .env? (y/N)' 'n'; if ($overwrite -ne 'y' -and $overwrite -ne 'Y'){ Log 'Keeping existing .env'; return } }

    Copy-Item -Path $envExample -Destination $envFile -Force

    $pgUser = Read-Input 'PostgreSQL username' 'aps_user'
    $pgPass = Read-Input 'PostgreSQL password' 'aps_password'
    $pgDb = Read-Input 'PostgreSQL database name' 'apsdb'

    "POSTGRES_USER=$pgUser" | Out-File -FilePath $envFile -Encoding utf8
    "POSTGRES_PASSWORD=$pgPass" | Out-File -FilePath $envFile -Encoding utf8 -Append
    "POSTGRES_DB=$pgDb" | Out-File -FilePath $envFile -Encoding utf8 -Append

    Success '.env created'
}

function Setup-Hosts{
    Log "Configuring hosts entry for aps-schedule.local (optional)"
    $answer = Read-Input "Add '127.0.0.1 aps-schedule.local' to hosts file?" 'y'
    if ($answer -ne 'y' -and $answer -ne 'Y'){ Warn 'Skipping hosts modification'; return }

    $hostsPath = "$env:windir\System32\drivers\etc\hosts"
    $entry = '127.0.0.1    aps-schedule.local'

    $isAdmin = ([bool](([System.Security.Principal.WindowsIdentity]::GetCurrent()).Groups -match 'S-1-5-32-544'))
    if (-not $isAdmin){ Warn 'Hosts modification requires Administrator privileges. Re-run PowerShell as Administrator to add hosts entry.'; return }

    $hostsContent = Get-Content -Path $hostsPath -ErrorAction SilentlyContinue
    if ($hostsContent -join "`n" -match 'aps-schedule.local') { Success 'Hosts entry already present' ; return }

    try {
        Add-Content -Path $hostsPath -Value $entry
        Success "Added hosts entry"
    } catch { ErrorMsg "Failed to update hosts: $_" }
}

function Start-DockerServices{
    Log 'Starting Docker services'

    # Detect which compose command to use
    $composeCmd = if (Test-CommandExists 'docker-compose') { 'docker-compose' } elseif ((Get-Command docker -ErrorAction SilentlyContinue) -and (& docker compose version 2>&1 -notmatch 'command not found')) { 'docker compose' } else { throw 'No docker compose available' }

    # Check for existing containers
    $existing = & docker ps -a --format '{{.Names}}' 2>$null | Select-String -Pattern 'aps-postgres|aps-backend|aps-frontend|aps-reverse-proxy' -SimpleMatch
    if ($existing){
        Write-Host 'Existing containers detected:'; $existing | ForEach-Object { Write-Host " - $_" }
        $action = Read-Input 'Action: (1) Remove and recreate, (2) Keep and reuse, (3) Cancel?' '2'
        switch ($action){
            '1' { & $composeCmd down --volumes; }
            '2' { & $composeCmd start 2>$null -ErrorAction SilentlyContinue; return }
            '3' { Write-Host 'Cancelled'; exit 0 }
            default { & $composeCmd start 2>$null -ErrorAction SilentlyContinue; return }
        }
    }

    Log 'Bringing up containers (may take a few minutes)'
    try {
        & $composeCmd up --build -d 2>&1 | Tee-Object -FilePath $LogFile
        Success 'Docker containers started'
    } catch { ErrorMsg "Failed to start containers: $_"; throw }
}

function Wait-ForPort([string]$host,[int]$port,[int]$retries=30){
    for ($i=0;$i -lt $retries;$i++){
        $r = Test-NetConnection -ComputerName $host -Port $port -WarningAction SilentlyContinue
        if ($r.TcpTestSucceeded){ Success "$host:$port is reachable"; return $true }
        Write-Host "Attempt $($i+1)/$retries...`r" -NoNewline
        Start-Sleep -Seconds 2
    }
    ErrorMsg "$host:$port did not respond in time"
    return $false
}

function Check-ServiceHealth{
    Log 'Checking service health'
    Wait-ForPort -host 'localhost' -port 5432 | Out-Null

    $backend = (& docker ps --filter 'name=aps-backend' --filter 'status=running' -q) -ne $null
    if ($backend) { Success 'Backend running' } else { Warn 'Backend not running' }

    $frontend = (& docker ps --filter 'name=aps-frontend' --filter 'status=running' -q) -ne $null
    if ($frontend) { Success 'Frontend running' } else { Warn 'Frontend not running' }

    $nginx = (& docker ps --filter 'name=aps-reverse-proxy' --filter 'status=running' -q) -ne $null
    if ($nginx) { Success 'Reverse proxy running' } else { Warn 'Reverse proxy not running' }
}

function Show-Completion{
    Write-Host "`n${Green}Installation Complete - $ProjectName${NC}`n"
    Write-Host "Access Points:`n  Application: $ProjectUrl`n  Fallback: $ProjectUrlFallback`n  API Docs: $ProjectUrl/docs`n  Database: localhost:5432`n"
    Write-Host "Useful Commands:`n  View logs: docker-compose logs -f`n  Stop services: docker-compose down`n  Start services: docker-compose up -d`n"
    Write-Host "Install log: $LogFile`n"
    Start-Process $ProjectUrl -ErrorAction SilentlyContinue
}

# Main
Clear-Host
Log "Start install: $(Get-Date)"

try{
    Ensure-Prereqs
    Setup-Env
    Setup-Hosts
    Start-DockerServices
    Check-ServiceHealth
    Show-Completion
    Log 'Installation finished'
} catch {
    ErrorMsg "Install failed: $_"
    Write-Host "Check log: $LogFile"
    exit 1
}
