import {
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
} from '@tanstack/react-router'

import { ProtectedLayout } from '../components/ProtectedLayout'
import { DashboardPage } from '../pages/DashboardPage'
import { LoginPage } from '../pages/LoginPage'
import { ProfilePage } from '../pages/ProfilePage'
import { UsersPage } from '../pages/UsersPage'

const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

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
  protectedRoute.addChildren([dashboardRoute, profileRoute, usersRoute]),
])

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
