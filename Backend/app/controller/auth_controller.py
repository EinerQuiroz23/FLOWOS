from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_role
from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.usuario_model import Usuario

from app.schemas.auth_schema import (
    LoginRequest,
    RecuperarContrasenaRequest,
    RegistroOrganizacionRequest,
    RestablecerContrasenaRequest,
    TokenResponse,
    RegistroEmpleadoRequest
)

from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        token = AuthService.login(
            db,
            datos.email,
            datos.contrasena
        )

        return TokenResponse(
            access_token=token
        )

    except ValueError as error:

        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


@router.post(
    "/registro-organizacion",
    response_model=TokenResponse,
    status_code=201
)
def registrar_organizacion(
    datos: RegistroOrganizacionRequest,
    db: Session = Depends(get_db)
):

    try:

        token = AuthService.registrar_organizacion(
            db,
            datos
        )

        return TokenResponse(
            access_token=token
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post(
    "/recuperar-contrasena/solicitar"
)
def solicitar_recuperacion(
    datos: RecuperarContrasenaRequest,
    db: Session = Depends(get_db)
):

    AuthService.solicitar_recuperacion(
        db,
        datos.email
    )

    return {
        "mensaje": (
            "Si el correo existe, se ha generado "
            "una solicitud de recuperación."
        )
    }


@router.post("/recuperar-contrasena/restablecer")
def restablecer_contrasena(
    datos: RestablecerContrasenaRequest,
    db: Session = Depends(get_db)
):
    try:
        AuthService.restablecer_contrasena(
            db,
            datos.email,
            datos.codigo,
            datos.nueva_contrasena
        )

        return {
            "mensaje": "Contraseña actualizada correctamente"
        }

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/me")
def obtener_usuario_actual(
    usuario: Usuario = Depends(
        get_current_user
    )
):

    return {
        "id_usuario": usuario.id_usuario,
        "id_persona": usuario.id_persona,
        "id_organizacion": usuario.id_organizacion,
        "id_rol": usuario.id_rol,
        "email": usuario.email,
        "nombre_usuario": usuario.nombre_usuario
    }


@router.get("/admin-test")
def prueba_admin(
    usuario: Usuario = Depends(
        require_role("ADMIN")
    )
):

    return {
        "mensaje": "Acceso autorizado",
        "usuario": usuario.nombre_usuario,
        "rol": usuario.id_rol
    }

@router.post("/registro-empleado",response_model=TokenResponse,status_code=201)
def registrar_empleado(
    datos: RegistroEmpleadoRequest,
    db: Session = Depends(get_db)
):

    try:
        token = AuthService.registrar_empleado(db, datos)

        return TokenResponse(
            access_token=token
        )

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )