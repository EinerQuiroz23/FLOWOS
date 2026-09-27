from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.database import get_db
from app.models.usuario_model import Usuario
from app.schemas.rol_schema import RolResponse
from app.services.rol_service import RolService


router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get(
    "/",
    response_model=list[RolResponse]
)
def obtener_roles(
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

    return RolService.obtener_activos(db)


@router.get(
    "/{id_rol}",
    response_model=RolResponse
)
def obtener_rol(
    id_rol: int,
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

    try:

        return RolService.obtener_por_id(
            db,
            id_rol
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )