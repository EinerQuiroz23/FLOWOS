from fastapi import Depends, HTTPException

from app.core.dependencies import get_current_user
from app.models.usuario_model import Usuario


ROLES = {
    "ADMIN": 1,
    "LIDER_PROYECTO": 2,
    "SECRETARIO": 3,
    "EMPLEADO": 4,
    "SUPER_ADMIN": 5,
}


def obtener_id_rol(nombre_rol: str) -> int:

    if nombre_rol not in ROLES:
        raise ValueError("Rol no válido")

    return ROLES[nombre_rol]


def require_role(nombre_rol: str):

    def verificar_rol(
        usuario: Usuario = Depends(get_current_user)
    ) -> Usuario:

        if usuario.id_rol != obtener_id_rol(nombre_rol):

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para realizar "
                    "esta acción"
                )
            )

        return usuario

    return verificar_rol


def require_any_role(*nombres_roles: str):

    ids_roles = {
        obtener_id_rol(nombre_rol)
        for nombre_rol in nombres_roles
    }

    def verificar_roles(
        usuario: Usuario = Depends(get_current_user)
    ) -> Usuario:

        if usuario.id_rol not in ids_roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para realizar "
                    "esta acción"
                )
            )

        return usuario

    return verificar_roles


def require_organization(
    id_organizacion: int,
    usuario: Usuario = Depends(get_current_user)
) -> Usuario:

    if usuario.id_organizacion != id_organizacion:

        raise HTTPException(
            status_code=403,
            detail=(
                "No tienes permisos para acceder "
                "a otra organización"
            )
        )

    return usuario