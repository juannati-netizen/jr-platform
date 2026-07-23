import { Box, CircularProgress, Typography } from '@mui/material'

export function LoadingScreen() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: 'linear-gradient(135deg, #f0fdfa 0%, #f8fafc 60%, #fff7ed 100%)',
      }}
    >
      <Box sx={{ textAlign: 'center' }}>
        <CircularProgress size={42} />
        <Typography sx={{ mt: 2 }} color="text.secondary">
          Preparando JR Platform…
        </Typography>
      </Box>
    </Box>
  )
}
