# API

Base local:

```text
http://localhost:8000
```

## Estado del sistema

```http
GET /health
```

Devuelve estado del backend, proveedor LLM y modo de ejecución.

## Crear proyecto

```http
POST /projects
```

```json
{
  "name": "Noctra Coffee",
  "brand_voice": "Premium, cinematográfica y emocional",
  "audience": "Creativos que trabajan de noche",
  "constraints": "Evitar clichés de cafetería hipster"
}
```

## Crear campaña

```http
POST /projects/{project_id}/campaigns
```

```json
{
  "brief": "Lanzar una marca de café premium para sesiones de trabajo profundo.",
  "channels": ["instagram", "youtube", "landing", "email"],
  "language": "es",
  "tone": "premium",
  "human_review": false
}
```

## Leer campaña

```http
GET /campaigns/{campaign_id}
```

## Eventos de campaña

```http
GET /campaigns/{campaign_id}/events
```

## Renombrar campaña

```http
PATCH /campaigns/{campaign_id}
```

```json
{
  "title": "Lanzamiento Noctra Coffee"
}
```

## Eliminar campaña

```http
DELETE /campaigns/{campaign_id}
```

## Exportar

```http
GET /campaigns/{campaign_id}/export/json
GET /campaigns/{campaign_id}/export/markdown
GET /campaigns/{campaign_id}/export/pdf
GET /campaigns/{campaign_id}/export/zip
```
