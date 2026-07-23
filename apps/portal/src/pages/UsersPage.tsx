import ManageAccountsOutlinedIcon from '@mui/icons-material/ManageAccountsOutlined'
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate } from '@tanstack/react-router'

import { ApiError } from '../api/client'
import type { UserRole } from '../api/types'
import { getUsers, updateUserRole } from '../api/users'
import { useAuth } from '../auth/AuthContext'
import { roleLabel } from '../utils/roles'

export function UsersPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: getUsers,
    enabled: user?.role === 'admin',
  })
  const roleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      updateUserRole(userId, role),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  if (user?.role !== 'admin') {
    return <Navigate to="/" />
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Gestión de usuarios</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Consulta las cuentas registradas y asigna permisos operativos.
        </Typography>
      </Box>

      {roleMutation.error && (
        <Alert severity="error">
          {roleMutation.error instanceof ApiError
            ? roleMutation.error.message
            : 'No se pudo actualizar el rol'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {usersQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando usuarios…</Typography>
            </Stack>
          )}

          {usersQuery.error && (
            <Alert severity="error" sx={{ m: 3 }}>
              {usersQuery.error instanceof ApiError
                ? usersQuery.error.message
                : 'No se pudo cargar la lista de usuarios'}
            </Alert>
          )}

          {usersQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Usuario</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Alta</TableCell>
                    <TableCell sx={{ width: 190 }}>Rol</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {usersQuery.data.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell>
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <ManageAccountsOutlinedIcon color="action" />
                          <Box>
                            <Typography fontWeight={700}>{item.full_name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {item.email}
                            </Typography>
                          </Box>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={item.is_active ? 'Activo' : 'Inactivo'}
                          color={item.is_active ? 'success' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{new Date(item.created_at).toLocaleDateString('es-ES')}</TableCell>
                      <TableCell>
                        <FormControl fullWidth size="small">
                          <InputLabel id={`role-${item.id}`}>Rol</InputLabel>
                          <Select
                            labelId={`role-${item.id}`}
                            label="Rol"
                            value={item.role}
                            disabled={item.id === user.id || roleMutation.isPending}
                            onChange={(event) =>
                              roleMutation.mutate({
                                userId: item.id,
                                role: event.target.value as UserRole,
                              })
                            }
                          >
                            <MenuItem value="user">{roleLabel('user')}</MenuItem>
                            <MenuItem value="admin">{roleLabel('admin')}</MenuItem>
                          </Select>
                        </FormControl>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Stack>
  )
}
