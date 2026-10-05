from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role
from app.models.usuario_model import Usuario
from app.schemas.mensaje_equipo_schema import (
    MensajeEquipoCreate,
    MensajeEquipoResponse,
)
from app.services.mensaje_equipo_service import MensajeEquipoService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get(
    "/equipo/{id_equipo}/mensajes",
    response_model=list[MensajeEquipoResponse],
)
def listar_mensajes(
    id_equipo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO",
        )
    ),
):
    try:
        service = MensajeEquipoService(db)
        return service.listar(
            id_equipo=id_equipo,
            id_organizacion=usuario.id_organizacion,
            id_persona=usuario.id_persona,
            id_rol=usuario.id_rol,
        )
    except ValueError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.post(
    "/equipo/{id_equipo}/mensajes",
    response_model=MensajeEquipoResponse,
    status_code=201,
)
def enviar_mensaje(
    id_equipo: int,
    datos: MensajeEquipoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO",
        )
    ),
):
    try:
        service = MensajeEquipoService(db)
        return service.crear(
            id_equipo=id_equipo,
            datos=datos,
            id_organizacion=usuario.id_organizacion,
            id_persona=usuario.id_persona,
            id_rol=usuario.id_rol,
        )
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(error))