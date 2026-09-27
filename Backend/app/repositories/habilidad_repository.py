from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.habilidad_model import Habilidad


class HabilidadRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[Habilidad]:
        consulta = select(Habilidad)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_habilidad: int
    ) -> Optional[Habilidad]:

        return self.db.get(
            Habilidad,
            id_habilidad
        )

    def obtener_por_nombre(
        self,
        nombre: str
    ) -> Optional[Habilidad]:

        consulta = select(Habilidad).where(
            Habilidad.nombre == nombre
        )

        return self.db.scalars(consulta).first()

    def obtener_activas(self) -> List[Habilidad]:

        consulta = select(Habilidad).where(
            Habilidad.estado == True
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def crear(
        self,
        habilidad: Habilidad
    ) -> Habilidad:

        self.db.add(habilidad)
        self.db.flush()

        return habilidad

    def actualizar(
        self,
        habilidad: Habilidad
    ) -> Habilidad:

        self.db.flush()

        return habilidad

    def cambiar_estado(
        self,
        habilidad: Habilidad,
        nuevo_estado: bool
    ) -> Habilidad:

        habilidad.estado = nuevo_estado

        self.db.flush()

        return habilidad