import { beforeEach, describe, expect, it } from 'vitest'

import { tokenStore } from './token-store'

describe('tokenStore', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('guarda, recupera y elimina el token de sesión', () => {
    tokenStore.set('token-de-prueba')
    expect(tokenStore.get()).toBe('token-de-prueba')

    tokenStore.clear()
    expect(tokenStore.get()).toBeNull()
  })
})
