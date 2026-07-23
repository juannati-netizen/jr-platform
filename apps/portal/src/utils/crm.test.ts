import { describe, expect, it } from 'vitest'

import { opportunityStageLabel } from './crm'

describe('opportunityStageLabel', () => {
  it('traduce una etapa del pipeline', () => {
    expect(opportunityStageLabel('negotiation')).toBe('Negociación')
  })
})
