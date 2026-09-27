from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role, require_role

from app.models.usuario_model import Usuario

from app.schemas.cargo_schema import (
    CargoCreate,
    CargoUpdate,
    CargoResponse
)

from app.services.cargo_service import CargoService


router = APIRouter(
    prefix="/cargos",
    tags=["Cargos"]
)


@router.get(
    "/",
    response_model=List[CargoResponse]
)
def obtener_cargos(
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
    service = CargoService(db)

    return service.obtener_todos()


@router.get(
    "/{id_cargo}",
    response_model=CargoResponse
)
def obtener_cargo_por_id(
    id_cargo: int,
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
    service = CargoService(db)

    cargo = service.obtener_por_id(id_cargo)

    if cargo is None:
        raise HTTPException(
            status_code=404,
            detail="El cargo no existe."
        )

    return cargo


@router.post(
    "/",
    response_model=CargoResponse,
    status_code=201
)
def crear_cargo(
    datos: CargoCreate,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = CargoService(db)

    try:
        return service.crear(datos)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.put(
    "/{id_cargo}",
    response_model=CargoResponse
)
def actualizar_cargo(
    id_cargo: int,
    datos: CargoUpdate,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = CargoService(db)

    try:
        return service.actualizar(
            id_cargo,
            datos
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_cargo}/activar",
    response_model=CargoResponse
)
def activar_cargo(
    id_cargo: int,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = CargoService(db)

    try:
        return service.activar(id_cargo)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_cargo}/desactivar",
    response_model=CargoResponse
)
def desactivar_cargo(
    id_cargo: int,
    usuario: Usuario = Depends(
        require_role("ADMIN")
    ),
    db: Session = Depends(get_db)
):
    service = CargoService(db)

    try:
        return service.desactivar(id_cargo)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )