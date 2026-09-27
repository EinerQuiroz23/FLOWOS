from typing import List

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.equipo_model import Equipo

from app.repositories.equipo_repository import EquipoRepository
from app.repositories.proyecto_repository import ProyectoRepository

from app.schemas.equipo_schema import (
    EquipoCreate,
    EquipoUpdate
)


class EquipoService:

    ESTADOS_VALIDOS = {
        "ACTIVO",
        "INACTIVO",
        "FINALIZADO"
    }

    def __init__(self, db: Session):
        self.db = db

        self.repository = EquipoRepository(db)
        self.proyecto_repository = ProyectoRepository(db)

    # ==========================================================
    # OBTENER TODOS LOS EQUIPOS DE LA ORGANIZACIÓN
    # ==========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[Equipo]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    # ==========================================================
    # OBTENER EQUIPO POR ID
    # ==========================================================

    def obtener_por_id(
        self,
        id_equipo: int,
        id_organizacion: int
    ) -> Equipo:

        equipo = self.repository.obtener_por_id_y_organizacion(
            id_equipo,
            id_organizacion
        )

        if equipo is None:
            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        return equipo

    # ==========================================================
    # OBTENER EQUIPOS DE UN PROYECTO
    # ==========================================================

    def obtener_por_proyecto(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> List[Equipo]:

        proyecto = self.proyecto_repository.obtener_por_id_organizacion(
            id_proyecto,
            id_organizacion
        )

        if proyecto is None:
            raise FlowosException(
                message="El proyecto indicado no existe.",
                code="PROYECTO_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_proyecto_y_organizacion(
            id_proyecto,
            id_organizacion
        )

    # ==========================================================
    # CREAR EQUIPO
    # ==========================================================

    def crear(
        self,
        datos: EquipoCreate,
        id_organizacion: int
    ) -> Equipo:

        proyecto = self.proyecto_repository.obtener_por_id_organizacion(
            datos.id_proyecto,
            id_organizacion
        )

        if proyecto is None:
            raise FlowosException(
                message="El proyecto indicado no existe.",
                code="PROYECTO_NO_EXISTE",
                status_code=404
            )

        equipo = Equipo(
            id_proyecto=datos.id_proyecto,
            nombre=datos.nombre,
            descripcion=datos.descripcion
        )

        try:

            self.repository.crear(equipo)

            self.db.commit()
            self.db.refresh(equipo)

            return equipo

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # ACTUALIZAR EQUIPO
    # ==========================================================

    def actualizar(
        self,
        id_equipo: int,
        datos: EquipoUpdate,
        id_organizacion: int
    ) -> Equipo:

        equipo = self.repository.obtener_por_id_y_organizacion(
            id_equipo,
            id_organizacion
        )

        if equipo is None:
            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # ------------------------------------------------------
        # SI CAMBIA DE PROYECTO, VALIDAR NUEVO PROYECTO
        # ------------------------------------------------------

        if "id_proyecto" in datos_actualizados:

            proyecto = (
                self.proyecto_repository
                .obtener_por_id_organizacion(
                    datos_actualizados["id_proyecto"],
                    id_organizacion
                )
            )

            if proyecto is None:
                raise FlowosException(
                    message="El proyecto indicado no existe.",
                    code="PROYECTO_NO_EXISTE",
                    status_code=404
                )

        # ------------------------------------------------------
        # ACTUALIZAR CAMPOS
        # ------------------------------------------------------

        for campo, valor in datos_actualizados.items():

            setattr(
                equipo,
                campo,
                valor
            )

        try:

            self.repository.actualizar(equipo)

            self.db.commit()
            self.db.refresh(equipo)

            return equipo

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # CAMBIAR ESTADO
    # ==========================================================

    def cambiar_estado(
        self,
        id_equipo: int,
        nuevo_estado: str,
        id_organizacion: int
    ) -> Equipo:

        equipo = self.repository.obtener_por_id_y_organizacion(
            id_equipo,
            id_organizacion
        )

        if equipo is None:
            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # NORMALIZAR Y VALIDAR ESTADO
        # ------------------------------------------------------

        nuevo_estado = nuevo_estado.strip().upper()

        if nuevo_estado not in self.ESTADOS_VALIDOS:

            raise FlowosException(
                message="El estado del equipo no es válido.",
                code="ESTADO_EQUIPO_INVALIDO",
                status_code=400
            )

        try:

            self.repository.cambiar_estado(
                equipo,
                nuevo_estado
            )

            self.db.commit()
            self.db.refresh(equipo)

            return equipo

        except Exception:

            self.db.rollback()

            raise
