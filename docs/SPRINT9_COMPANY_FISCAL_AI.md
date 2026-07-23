# Sprint 9 — Empresa, ejercicios fiscales, VERI*FACTU e IA

## Alcance

El sprint incorpora un centro de configuración empresarial para administradores:

- Razón social, nombre comercial y NIF/CIF.
- Dirección, contacto, IBAN, moneda, zona horaria y series documentales.
- Apertura, cierre y reapertura de ejercicios fiscales.
- Lista de preparación técnica para VERI*FACTU.
- Configuración no sensible del Centro de IA.
- Registro de cambios de configuración.

## Seguridad de IA

Las claves no se almacenan en PostgreSQL. Se leen desde:

```env
AI_API_KEY=
AI_BASE_URL=
```

El portal solo muestra si están configuradas.

## VERI*FACTU

El panel es una herramienta de preparación y control. Esta versión no:

- Certifica el cumplimiento.
- Firma una declaración responsable.
- Envía registros reales a la AEAT.
- Sustituye la revisión fiscal o técnica correspondiente.

La activación real requerirá implementar y validar los registros de facturación, encadenamiento,
QR, remisión, gestión de errores y declaración responsable conforme a la normativa aplicable.
