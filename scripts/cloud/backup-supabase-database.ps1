param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [string]$OutputDirectory = ".\backups"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$resolvedDirectory = (Resolve-Path $OutputDirectory).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupName = "jr-platform-supabase-$timestamp.dump"

Write-Host "Creando una copia lógica de Supabase..."
docker run --rm `
    -v "${resolvedDirectory}:/backups" `
    postgres:16-alpine `
    pg_dump `
    --format=custom `
    --no-owner `
    --no-privileges `
    --file="/backups/$backupName" `
    $DatabaseUrl

Write-Host "Copia creada: $(Join-Path $resolvedDirectory $backupName)" -ForegroundColor Green
