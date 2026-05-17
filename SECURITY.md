# Seguridad

## Variables sensibles

No subas claves reales al repositorio.

Archivos que deben permanecer locales:

```text
.env
.env.local
apps/api/.env
apps/web/.env.local
```

## API keys

Si una API key se publica por error, revócala inmediatamente desde el panel del proveedor y genera una nueva.

## Demo pública

Para demos públicas se recomienda usar:

```env
LLM_PROVIDER=mock
MOCK_MODE=true
```

Así evitas exponer credenciales o consumir tokens por uso externo.
