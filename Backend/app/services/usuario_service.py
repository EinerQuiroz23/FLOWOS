from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.models.usuario_model import Usuario

from app.repositories.persona_repository import PersonaRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.usuario_repository import UsuarioRepository

from app.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioUpdate
)


class UsuarioService:

    @staticmethod
    def obtener_todos(
        db: Session,
        id_organizacion: int
    ) -> list[Usuario]:

        return UsuarioRepository.obtener_por_organizacion(
            db,
            id_organizacion
        )

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_usuario: int,
        id_organizacion: int
    ) -> Usuario:

        usuario = UsuarioRepository.obtener_por_id(
            db,
            id_usuario
        )

        if (
            usuario is None
            or usuario.id_organizacion != id_organizacion
        ):
            raise ValueError(
                "El usuario no existe"
            )

        return usuario

    @staticmethod
    def crear(
        db: Session,
        datos: UsuarioCreate,
        id_organizacion: int
    ) -> Usuario:

        persona_repository = PersonaRepository(db)

        persona = persona_repository.obtener_por_id_organizacion(
        datos.id_persona,
        id_organizacion
)

        if persona is None:
            raise ValueError(
                "La persona no pertenece a la organización"
            )

        rol = RolRepository.obtener_por_id(
            db,
            datos.id_rol
        )

        if rol is None or not rol.estado:
            raise ValueError(
                "El rol no existe o está inactivo"
            )

        # El ADMIN principal nace con la organización.
        if datos.id_rol == 1:
            raise ValueError(
                "El ADMIN principal se crea durante "
                "el registro de la organización"
            )

        if UsuarioRepository.obtener_por_email_organizacion(
            db,
            datos.email,
            id_organizacion
        ):
            raise ValueError(
                "Ya existe un usuario con ese correo"
            )

        if UsuarioRepository.obtener_por_nombre_usuario_organizacion(
            db,
            datos.nombre_usuario,
            id_organizacion
        ):
            raise ValueError(
                "Ya existe un usuario con ese nombre de usuario"
            )

        if UsuarioRepository.obtener_por_persona(
            db,
            datos.id_persona
        ):
            raise ValueError(
                "La persona ya tiene una cuenta de usuario"
            )

        usuario = Usuario(
            id_organizacion=id_organizacion,
            id_persona=datos.id_persona,
            id_rol=datos.id_rol,
            nombre_usuario=datos.nombre_usuario.strip(),
            email=datos.email,
            contrasena_hash=hash_password(
                datos.contrasena
            )
        )

        UsuarioRepository.crear(
            db,
            usuario
        )

        db.commit()
        db.refresh(usuario)

        return usuario

    @staticmethod
    def actualizar(
        db: Session,
        id_usuario: int,
        datos: UsuarioUpdate,
        id_organizacion: int
    ) -> Usuario:

        usuario = UsuarioService.obtener_por_id(
            db,
            id_usuario,
            id_organizacion
        )

        cambios = datos.model_dump(
            exclude_unset=True
        )

        if "id_rol" in cambios:

            rol = RolRepository.obtener_por_id(
                db,
                cambios["id_rol"]
            )

            if rol is None or not rol.estado:
                raise ValueError(
                    "El rol no existe o está inactivo"
                )

            if (
                cambios["id_rol"] == 1
                and usuario.id_rol != 1
            ):
                raise ValueError(
                    "No se puede asignar ADMIN desde este endpoint"
                )

            if (
                usuario.id_rol == 1
                and cambios["id_rol"] != 1
            ):
                raise ValueError(
                    "El ADMIN principal no puede cambiar su rol"
                )

        if "email" in cambios:

            existente = (
                UsuarioRepository
                .obtener_por_email_organizacion(
                    db,
                    cambios["email"],
                    id_organizacion
                )
            )

            if (
                existente
                and existente.id_usuario != id_usuario
            ):
                raise ValueError(
                    "Ya existe otro usuario con ese correo"
                )

        if "nombre_usuario" in cambios:

            cambios["nombre_usuario"] = (
                cambios["nombre_usuario"].strip()
            )

            existente = (
                UsuarioRepository
                .obtener_por_nombre_usuario_organizacion(
                    db,
                    cambios["nombre_usuario"],
                    id_organizacion
                )
            )

            if (
                existente
                and existente.id_usuario != id_usuario
            ):
                raise ValueError(
                    "Ya existe otro usuario con ese nombre de usuario"
                )

        for campo, valor in cambios.items():
            setattr(
                usuario,
                campo,
                valor
            )

        db.flush()
        db.commit()
        db.refresh(usuario)

        return usuario

    @staticmethod
    def activar(
        db: Session,
        id_usuario: int,
        id_organizacion: int
    ) -> Usuario:

        usuario = UsuarioService.obtener_por_id(
            db,
            id_usuario,
            id_organizacion
        )

        if usuario.estado:
            raise ValueError(
                "El usuario ya está activo"
            )

        usuario.estado = True

        db.commit()
        db.refresh(usuario)

        return usuario

    @staticmethod
    def desactivar(
        db: Session,
        id_usuario: int,
        id_organizacion: int
    ) -> Usuario:

        usuario = UsuarioService.obtener_por_id(
            db,
            id_usuario,
            id_organizacion
        )

        if usuario.id_rol == 1:
            raise ValueError(
                "El ADMIN principal no puede desactivarse"
            )

        if not usuario.estado:
            raise ValueError(
                "El usuario ya está inactivo"
            )

        usuario.estado = False

        db.commit()
        db.refresh(usuario)

        return usuario