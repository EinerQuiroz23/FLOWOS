from sqlalchemy.orm import Session

from app.models.rol_model import Rol


class RolRepository:

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_rol: int
    ) -> Rol | None:

        return (
            db.query(Rol)
            .filter(
                Rol.id_rol == id_rol
            )
            .first()
        )

    @staticmethod
    def obtener_por_nombre(
        db: Session,
        nombre: str
    ) -> Rol | None:

        return (
            db.query(Rol)
            .filter(
                Rol.nombre == nombre
            )
            .first()
        )

    @staticmethod
    def obtener_activos(
        db: Session
    ) -> list[Rol]:

        return (
            db.query(Rol)
            .filter(
                Rol.estado == True
            )
            .all()
        )