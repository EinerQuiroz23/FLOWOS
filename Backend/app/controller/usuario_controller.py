from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_role, require_any_role
from app.core.database import get_db

from app.models.usuario_model import Usuario

from app.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate
)

from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


class CambiarNombreUsuarioRequest(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=100)


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


# ==========================================================
# CAMBIAR MI NOMBRE DE USUARIO (antes de /{id_usuario})
# ==========================================================

@router.patch("/me/nombre-usuario")
def cambiar_mi_nombre_usuario(
    datos: CambiarNombreUsuarioRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO",
            "SUPER_ADMIN"
        )
    )
):
    nombre = datos.nombre_usuario.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario es obligatorio"
        )

    existente = UsuarioRepository.obtener_por_nombre_usuario(db, nombre)

    if existente is not None and existente.id_usuario != usuario.id_usuario:
        raise HTTPException(
            status_code=400,
            detail="Ese nombre de usuario ya está en uso"
        )

    usuario.nombre_usuario = nombre
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Nombre de usuario actualizado",
        "nombre_usuario": usuario.nombre_usuario
    }


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