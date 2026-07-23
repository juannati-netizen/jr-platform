# Seguridad

- No publiques contraseñas, tokens, cadenas `DATABASE_URL` ni archivos `.env`.
- No subas a GitHub copias `.dump`, `.backup` ni la carpeta `backups/`.
- Cambia `JWT_SECRET_KEY` y `INITIAL_ADMIN_PASSWORD` antes de desplegar.
- Utiliza HTTPS fuera del entorno local.
- Activa MFA en GitHub, Render y Supabase.
- Guarda las contraseñas en un gestor de contraseñas y no las reutilices.
- Mantén copias periódicas fuera del proveedor cloud.
- Los problemas de seguridad deben comunicarse de forma privada al propietario del repositorio.
