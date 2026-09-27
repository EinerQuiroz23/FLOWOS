from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.habilidad_model import Habilidad
from app.repositories.habilidad_repository import HabilidadRepository
from app.schemas.habilidad_schema import (
    HabilidadCreate,
    HabilidadUpdate
)


class HabilidadService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = HabilidadRepository(db)

    def obtener_todos(self) -> List[Habilidad]:
        return self.repository.obtener_todos()

    def obtener_por_id(
        self,
        id_habilidad: int
    ) -> Optional[Habilidad]:

        return self.repository.obtener_por_id(
            id_habilidad
        )

    def crear(
        self,
        datos: HabilidadCreate
    ) -> Habilidad:

        existente = self.repository.obtener_por_nombre(
            datos.nombre
        )

        if existente is not None:
            raise ValueError(
                "Ya existe una habilidad con ese nombre."
            )

        habilidad = Habilidad(
            nombre=datos.nombre,
            descripcion=datos.descripcion
        )

        try:
            self.repository.crear(habilidad)

            self.db.commit()

            return habilidad

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_habilidad: int,
        datos: HabilidadUpdate
    ) -> Habilidad:

        habilidad = self.repository.obtener_por_id(
            id_habilidad
        )

        if habilidad is None:
            raise ValueError(
                "La habilidad no existe."
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        if "nombre" in datos_actualizados:

            existente = self.repository.obtener_por_nombre(
                datos_actualizados["nombre"]
            )

            if (
                existente is not None
                and existente.id_habilidad != id_habilidad
            ):
                raise ValueError(
                    "Ya existe otra habilidad con ese nombre."
                )

        for campo, valor in datos_actualizados.items():
            setattr(
                habilidad,
                campo,
                valor
            )

        try:
            self.repository.actualizar(habilidad)

            self.db.commit()

            return habilidad

        except Exception:
            self.db.rollback()
            raise

    def activar(
        self,
        id_habilidad: int
    ) -> Habilidad:

        habilidad = self.repository.obtener_por_id(
            id_habilidad
        )

        if habilidad is None:
            raise ValueError(
                "La habilidad no existe."
            )

        if habilidad.estado:
            raise ValueError(
                "La habilidad ya está activa."
            )

        try:
            self.repository.cambiar_estado(
                habilidad,
                True
            )

            self.db.commit()

            return habilidad

        except Exception:
            self.db.rollback()
            raise

    def desactivar(
        self,
        id_habilidad: int
    ) -> Habilidad:

        habilidad = self.repository.obtener_por_id(
            id_habilidad
        )

        if habilidad is None:
            raise ValueError(
                "La habilidad no existe."
            )

        if not habilidad.estado:
            raise ValueError(
                "La habilidad ya está inactiva."
            )

        try:
            self.repository.cambiar_estado(
                habilidad,
                False
            )

            self.db.commit()

            return habilidad

        except Exception:
            self.db.rollback()
            raise