from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.usuario_model import Usuario

from app.schemas.habilidad_schema import (
    HabilidadCreate,
    HabilidadUpdate,
    HabilidadResponse
)

from app.services.habilidad_service import HabilidadService


router = APIRouter(
    prefix="/habilidades",
    tags=["Habilidades"]
)


@router.get(
    "/",
    response_model=List[HabilidadResponse]
)
def obtener_habilidades(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    return service.obtener_todos()


@router.get(
    "/{id_habilidad}",
    response_model=HabilidadResponse
)
def obtener_habilidad_por_id(
    id_habilidad: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    habilidad = service.obtener_por_id(
        id_habilidad
    )

    if habilidad is None:
        raise HTTPException(
            status_code=404,
            detail="La habilidad no existe."
        )

    return habilidad


@router.post(
    "/",
    response_model=HabilidadResponse,
    status_code=201
)
def crear_habilidad(
    datos: HabilidadCreate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    try:
        return service.crear(datos)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.put(
    "/{id_habilidad}",
    response_model=HabilidadResponse
)
def actualizar_habilidad(
    id_habilidad: int,
    datos: HabilidadUpdate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    try:
        return service.actualizar(
            id_habilidad,
            datos
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_habilidad}/activar",
    response_model=HabilidadResponse
)
def activar_habilidad(
    id_habilidad: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    try:
        return service.activar(id_habilidad)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_habilidad}/desactivar",
    response_model=HabilidadResponse
)
def desactivar_habilidad(
    id_habilidad: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = HabilidadService(db)

    try:
        return service.desactivar(id_habilidad)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )