from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.persona_schema import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse
)

from app.services.persona_service import PersonaService

from sqlalchemy import func, select
from app.models.equipo_persona_model import EquipoPersona
from app.models.asignacion_tarea_model import AsignacionTarea
from app.models.persona_model import Persona

router = APIRouter(
    prefix="/personas",
    tags=["Personas"]
)


# ==========================================================
# OBTENER TODAS LAS PERSONAS
# ==========================================================

@router.get(
    "/",
    response_model=List[PersonaResponse]
)
def obtener_personas(
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )




@router.get(
    "/me",
    response_model=PersonaResponse
)
def obtener_mi_persona(
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    persona = service.obtener_por_id(
        usuario.id_persona,
        usuario.id_organizacion
    )

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró tu perfil de persona."
        )

    return persona

@router.get("/{id_persona}/ocupacion")
def obtener_ocupacion(
    id_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    persona = (
        db.query(Persona)
        .filter(
            Persona.id_persona == id_persona,
            Persona.id_organizacion == usuario.id_organizacion,
        )
        .first()
    )
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    consulta = (
        select(
            func.coalesce(func.sum(AsignacionTarea.dedicacion), 0).label(
                "ocupacion"
            )
        )
        .select_from(EquipoPersona)
        .join(
            AsignacionTarea,
            AsignacionTarea.id_equipo_persona
            == EquipoPersona.id_equipo_persona,
        )
        .where(
            EquipoPersona.id_persona == id_persona,
            AsignacionTarea.estado.in_(["ASIGNADA", "EN_PROGRESO"]),
        )
    )
    ocupacion = float(db.execute(consulta).scalar() or 0)
    capacidad = float(persona.capacidad_horas_semana or 0)
    disponibilidad = max(0.0, 100.0 - ocupacion)

    return {
        "id_persona": id_persona,
        "capacidad_horas_semana": capacidad,
        "ocupacion_pct": round(ocupacion, 2),
        "disponibilidad_pct": round(disponibilidad, 2),
    }
# ==========================================================
# OBTENER PERSONA POR ID
# ==========================================================

@router.get(
    "/{id_persona}",
    response_model=PersonaResponse
)
def obtener_persona_por_id(
    id_persona: int,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    persona = service.obtener_por_id(
        id_persona,
        usuario.id_organizacion
    )

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="La persona no existe."
        )

    return persona


# ==========================================================
# CREAR PERSONA
# ==========================================================

@router.post(
    "/",
    response_model=PersonaResponse,
    status_code=201
)
def crear_persona(
    datos: PersonaCreate,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    try:

        return service.crear(
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# ACTUALIZAR PERSONA
# ==========================================================

@router.put(
    "/{id_persona}",
    response_model=PersonaResponse
)
def actualizar_persona(
    id_persona: int,
    datos: PersonaUpdate,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    try:

        return service.actualizar(
            id_persona,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# ACTIVAR PERSONA
# ==========================================================

@router.patch(
    "/{id_persona}/activar",
    response_model=PersonaResponse
)
def activar_persona(
    id_persona: int,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    try:

        return service.activar(
            id_persona,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# DESACTIVAR PERSONA
# ==========================================================

@router.patch(
    "/{id_persona}/desactivar",
    response_model=PersonaResponse
)
def desactivar_persona(
    id_persona: int,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)

    try:

        return service.desactivar(
            id_persona,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )