import { describe, expect, it } from 'vitest'

import { euro, invoiceStatusLabel, paymentMethodLabel, quoteStatusLabel } from './finance'

describe('financial labels', () => {
  it('translates financial values', () => {
    expect(quoteStatusLabel('accepted')).toBe('Aceptado')
    expect(invoiceStatusLabel('partial')).toBe('Cobro parcial')
    expect(paymentMethodLabel('bank_transfer')).toBe('Transferencia')
  })

  it('formats euro amounts', () => {
    expect(euro('123.45')).toContain('123,45')
  })
})
