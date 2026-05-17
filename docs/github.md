# Publicar en GitHub

## 1. Revisar archivos sensibles

Antes de subir, confirma que no existan:

```text
.env
apps/api/.env
apps/web/.env.local
.venv/
node_modules/
.next/
agentops.db
```

## 2. Inicializar Git

```bash
git init
git add .
git status
```

Revisa que no aparezcan credenciales ni archivos generados.

## 3. Primer commit

```bash
git commit -m "Initial release: Multimedia AgentOps Studio"
```

## 4. Crear repo en GitHub

Nombre recomendado:

```text
multimedia-agentops-studio
```

Descripción sugerida:

```text
Full-stack multi-agent AI platform for generating multimedia campaigns from creative briefs.
```

Topics sugeridos:

```text
ai, agents, multi-agent, fastapi, nextjs, typescript, python, groq, llm, creative-ai, portfolio-project
```

## 5. Subir

```bash
git branch -M main
git remote add origin https://github.com/TU-USUARIO/multimedia-agentops-studio.git
git push -u origin main
```

## 6. Después de subir

Agrega al repo:

- capturas en `docs/screenshots/`;
- video demo en la descripción del README o en LinkedIn;
- link del proyecto en tu CV y portfolio.
