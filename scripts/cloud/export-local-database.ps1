param(
    [string]$OutputDirectory = ".\backups"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$containerFile = "/tmp/jr-platform-$timestamp.dump"
$localFile = Join-Path $OutputDirectory "jr-platform-$timestamp.dump"

Write-Host "Creando copia de PostgreSQL dentro del contenedor..."
docker compose exec -T db sh -c "pg_dump -U \"`$POSTGRES_USER\" -d \"`$POSTGRES_DB\" --format=custom --no-owner --no-privileges --file=$containerFile"

Write-Host "Copiando la copia al ordenador..."
docker compose cp "db:$containerFile" $localFile
docker compose exec -T db rm -f $containerFile

Write-Host "Copia creada: $localFile" -ForegroundColor Green
