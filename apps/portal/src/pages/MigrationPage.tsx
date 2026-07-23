import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material'
import { type ChangeEvent, useState } from 'react'

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
      'supplier_tax_id,work_order_title,description,category,status,expense_date,subtotal,tax_rate,reference,notes\nB87654321,Instalación eléctrica,Material eléctrico,materials,paid,2026-07-02,100.00,21.00,TICKET-001,Importado desde escritorio\n',
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
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    setSelectedFile(file?.name ?? null)
  }

  return (
    <Stack spacing={2}>
      <Box>
        <Chip label="Transición desde JR Platform Desktop" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.2 }}>
          Centro de migración
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.6, maxWidth: 850 }}>
          Prepara los datos de la aplicación de escritorio para trasladarlos a la versión web sin
          perder clientes, trabajos, facturas ni compras.
        </Typography>
      </Box>

      <Alert severity="info" icon={<InfoOutlinedIcon />}>
        Esta fase prepara y valida los archivos. La importación definitiva se hará después de revisar
        una muestra de los datos exportados desde la aplicación de escritorio.
      </Alert>

      <Grid container spacing={1.5}>
        <Grid size={{ xs: 12, lg: 5 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6">1. Localizar los datos de origen</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.7 }}>
                En el ordenador actual necesitamos encontrar uno de estos elementos:
              </Typography>
              <Stack spacing={1.1} sx={{ mt: 2 }}>
                {[
                  'Exportaciones CSV o Excel de clientes, proveedores, trabajos y facturas.',
                  'Archivo de base de datos: .db, .sqlite, .sqlite3, .mdb o .accdb.',
                  'Carpeta de datos, copias de seguridad o documentos generados.',
                  'Capturas de las pantallas de exportación disponibles.',
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
              <Typography variant="h6">2. Cargar una muestra para revisar</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.7 }}>
                Selecciona un archivo exportado. En esta versión solo se registra el nombre del archivo;
                no se modifica la base de datos.
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
                  <Button component="label" variant="contained">
                    Elegir archivo
                    <input
                      hidden
                      type="file"
                      accept=".csv,.xlsx,.xls,.db,.sqlite,.sqlite3,.mdb,.accdb"
                      onChange={handleFile}
                    />
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
          Sirven para comparar las columnas de la aplicación antigua con el formato de JR Platform Web.
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
                <Button
                  sx={{ mt: 1.6 }}
                  variant="outlined"
                  startIcon={<DownloadOutlinedIcon />}
                  onClick={() => downloadTemplate(template)}
                >
                  Descargar {template.filename}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6">Orden recomendado de migración</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.8 }}>
            1. Usuarios → 2. Clientes y proveedores → 3. Trabajos → 4. Presupuestos y facturas →
            5. Pagos y gastos → 6. Documentos adjuntos.
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
