from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Response

from app.core.config import get_settings
from app.core.db import init_db
from app.core.files import ensure_dirs
from app.routes import campaigns, health, projects, ws

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.2.1",
    description="Orquestación multiagente para campañas multimedia",
)


@app.middleware("http")
async def request_guard(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.max_request_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": "La solicitud es demasiado grande. Reduce el brief o el archivo adjunto.", "status_code": 413},
        )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "status_code": exc.status_code})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "status_code": 422})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    message = "Ocurrió un error interno. Revisa los logs del backend."
    if not settings.is_production:
        message = str(exc)[:600]
    return JSONResponse(status_code=500, content={"detail": message, "status_code": 500})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False, response_model=None)
def root() -> dict[str, object]:
    return {
        "status": "ok",
        "name": "Multimedia AgentOps Studio API",
        "message": "API running",
        "health": "/health",
        "docs": "/docs"
    }


@app.head("/", include_in_schema=False)
def root_head() -> Response:
    return Response(status_code=204)

@app.get("/docs-link", include_in_schema=False)
def docs_link() -> RedirectResponse:
    return RedirectResponse(url="/docs")

@app.on_event("startup")
def startup() -> None:
    ensure_dirs()
    init_db()


app.include_router(health.router)
app.include_router(projects.router)
app.include_router(campaigns.router)
app.include_router(ws.router)
