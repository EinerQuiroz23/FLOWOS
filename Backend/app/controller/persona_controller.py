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