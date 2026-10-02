from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.equipo_persona_schema import (
    EquipoPersonaCreate,
    EquipoPersonaUpdate,
    EquipoPersonaResponse
)

from app.services.equipo_persona_service import (
    EquipoPersonaService
)


router = APIRouter(
    prefix="/equipos-personas",
    tags=["Equipos - Personas"]
)


# ==========================================================
# OBTENER TODOS
# ==========================================================

@router.get(
    "/",
    response_model=List[EquipoPersonaResponse]
)
def obtener_registros(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = EquipoPersonaService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR EQUIPO
#
# IMPORTANTE: ESTA RUTA DEBE ESTAR ANTES DE /{id}
# ==========================================================

@router.get(
    "/equipo/{id_equipo}",
    response_model=List[EquipoPersonaResponse]
)
def obtener_por_equipo(
    id_equipo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = EquipoPersonaService(db)

    return service.obtener_por_equipo(
        id_equipo,
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR PERSONA
# ==========================================================

@router.get(
    "/persona/{id_persona}",
    response_model=List[EquipoPersonaResponse]
)
def obtener_por_persona(
    id_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = EquipoPersonaService(db)

    return service.obtener_por_persona(
        id_persona,
        usuario.id_organizacion
    )



@router.get(
    "/me",
    response_model=List[EquipoPersonaResponse]
)
def obtener_mis_equipos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = EquipoPersonaService(db)

    return service.obtener_por_persona(
        usuario.id_persona,
        usuario.id_organizacion
    )

# ==========================================================
# OBTENER POR ID
# ==========================================================

@router.get(
    "/{id_equipo_persona}",
    response_model=EquipoPersonaResponse
)
def obtener_registro_por_id(
    id_equipo_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = EquipoPersonaService(db)

    registro = service.obtener_por_id(
        id_equipo_persona,
        usuario.id_organizacion
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="El registro equipo-persona no existe."
        )

    return registro


# ==========================================================
# CREAR
# ==========================================================

@router.post(
    "/",
    response_model=EquipoPersonaResponse,
    status_code=201
)
def crear_registro(
    datos: EquipoPersonaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoPersonaService(db)

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
# ACTUALIZAR
# ==========================================================

@router.put(
    "/{id_equipo_persona}",
    response_model=EquipoPersonaResponse
)
def actualizar_registro(
    id_equipo_persona: int,
    datos: EquipoPersonaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoPersonaService(db)

    try:
        return service.actualizar(
            id_equipo_persona,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# FINALIZAR PARTICIPACIÓN
# ==========================================================

@router.patch(
    "/{id_equipo_persona}/finalizar",
    response_model=EquipoPersonaResponse
)
def finalizar_registro(
    id_equipo_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoPersonaService(db)

    try:
        return service.finalizar(
            id_equipo_persona,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )