import type { Invoice, Quote } from '../api/types'
import { euro, invoiceStatusLabel, quoteStatusLabel } from './finance'

function escapeHtml(value: string | null | undefined): string {
  return (value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

export function printFinancialDocument(document: Quote | Invoice): void {
  const popup = window.open('', '_blank', 'width=900,height=700')
  if (!popup) {
    return
  }

  const isInvoice = 'paid_total' in document
  const title = isInvoice ? 'Factura' : 'Presupuesto'
  const status = isInvoice
    ? invoiceStatusLabel(document.status)
    : quoteStatusLabel(document.status)
  const dateLabel = new Intl.DateTimeFormat('es-ES').format(new Date(document.issue_date))
  const items = document.items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.description)}</td>
          <td class="number">${escapeHtml(item.quantity)}</td>
          <td class="number">${euro(item.unit_price)}</td>
          <td class="number">${escapeHtml(item.tax_rate)}%</td>
          <td class="number">${euro(item.line_total)}</td>
        </tr>`,
    )
    .join('')

  const paymentSummary = isInvoice
    ? `<div class="summary-row"><span>Cobrado</span><strong>${euro(document.paid_total)}</strong></div>
       <div class="summary-row"><span>Pendiente</span><strong>${euro(document.pending_total)}</strong></div>`
    : ''

  popup.document.write(`<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>${title} ${escapeHtml(document.number)}</title>
<style>
body{font-family:Arial,sans-serif;color:#172033;margin:40px}header{display:flex;justify-content:space-between;margin-bottom:40px}.brand{font-size:28px;font-weight:800;color:#0f766e}.meta{text-align:right}table{width:100%;border-collapse:collapse;margin-top:28px}th,td{padding:12px;border-bottom:1px solid #d8dee8;text-align:left}.number{text-align:right}.summary{width:330px;margin:28px 0 0 auto}.summary-row{display:flex;justify-content:space-between;padding:7px 0}.total{font-size:20px;border-top:2px solid #172033;margin-top:8px;padding-top:12px}.notes{margin-top:32px;padding:16px;background:#f4f6f8;border-radius:8px}@media print{body{margin:20px}}
</style>
</head>
<body>
<header><div><div class="brand">JR Platform</div><div>${title}</div></div><div class="meta"><strong>${escapeHtml(document.number)}</strong><br/>${dateLabel}<br/>${escapeHtml(status)}</div></header>
<section><strong>Cliente</strong><h2>${escapeHtml(document.client.name)}</h2></section>
<table><thead><tr><th>Concepto</th><th class="number">Cantidad</th><th class="number">Precio</th><th class="number">IVA</th><th class="number">Total</th></tr></thead><tbody>${items}</tbody></table>
<div class="summary"><div class="summary-row"><span>Base imponible</span><strong>${euro(document.subtotal)}</strong></div><div class="summary-row"><span>Impuestos</span><strong>${euro(document.tax_total)}</strong></div><div class="summary-row total"><span>Total</span><strong>${euro(document.total)}</strong></div>${paymentSummary}</div>
${document.notes ? `<div class="notes"><strong>Notas</strong><p>${escapeHtml(document.notes)}</p></div>` : ''}
<script>window.onload=()=>{window.print()}</script>
</body></html>`)
  popup.document.close()
}
