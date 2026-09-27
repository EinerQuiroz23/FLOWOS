from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo_persona_model import EquipoPersona
from app.models.equipo_model import Equipo
from app.models.proyecto_model import Proyecto
from app.models.persona_model import Persona


class EquipoPersonaRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[EquipoPersona]:
        consulta = select(EquipoPersona)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_equipo_persona: int
    ) -> Optional[EquipoPersona]:

        return self.db.get(
            EquipoPersona,
            id_equipo_persona
        )

    def obtener_por_equipo(
        self,
        id_equipo: int
    ) -> List[EquipoPersona]:

        consulta = select(EquipoPersona).where(
            EquipoPersona.id_equipo == id_equipo
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_persona(
        self,
        id_persona: int
    ) -> List[EquipoPersona]:

        consulta = select(EquipoPersona).where(
            EquipoPersona.id_persona == id_persona
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_equipo_y_persona(
        self,
        id_equipo: int,
        id_persona: int
    ) -> Optional[EquipoPersona]:

        consulta = select(EquipoPersona).where(
            EquipoPersona.id_equipo == id_equipo,
            EquipoPersona.id_persona == id_persona
        )

        return self.db.scalars(consulta).first()

    def obtener_integrantes_activos(
        self,
        id_equipo: int
    ) -> List[EquipoPersona]:

        consulta = select(EquipoPersona).where(
            EquipoPersona.id_equipo == id_equipo,
            EquipoPersona.fecha_fin.is_(None)
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # MÉTODOS CON AISLAMIENTO POR ORGANIZACIÓN
    # ==========================================================

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Equipo,
                EquipoPersona.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_y_organizacion(
        self,
        id_equipo_persona: int,
        id_organizacion: int
    ) -> Optional[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Equipo,
                EquipoPersona.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                EquipoPersona.id_equipo_persona == id_equipo_persona,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_equipo_y_organizacion(
        self,
        id_equipo: int,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Equipo,
                EquipoPersona.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                EquipoPersona.id_equipo == id_equipo,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_persona_y_organizacion(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Persona,
                EquipoPersona.id_persona == Persona.id_persona
            )
            .where(
                EquipoPersona.id_persona == id_persona,
                Persona.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_equipo_y_persona_y_organizacion(
        self,
        id_equipo: int,
        id_persona: int,
        id_organizacion: int
    ) -> Optional[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Equipo,
                EquipoPersona.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                EquipoPersona.id_equipo == id_equipo,
                EquipoPersona.id_persona == id_persona,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_integrantes_activos_por_organizacion(
        self,
        id_equipo: int,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        consulta = (
            select(EquipoPersona)
            .join(
                Equipo,
                EquipoPersona.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                EquipoPersona.id_equipo == id_equipo,
                EquipoPersona.fecha_fin.is_(None),
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # PERSISTENCIA
    # ==========================================================

    def crear(
        self,
        equipo_persona: EquipoPersona
    ) -> EquipoPersona:

        self.db.add(equipo_persona)

        self.db.flush()

        return equipo_persona

    def actualizar(
        self,
        equipo_persona: EquipoPersona
    ) -> EquipoPersona:

        self.db.flush()

        return equipo_persona

    def finalizar(
        self,
        equipo_persona: EquipoPersona
    ) -> EquipoPersona:

        from datetime import datetime

        equipo_persona.fecha_fin = datetime.now()

        self.db.flush()

        return equipo_persona