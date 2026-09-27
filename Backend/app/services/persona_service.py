from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.persona_model import Persona
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona_schema import (
    PersonaCreate,
    PersonaUpdate
)


class PersonaService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = PersonaRepository(db)

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[Persona]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    def obtener_por_id(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> Optional[Persona]:

        return self.repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

    def crear(
        self,
        datos: PersonaCreate,
        id_organizacion: int
    ) -> Persona:

        persona_existente = (
            self.repository.obtener_por_email_organizacion(
                datos.email,
                id_organizacion
            )
        )

        if persona_existente is not None:
            raise ValueError(
                "Ya existe una persona registrada con ese email."
            )

        persona = Persona(
            id_organizacion=id_organizacion,
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
            telefono=datos.telefono,
            capacidad_horas_semana=datos.capacidad_horas_semana
        )

        try:
            self.repository.crear(persona)

            self.db.commit()

            return persona

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_persona: int,
        datos: PersonaUpdate,
        id_organizacion: int
    ) -> Persona:

        persona = self.repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:
            raise ValueError(
                "La persona no existe."
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        if "email" in datos_actualizados:

            persona_con_email = (
                self.repository.obtener_por_email_organizacion(
                    datos_actualizados["email"],
                    id_organizacion
                )
            )

            if (
                persona_con_email is not None
                and persona_con_email.id_persona != id_persona
            ):
                raise ValueError(
                    "El email ya está registrado para otra persona."
                )

        for campo, valor in datos_actualizados.items():
            setattr(
                persona,
                campo,
                valor
            )

        try:
            self.repository.actualizar(persona)

            self.db.commit()

            return persona

        except Exception:
            self.db.rollback()
            raise

    def activar(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> Persona:

        persona = self.repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:
            raise ValueError(
                "La persona no existe."
            )

        if persona.estado:
            raise ValueError(
                "La persona ya se encuentra activa."
            )

        try:
            self.repository.activar(persona)

            self.db.commit()

            return persona

        except Exception:
            self.db.rollback()
            raise

    def desactivar(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> Persona:

        persona = self.repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:
            raise ValueError(
                "La persona no existe."
            )

        if not persona.estado:
            raise ValueError(
                "La persona ya se encuentra inactiva."
            )

        try:
            self.repository.desactivar(persona)

            self.db.commit()

            return persona

        except Exception:
            self.db.rollback()
            raise