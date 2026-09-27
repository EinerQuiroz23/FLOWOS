from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persona_cargo_model import PersonaCargo
from app.models.persona_model import Persona


class PersonaCargoRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[PersonaCargo]:
        consulta = select(PersonaCargo)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_persona_cargo: int
    ) -> Optional[PersonaCargo]:

        return self.db.get(
            PersonaCargo,
            id_persona_cargo
        )

    def obtener_por_persona(
        self,
        id_persona: int
    ) -> List[PersonaCargo]:

        consulta = select(PersonaCargo).where(
            PersonaCargo.id_persona == id_persona
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_cargo(
        self,
        id_cargo: int
    ) -> List[PersonaCargo]:

        consulta = select(PersonaCargo).where(
            PersonaCargo.id_cargo == id_cargo
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_cargo_actual(
        self,
        id_persona: int
    ) -> Optional[PersonaCargo]:

        consulta = select(PersonaCargo).where(
            PersonaCargo.id_persona == id_persona,
            PersonaCargo.fecha_fin.is_(None)
        )

        return self.db.scalars(consulta).first()

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[PersonaCargo]:

        consulta = (
            select(PersonaCargo)
            .join(
                Persona,
                PersonaCargo.id_persona == Persona.id_persona
            )
            .where(
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_y_organizacion(
        self,
        id_persona_cargo: int,
        id_organizacion: int
    ) -> Optional[PersonaCargo]:

        consulta = (
            select(PersonaCargo)
            .join(
                Persona,
                PersonaCargo.id_persona == Persona.id_persona
            )
            .where(
                PersonaCargo.id_persona_cargo == id_persona_cargo,
                Persona.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_persona_y_organizacion(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[PersonaCargo]:

        consulta = (
            select(PersonaCargo)
            .join(
                Persona,
                PersonaCargo.id_persona == Persona.id_persona
            )
            .where(
                PersonaCargo.id_persona == id_persona,
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def crear(
        self,
        persona_cargo: PersonaCargo
    ) -> PersonaCargo:

        self.db.add(persona_cargo)
        self.db.flush()

        return persona_cargo

    def actualizar(
        self,
        persona_cargo: PersonaCargo
    ) -> PersonaCargo:

        self.db.flush()

        return persona_cargo