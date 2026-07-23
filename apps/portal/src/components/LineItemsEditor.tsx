import AddOutlinedIcon from '@mui/icons-material/AddOutlined'
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined'
import { Button, Grid, IconButton, Stack, TextField, Typography } from '@mui/material'

import type { LineItemInput } from '../api/finance'
import { euro } from '../utils/finance'

interface LineItemsEditorProps {
  items: LineItemInput[]
  onChange: (items: LineItemInput[]) => void
}

const emptyItem: LineItemInput = {
  description: '',
  quantity: '1.00',
  unit_price: '0.00',
  tax_rate: '7.00',
}

export function LineItemsEditor({ items, onChange }: LineItemsEditorProps) {
  const update = (index: number, field: keyof LineItemInput, value: string) => {
    onChange(items.map((item, itemIndex) => (itemIndex === index ? { ...item, [field]: value } : item)))
  }

  const remove = (index: number) => {
    if (items.length > 1) {
      onChange(items.filter((_, itemIndex) => itemIndex !== index))
    }
  }

  const estimatedTotal = items.reduce((total, item) => {
    const subtotal = Number(item.quantity) * Number(item.unit_price)
    return total + subtotal * (1 + Number(item.tax_rate) / 100)
  }, 0)

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="subtitle1" fontWeight={800}>Conceptos</Typography>
        <Button
          size="small"
          startIcon={<AddOutlinedIcon />}
          onClick={() => onChange([...items, { ...emptyItem }])}
        >
          Añadir línea
        </Button>
      </Stack>
      {items.map((item, index) => (
        <Grid container spacing={1.5} key={`${index}-${items.length}`} alignItems="center">
          <Grid size={{ xs: 12, md: 5 }}>
            <TextField
              fullWidth
              required
              label="Descripción"
              value={item.description}
              onChange={(event) => update(index, 'description', event.target.value)}
            />
          </Grid>
          <Grid size={{ xs: 4, md: 2 }}>
            <TextField
              fullWidth
              required
              type="number"
              label="Cantidad"
              value={item.quantity}
              slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
              onChange={(event) => update(index, 'quantity', event.target.value)}
            />
          </Grid>
          <Grid size={{ xs: 4, md: 2 }}>
            <TextField
              fullWidth
              required
              type="number"
              label="Precio"
              value={item.unit_price}
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              onChange={(event) => update(index, 'unit_price', event.target.value)}
            />
          </Grid>
          <Grid size={{ xs: 3, md: 2 }}>
            <TextField
              fullWidth
              required
              type="number"
              label="IGIC %"
              value={item.tax_rate}
              slotProps={{ htmlInput: { min: 0, max: 100, step: 0.01 } }}
              onChange={(event) => update(index, 'tax_rate', event.target.value)}
            />
          </Grid>
          <Grid size={{ xs: 1, md: 1 }}>
            <IconButton
              aria-label="Eliminar concepto"
              disabled={items.length === 1}
              onClick={() => remove(index)}
            >
              <DeleteOutlineOutlinedIcon />
            </IconButton>
          </Grid>
        </Grid>
      ))}
      <Typography textAlign="right" fontWeight={800}>
        Total estimado: {euro(estimatedTotal)}
      </Typography>
    </Stack>
  )
}
