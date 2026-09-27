from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.nivel_habilidad_model import NivelHabilidad
from app.repositories.nivel_habilidad_repository import NivelHabilidadRepository
from app.schemas.nivel_habilidad_schema import (
    NivelHabilidadCreate,
    NivelHabilidadUpdate
)


class NivelHabilidadService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = NivelHabilidadRepository(db)

    def obtener_todos(self) -> List[NivelHabilidad]:
        return self.repository.obtener_todos()

    def obtener_por_id(
        self,
        id_nivel: int
    ) -> Optional[NivelHabilidad]:

        return self.repository.obtener_por_id(
            id_nivel
        )

    def crear(
        self,
        datos: NivelHabilidadCreate
    ) -> NivelHabilidad:

        existente = self.repository.obtener_por_nombre(
            datos.nombre
        )

        if existente is not None:
            raise ValueError(
                "Ya existe un nivel de habilidad con ese nombre."
            )

        nivel = NivelHabilidad(
            nombre=datos.nombre,
            descripcion=datos.descripcion
        )

        try:
            self.repository.crear(nivel)

            self.db.commit()

            return nivel

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_nivel: int,
        datos: NivelHabilidadUpdate
    ) -> NivelHabilidad:

        nivel = self.repository.obtener_por_id(
            id_nivel
        )

        if nivel is None:
            raise ValueError(
                "El nivel de habilidad no existe."
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
                and existente.id_nivel != id_nivel
            ):
                raise ValueError(
                    "Ya existe otro nivel con ese nombre."
                )

        for campo, valor in datos_actualizados.items():
            setattr(
                nivel,
                campo,
                valor
            )

        try:
            self.repository.actualizar(nivel)

            self.db.commit()

            return nivel

        except Exception:
            self.db.rollback()
            raise