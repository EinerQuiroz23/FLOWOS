from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.proyecto_model import Proyecto


class ProyectoRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[Proyecto]:
        consulta = select(Proyecto)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_proyecto: int
    ) -> Optional[Proyecto]:

        return self.db.get(Proyecto, id_proyecto)

    def obtener_por_nombre(
        self,
        nombre: str
    ) -> Optional[Proyecto]:

        consulta = select(Proyecto).where(
            Proyecto.nombre == nombre
        )

        return self.db.scalars(consulta).first()

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[Proyecto]:

        consulta = select(Proyecto).where(
            Proyecto.id_organizacion == id_organizacion
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_organizacion(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> Optional[Proyecto]:

        consulta = select(Proyecto).where(
            Proyecto.id_proyecto == id_proyecto,
            Proyecto.id_organizacion == id_organizacion
        )

        return self.db.scalars(consulta).first()

    def crear(
        self,
        proyecto: Proyecto
    ) -> Proyecto:

        self.db.add(proyecto)
        self.db.flush()

        return proyecto

    def actualizar(
        self,
        proyecto: Proyecto
    ) -> Proyecto:

        self.db.flush()

        return proyecto

    def cambiar_estado(
        self,
        proyecto: Proyecto,
        nuevo_estado: str
    ) -> Proyecto:

        proyecto.estado = nuevo_estado
        self.db.flush()

        return proyecto