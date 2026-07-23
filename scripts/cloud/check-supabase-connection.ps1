param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl
)

$ErrorActionPreference = "Stop"

Write-Host "Comprobando la conexión cifrada con Supabase..."
docker run --rm `
    postgres:16-alpine `
    psql `
    $DatabaseUrl `
    --set=ON_ERROR_STOP=1 `
    --command="select current_database() as database, current_user as user_name, version();"

Write-Host "Conexión con Supabase correcta." -ForegroundColor Green
