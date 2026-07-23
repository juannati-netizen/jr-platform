import { describe, expect, it } from 'vitest'

import { expenseCategoryLabel, expenseStatusLabel } from './procurement'

describe('procurement labels', () => {
  it('translates expense values', () => {
    expect(expenseCategoryLabel('materials')).toBe('Materiales')
    expect(expenseStatusLabel('paid')).toBe('Pagado')
  })
})
