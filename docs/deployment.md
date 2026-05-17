# Deploy

## Opción recomendada para portfolio

Para un repositorio público, la opción más segura es publicar el código, capturas y video demo. La ejecución con IA real puede hacerse localmente usando tu propia API key.

## Demo pública sin consumo de tokens

Puedes desplegar el backend con:

```env
LLM_PROVIDER=mock
MOCK_MODE=true
```

Así la interfaz funciona sin exponer credenciales ni consumir tokens.

## Frontend

Opciones recomendadas:

- Vercel;
- Netlify;
- Docker.

Variable necesaria:

```env
NEXT_PUBLIC_API_URL=https://tu-api.com
```

## Backend

Opciones recomendadas:

- Render;
- Railway;
- Fly.io;
- Cloud Run;
- Docker en VPS.

Variables principales:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
MOCK_MODE=false
DATABASE_URL=postgresql+psycopg://user:password@host:5432/db
CORS_ORIGINS=https://tu-frontend.com
MAX_OUTPUT_TOKENS=1200
```

## Docker local

```bash
cp .env.example .env
docker compose up --build
```

## Notas de seguridad

- No subas `.env`.
- No pongas API keys en el frontend.
- Limita `CORS_ORIGINS` al dominio real.
- Usa `MOCK_MODE=true` si la demo será pública.
- Revisa logs y consumo de tokens del proveedor.
