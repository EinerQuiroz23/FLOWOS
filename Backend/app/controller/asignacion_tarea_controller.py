from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.asignacion_tarea_schema import (
    AsignacionTareaCreate,
    AsignacionTareaUpdate,
    AsignacionTareaResponse
)

from app.services.asignacion_tarea_service import (
    AsignacionTareaService
)


router = APIRouter(
    prefix="/asignaciones-tareas",
    tags=["Asignaciones de Tareas"]
)


# ==========================================================
# OBTENER TODAS
# ==========================================================

@router.get(
    "/",
    response_model=List[AsignacionTareaResponse]
)
def obtener_asignaciones(
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
    service = AsignacionTareaService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR TAREA
#
# IMPORTANTE: ANTES DE /{id_asignacion}
# ==========================================================

@router.get(
    "/tarea/{id_tarea}",
    response_model=List[AsignacionTareaResponse]
)
def obtener_por_tarea(
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
    service = AsignacionTareaService(db)

    return service.obtener_por_tarea(
        id_tarea,
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR EQUIPO-PERSONA
# ==========================================================

@router.get(
    "/equipo-persona/{id_equipo_persona}",
    response_model=List[AsignacionTareaResponse]
)
def obtener_por_equipo_persona(
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
    service = AsignacionTareaService(db)

    return service.obtener_por_equipo_persona(
        id_equipo_persona,
        usuario.id_organizacion
    )


# ==========================================================
# OBTENER POR ID
# ==========================================================

@router.get(
    "/{id_asignacion}",
    response_model=AsignacionTareaResponse
)
def obtener_asignacion_por_id(
    id_asignacion: int,
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
    service = AsignacionTareaService(db)

    asignacion = service.obtener_por_id(
        id_asignacion,
        usuario.id_organizacion
    )

    if asignacion is None:
        raise HTTPException(
            status_code=404,
            detail="La asignación no existe."
        )

    return asignacion


# ==========================================================
# CREAR
# ==========================================================

@router.post(
    "/",
    response_model=AsignacionTareaResponse,
    status_code=201
)
def crear_asignacion(
    datos: AsignacionTareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = AsignacionTareaService(db)

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
    "/{id_asignacion}",
    response_model=AsignacionTareaResponse
)
def actualizar_asignacion(
    id_asignacion: int,
    datos: AsignacionTareaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = AsignacionTareaService(db)

    try:
        return service.actualizar(
            id_asignacion,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# CAMBIAR ESTADO
# ==========================================================

@router.patch(
    "/{id_asignacion}/estado",
    response_model=AsignacionTareaResponse
)
def cambiar_estado(
    id_asignacion: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = AsignacionTareaService(db)

    try:
        return service.cambiar_estado(
            id_asignacion,
            nuevo_estado,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )