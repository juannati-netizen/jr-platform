import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import LocalOfferOutlinedIcon from '@mui/icons-material/LocalOfferOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { type ChangeEvent, useState } from 'react'

import { ApiError } from '../api/client'
import { importLegacyTariff } from '../api/inventory'

interface TemplateDefinition {
  name: string
  filename: string
  description: string
  content: string
}

const templates: TemplateDefinition[] = [
  {
    name: 'Clientes',
    filename: 'clientes.csv',
    description: 'Empresas y particulares con sus datos de contacto.',
    content:
      'name,tax_id,email,phone,address,notes,is_active\nCliente ejemplo,B12345678,cliente@example.com,600000000,Calle Ejemplo 1,Importado desde escritorio,true\n',
  },
  {
    name: 'Proveedores',
    filename: 'proveedores.csv',
    description: 'Directorio de compras y suministradores.',
    content:
      'name,tax_id,email,phone,address,notes,is_active\nProveedor ejemplo,B87654321,proveedor@example.com,611111111,Polígono Industrial 2,Importado desde escritorio,true\n',
  },
  {
    name: 'Trabajos',
    filename: 'trabajos.csv',
    description: 'Órdenes de trabajo vinculadas a clientes.',
    content:
      'client_tax_id,title,description,status,priority,scheduled_for,assignee_email\nB12345678,Instalación eléctrica,Descripción del trabajo,planned,normal,2026-08-01T09:00:00,admin@jrplatform.com\n',
  },
  {
    name: 'Facturas',
    filename: 'facturas.csv',
    description: 'Cabeceras de facturas y estado de cobro.',
    content:
      'number,client_tax_id,issue_date,due_date,status,notes\nF-2026-0001,B12345678,2026-07-01,2026-07-31,issued,Importada desde escritorio\n',
  },
  {
    name: 'Gastos',
    filename: 'gastos.csv',
    description: 'Compras, materiales y otros costes.',
    content:
      'supplier_tax_id,work_order_title,description,category,status,expense_date,subtotal,tax_rate,reference,notes\nB87654321,Instalación eléctrica,Material eléctrico,materials,paid,2026-07-02,100.00,7.00,TICKET-001,Importado desde escritorio\n',
  },
]

function downloadTemplate(template: TemplateDefinition) {
  const blob = new Blob([template.content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = template.filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export function MigrationPage() {
  const queryClient = useQueryClient()
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const importMutation = useMutation({
    mutationFn: importLegacyTariff,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['catalog'] }),
        queryClient.invalidateQueries({ queryKey: ['catalog-families'] }),
        queryClient.invalidateQueries({ queryKey: ['inventory'] }),
        queryClient.invalidateQueries({ queryKey: ['warehouses'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
      ])
    },
  })

  const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    setSelectedFile(file?.name ?? null)
  }

  return (
    <Stack spacing={2}>
      <Box>
        <Chip label="Transición desde JR Platform Desktop" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.2 }}>Centro de migración</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.6, maxWidth: 850 }}>
          Importa los datos útiles de la aplicación de escritorio y prepara futuras migraciones.
        </Typography>
      </Box>

      <Alert severity="info" icon={<InfoOutlinedIcon />}>
        El tarifario privado está guardado en <strong>private-import/tariff_items.csv</strong>. La
        carpeta está excluida de Git para que los precios no se publiquen en el repositorio.
      </Alert>

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" gap={2}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <LocalOfferOutlinedIcon color="primary" />
                <Typography variant="h6">Tarifario heredado</Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.8 }}>
                Se detectaron 1.135 artículos en la base SQLite antigua. La importación es
                idempotente: puedes repetirla sin duplicar códigos.
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<CloudUploadOutlinedIcon />}
              onClick={() => importMutation.mutate()}
              disabled={importMutation.isPending}
            >
              Importar tarifario
            </Button>
          </Stack>
          {importMutation.isPending && <LinearProgress sx={{ mt: 2 }} />}
          {importMutation.data && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {importMutation.data.total_rows} filas procesadas: {importMutation.data.created}{' '}
              artículos creados, {importMutation.data.updated} actualizados y{' '}
              {importMutation.data.skipped} omitidos.
            </Alert>
          )}
          {importMutation.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {importMutation.error instanceof ApiError
                ? importMutation.error.message
                : 'No se pudo importar el tarifario'}
            </Alert>
          )}
        </CardContent>
      </Card>

      <Grid container spacing={1.5}>
        <Grid size={{ xs: 12, lg: 5 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6">Otros datos disponibles</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.7 }}>
                La copia analizada incluye el código fuente, 131 tablas y copias de seguridad, pero
                clientes, proveedores, trabajos y facturas estaban vacíos.
              </Typography>
              <Stack spacing={1.1} sx={{ mt: 2 }}>
                {[
                  '1.135 artículos de tarifario listos para importar.',
                  '1 almacén principal detectado.',
                  'Esquema completo disponible como referencia funcional.',
                  'Las bases SQLite superaron la comprobación de integridad.',
                ].map((item) => (
                  <Stack key={item} direction="row" spacing={1} alignItems="flex-start">
                    <CheckCircleOutlineIcon color="primary" fontSize="small" />
                    <Typography variant="body2">{item}</Typography>
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 7 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6">Revisar una exportación futura</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.7 }}>
                Selecciona un archivo para comprobar su nombre antes de preparar un importador.
                El navegador no lo envía ni modifica la base de datos.
              </Typography>
              <Box
                sx={{
                  mt: 2,
                  minHeight: 150,
                  border: '1px dashed',
                  borderColor: selectedFile ? 'success.main' : 'primary.main',
                  bgcolor: '#141d26',
                  display: 'grid',
                  placeItems: 'center',
                  textAlign: 'center',
                  p: 2,
                }}
              >
                <Stack alignItems="center" spacing={1.1}>
                  {selectedFile ? (
                    <FolderOpenOutlinedIcon color="success" sx={{ fontSize: 38 }} />
                  ) : (
                    <CloudUploadOutlinedIcon color="primary" sx={{ fontSize: 38 }} />
                  )}
                  <Typography fontWeight={700}>
                    {selectedFile ?? 'Selecciona un CSV, Excel o archivo de base de datos'}
                  </Typography>
                  <Button component="label" variant="outlined">
                    Elegir archivo
                    <input hidden type="file" accept=".csv,.xlsx,.xls,.db,.sqlite,.sqlite3,.mdb,.accdb" onChange={handleFile} />
                  </Button>
                </Stack>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box>
        <Typography variant="h5">Plantillas de intercambio</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Formatos para preparar futuras importaciones desde otras herramientas.
        </Typography>
      </Box>

      <Grid container spacing={1.4}>
        {templates.map((template) => (
          <Grid key={template.filename} size={{ xs: 12, sm: 6, lg: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6">{template.name}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.6, minHeight: 42 }}>
                  {template.description}
                </Typography>
                <Button sx={{ mt: 1.6 }} variant="outlined" startIcon={<DownloadOutlinedIcon />} onClick={() => downloadTemplate(template)}>
                  Descargar {template.filename}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  )
}
