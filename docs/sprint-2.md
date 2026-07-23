# Sprint 2 — Portal web

## Objetivo

Entregar una interfaz web operativa conectada a la identidad construida en Sprint 1.

## Arquitectura

- `apps/api`: API FastAPI y autenticación JWT.
- `apps/portal`: React, TypeScript y Vite.
- `deployment/portal`: imágenes Docker de desarrollo y producción.
- Vite reenvía `/api` al contenedor de FastAPI durante el desarrollo.
- Nginx sirve la compilación y reenvía `/api` en producción.

## Rutas

- `/login`: acceso al portal.
- `/`: panel protegido.
- `/profile`: perfil del usuario autenticado.
- `/users`: gestión de roles, exclusiva para administradores.

## Seguridad

El token se conserva en `sessionStorage`, por lo que se elimina al cerrar la sesión del navegador. Esta solución es adecuada para el entorno de desarrollo actual. Antes de producción se migrará a una estrategia con cookies HttpOnly y protección CSRF.

## Criterios de aceptación

- El administrador puede iniciar sesión.
- Un visitante no autenticado es redirigido a `/login`.
- El panel muestra los datos de la cuenta actual.
- Un administrador puede consultar usuarios y cambiar roles.
- Un usuario estándar no puede acceder a la administración.
- Backend y frontend superan sus comprobaciones de CI.
