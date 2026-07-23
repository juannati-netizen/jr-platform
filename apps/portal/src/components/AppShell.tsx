import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined'
import AnalyticsOutlinedIcon from '@mui/icons-material/AnalyticsOutlined'
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import CorporateFareOutlinedIcon from '@mui/icons-material/CorporateFareOutlined'
import EngineeringOutlinedIcon from '@mui/icons-material/EngineeringOutlined'
import CreditCardOutlinedIcon from '@mui/icons-material/CreditCardOutlined'
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import HandshakeOutlinedIcon from '@mui/icons-material/HandshakeOutlined'
import KeyboardCommandKeyIcon from '@mui/icons-material/KeyboardCommandKey'
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import LocalOfferOutlinedIcon from '@mui/icons-material/LocalOfferOutlined'
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined'
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined'
import MenuIcon from '@mui/icons-material/Menu'
import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined'
import PeopleAltOutlinedIcon from '@mui/icons-material/PeopleAltOutlined'
import PushPinOutlinedIcon from '@mui/icons-material/PushPinOutlined'
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined'
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined'
import SearchIcon from '@mui/icons-material/Search'
import SettingsSuggestOutlinedIcon from '@mui/icons-material/SettingsSuggestOutlined'
import SyncAltOutlinedIcon from '@mui/icons-material/SyncAltOutlined'
import TrendingUpOutlinedIcon from '@mui/icons-material/TrendingUpOutlined'
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Collapse,
  Divider,
  Drawer,
  IconButton,
  InputAdornment,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  TextField,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material'
import { Link, Outlet, useRouterState } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { type ReactNode, useMemo, useState } from 'react'

import { getCompanyProfile } from '../api/settings'
import { useAuth } from '../auth/AuthContext'

const drawerWidth = 238
const globalBarHeight = 36
const workspaceBarHeight = 54

interface NavigationItem {
  label: string
  to: string
  icon: ReactNode
  visible: boolean
}

interface NavigationGroup {
  id: string
  label: string
  items: NavigationItem[]
}

