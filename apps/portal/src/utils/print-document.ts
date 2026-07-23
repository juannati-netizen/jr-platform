import type { CompanyPublicProfile } from '../api/settings'
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

function companyAddress(company?: CompanyPublicProfile): string {
  if (!company) return ''
  return [company.address, company.postal_code, company.city, company.province]
    .filter(Boolean)
    .join(' · ')
}

export function printFinancialDocument(
  document: Quote | Invoice,
  company?: CompanyPublicProfile,
): void {
  const popup = window.open('', '_blank', 'width=900,height=700')
  if (!popup) return

  const isInvoice = 'paid_total' in document
  const title = isInvoice ? 'Factura' : 'Presupuesto'
  const status = isInvoice
    ? invoiceStatusLabel(document.status)
    : quoteStatusLabel(document.status)
  const dateLabel = new Intl.DateTimeFormat('es-ES').format(new Date(document.issue_date))
  const companyName = company?.trade_name || company?.legal_name || 'JR Platform'
  const brandColor = company?.brand_color || '#0f766e'
  const logo = company?.logo_data_url
    ? `<img class="logo" src="${escapeHtml(company.logo_data_url)}" alt="${escapeHtml(companyName)}" />`
    : ''
  const companyDetails = company
    ? `<div class="company-details">${escapeHtml(company.legal_name)} · ${escapeHtml(company.tax_id)}<br/>${escapeHtml(companyAddress(company))}<br/>${escapeHtml(company.email)} ${escapeHtml(company.phone)}</div>`
    : ''
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
body{font-family:Arial,sans-serif;color:#172033;margin:40px}header{display:flex;justify-content:space-between;gap:24px;margin-bottom:36px}.identity{display:flex;gap:18px;align-items:flex-start}.logo{width:120px;height:72px;object-fit:contain}.brand{font-size:28px;font-weight:800;color:${brandColor}}.company-details{font-size:12px;color:#536071;line-height:1.5;margin-top:7px}.meta{text-align:right}table{width:100%;border-collapse:collapse;margin-top:28px}th,td{padding:12px;border-bottom:1px solid #d8dee8;text-align:left}.number{text-align:right}.summary{width:330px;margin:28px 0 0 auto}.summary-row{display:flex;justify-content:space-between;padding:7px 0}.total{font-size:20px;border-top:2px solid #172033;margin-top:8px;padding-top:12px}.notes{margin-top:32px;padding:16px;background:#f4f6f8;border-radius:8px}.footer{margin-top:38px;padding-top:14px;border-top:1px solid #d8dee8;font-size:11px;color:#536071;text-align:center}@media print{body{margin:20px}}
</style>
</head>
<body>
<header><div class="identity">${logo}<div><div class="brand">${escapeHtml(companyName)}</div><div>${title}</div>${companyDetails}</div></div><div class="meta"><strong>${escapeHtml(document.number)}</strong><br/>${dateLabel}<br/>${escapeHtml(status)}</div></header>
<section><strong>Cliente</strong><h2>${escapeHtml(document.client.name)}</h2></section>
<table><thead><tr><th>Concepto</th><th class="number">Cantidad</th><th class="number">Precio</th><th class="number">Impuesto</th><th class="number">Total</th></tr></thead><tbody>${items}</tbody></table>
<div class="summary"><div class="summary-row"><span>Base imponible</span><strong>${euro(document.subtotal)}</strong></div><div class="summary-row"><span>Impuestos</span><strong>${euro(document.tax_total)}</strong></div><div class="summary-row total"><span>Total</span><strong>${euro(document.total)}</strong></div>${paymentSummary}</div>
${document.notes ? `<div class="notes"><strong>Notas</strong><p>${escapeHtml(document.notes)}</p></div>` : ''}
${company?.document_footer ? `<div class="footer">${escapeHtml(company.document_footer)}</div>` : ''}
<script>window.onload=()=>{window.print()}</script>
</body></html>`)
  popup.document.close()
}
