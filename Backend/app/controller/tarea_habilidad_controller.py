from typing import List
from sqlalchemy import text


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.tarea_habilidad_schema import (
    TareaHabilidadCreate,
    TareaHabilidadUpdate,
    TareaHabilidadResponse
)

from app.services.tarea_habilidad_service import (
    TareaHabilidadService
)


router = APIRouter(
    prefix="/tareas-habilidades",
    tags=["Tareas - Habilidades"]
)


# =========================================================
# CONSULTAR POR TAREA
# =========================================================

@router.get(
    "/tarea/{id_tarea}",
    response_model=List[TareaHabilidadResponse]
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
    service = TareaHabilidadService(db)

    return service.obtener_por_tarea(
        id_tarea,
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR POR HABILIDAD
# =========================================================

@router.get(
    "/habilidad/{id_habilidad}",
    response_model=List[TareaHabilidadResponse]
)
def obtener_por_habilidad(
    id_habilidad: int,
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
    service = TareaHabilidadService(db)

    return service.obtener_por_habilidad(
        id_habilidad,
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR TODOS
# =========================================================

@router.get(
    "/",
    response_model=List[TareaHabilidadResponse]
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
    service = TareaHabilidadService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR POR ID
# =========================================================

@router.get(
    "/{id_tarea_habilidad}",
    response_model=TareaHabilidadResponse
)
def obtener_registro_por_id(
    id_tarea_habilidad: int,
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
    service = TareaHabilidadService(db)

    registro = service.obtener_por_id(
        id_tarea_habilidad,
        usuario.id_organizacion
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="El registro tarea-habilidad no existe."
        )

    return registro


# =========================================================
# CREAR
# =========================================================

@router.post(
    "/",
    response_model=TareaHabilidadResponse,
    status_code=201
)
def crear_registro(
    datos: TareaHabilidadCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = TareaHabilidadService(db)

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


# =========================================================
# ACTUALIZAR
# =========================================================

@router.put(
    "/{id_tarea_habilidad}",
    response_model=TareaHabilidadResponse
)
def actualizar_registro(
    id_tarea_habilidad: int,
    datos: TareaHabilidadUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = TareaHabilidadService(db)

    try:
        return service.actualizar(
            id_tarea_habilidad,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.delete("/{id_tarea_habilidad}", status_code=204)
def eliminar_tarea_habilidad(
    id_tarea_habilidad: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "SECRETARIO")
    ),
):
    fila = db.execute(
        text(
            """
            DELETE FROM tarea_habilidad AS th
            USING tarea AS t, proyecto AS p
            WHERE th.id_tarea_habilidad = :id
              AND t.id_tarea = th.id_tarea
              AND p.id_proyecto = t.id_proyecto
              AND p.id_organizacion = :org
            RETURNING th.id_tarea_habilidad
            """
        ),
        {"id": id_tarea_habilidad, "org": usuario.id_organizacion},
    ).first()

    if not fila:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail="No se encontró esa habilidad en la tarea",
        )

    db.commit()