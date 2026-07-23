# Sprint 1: autenticación y usuarios

## Flujo de uso

1. La API ejecuta las migraciones.
2. Se crea el administrador inicial configurado en `.env`.
3. Los usuarios pueden registrarse en `/api/v1/auth/register`.
4. El inicio de sesión devuelve un token JWT.
5. El token se envía como `Authorization: Bearer <token>`.
6. Los endpoints administrativos validan el rol `admin`.

## Decisiones técnicas

- Los roles se almacenan como texto para mantener compatibilidad entre PostgreSQL y SQLite.
- Las contraseñas se almacenan con PBKDF2-SHA256, sal aleatoria y 600.000 iteraciones.
- El JWT contiene el identificador del usuario en `sub` y una fecha de expiración.
- La API nunca devuelve el hash de la contraseña.
