from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.persona_cargo_model import PersonaCargo

from app.repositories.persona_cargo_repository import (
    PersonaCargoRepository
)

from app.repositories.persona_repository import PersonaRepository
from app.repositories.cargo_repository import CargoRepository

from app.schemas.persona_cargo_schema import (
    PersonaCargoCreate,
    PersonaCargoUpdate
)


class PersonaCargoService:

    def __init__(self, db: Session):
        self.db = db

        self.repository = PersonaCargoRepository(db)

        self.persona_repository = PersonaRepository(db)
        self.cargo_repository = CargoRepository(db)

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[PersonaCargo]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    def obtener_por_id(
        self,
        id_persona_cargo: int,
        id_organizacion: int
    ) -> Optional[PersonaCargo]:

        return self.repository.obtener_por_id_y_organizacion(
            id_persona_cargo,
            id_organizacion
        )

    def obtener_por_persona(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[PersonaCargo]:

        persona = self.persona_repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:
            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_persona_y_organizacion(
            id_persona,
            id_organizacion
        )

    def crear(
        self,
        datos: PersonaCargoCreate,
        id_organizacion: int
    ) -> PersonaCargo:

        persona = self.persona_repository.obtener_por_id_organizacion(
            datos.id_persona,
            id_organizacion
        )

        if persona is None:
            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        cargo = self.cargo_repository.obtener_por_id(
            datos.id_cargo
        )

        if cargo is None:
            raise FlowosException(
                message="El cargo indicado no existe.",
                code="CARGO_NO_EXISTE",
                status_code=404
            )

        registro = PersonaCargo(
            id_persona=datos.id_persona,
            id_cargo=datos.id_cargo,
            fecha_inicio=datos.fecha_inicio,
            fecha_fin=datos.fecha_fin
        )

        try:
            self.repository.crear(registro)

            self.db.commit()

            return registro

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_persona_cargo: int,
        datos: PersonaCargoUpdate,
        id_organizacion: int
    ) -> PersonaCargo:

        registro = self.repository.obtener_por_id_y_organizacion(
            id_persona_cargo,
            id_organizacion
        )

        if registro is None:
            raise FlowosException(
                message=(
                    "El registro de cargo de la persona "
                    "no existe."
                ),
                code="PERSONA_CARGO_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        id_persona_final = datos_actualizados.get(
            "id_persona",
            registro.id_persona
        )

        id_cargo_final = datos_actualizados.get(
            "id_cargo",
            registro.id_cargo
        )

        persona = self.persona_repository.obtener_por_id_organizacion(
            id_persona_final,
            id_organizacion
        )

        if persona is None:
            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        cargo = self.cargo_repository.obtener_por_id(
            id_cargo_final
        )

        if cargo is None:
            raise FlowosException(
                message="El cargo indicado no existe.",
                code="CARGO_NO_EXISTE",
                status_code=404
            )

        for campo, valor in datos_actualizados.items():
            setattr(
                registro,
                campo,
                valor
            )

        try:
            self.repository.actualizar(registro)

            self.db.commit()

            return registro

        except Exception:
            self.db.rollback()
            raise