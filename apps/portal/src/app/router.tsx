import { Outlet, createRootRoute, createRoute, createRouter } from '@tanstack/react-router'

import { ProtectedLayout } from '../components/ProtectedLayout'
import { CatalogPage } from '../pages/CatalogPage'
import { ClientsPage } from '../pages/ClientsPage'
import { CrmPage } from '../pages/CrmPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ExpensesPage } from '../pages/ExpensesPage'
import { InventoryPage } from '../pages/InventoryPage'
import { InvoicesPage } from '../pages/InvoicesPage'
import { LoginPage } from '../pages/LoginPage'
import { MigrationPage } from '../pages/MigrationPage'
import { ProfilePage } from '../pages/ProfilePage'
import { ProfitabilityPage } from '../pages/ProfitabilityPage'
import { ProjectsPage } from '../pages/ProjectsPage'
import { QuotesPage } from '../pages/QuotesPage'
import { SettingsPage } from '../pages/SettingsPage'
import { SuppliersPage } from '../pages/SuppliersPage'
import { UsersPage } from '../pages/UsersPage'
import { WorkOrdersPage } from '../pages/WorkOrdersPage'

const rootRoute = createRootRoute({ component: () => <Outlet /> })

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
})

const protectedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'protected',
  component: ProtectedLayout,
})

const dashboardRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/',
  component: DashboardPage,
})

const catalogRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/catalog',
  component: CatalogPage,
})

const inventoryRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/inventory',
  component: InventoryPage,
})

const crmRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/crm',
  component: CrmPage,
})

const projectsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/projects',
  component: ProjectsPage,
})

const clientsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/clients',
  component: ClientsPage,
})

const workOrdersRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/work-orders',
  component: WorkOrdersPage,
})

const quotesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/quotes',
  component: QuotesPage,
})

const invoicesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/invoices',
  component: InvoicesPage,
})

const suppliersRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/suppliers',
  component: SuppliersPage,
})

const expensesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/expenses',
  component: ExpensesPage,
})

const profitabilityRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/profitability',
  component: ProfitabilityPage,
})

const migrationRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/migration',
  component: MigrationPage,
})

const settingsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/settings',
  component: SettingsPage,
})

const profileRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/profile',
  component: ProfilePage,
})

const usersRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/users',
  component: UsersPage,
})

const routeTree = rootRoute.addChildren([
  loginRoute,
  protectedRoute.addChildren([
    dashboardRoute,
    crmRoute,
    projectsRoute,
    clientsRoute,
    catalogRoute,
    inventoryRoute,
    workOrdersRoute,
    quotesRoute,
    invoicesRoute,
    suppliersRoute,
    expensesRoute,
    profitabilityRoute,
    migrationRoute,
    settingsRoute,
    profileRoute,
    usersRoute,
  ]),
])

export const router = createRouter({ routeTree, defaultPreload: 'intent' })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
