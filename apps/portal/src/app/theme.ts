import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2d91cf',
      dark: '#1f6f9f',
      light: '#68b8ea',
    },
    secondary: {
      main: '#f2b84b',
    },
    success: {
      main: '#39b66d',
    },
    warning: {
      main: '#f2b84b',
    },
    error: {
      main: '#e85d68',
    },
    background: {
      default: '#111820',
      paper: '#1b2530',
    },
    divider: '#344250',
    text: {
      primary: '#eaf2f8',
      secondary: '#9fb2c2',
    },
  },
  shape: {
    borderRadius: 7,
  },
  typography: {
    fontFamily: 'Inter, "Segoe UI", ui-sans-serif, system-ui, sans-serif',
    fontSize: 13,
    h4: {
      fontWeight: 750,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 720,
    },
    h6: {
      fontWeight: 700,
    },
    button: {
      fontWeight: 650,
      textTransform: 'none',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: '#536577 #111820',
          '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
            width: 10,
            height: 10,
          },
          '&::-webkit-scrollbar-track, & *::-webkit-scrollbar-track': {
            background: '#111820',
          },
          '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
            background: '#536577',
            borderRadius: 6,
            border: '2px solid #111820',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          minHeight: 32,
          borderRadius: 5,
          paddingInline: 14,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #344250',
          boxShadow: 'none',
          backgroundColor: '#1b2530',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: '#141d26',
          '& fieldset': {
            borderColor: '#3b4a59',
          },
          '&:hover fieldset': {
            borderColor: '#5a6f82',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          backgroundColor: '#141d26',
          color: '#d9e7f1',
          fontWeight: 700,
        },
        root: {
          borderColor: '#344250',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          border: '1px solid #344250',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 5,
        },
      },
    },
  },
})
