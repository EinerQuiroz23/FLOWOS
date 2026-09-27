from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.nivel_habilidad_model import NivelHabilidad


class NivelHabilidadRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[NivelHabilidad]:
        consulta = select(NivelHabilidad)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_nivel: int
    ) -> Optional[NivelHabilidad]:

        return self.db.get(
            NivelHabilidad,
            id_nivel
        )

    def obtener_por_nombre(
        self,
        nombre: str
    ) -> Optional[NivelHabilidad]:

        consulta = select(NivelHabilidad).where(
            NivelHabilidad.nombre == nombre
        )

        return self.db.scalars(consulta).first()

    def obtener_activos(self) -> List[NivelHabilidad]:

        consulta = select(NivelHabilidad).where(
            NivelHabilidad.estado == True
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def crear(
        self,
        nivel: NivelHabilidad
    ) -> NivelHabilidad:

        self.db.add(nivel)
        self.db.flush()

        return nivel

    def actualizar(
        self,
        nivel: NivelHabilidad
    ) -> NivelHabilidad:

        self.db.flush()

        return nivel