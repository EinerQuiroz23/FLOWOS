from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.proyecto_schema import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse
)

from app.services.proyecto_service import ProyectoService


router = APIRouter(
    prefix="/proyectos",
    tags=["Proyectos"]
)


@router.get(
    "/",
    response_model=List[ProyectoResponse]
)
def obtener_proyectos(
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
    service = ProyectoService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


@router.get(
    "/{id_proyecto}",
    response_model=ProyectoResponse
)
def obtener_proyecto_por_id(
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
    service = ProyectoService(db)

    proyecto = service.obtener_por_id(
        id_proyecto,
        usuario.id_organizacion
    )

    if proyecto is None:
        raise HTTPException(
            status_code=404,
            detail="El proyecto no existe."
        )

    return proyecto


@router.post(
    "/",
    response_model=ProyectoResponse,
    status_code=201
)
def crear_proyecto(
    datos: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = ProyectoService(db)

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


@router.put(
    "/{id_proyecto}",
    response_model=ProyectoResponse
)
def actualizar_proyecto(
    id_proyecto: int,
    datos: ProyectoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = ProyectoService(db)

    try:

        return service.actualizar(
            id_proyecto,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_proyecto}/estado",
    response_model=ProyectoResponse
)
def cambiar_estado(
    id_proyecto: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO"
        )
    )
):
    service = ProyectoService(db)

    try:

        return service.cambiar_estado(
            id_proyecto,
            nuevo_estado,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )