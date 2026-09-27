from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo_model import Equipo
from app.models.proyecto_model import Proyecto


class EquipoRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[Equipo]:
        consulta = select(Equipo)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_equipo: int
    ) -> Optional[Equipo]:

        return self.db.get(Equipo, id_equipo)

    def obtener_por_proyecto(
        self,
        id_proyecto: int
    ) -> List[Equipo]:

        consulta = select(Equipo).where(
            Equipo.id_proyecto == id_proyecto
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[Equipo]:

        consulta = (
            select(Equipo)
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
        id_equipo: int,
        id_organizacion: int
    ) -> Optional[Equipo]:

        consulta = (
            select(Equipo)
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Equipo.id_equipo == id_equipo,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_proyecto_y_organizacion(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> List[Equipo]:

        consulta = (
            select(Equipo)
            .join(
                Proyecto,
                Equipo.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Equipo.id_proyecto == id_proyecto,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def crear(
        self,
        equipo: Equipo
    ) -> Equipo:

        self.db.add(equipo)
        self.db.flush()

        return equipo

    def actualizar(
        self,
        equipo: Equipo
    ) -> Equipo:

        self.db.flush()

        return equipo

    def cambiar_estado(
        self,
        equipo: Equipo,
        nuevo_estado: str
    ) -> Equipo:

        equipo.estado = nuevo_estado

        self.db.flush()

        return equipo