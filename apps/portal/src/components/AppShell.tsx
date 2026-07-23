import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined'
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import CreditCardOutlinedIcon from '@mui/icons-material/CreditCardOutlined'
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined'
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined'
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined'
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined'
import TrendingUpOutlinedIcon from '@mui/icons-material/TrendingUpOutlined'
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined'
import MenuIcon from '@mui/icons-material/Menu'
import PeopleAltOutlinedIcon from '@mui/icons-material/PeopleAltOutlined'
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material'
import { Link, Outlet, useRouterState } from '@tanstack/react-router'
import { useMemo, useState } from 'react'

import { useAuth } from '../auth/AuthContext'

const drawerWidth = 260

export function AppShell() {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const pathname = useRouterState({ select: (state) => state.location.pathname })

  const navigation = useMemo(
    () => [
      { label: 'Panel', to: '/', icon: <DashboardOutlinedIcon />, visible: true },
      { label: 'Clientes', to: '/clients', icon: <BusinessOutlinedIcon />, visible: true },
      { label: 'Trabajos', to: '/work-orders', icon: <AssignmentOutlinedIcon />, visible: true },
      { label: 'Presupuestos', to: '/quotes', icon: <RequestQuoteOutlinedIcon />, visible: true },
      { label: 'Facturas', to: '/invoices', icon: <ReceiptLongOutlinedIcon />, visible: true },
      {
        label: 'Proveedores',
        to: '/suppliers',
        icon: <LocalShippingOutlinedIcon />,
        visible: user?.role === 'admin',
      },
      {
        label: 'Gastos',
        to: '/expenses',
        icon: <CreditCardOutlinedIcon />,
        visible: user?.role === 'admin',
      },
      {
        label: 'Rentabilidad',
        to: '/profitability',
        icon: <TrendingUpOutlinedIcon />,
        visible: user?.role === 'admin',
      },
      { label: 'Mi perfil', to: '/profile', icon: <AccountCircleOutlinedIcon />, visible: true },
      {
        label: 'Usuarios',
        to: '/users',
        icon: <PeopleAltOutlinedIcon />,
        visible: user?.role === 'admin',
      },
    ],
    [user?.role],
  )

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ px: 2.5 }}>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Avatar sx={{ bgcolor: 'primary.main', fontWeight: 800 }}>JR</Avatar>
          <Box>
            <Typography variant="h6" lineHeight={1.1}>JR Platform</Typography>
            <Typography variant="caption" color="text.secondary">Portal operativo</Typography>
          </Box>
        </Stack>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1.5, py: 2 }}>
        {navigation.filter((item) => item.visible).map((item) => (
          <ListItemButton
            key={item.to}
            component={Link}
            to={item.to}
            selected={pathname === item.to}
            onClick={() => setMobileOpen(false)}
            sx={{ borderRadius: 2, mb: 0.5 }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        <Stack direction="row" alignItems="center" spacing={1.25}>
          <Avatar sx={{ width: 38, height: 38 }}>{user?.full_name.charAt(0).toUpperCase()}</Avatar>
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography variant="body2" fontWeight={700} noWrap>{user?.full_name}</Typography>
            <Typography variant="caption" color="text.secondary" noWrap display="block">
              {user?.email}
            </Typography>
          </Box>
          <Tooltip title="Cerrar sesión">
            <IconButton onClick={logout} aria-label="Cerrar sesión"><LogoutOutlinedIcon /></IconButton>
          </Tooltip>
        </Stack>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{
          borderBottom: '1px solid',
          borderColor: 'divider',
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            onClick={() => setMobileOpen((value) => !value)}
            sx={{ mr: 2, display: { md: 'none' } }}
            aria-label="Abrir navegación"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" color="text.primary">Centro de control</Typography>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          p: { xs: 2, sm: 3, lg: 4 },
          pt: { xs: 11, sm: 12 },
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
