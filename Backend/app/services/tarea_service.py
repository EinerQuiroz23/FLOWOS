from typing import List

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.tarea_model import Tarea

from app.repositories.tarea_repository import TareaRepository
from app.repositories.proyecto_repository import ProyectoRepository
from app.repositories.equipo_repository import EquipoRepository

from app.schemas.tarea_schema import (
    TareaCreate,
    TareaUpdate
)


class TareaService:

    ESTADOS_VALIDOS = {
        "PENDIENTE",
        "EN_PROGRESO",
        "BLOQUEADA",
        "FINALIZADA",
        "CANCELADA"
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = TareaRepository(db)

        self.proyecto_repository = ProyectoRepository(db)

        self.equipo_repository = EquipoRepository(db)

    # ==========================================================
    # OBTENER TODAS LAS TAREAS DE LA ORGANIZACIÓN
    # ==========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[Tarea]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    # ==========================================================
    # OBTENER TAREA POR ID
    # ==========================================================

    def obtener_por_id(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> Tarea:

        tarea = self.repository.obtener_por_id_organizacion(
            id_tarea,
            id_organizacion
        )

        if tarea is None:

            raise FlowosException(
                message="La tarea indicada no existe.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        return tarea

    # ==========================================================
    # OBTENER TAREAS DE UN PROYECTO
    # ==========================================================

    def obtener_por_proyecto(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> List[Tarea]:

        proyecto = (
            self.proyecto_repository
            .obtener_por_id_organizacion(
                id_proyecto,
                id_organizacion
            )
        )

        if proyecto is None:

            raise FlowosException(
                message="El proyecto indicado no existe.",
                code="PROYECTO_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_proyecto_organizacion(
            id_proyecto,
            id_organizacion
        )

    # ==========================================================
    # CREAR TAREA
    # ==========================================================

    def crear(
        self,
        datos: TareaCreate,
        id_organizacion: int
    ) -> Tarea:

        # ------------------------------------------------------
        # VALIDAR PROYECTO
        # ------------------------------------------------------

        proyecto = (
            self.proyecto_repository
            .obtener_por_id_organizacion(
                datos.id_proyecto,
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
        # VALIDAR EQUIPO
        # ------------------------------------------------------

        equipo = (
            self.equipo_repository
            .obtener_por_id_y_organizacion(
                datos.id_equipo,
                id_organizacion
            )
        )

        if equipo is None:

            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # VALIDAR EQUIPO → PROYECTO
        # ------------------------------------------------------

        if equipo.id_proyecto != datos.id_proyecto:

            raise FlowosException(
                message=(
                    "El equipo indicado no pertenece "
                    "al proyecto de la tarea."
                ),
                code="EQUIPO_NO_PERTENECE_AL_PROYECTO",
                status_code=400
            )

        # ------------------------------------------------------
        # CREAR TAREA
        # ------------------------------------------------------

        tarea = Tarea(
            id_proyecto=datos.id_proyecto,
            id_equipo=datos.id_equipo,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            prioridad=datos.prioridad,
            horas_estimadas=datos.horas_estimadas,
            fecha_inicio=datos.fecha_inicio,
            fecha_limite=datos.fecha_limite
        )

        try:

            self.repository.crear(tarea)

            self.db.commit()
            self.db.refresh(tarea)

            return tarea

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # ACTUALIZAR TAREA
    # ==========================================================

    def actualizar(
        self,
        id_tarea: int,
        datos: TareaUpdate,
        id_organizacion: int
    ) -> Tarea:

        tarea = (
            self.repository
            .obtener_por_id_organizacion(
                id_tarea,
                id_organizacion
            )
        )

        if tarea is None:

            raise FlowosException(
                message="La tarea indicada no existe.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # ------------------------------------------------------
        # DETERMINAR PROYECTO Y EQUIPO FINALES
        # ------------------------------------------------------

        nuevo_id_proyecto = datos_actualizados.get(
            "id_proyecto",
            tarea.id_proyecto
        )

        nuevo_id_equipo = datos_actualizados.get(
            "id_equipo",
            tarea.id_equipo
        )

        # ------------------------------------------------------
        # VALIDAR PROYECTO
        # ------------------------------------------------------

        proyecto = (
            self.proyecto_repository
            .obtener_por_id_organizacion(
                nuevo_id_proyecto,
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
        # VALIDAR EQUIPO
        # ------------------------------------------------------

        equipo = (
            self.equipo_repository
            .obtener_por_id_y_organizacion(
                nuevo_id_equipo,
                id_organizacion
            )
        )

        if equipo is None:

            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # VALIDAR EQUIPO → PROYECTO
        # ------------------------------------------------------

        if equipo.id_proyecto != nuevo_id_proyecto:

            raise FlowosException(
                message=(
                    "El equipo indicado no pertenece "
                    "al proyecto de la tarea."
                ),
                code="EQUIPO_NO_PERTENECE_AL_PROYECTO",
                status_code=400
            )

        # ------------------------------------------------------
        # ACTUALIZAR CAMPOS
        # ------------------------------------------------------

        for campo, valor in datos_actualizados.items():

            setattr(
                tarea,
                campo,
                valor
            )

        try:

            self.repository.actualizar(tarea)

            self.db.commit()
            self.db.refresh(tarea)

            return tarea

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # CAMBIAR ESTADO
    # ==========================================================

    def cambiar_estado(
        self,
        id_tarea: int,
        nuevo_estado: str,
        id_organizacion: int
    ) -> Tarea:

        tarea = (
            self.repository
            .obtener_por_id_organizacion(
                id_tarea,
                id_organizacion
            )
        )

        if tarea is None:

            raise FlowosException(
                message="La tarea indicada no existe.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # VALIDAR ESTADO
        # ------------------------------------------------------

        nuevo_estado = nuevo_estado.strip().upper()

        if nuevo_estado not in self.ESTADOS_VALIDOS:

            raise FlowosException(
                message="El estado indicado no es válido.",
                code="ESTADO_TAREA_INVALIDO",
                status_code=400
            )

        # ------------------------------------------------------
        # ACTUALIZAR ESTADO
        # ------------------------------------------------------

        try:

            self.repository.cambiar_estado(
                tarea,
                nuevo_estado
            )

            self.db.commit()
            self.db.refresh(tarea)

            return tarea

        except Exception:

            self.db.rollback()

            raise