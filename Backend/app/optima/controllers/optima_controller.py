from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_role

from app.models.usuario_model import Usuario

from app.optima.models.candidato_optima import CandidatoOptima
from app.optima.models.propuesta_equipo import PropuestaEquipo

from app.optima.service.optima_service import OptimaService
from app.optima.service.optima_team_service import OptimaTeamService


router = APIRouter(
    prefix="/optima",
    tags=["OPTIMA"]
)


@router.get(
    "/tarea/{id_tarea}",
    response_model=List[CandidatoOptima]
)
def evaluar_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    service = OptimaService(db)

    return service.evaluar_tarea(
        id_tarea=id_tarea,
        id_organizacion=usuario.id_organizacion
    )


@router.get(
    "/proyecto/{id_proyecto}/propuesta-equipo",
    response_model=PropuestaEquipo
)
def proponer_equipo(
    id_proyecto: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    service = OptimaTeamService(db)

    return service.proponer_equipo(
        id_proyecto=id_proyecto,
        id_organizacion=usuario.id_organizacion
    )