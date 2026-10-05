from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.excepcions.base import FlowosException
from app.core.excepcions.handlers import flowos_exception_handler

from app.controller.persona_controller import router as persona_router
from app.controller.habilidad_controller import router as habilidad_router
from app.controller.nivel_habilidad_controller import router as nivel_habilidad_router
from app.controller.persona_habilidad_controller import router as persona_habilidad_router
from app.controller.cargo_controller import router as cargo_router
from app.controller.persona_cargo_controller import router as persona_cargo_router
from app.controller.proyecto_controller import router as proyecto_router
from app.controller.equipo_controller import router as equipo_router
from app.controller.equipo_persona_controller import router as equipo_persona_router
from app.controller.tarea_controller import router as tarea_router
from app.controller.tarea_habilidad_controller import router as tarea_habilidad_router
from app.controller.asignacion_tarea_controller import router as asignacion_tarea_router
from app.controller.auth_controller import router as auth_router
from app.controller.organizacion_controller import router as organizacion_router
from app.controller.rol_controller import router as rol_router
from app.controller.usuario_controller import router as usuario_router
from app.optima.controllers.optima_controller import router as optima_router
from app.controller.vista_controller import router as vista_router
from app.controller.mensaje_equipo_controller import router as mensaje_equipo_router
from app.controller.chat_ws import router as chat_ws_router 




def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


docs_enabled = settings.ENVIRONMENT.lower() != "production"


app = FastAPI(
    title="FLOWOS API",
    description="API de la plataforma inteligente de optimización organizacional FLOWOS.",
    version="1.0.0",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=_csv(settings.ALLOWED_HOSTS),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_csv(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    if settings.ENVIRONMENT.lower() == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


app.add_exception_handler(
    FlowosException,
    flowos_exception_handler,
)


app.include_router(persona_router)
app.include_router(habilidad_router)
app.include_router(nivel_habilidad_router)
app.include_router(persona_habilidad_router)
app.include_router(cargo_router)
app.include_router(persona_cargo_router)
app.include_router(proyecto_router)
app.include_router(equipo_router)
app.include_router(equipo_persona_router)
app.include_router(tarea_router)
app.include_router(tarea_habilidad_router)
app.include_router(asignacion_tarea_router)
app.include_router(optima_router)
app.include_router(auth_router)
app.include_router(organizacion_router)
app.include_router(rol_router)
app.include_router(usuario_router)
app.include_router(vista_router)
app.include_router(mensaje_equipo_router)
app.include_router(chat_ws_router)    


@app.get("/")
def root():
    return {
        "message": "FLOWOS API funcionando correctamente"
    }