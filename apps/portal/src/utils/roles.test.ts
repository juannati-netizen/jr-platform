import { describe, expect, it } from 'vitest'

import { roleLabel } from './roles'

describe('roleLabel', () => {
  it('traduce los roles de la API', () => {
    expect(roleLabel('admin')).toBe('Administrador')
    expect(roleLabel('user')).toBe('Usuario')
    expect(roleLabel(undefined)).toBe('Sin rol')
  })
})
