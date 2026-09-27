from sqlalchemy.orm import Session

from app.models.usuario_model import Usuario


class UsuarioRepository:

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_usuario: int
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.id_usuario == id_usuario
            )
            .first()
        )

    @staticmethod
    def obtener_por_email(
        db: Session,
        email: str
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.email == email
            )
            .first()
        )

    @staticmethod
    def obtener_por_email_organizacion(
        db: Session,
        email: str,
        id_organizacion: int
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.email == email,
                Usuario.id_organizacion == id_organizacion
            )
            .first()
        )

    @staticmethod
    def obtener_por_nombre_usuario_organizacion(
        db: Session,
        nombre_usuario: str,
        id_organizacion: int
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.id_organizacion == id_organizacion
            )
            .first()
        )

    @staticmethod
    def obtener_por_persona(
        db: Session,
        id_persona: int
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.id_persona == id_persona
            )
            .first()
        )

    @staticmethod
    def obtener_por_organizacion(
        db: Session,
        id_organizacion: int
    ) -> list[Usuario]:

        return (
            db.query(Usuario)
            .filter(
                Usuario.id_organizacion == id_organizacion
            )
            .all()
        )

    @staticmethod
    def obtener_activos_por_organizacion(
        db: Session,
        id_organizacion: int
    ) -> list[Usuario]:

        return (
            db.query(Usuario)
            .filter(
                Usuario.id_organizacion == id_organizacion,
                Usuario.estado.is_(True)
            )
            .all()
        )

    @staticmethod
    def crear(
        db: Session,
        usuario: Usuario
    ) -> Usuario:

        db.add(usuario)
        db.flush()

        return usuario

    @staticmethod
    def obtener_por_nombre_usuario(
        db: Session,
        nombre_usuario: str
    ) -> Usuario | None:

        return (
            db.query(Usuario)
            .filter(
                Usuario.nombre_usuario == nombre_usuario
            )
            .first()
        )