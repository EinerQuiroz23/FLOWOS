from typing import List 
from sqlalchemy import text 



from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.tarea_schema import (
    TareaCreate,
    TareaUpdate,
    TareaResponse, 
    MiTareaResponse
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

#=========================================================
# OBTENER MIS TAREAS    

@router.get(
    "/mias",
    response_model=List[MiTareaResponse]
)
def obtener_mis_tareas(
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

    return service.obtener_mias(
        id_persona=usuario.id_persona,
        id_organizacion=usuario.id_organizacion
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



@router.put("/{id_tarea}")
def actualizar_tarea(
    id_tarea: int,
    datos: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "SECRETARIO")
    ),
):
    permitidos = {
        "nombre",
        "descripcion",
        "prioridad",
        "horas_estimadas",
        "fecha_inicio",
        "fecha_limite",
        "estado",
    }
    cambios = {k: v for k, v in datos.items() if k in permitidos}
    if not cambios:
        raise HTTPException(status_code=400, detail="Nada para actualizar")

    sets = ", ".join(f"{campo} = :{campo}" for campo in cambios)
    fila = db.execute(
        text(
            f"""
            UPDATE tarea AS t
            SET {sets}
            FROM proyecto AS p
            WHERE t.id_tarea = :id
              AND p.id_proyecto = t.id_proyecto
              AND p.id_organizacion = :org
            RETURNING t.id_tarea, t.nombre, t.descripcion, t.prioridad,
                      t.horas_estimadas, t.fecha_inicio, t.fecha_limite,
                      t.estado, t.id_proyecto, t.id_equipo
            """
        ),
        {**cambios, "id": id_tarea, "org": usuario.id_organizacion},
    ).mappings().first()

    if not fila:
        db.rollback()
        raise HTTPException(status_code=404, detail="La tarea no existe")

    db.commit()
    return dict(fila)


@router.delete("/{id_tarea}", status_code=204)
def eliminar_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "SECRETARIO")
    ),
):
    fila = db.execute(
        text(
            """
            DELETE FROM tarea AS t
            USING proyecto AS p
            WHERE t.id_tarea = :id
              AND p.id_proyecto = t.id_proyecto
              AND p.id_organizacion = :org
            RETURNING t.id_tarea
            """
        ),
        {"id": id_tarea, "org": usuario.id_organizacion},
    ).first()

    if not fila:
        db.rollback()
        raise HTTPException(status_code=404, detail="La tarea no existe")

    db.commit()