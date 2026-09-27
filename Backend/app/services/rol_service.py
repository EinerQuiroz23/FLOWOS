from sqlalchemy.orm import Session

from app.models.rol_model import Rol
from app.repositories.rol_repository import RolRepository


class RolService:

    @staticmethod
    def obtener_activos(
        db: Session
    ) -> list[Rol]:

        return RolRepository.obtener_activos(db)

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_rol: int
    ) -> Rol:

        rol = RolRepository.obtener_por_id(
            db,
            id_rol
        )

        if rol is None or not rol.estado:

            raise ValueError(
                "El rol no existe o está inactivo"
            )

        return rol