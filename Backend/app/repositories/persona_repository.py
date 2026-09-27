from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persona_model import Persona


class PersonaRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[Persona]:
        consulta = select(Persona)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_persona: int
    ) -> Optional[Persona]:

        return self.db.get(Persona, id_persona)

    def obtener_por_email(
        self,
        email: str
    ) -> Optional[Persona]:

        consulta = select(Persona).where(
            Persona.email == email
        )

        return self.db.scalars(consulta).first()

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[Persona]:

        consulta = select(Persona).where(
            Persona.id_organizacion == id_organizacion
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_organizacion(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> Optional[Persona]:

        consulta = select(Persona).where(
            Persona.id_persona == id_persona,
            Persona.id_organizacion == id_organizacion
        )

        return self.db.scalars(consulta).first()

    def obtener_activas_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[Persona]:

        consulta = select(Persona).where(
            Persona.id_organizacion == id_organizacion,
            Persona.estado == True
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_email_organizacion(
        self,
        email: str,
        id_organizacion: int
    ) -> Optional[Persona]:

        consulta = select(Persona).where(
            Persona.email == email,
            Persona.id_organizacion == id_organizacion
        )

        return self.db.scalars(consulta).first()

    def crear(
        self,
        persona: Persona
    ) -> Persona:

        self.db.add(persona)
        self.db.flush()

        return persona

    def actualizar(
        self,
        persona: Persona
    ) -> Persona:

        self.db.flush()

        return persona

    def activar(
        self,
        persona: Persona
    ) -> Persona:

        persona.estado = True
        self.db.flush()

        return persona

    def desactivar(
        self,
        persona: Persona
    ) -> Persona:

        persona.estado = False
        self.db.flush()

        return persona