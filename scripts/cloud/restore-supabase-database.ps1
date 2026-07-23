param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"
$resolvedBackup = Resolve-Path $BackupPath
$backupDirectory = Split-Path $resolvedBackup -Parent
$backupName = Split-Path $resolvedBackup -Leaf

Write-Warning "Esta operación reemplazará el contenido de la base de datos Supabase indicada."
Write-Warning "Comprueba que la URL corresponde al proyecto correcto y que tienes una copia reciente."
$confirmation = Read-Host "Escribe RESTAURAR para continuar"
if ($confirmation -ne "RESTAURAR") {
    Write-Host "Operación cancelada."
    exit 1
}

Write-Host "Restaurando la copia en Supabase PostgreSQL..."
docker run --rm `
    -v "${backupDirectory}:/backups:ro" `
    postgres:16-alpine `
    pg_restore `
    --clean `
    --if-exists `
    --exit-on-error `
    --no-owner `
    --no-privileges `
    --dbname=$DatabaseUrl `
    "/backups/$backupName"

Write-Host "Restauración terminada correctamente." -ForegroundColor Green