export function AppShell() {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    overview: true,
    commercial: true,
    procurement: true,
    management: false,
    system: false,
  })
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const companyQuery = useQuery({
    queryKey: ['company-profile'],
    queryFn: getCompanyProfile,
    enabled: user?.role === 'admin',
    retry: false,
  })
  const workspaceName = companyQuery.data?.trade_name || companyQuery.data?.legal_name || 'JR ENERGY'

  const groups = useMemo<NavigationGroup[]>(
    () => [
      {
        id: 'overview',
        label: 'VISIÓN GENERAL',
        items: [
          { label: 'Centro de Control', to: '/', icon: <DashboardOutlinedIcon />, visible: true },
          {
            label: 'Analítica',
            to: '/profitability',
            icon: <AnalyticsOutlinedIcon />,
            visible: user?.role === 'admin',
          },
          {
            label: 'Centro de operaciones',
            to: '/work-orders',
            icon: <AssignmentOutlinedIcon />,
            visible: true,
          },
        ],
      },
      {
        id: 'commercial',
        label: 'COMERCIAL',
        items: [
          { label: 'CRM comercial', to: '/crm', icon: <HandshakeOutlinedIcon />, visible: true },
          { label: 'Clientes', to: '/clients', icon: <BusinessOutlinedIcon />, visible: true },
          {
            label: 'Presupuestos',
            to: '/quotes',
            icon: <RequestQuoteOutlinedIcon />,
            visible: true,
          },
          {
            label: 'Facturas y cobros',
            to: '/invoices',
            icon: <ReceiptLongOutlinedIcon />,
            visible: true,
          },
        ],
      },
      {
        id: 'procurement',
        label: 'COMPRAS Y ALMACÉN',
        items: [
          {
            label: 'Proveedores',
            to: '/suppliers',
            icon: <LocalShippingOutlinedIcon />,
            visible: user?.role === 'admin',
          },
          {
            label: 'Tarifario y materiales',
            to: '/catalog',
            icon: <LocalOfferOutlinedIcon />,
            visible: true,
          },
          {
            label: 'Almacén e inventario',
            to: '/inventory',
            icon: <Inventory2OutlinedIcon />,
            visible: true,
          },
          {
            label: 'Gastos y compras',
            to: '/expenses',
            icon: <CreditCardOutlinedIcon />,
            visible: user?.role === 'admin',
          },
        ],
      },
      {
        id: 'management',
        label: 'GESTIÓN',
        items: [
          {
            label: 'Rentabilidad',
            to: '/profitability',
            icon: <TrendingUpOutlinedIcon />,
            visible: user?.role === 'admin',
          },
          {
            label: 'Obras y expedientes',
            to: '/projects',
            icon: <EngineeringOutlinedIcon />,
            visible: true,
          },
          {
            label: 'Mi perfil',
            to: '/profile',
            icon: <AccountCircleOutlinedIcon />,
            visible: true,
          },
        ],
      },
      {
        id: 'system',
        label: 'SISTEMA',
        items: [
          {
            label: 'Configuración empresarial',
            to: '/settings',
            icon: <CorporateFareOutlinedIcon />,
            visible: user?.role === 'admin',
          },
          {
            label: 'Centro de migración',
            to: '/migration',
            icon: <SyncAltOutlinedIcon />,
            visible: user?.role === 'admin',
          },
          {
            label: 'Usuarios',
            to: '/users',
            icon: <PeopleAltOutlinedIcon />,
            visible: user?.role === 'admin',
          },
        ],
      },
    ],
    [user?.role],
  )

  const toggleGroup = (groupId: string) => {
    setOpenGroups((current) => ({ ...current, [groupId]: !current[groupId] }))
  }

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#121b24' }}>
      <Stack direction="row" alignItems="center" spacing={1.25} sx={{ px: 1.5, py: 1.3 }}>
        <Avatar
          variant="rounded"
          sx={{ width: 34, height: 34, bgcolor: '#263849', color: 'primary.light', fontWeight: 850 }}
        >
          JR
        </Avatar>
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Typography variant="subtitle2" fontWeight={800} noWrap>
            {workspaceName}
          </Typography>
          <Typography variant="caption" color="primary.light" noWrap display="block">
            ENTERPRISE WORKSPACE
          </Typography>
        </Box>
        <IconButton size="small" color="primary" aria-label="Contraer menú">
          <MenuIcon fontSize="small" />
        </IconButton>
      </Stack>
      <Divider />

      <Box sx={{ overflowY: 'auto', flex: 1, py: 0.75 }}>
        {groups.map((group) => {
          const visibleItems = group.items.filter((item) => item.visible)
          if (visibleItems.length === 0) return null
          const isOpen = openGroups[group.id] ?? false
          const containsActive = visibleItems.some((item) => item.to === pathname)

          return (
            <Box key={group.id} sx={{ mb: 0.4 }}>
              <ListItemButton
                onClick={() => toggleGroup(group.id)}
                dense
                sx={{
                  minHeight: 29,
                  px: 1.25,
                  color: containsActive ? 'text.primary' : 'text.secondary',
                }}
              >
                <ListItemText
                  primary={group.label}
                  primaryTypographyProps={{ fontSize: 11, fontWeight: 760, letterSpacing: '0.02em' }}
                />
                {isOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
              </ListItemButton>
              <Collapse in={isOpen} timeout="auto" unmountOnExit>
                <List disablePadding sx={{ px: 0.75 }}>
                  {visibleItems.map((item) => (
                    <ListItemButton
                      key={`${group.id}-${item.to}`}
                      component={Link}
                      to={item.to}
                      selected={pathname === item.to}
                      onClick={() => setMobileOpen(false)}
                      sx={{
                        minHeight: 31,
                        borderRadius: 1,
                        mb: 0.25,
                        px: 1,
                        '&.Mui-selected': {
                          bgcolor: 'primary.main',
                          color: '#fff',
                          '&:hover': { bgcolor: 'primary.dark' },
                          '& .MuiListItemIcon-root': { color: '#fff' },
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 28, color: 'text.secondary' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.label}
                        primaryTypographyProps={{ fontSize: 12.5, fontWeight: pathname === item.to ? 720 : 520 }}
                      />
                    </ListItemButton>
                  ))}
                </List>
              </Collapse>
            </Box>
          )
        })}
      </Box>

      <Box sx={{ p: 1.1 }}>
        <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 0.8, bgcolor: '#17222d' }}>
          <Stack direction="row" alignItems="center" spacing={0.8}>
            <Avatar sx={{ width: 29, height: 29, fontSize: 12, bgcolor: 'primary.dark' }}>
              {user?.full_name.charAt(0).toUpperCase()}
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="caption" fontWeight={750} display="block" noWrap>
                {user?.full_name}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" noWrap>
                {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
              </Typography>
            </Box>
            <Tooltip title="Cerrar sesión">
              <IconButton size="small" onClick={logout} aria-label="Cerrar sesión">
                <LogoutOutlinedIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 2,
          height: globalBarHeight,
          bgcolor: '#1a232c',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar variant="dense" sx={{ minHeight: `${globalBarHeight}px !important`, px: 1.25 }}>
          <Typography variant="caption" fontWeight={760} sx={{ mr: 3 }}>
            JR Electricista · JR Platform 0.9.0
          </Typography>
          <Stack direction="row" spacing={2.5} sx={{ display: { xs: 'none', md: 'flex' } }}>
            {['Espacio de trabajo', 'Apariencia', 'Perfiles', 'Herramientas'].map((item) => (
              <Typography key={item} variant="caption" color="text.secondary">
                {item}
              </Typography>
            ))}
          </Stack>
        </Toolbar>
      </AppBar>

      <AppBar
        position="fixed"
        sx={{
          top: globalBarHeight,
          height: workspaceBarHeight,
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: '#141d26',
          borderBottom: '1px solid',
          borderColor: 'divider',
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ minHeight: `${workspaceBarHeight}px !important`, px: 1.5, gap: 1 }}>
          <IconButton
            onClick={() => setMobileOpen((value) => !value)}
            sx={{ display: { md: 'none' } }}
            aria-label="Abrir navegación"
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Resumen ejecutivo
            </Typography>
            <Typography variant="subtitle2" fontWeight={760} noWrap>
              ESPACIO DE TRABAJO
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<SettingsSuggestOutlinedIcon />}
            sx={{ display: { xs: 'none', lg: 'inline-flex' } }}
          >
            IA y cumplimiento
          </Button>
          <Tooltip title="Fijar vista">
            <IconButton color="primary" sx={{ bgcolor: 'rgba(45,145,207,0.12)' }}>
              <PushPinOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<KeyboardCommandKeyIcon />}
            sx={{ display: { xs: 'none', lg: 'inline-flex' } }}
          >
            Comandos
          </Button>
          <Tooltip title="Notificaciones">
            <IconButton color="warning">
              <NotificationsNoneOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <TextField
            size="small"
            placeholder="Buscar en el ERP"
            sx={{ width: 205, display: { xs: 'none', sm: 'block' } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              top: globalBarHeight,
              height: `calc(100% - ${globalBarHeight}px)`,
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              top: globalBarHeight,
              height: `calc(100% - ${globalBarHeight}px)`,
              width: drawerWidth,
              boxSizing: 'border-box',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
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
          minWidth: 0,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          px: { xs: 1.5, sm: 2, lg: 2.5 },
          pb: 3,
          pt: `${globalBarHeight + workspaceBarHeight + 18}px`,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
