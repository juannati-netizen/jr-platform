import { Box, CircularProgress, Stack, Typography } from '@mui/material'

export function LoadingScreen() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background:
          'radial-gradient(circle at 50% 30%, rgba(45,145,207,0.2), transparent 35%), #111820',
      }}
    >
      <Stack alignItems="center" spacing={2}>
        <CircularProgress />
        <Typography color="text.secondary">Iniciando JR Enterprise Workspace…</Typography>
      </Stack>
    </Box>
  )
}
