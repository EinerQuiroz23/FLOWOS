from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.equipo_schema import (
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse
)

from app.services.equipo_service import EquipoService


router = APIRouter(
    prefix="/equipos",
    tags=["Equipos"]
)


# ==========================================================
# OBTENER TODOS LOS EQUIPOS
# ==========================================================

@router.get(
    "/",
    response_model=List[EquipoResponse]
)
def obtener_equipos(
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
    service = EquipoService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER EQUIPOS DE UN PROYECTO
# ==========================================================

@router.get(
    "/proyecto/{id_proyecto}",
    response_model=List[EquipoResponse]
)
def obtener_por_proyecto(
    id_proyecto: int,
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
    service = EquipoService(db)

    return service.obtener_por_proyecto(
        id_proyecto,
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER EQUIPO POR ID
# ==========================================================

@router.get(
    "/{id_equipo}",
    response_model=EquipoResponse
)
def obtener_equipo_por_id(
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
    service = EquipoService(db)

    return service.obtener_por_id(
        id_equipo,
        usuario.id_organizacion
    )


# ==========================================================
# CREAR EQUIPO
# ==========================================================

@router.post(
    "/",
    response_model=EquipoResponse,
    status_code=201
)
def crear_equipo(
    datos: EquipoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoService(db)

    return service.crear(
        datos,
        usuario.id_organizacion
    )


# ==========================================================
# ACTUALIZAR EQUIPO
# ==========================================================

@router.put(
    "/{id_equipo}",
    response_model=EquipoResponse
)
def actualizar_equipo(
    id_equipo: int,
    datos: EquipoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoService(db)

    return service.actualizar(
        id_equipo,
        datos,
        usuario.id_organizacion
    )


# ==========================================================
# CAMBIAR ESTADO
# ==========================================================

@router.patch(
    "/{id_equipo}/estado",
    response_model=EquipoResponse
)
def cambiar_estado(
    id_equipo: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = EquipoService(db)

    return service.cambiar_estado(
        id_equipo,
        nuevo_estado,
        usuario.id_organizacion
    )