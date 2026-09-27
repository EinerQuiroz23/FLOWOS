from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.persona_cargo_schema import (
    PersonaCargoCreate,
    PersonaCargoUpdate,
    PersonaCargoResponse
)

from app.services.persona_cargo_service import PersonaCargoService


router = APIRouter(
    prefix="/personas-cargos",
    tags=["Personas - Cargos"]
)


@router.get(
    "/",
    response_model=List[PersonaCargoResponse]
)
def obtener_registros(
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
    service = PersonaCargoService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


@router.get(
    "/persona/{id_persona}",
    response_model=List[PersonaCargoResponse]
)
def obtener_por_persona(
    id_persona: int,
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
    service = PersonaCargoService(db)

    return service.obtener_por_persona(
        id_persona,
        usuario.id_organizacion
    )


@router.get(
    "/{id_persona_cargo}",
    response_model=PersonaCargoResponse
)
def obtener_registro_por_id(
    id_persona_cargo: int,
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
    service = PersonaCargoService(db)

    registro = service.obtener_por_id(
        id_persona_cargo,
        usuario.id_organizacion
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="El registro persona-cargo no existe."
        )

    return registro


@router.post(
    "/",
    response_model=PersonaCargoResponse,
    status_code=201
)
def crear_registro(
    datos: PersonaCargoCreate,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaCargoService(db)

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
    "/{id_persona_cargo}",
    response_model=PersonaCargoResponse
)
def actualizar_registro(
    id_persona_cargo: int,
    datos: PersonaCargoUpdate,
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    ),
    db: Session = Depends(get_db)
):
    service = PersonaCargoService(db)

    try:
        return service.actualizar(
            id_persona_cargo,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )