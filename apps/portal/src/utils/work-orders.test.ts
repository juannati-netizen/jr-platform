import { describe, expect, it } from 'vitest'

import {
  statusColor,
  workOrderPriorityLabel,
  workOrderStatusLabel,
} from './work-orders'

describe('work order labels', () => {
  it('translates operational values', () => {
    expect(workOrderStatusLabel('in_progress')).toBe('En curso')
    expect(workOrderPriorityLabel('urgent')).toBe('Urgente')
    expect(statusColor('completed')).toBe('success')
  })
})
