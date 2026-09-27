from sqlalchemy.orm import Session

from app.models.organizacion_model import Organizacion


class OrganizacionRepository:

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_organizacion: int
    ) -> Organizacion | None:

        return (
            db.query(Organizacion)
            .filter(
                Organizacion.id_organizacion == id_organizacion
            )
            .first()
        )

    @staticmethod
    def obtener_por_nombre(
        db: Session,
        nombre: str
    ) -> Organizacion | None:

        return (
            db.query(Organizacion)
            .filter(
                Organizacion.nombre == nombre
            )
            .first()
        )

    @staticmethod
    def obtener_por_codigo(
        db: Session,
        codigo: str
    ) -> Organizacion | None:

        return (
            db.query(Organizacion)
            .filter(
                Organizacion.codigo == codigo
            )
            .first()
        )

    @staticmethod
    def obtener_activas(
        db: Session
    ) -> list[Organizacion]:

        return (
            db.query(Organizacion)
            .filter(
                Organizacion.estado == True
            )
            .all()
        )

    @staticmethod
    def crear(
        db: Session,
        organizacion: Organizacion
    ) -> Organizacion:

        db.add(organizacion)
        db.flush()

        return organizacion