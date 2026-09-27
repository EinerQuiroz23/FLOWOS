from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.database import get_db
from app.models.usuario_model import Usuario
from app.schemas.organizacion_schema import OrganizacionCreate, OrganizacionResponse
from app.services.organizacion_service import OrganizacionService

from app.core.authorization import require_role

from app.schemas.auth_schema import CrearAdminOrganizacionRequest
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/organizaciones",
    tags=["Organizaciones"]
)


@router.get(
    "/me",
    response_model=OrganizacionResponse
)
def obtener_mi_organizacion(
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

        return OrganizacionService.obtener_por_id(
            db,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

@router.post(
    "",
    response_model=OrganizacionResponse,
    status_code=201
)
def crear_organizacion(
    datos: OrganizacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("SUPER_ADMIN"))
):
    try:
        organizacion = OrganizacionService.crear(db, datos)
        db.commit()
        db.refresh(organizacion)
        return organizacion

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
            )

@router.get(
    "/{id_organizacion}",
    response_model=OrganizacionResponse
)
def obtener_organizacion(
    id_organizacion: int,
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

    if id_organizacion != usuario.id_organizacion:

        raise HTTPException(
            status_code=403,
            detail="No puedes acceder a otra organización"
        )

    try:

        return OrganizacionService.obtener_por_id(
            db,
            id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

@router.post(
    "/{id_organizacion}/admin",
    status_code=201
)
def crear_admin_organizacion(
    id_organizacion: int,
    datos: CrearAdminOrganizacionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_role("SUPER_ADMIN"))
):
    try:
        resultado = AuthService.crear_admin_organizacion(
            db,
            id_organizacion,
            datos
        )
        return resultado

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )