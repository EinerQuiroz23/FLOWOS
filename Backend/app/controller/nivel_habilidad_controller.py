from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role, require_role

from app.models.usuario_model import Usuario

from app.schemas.nivel_habilidad_schema import (
    NivelHabilidadCreate,
    NivelHabilidadUpdate,
    NivelHabilidadResponse
)

from app.services.nivel_habilidad_service import NivelHabilidadService


router = APIRouter(
    prefix="/niveles-habilidad",
    tags=["Niveles de Habilidad"]
)


# ==========================================================
# OBTENER TODOS LOS NIVELES
# ==========================================================

@router.get(
    "/",
    response_model=List[NivelHabilidadResponse]
)
def obtener_niveles(
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
    service = NivelHabilidadService(db)

    return service.obtener_todos()


# ==========================================================
# OBTENER NIVEL POR ID
# ==========================================================

@router.get(
    "/{id_nivel}",
    response_model=NivelHabilidadResponse
)
def obtener_nivel_por_id(
    id_nivel: int,
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
    service = NivelHabilidadService(db)

    nivel = service.obtener_por_id(
        id_nivel
    )

    if nivel is None:
        raise HTTPException(
            status_code=404,
            detail="El nivel de habilidad no existe."
        )

    return nivel


# ==========================================================
# CREAR NIVEL
# ==========================================================

@router.post(
    "/",
    response_model=NivelHabilidadResponse,
    status_code=201
)
def crear_nivel(
    datos: NivelHabilidadCreate,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = NivelHabilidadService(db)

    try:

        return service.crear(
            datos
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# ACTUALIZAR NIVEL
# ==========================================================

@router.put(
    "/{id_nivel}",
    response_model=NivelHabilidadResponse
)
def actualizar_nivel(
    id_nivel: int,
    datos: NivelHabilidadUpdate,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = NivelHabilidadService(db)

    try:

        return service.actualizar(
            id_nivel,
            datos
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )