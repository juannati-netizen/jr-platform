import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { AppProviders } from './app/providers'
import './styles.css'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('No se encontró el elemento raíz del portal')
}

createRoot(rootElement).render(
  <StrictMode>
    <AppProviders />
  </StrictMode>,
)
