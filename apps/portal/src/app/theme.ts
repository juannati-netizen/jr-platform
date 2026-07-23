import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0f766e',
      dark: '#115e59',
      light: '#14b8a6',
    },
    secondary: {
      main: '#d97706',
    },
    background: {
      default: '#f3f4f6',
      paper: '#ffffff',
    },
  },
  shape: {
    borderRadius: 12,
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif',
    h4: {
      fontWeight: 800,
    },
    h5: {
      fontWeight: 750,
    },
    h6: {
      fontWeight: 700,
    },
    button: {
      fontWeight: 700,
      textTransform: 'none',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #e5e7eb',
          boxShadow: '0 12px 32px rgba(15, 23, 42, 0.06)',
        },
      },
    },
  },
})
