from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_role
from app.core.database import get_db

from app.models.usuario_model import Usuario

from app.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate
)

from app.services.usuario_service import UsuarioService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.get(
    "/",
    response_model=list[UsuarioResponse]
)
def obtener_usuarios(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    return UsuarioService.obtener_todos(
        db,
        usuario.id_organizacion
    )


@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse
)
def obtener_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    try:

        return UsuarioService.obtener_por_id(
            db,
            id_usuario,
            usuario.id_organizacion
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=201
)
def crear_usuario(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    try:

        return UsuarioService.crear(
            db,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.put(
    "/{id_usuario}",
    response_model=UsuarioResponse
)
def actualizar_usuario(
    id_usuario: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    try:

        return UsuarioService.actualizar(
            db,
            id_usuario,
            datos,
            usuario.id_organizacion
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_usuario}/activar",
    response_model=UsuarioResponse
)
def activar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    try:

        return UsuarioService.activar(
            db,
            id_usuario,
            usuario.id_organizacion
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.patch(
    "/{id_usuario}/desactivar",
    response_model=UsuarioResponse
)
def desactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    try:

        return UsuarioService.desactivar(
            db,
            id_usuario,
            usuario.id_organizacion
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )