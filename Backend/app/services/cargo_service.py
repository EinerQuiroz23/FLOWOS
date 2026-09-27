from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.cargo_model import Cargo
from app.repositories.cargo_repository import CargoRepository
from app.schemas.cargo_schema import (
    CargoCreate,
    CargoUpdate
)


class CargoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CargoRepository(db)

    def obtener_todos(self) -> List[Cargo]:
        return self.repository.obtener_todos()

    def obtener_por_id(
        self,
        id_cargo: int
    ) -> Optional[Cargo]:

        return self.repository.obtener_por_id(
            id_cargo
        )

    def crear(
        self,
        datos: CargoCreate
    ) -> Cargo:

        existente = self.repository.obtener_por_nombre(
            datos.nombre
        )

        if existente is not None:
            raise ValueError(
                "Ya existe un cargo con ese nombre."
            )

        cargo = Cargo(
            nombre=datos.nombre,
            descripcion=datos.descripcion
        )

        try:
            self.repository.crear(cargo)

            self.db.commit()

            return cargo

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_cargo: int,
        datos: CargoUpdate
    ) -> Cargo:

        cargo = self.repository.obtener_por_id(
            id_cargo
        )

        if cargo is None:
            raise ValueError(
                "El cargo no existe."
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        if "nombre" in datos_actualizados:

            existente = self.repository.obtener_por_nombre(
                datos_actualizados["nombre"]
            )

            if (
                existente is not None
                and existente.id_cargo != id_cargo
            ):
                raise ValueError(
                    "Ya existe otro cargo con ese nombre."
                )

        for campo, valor in datos_actualizados.items():
            setattr(
                cargo,
                campo,
                valor
            )

        try:
            self.repository.actualizar(cargo)

            self.db.commit()

            return cargo

        except Exception:
            self.db.rollback()
            raise

    def activar(
        self,
        id_cargo: int
    ) -> Cargo:

        cargo = self.repository.obtener_por_id(
            id_cargo
        )

        if cargo is None:
            raise ValueError(
                "El cargo no existe."
            )

        if cargo.estado:
            raise ValueError(
                "El cargo ya está activo."
            )

        try:
            self.repository.cambiar_estado(
                cargo,
                True
            )

            self.db.commit()

            return cargo

        except Exception:
            self.db.rollback()
            raise

    def desactivar(
        self,
        id_cargo: int
    ) -> Cargo:

        cargo = self.repository.obtener_por_id(
            id_cargo
        )

        if cargo is None:
            raise ValueError(
                "El cargo no existe."
            )

        if not cargo.estado:
            raise ValueError(
                "El cargo ya está inactivo."
            )

        try:
            self.repository.cambiar_estado(
                cargo,
                False
            )

            self.db.commit()

            return cargo

        except Exception:
            self.db.rollback()
            raise