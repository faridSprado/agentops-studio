# Arquitectura

Multimedia AgentOps Studio usa una arquitectura cliente-servidor orientada a flujos de IA.

## Componentes

```text
Frontend Next.js
  -> API FastAPI
    -> Orquestador de agentes
      -> Proveedor LLM
      -> Persistencia SQLite
      -> Exportador de entregables
```

## Frontend

El frontend está construido con Next.js, React, TypeScript y Tailwind CSS.

Responsabilidades:

- capturar el brief;
- mostrar estado del sistema;
- visualizar el timeline de agentes;
- renderizar la campaña final;
- gestionar historial local;
- consumir endpoints de exportación.

## Backend

El backend está construido con FastAPI y Python.

Responsabilidades:

- validar entradas;
- limitar tamaño de requests;
- ejecutar el flujo de agentes;
- manejar errores del proveedor LLM;
- guardar campañas;
- exportar resultados.

## Flujo de agentes

```text
Normalizer
-> Research
-> Strategy
-> Copy
-> Storyboard
-> Visual Direction
-> Execution Plan
-> KPIs
-> Brand Review
-> Evaluation
-> Assembler
```

## Persistencia

En desarrollo local usa SQLite. Para producción se puede cambiar `DATABASE_URL` a PostgreSQL.

## Resiliencia

El backend intenta reparar respuestas JSON inválidas o truncadas. Si no puede recuperar toda la respuesta, genera una salida de respaldo para que el flujo pueda continuar.

## Seguridad básica

- CORS configurable por entorno.
- Límite de tamaño por request.
- Sanitización de entradas.
- Validación de canales.
- Headers de seguridad.
- Variables sensibles fuera del repositorio.
