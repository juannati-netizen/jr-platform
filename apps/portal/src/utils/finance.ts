import type { InvoiceStatus, PaymentMethod, QuoteStatus } from '../api/types'

export const quoteStatusOptions: Array<{ value: QuoteStatus; label: string }> = [
  { value: 'draft', label: 'Borrador' },
  { value: 'sent', label: 'Enviado' },
  { value: 'accepted', label: 'Aceptado' },
  { value: 'rejected', label: 'Rechazado' },
  { value: 'expired', label: 'Caducado' },
]

export const invoiceStatusOptions: Array<{ value: InvoiceStatus; label: string }> = [
  { value: 'issued', label: 'Emitida' },
  { value: 'partial', label: 'Cobro parcial' },
  { value: 'paid', label: 'Cobrada' },
  { value: 'cancelled', label: 'Cancelada' },
]

export const paymentMethodOptions: Array<{ value: PaymentMethod; label: string }> = [
  { value: 'cash', label: 'Efectivo' },
  { value: 'bank_transfer', label: 'Transferencia' },
  { value: 'card', label: 'Tarjeta' },
  { value: 'direct_debit', label: 'Domiciliación' },
  { value: 'other', label: 'Otro' },
]

export function quoteStatusLabel(status: QuoteStatus): string {
  return quoteStatusOptions.find((item) => item.value === status)?.label ?? status
}

export function invoiceStatusLabel(status: InvoiceStatus): string {
  return invoiceStatusOptions.find((item) => item.value === status)?.label ?? status
}

export function paymentMethodLabel(method: PaymentMethod): string {
  return paymentMethodOptions.find((item) => item.value === method)?.label ?? method
}

export function euro(value: string | number): string {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(value))
}

type ChipColor = 'default' | 'primary' | 'warning' | 'error' | 'success' | 'info'

export function quoteStatusColor(status: QuoteStatus): ChipColor {
  const colors: Record<QuoteStatus, ChipColor> = {
    draft: 'default',
    sent: 'info',
    accepted: 'success',
    rejected: 'error',
    expired: 'warning',
  }
  return colors[status]
}

export function invoiceStatusColor(status: InvoiceStatus): ChipColor {
  const colors: Record<InvoiceStatus, ChipColor> = {
    issued: 'info',
    partial: 'warning',
    paid: 'success',
    cancelled: 'error',
  }
  return colors[status]
}
