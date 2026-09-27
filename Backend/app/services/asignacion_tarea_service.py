from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.asignacion_tarea_model import AsignacionTarea

from app.repositories.asignacion_tarea_repository import (
    AsignacionTareaRepository
)

from app.repositories.tarea_repository import TareaRepository

from app.repositories.equipo_persona_repository import (
    EquipoPersonaRepository
)

from app.repositories.equipo_repository import EquipoRepository

from app.schemas.asignacion_tarea_schema import (
    AsignacionTareaCreate,
    AsignacionTareaUpdate
)


class AsignacionTareaService:

    ESTADOS_VALIDOS = {
        "ASIGNADA",
        "EN_PROGRESO",
        "FINALIZADA",
        "CANCELADA"
    }

    ESTADOS_ACTIVOS = {
        "ASIGNADA",
        "EN_PROGRESO"
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = AsignacionTareaRepository(db)

        self.tarea_repository = TareaRepository(db)

        self.equipo_persona_repository = (
            EquipoPersonaRepository(db)
        )

        self.equipo_repository = EquipoRepository(db)

    # ==========================================================
    # OBTENER TODOS
    # ==========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================

    def obtener_por_id(
        self,
        id_asignacion: int,
        id_organizacion: int
    ) -> Optional[AsignacionTarea]:

        return self.repository.obtener_por_id_y_organizacion(
            id_asignacion,
            id_organizacion
        )

    # ==========================================================
    # OBTENER POR TAREA
    # ==========================================================

    def obtener_por_tarea(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        tarea = self.tarea_repository.obtener_por_id_organizacion(
            id_tarea,
            id_organizacion
        )

        if tarea is None:

            raise FlowosException(
                message="La tarea indicada no existe.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_tarea_y_organizacion(
            id_tarea,
            id_organizacion
        )

    # ==========================================================
    # OBTENER POR EQUIPO-PERSONA
    # ==========================================================

    def obtener_por_equipo_persona(
        self,
        id_equipo_persona: int,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        equipo_persona = (
            self.equipo_persona_repository
            .obtener_por_id_y_organizacion(
                id_equipo_persona,
                id_organizacion
            )
        )

        if equipo_persona is None:

            raise FlowosException(
                message=(
                    "La relación equipo-persona indicada "
                    "no existe."
                ),
                code="EQUIPO_PERSONA_NO_EXISTE",
                status_code=404
            )

        return (
            self.repository
            .obtener_por_equipo_persona_y_organizacion(
                id_equipo_persona,
                id_organizacion
            )
        )

    # ==========================================================
    # CREAR ASIGNACIÓN
    # ==========================================================

    def crear(
        self,
        datos: AsignacionTareaCreate,
        id_organizacion: int
    ) -> AsignacionTarea:

        # ------------------------------------------------------
        # 1. VALIDAR TAREA
        # ------------------------------------------------------

        tarea = (
            self.tarea_repository
            .obtener_por_id_organizacion(
                datos.id_tarea,
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
        # 2. VALIDAR EQUIPO-PERSONA
        # ------------------------------------------------------

        equipo_persona = (
            self.equipo_persona_repository
            .obtener_por_id_y_organizacion(
                datos.id_equipo_persona,
                id_organizacion
            )
        )

        if equipo_persona is None:

            raise FlowosException(
                message=(
                    "La relación equipo-persona indicada "
                    "no existe."
                ),
                code="EQUIPO_PERSONA_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # 3. VALIDAR EQUIPO
        # ------------------------------------------------------

        equipo = (
            self.equipo_repository
            .obtener_por_id_y_organizacion(
                equipo_persona.id_equipo,
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
        # 4. EL EQUIPO DEBE ESTAR ACTIVO
        # ------------------------------------------------------

        if equipo.estado != "ACTIVO":

            raise FlowosException(
                message=(
                    "No se puede asignar una tarea a una "
                    "persona cuyo equipo no está activo."
                ),
                code="EQUIPO_NO_ACTIVO",
                status_code=400
            )

        # ------------------------------------------------------
        # 5. LA TAREA DEBE PERTENECER AL MISMO EQUIPO
        # ------------------------------------------------------

        if tarea.id_equipo != equipo.id_equipo:

            raise FlowosException(
                message=(
                    "La persona no pertenece al equipo "
                    "responsable de esta tarea."
                ),
                code="EQUIPOS_NO_COINCIDEN",
                status_code=409
            )

        # ------------------------------------------------------
        # 6. VALIDAR DUPLICADO
        # ------------------------------------------------------

        existente = (
            self.repository
            .obtener_por_tarea_y_persona(
                datos.id_tarea,
                datos.id_equipo_persona
            )
        )

        if existente is not None:

            raise FlowosException(
                message=(
                    "Esta persona ya está asignada "
                    "a la tarea."
                ),
                code="PERSONA_YA_ASIGNADA",
                status_code=409
            )

        # ------------------------------------------------------
        # 7. CREAR ASIGNACIÓN
        # ------------------------------------------------------

        asignacion = AsignacionTarea(
            id_tarea=datos.id_tarea,
            id_equipo_persona=datos.id_equipo_persona,
            fecha_asignacion=datos.fecha_asignacion,
            fecha_inicio=datos.fecha_inicio,
            fecha_limite=datos.fecha_limite,
            dedicacion=datos.dedicacion
        )

        try:

            self.repository.crear(
                asignacion
            )

            self.db.commit()

            return asignacion

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================

    def actualizar(
        self,
        id_asignacion: int,
        datos: AsignacionTareaUpdate,
        id_organizacion: int
    ) -> AsignacionTarea:

        # ------------------------------------------------------
        # 1. BUSCAR ASIGNACIÓN
        # ------------------------------------------------------

        asignacion = (
            self.repository
            .obtener_por_id_y_organizacion(
                id_asignacion,
                id_organizacion
            )
        )

        if asignacion is None:

            raise FlowosException(
                message="La asignación no existe.",
                code="ASIGNACION_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # ------------------------------------------------------
        # 2. DETERMINAR TAREA FINAL
        # ------------------------------------------------------

        id_tarea = datos_actualizados.get(
            "id_tarea",
            asignacion.id_tarea
        )

        # ------------------------------------------------------
        # 3. DETERMINAR EQUIPO-PERSONA FINAL
        # ------------------------------------------------------

        id_equipo_persona = datos_actualizados.get(
            "id_equipo_persona",
            asignacion.id_equipo_persona
        )

        # ------------------------------------------------------
        # 4. VALIDAR TAREA
        # ------------------------------------------------------

        tarea = (
            self.tarea_repository
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
        # 5. VALIDAR EQUIPO-PERSONA
        # ------------------------------------------------------

        equipo_persona = (
            self.equipo_persona_repository
            .obtener_por_id_y_organizacion(
                id_equipo_persona,
                id_organizacion
            )
        )

        if equipo_persona is None:

            raise FlowosException(
                message=(
                    "La relación equipo-persona indicada "
                    "no existe."
                ),
                code="EQUIPO_PERSONA_NO_EXISTE",
                status_code=404
            )

        # ------------------------------------------------------
        # 6. VALIDAR EQUIPO
        # ------------------------------------------------------

        equipo = (
            self.equipo_repository
            .obtener_por_id_y_organizacion(
                equipo_persona.id_equipo,
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
        # 7. VALIDAR EQUIPO ACTIVO
        # ------------------------------------------------------

        if equipo.estado != "ACTIVO":

            raise FlowosException(
                message=(
                    "No se puede asignar una tarea a una "
                    "persona cuyo equipo no está activo."
                ),
                code="EQUIPO_NO_ACTIVO",
                status_code=400
            )

        # ------------------------------------------------------
        # 8. VALIDAR QUE TAREA Y EQUIPO COINCIDAN
        # ------------------------------------------------------

        if tarea.id_equipo != equipo.id_equipo:

            raise FlowosException(
                message=(
                    "La persona no pertenece al equipo "
                    "responsable de esta tarea."
                ),
                code="EQUIPOS_NO_COINCIDEN",
                status_code=409
            )

        # ------------------------------------------------------
        # 9. VALIDAR DUPLICADO
        # ------------------------------------------------------

        existente = (
            self.repository
            .obtener_por_tarea_y_persona(
                id_tarea,
                id_equipo_persona
            )
        )

        if (
            existente is not None
            and existente.id_asignacion != id_asignacion
        ):

            raise FlowosException(
                message=(
                    "Esta persona ya está asignada "
                    "a la tarea."
                ),
                code="PERSONA_YA_ASIGNADA",
                status_code=409
            )

        # ------------------------------------------------------
        # 10. ACTUALIZAR
        # ------------------------------------------------------

        for campo, valor in datos_actualizados.items():

            setattr(
                asignacion,
                campo,
                valor
            )

        try:

            self.repository.actualizar(
                asignacion
            )

            self.db.commit()

            return asignacion

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # CAMBIAR ESTADO
    # ==========================================================

    def cambiar_estado(
        self,
        id_asignacion: int,
        nuevo_estado: str,
        id_organizacion: int
    ) -> AsignacionTarea:

        asignacion = (
            self.repository
            .obtener_por_id_y_organizacion(
                id_asignacion,
                id_organizacion
            )
        )

        if asignacion is None:

            raise FlowosException(
                message="La asignación no existe.",
                code="ASIGNACION_NO_EXISTE",
                status_code=404
            )

        nuevo_estado = nuevo_estado.strip().upper()

        if nuevo_estado not in self.ESTADOS_VALIDOS:

            raise FlowosException(
                message=(
                    "El estado de la asignación "
                    "no es válido."
                ),
                code="ESTADO_ASIGNACION_INVALIDO",
                status_code=400
            )

        try:

            self.repository.cambiar_estado(
                asignacion,
                nuevo_estado
            )

            self.db.commit()

            return asignacion

        except Exception:

            self.db.rollback()

            raise