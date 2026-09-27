from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cargo_model import Cargo


class CargoRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[Cargo]:
        consulta = select(Cargo)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_cargo: int
    ) -> Optional[Cargo]:

        return self.db.get(
            Cargo,
            id_cargo
        )

    def obtener_por_nombre(
        self,
        nombre: str
    ) -> Optional[Cargo]:

        consulta = select(Cargo).where(
            Cargo.nombre == nombre
        )

        return self.db.scalars(consulta).first()

    def obtener_activos(self) -> List[Cargo]:

        consulta = select(Cargo).where(
            Cargo.estado == True
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def crear(
        self,
        cargo: Cargo
    ) -> Cargo:

        self.db.add(cargo)
        self.db.flush()

        return cargo

    def actualizar(
        self,
        cargo: Cargo
    ) -> Cargo:

        self.db.flush()

        return cargo

    def cambiar_estado(
        self,
        cargo: Cargo,
        nuevo_estado: bool
    ) -> Cargo:

        cargo.estado = nuevo_estado

        self.db.flush()

        return cargo