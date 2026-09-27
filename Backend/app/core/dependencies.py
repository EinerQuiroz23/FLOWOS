from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario_model import Usuario


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:

    try:
        token = credentials.credentials

        payload = decode_access_token(token)

        id_usuario = payload.get("sub")

        if not id_usuario:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        usuario = UsuarioRepository.obtener_por_id(
            db,
            int(id_usuario)
        )

        if usuario is None or not usuario.estado:
            raise HTTPException(
                status_code=401,
                detail="Usuario no válido"
            )

        # =====================================================
        # VALIDAR QUE EL TOKEN COINCIDA CON LA BASE DE DATOS
        # =====================================================

        id_organizacion_token = payload.get(
            "id_organizacion"
        )

        id_rol_token = payload.get(
            "id_rol"
        )

        if (
            id_organizacion_token is None
            or int(id_organizacion_token)
            != usuario.id_organizacion
        ):
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        if (
            id_rol_token is None
            or int(id_rol_token)
            != usuario.id_rol
        ):
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        return usuario

    except HTTPException:
        raise

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )