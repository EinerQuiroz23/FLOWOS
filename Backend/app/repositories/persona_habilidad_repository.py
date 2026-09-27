from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persona_habilidad_model import PersonaHabilidad
from app.models.persona_model import Persona


class PersonaHabilidadRepository:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # CONSULTAS GENERALES
    # =========================================================

    def obtener_todos(self) -> List[PersonaHabilidad]:

        consulta = select(PersonaHabilidad)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_persona_habilidad: int
    ) -> Optional[PersonaHabilidad]:

        return self.db.get(
            PersonaHabilidad,
            id_persona_habilidad
        )

    def obtener_por_persona(
        self,
        id_persona: int
    ) -> List[PersonaHabilidad]:

        consulta = select(PersonaHabilidad).where(
            PersonaHabilidad.id_persona == id_persona
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_habilidad(
        self,
        id_habilidad: int
    ) -> List[PersonaHabilidad]:

        consulta = select(PersonaHabilidad).where(
            PersonaHabilidad.id_habilidad == id_habilidad
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_persona_y_habilidad(
        self,
        id_persona: int,
        id_habilidad: int
    ) -> Optional[PersonaHabilidad]:

        consulta = select(PersonaHabilidad).where(
            PersonaHabilidad.id_persona == id_persona,
            PersonaHabilidad.id_habilidad == id_habilidad
        )

        return self.db.scalars(consulta).first()

    # =========================================================
    # CONSULTAS POR ORGANIZACIÓN
    # =========================================================

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        consulta = (
            select(PersonaHabilidad)
            .join(
                Persona,
                PersonaHabilidad.id_persona == Persona.id_persona
            )
            .where(
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_y_organizacion(
        self,
        id_persona_habilidad: int,
        id_organizacion: int
    ) -> Optional[PersonaHabilidad]:

        consulta = (
            select(PersonaHabilidad)
            .join(
                Persona,
                PersonaHabilidad.id_persona == Persona.id_persona
            )
            .where(
                PersonaHabilidad.id_persona_habilidad
                == id_persona_habilidad,
                Persona.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_persona_y_organizacion(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        consulta = (
            select(PersonaHabilidad)
            .join(
                Persona,
                PersonaHabilidad.id_persona == Persona.id_persona
            )
            .where(
                PersonaHabilidad.id_persona == id_persona,
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_habilidad_y_organizacion(
        self,
        id_habilidad: int,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        consulta = (
            select(PersonaHabilidad)
            .join(
                Persona,
                PersonaHabilidad.id_persona == Persona.id_persona
            )
            .where(
                PersonaHabilidad.id_habilidad == id_habilidad,
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_persona_y_habilidad_y_organizacion(
        self,
        id_persona: int,
        id_habilidad: int,
        id_organizacion: int
    ) -> Optional[PersonaHabilidad]:

        consulta = (
            select(PersonaHabilidad)
            .join(
                Persona,
                PersonaHabilidad.id_persona == Persona.id_persona
            )
            .where(
                PersonaHabilidad.id_persona == id_persona,
                PersonaHabilidad.id_habilidad == id_habilidad,
                Persona.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    # =========================================================
    # PERSISTENCIA
    # =========================================================

    def crear(
        self,
        persona_habilidad: PersonaHabilidad
    ) -> PersonaHabilidad:

        self.db.add(persona_habilidad)
        self.db.flush()

        return persona_habilidad

    def actualizar(
        self,
        persona_habilidad: PersonaHabilidad
    ) -> PersonaHabilidad:

        self.db.flush()

        return persona_habilidad