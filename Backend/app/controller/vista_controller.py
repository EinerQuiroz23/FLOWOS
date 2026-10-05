from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_role
from app.core.database import get_db
from app.models.usuario_model import Usuario
from app.schemas.vista_schema import VistaAnalizarRequest, VistaAnalizarResponse
from app.services.vista_service import VistaService

router = APIRouter(
    prefix="/vista",
    tags=["VISTA"],
)


@router.post(
    "/analizar",
    response_model=VistaAnalizarResponse,
)
def analizar_requisitos(
    datos: VistaAnalizarRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("ADMIN")),
):
    try:
        return VistaService.analizar(
            db,
            datos,
            usuario.id_organizacion,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))