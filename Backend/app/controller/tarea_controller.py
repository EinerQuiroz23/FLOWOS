from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.tarea_schema import (
    TareaCreate,
    TareaUpdate,
    TareaResponse
)

from app.services.tarea_service import TareaService


router = APIRouter(
    prefix="/tareas",
    tags=["Tareas"]
)


# ==========================================================
# OBTENER TODAS
# ==========================================================

@router.get(
    "/",
    response_model=List[TareaResponse]
)
def obtener_tareas(
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
    service = TareaService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR PROYECTO
#
# IMPORTANTE:
# ESTA RUTA VA ANTES DE /{id_tarea}
# ==========================================================

@router.get(
    "/proyecto/{id_proyecto}",
    response_model=List[TareaResponse]
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
    service = TareaService(db)

    return service.obtener_por_proyecto(
        id_proyecto,
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR ID
# ==========================================================

@router.get(
    "/{id_tarea}",
    response_model=TareaResponse
)
def obtener_tarea_por_id(
    id_tarea: int,
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
    service = TareaService(db)

    return service.obtener_por_id(
        id_tarea,
        usuario.id_organizacion
    )


# ==========================================================
# CREAR
# ==========================================================

@router.post(
    "/",
    response_model=TareaResponse,
    status_code=201
)
def crear_tarea(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = TareaService(db)

    return service.crear(
        datos,
        usuario.id_organizacion
    )


# ==========================================================
# ACTUALIZAR
# ==========================================================

@router.put(
    "/{id_tarea}",
    response_model=TareaResponse
)
def actualizar_tarea(
    id_tarea: int,
    datos: TareaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = TareaService(db)

    return service.actualizar(
        id_tarea,
        datos,
        usuario.id_organizacion
    )


# ==========================================================
# CAMBIAR ESTADO
# ==========================================================

@router.patch(
    "/{id_tarea}/estado",
    response_model=TareaResponse
)
def cambiar_estado(
    id_tarea: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = TareaService(db)

    return service.cambiar_estado(
        id_tarea,
        nuevo_estado,
        usuario.id_organizacion
    )