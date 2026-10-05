from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_role

from app.models.usuario_model import Usuario

from app.optima.models.candidato_optima import CandidatoOptima
from app.optima.models.propuesta_equipo import PropuestaEquipo

from app.optima.service.optima_service import OptimaService
from app.optima.service.optima_team_service import OptimaTeamService

from app.services.optima_confirm_service import OptimaConfirmService
from app.schemas.optima_confirm_schema import (
    OptimaConfirmarRequest,
    OptimaConfirmarResponse,
)

router = APIRouter(
    prefix="/optima",
    tags=["OPTIMA"],
)


@router.get(
    "/tarea/{id_tarea}",
    response_model=List[CandidatoOptima],
)
def evaluar_tarea(
    id_tarea: int,
    alcance: str = Query(
        default="equipo",
        description="equipo | proyecto | organizacion",
    ),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("ADMIN")),
):
    service = OptimaService(db)

    return service.evaluar_tarea(
        id_tarea=id_tarea,
        id_organizacion=usuario.id_organizacion,
        alcance=alcance,
    )


@router.get(
    "/proyecto/{id_proyecto}/propuesta-equipo",
    response_model=PropuestaEquipo,
)
def proponer_equipo(
    id_proyecto: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("ADMIN")),
):
    service = OptimaTeamService(db)

    return service.proponer_equipo(
        id_proyecto=id_proyecto,
        id_organizacion=usuario.id_organizacion,
    )


@router.post(
    "/proyecto/{id_proyecto}/confirmar",
    response_model=OptimaConfirmarResponse,
)
def confirmar_propuesta_optima(
    id_proyecto: int,
    datos: OptimaConfirmarRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("ADMIN")),
):
    try:
        service = OptimaConfirmService(db)
        return service.confirmar(
            id_proyecto=id_proyecto,
            id_organizacion=usuario.id_organizacion,
            nombre_equipo=datos.nombre_equipo,
        )
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(error))