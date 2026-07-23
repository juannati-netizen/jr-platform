import { Outlet, createRootRoute, createRoute, createRouter } from '@tanstack/react-router'

import { ProtectedLayout } from '../components/ProtectedLayout'
import { ClientsPage } from '../pages/ClientsPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ExpensesPage } from '../pages/ExpensesPage'
import { InvoicesPage } from '../pages/InvoicesPage'
import { LoginPage } from '../pages/LoginPage'
import { ProfilePage } from '../pages/ProfilePage'
import { ProfitabilityPage } from '../pages/ProfitabilityPage'
import { QuotesPage } from '../pages/QuotesPage'
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
    clientsRoute,
    workOrdersRoute,
    quotesRoute,
    invoicesRoute,
    suppliersRoute,
    expensesRoute,
    profitabilityRoute,
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
