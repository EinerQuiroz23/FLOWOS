from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.equipo_persona_model import EquipoPersona

from app.repositories.equipo_persona_repository import (
    EquipoPersonaRepository
)

from app.repositories.equipo_repository import EquipoRepository
from app.repositories.persona_repository import PersonaRepository

from app.schemas.equipo_persona_schema import (
    EquipoPersonaCreate,
    EquipoPersonaUpdate
)


class EquipoPersonaService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = EquipoPersonaRepository(db)

        self.equipo_repository = EquipoRepository(db)

        self.persona_repository = PersonaRepository(db)

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    def obtener_por_id(
        self,
        id_equipo_persona: int,
        id_organizacion: int
    ) -> Optional[EquipoPersona]:

        return self.repository.obtener_por_id_y_organizacion(
            id_equipo_persona,
            id_organizacion
        )

    def obtener_por_equipo(
        self,
        id_equipo: int,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        # -----------------------------------
        # VALIDAR EQUIPO
        # -----------------------------------

        equipo = self.equipo_repository.obtener_por_id_y_organizacion(
            id_equipo,
            id_organizacion
        )

        if equipo is None:

            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # OBTENER PERSONAS
        # -----------------------------------

        return self.repository.obtener_por_equipo_y_organizacion(
            id_equipo,
            id_organizacion
        )

    def obtener_por_persona(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[EquipoPersona]:

        # -----------------------------------
        # VALIDAR PERSONA
        # -----------------------------------

        persona = self.persona_repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:

            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # OBTENER EQUIPOS
        # -----------------------------------

        return self.repository.obtener_por_persona_y_organizacion(
            id_persona,
            id_organizacion
        )

    # ==========================================================
    # CREAR
    # ==========================================================

    def crear(
        self,
        datos: EquipoPersonaCreate,
        id_organizacion: int
    ) -> EquipoPersona:

        # -----------------------------------
        # VALIDAR EQUIPO
        # -----------------------------------

        equipo = self.equipo_repository.obtener_por_id_y_organizacion(
            datos.id_equipo,
            id_organizacion
        )

        if equipo is None:

            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR PERSONA
        # -----------------------------------

        persona = self.persona_repository.obtener_por_id_organizacion(
            datos.id_persona,
            id_organizacion
        )

        if persona is None:

            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------

        existente = (
            self.repository
            .obtener_por_equipo_y_persona_y_organizacion(
                datos.id_equipo,
                datos.id_persona,
                id_organizacion
            )
        )

        if existente is not None:

            raise FlowosException(
                message="La persona ya pertenece a este equipo.",
                code="PERSONA_YA_PERTENECE_AL_EQUIPO",
                status_code=409
            )

        # -----------------------------------
        # CREAR RELACIÓN
        # -----------------------------------

        equipo_persona = EquipoPersona(
            id_equipo=datos.id_equipo,
            id_persona=datos.id_persona,
            rol_equipo=datos.rol_equipo,
            dedicacion=datos.dedicacion,
            fecha_inicio=datos.fecha_inicio,
            fecha_fin=datos.fecha_fin
        )

        try:

            self.repository.crear(
                equipo_persona
            )

            self.db.commit()

            return equipo_persona

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================

    def actualizar(
        self,
        id_equipo_persona: int,
        datos: EquipoPersonaUpdate,
        id_organizacion: int
    ) -> EquipoPersona:

        # -----------------------------------
        # BUSCAR RELACIÓN
        # -----------------------------------

        registro = (
            self.repository
            .obtener_por_id_y_organizacion(
                id_equipo_persona,
                id_organizacion
            )
        )

        if registro is None:

            raise FlowosException(
                message="La relación equipo-persona no existe.",
                code="EQUIPO_PERSONA_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # -----------------------------------
        # DETERMINAR EQUIPO FINAL
        # -----------------------------------

        id_equipo = datos_actualizados.get(
            "id_equipo",
            registro.id_equipo
        )

        # -----------------------------------
        # DETERMINAR PERSONA FINAL
        # -----------------------------------

        id_persona = datos_actualizados.get(
            "id_persona",
            registro.id_persona
        )

        # -----------------------------------
        # VALIDAR EQUIPO
        # -----------------------------------

        equipo = self.equipo_repository.obtener_por_id_y_organizacion(
            id_equipo,
            id_organizacion
        )

        if equipo is None:

            raise FlowosException(
                message="El equipo indicado no existe.",
                code="EQUIPO_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR PERSONA
        # -----------------------------------

        persona = self.persona_repository.obtener_por_id_organizacion(
            id_persona,
            id_organizacion
        )

        if persona is None:

            raise FlowosException(
                message="La persona indicada no existe.",
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------

        existente = (
            self.repository
            .obtener_por_equipo_y_persona_y_organizacion(
                id_equipo,
                id_persona,
                id_organizacion
            )
        )

        if (
            existente is not None
            and existente.id_equipo_persona != id_equipo_persona
        ):

            raise FlowosException(
                message="La persona ya pertenece a este equipo.",
                code="PERSONA_YA_PERTENECE_AL_EQUIPO",
                status_code=409
            )

        # -----------------------------------
        # ACTUALIZAR
        # -----------------------------------

        for campo, valor in datos_actualizados.items():

            setattr(
                registro,
                campo,
                valor
            )

        try:

            self.repository.actualizar(
                registro
            )

            self.db.commit()

            return registro

        except Exception:

            self.db.rollback()

            raise

    # ==========================================================
    # FINALIZAR PARTICIPACIÓN
    # ==========================================================

    def finalizar(
        self,
        id_equipo_persona: int,
        id_organizacion: int
    ) -> EquipoPersona:

        registro = (
            self.repository
            .obtener_por_id_y_organizacion(
                id_equipo_persona,
                id_organizacion
            )
        )

        if registro is None:

            raise FlowosException(
                message="La relación equipo-persona no existe.",
                code="EQUIPO_PERSONA_NO_EXISTE",
                status_code=404
            )

        if registro.fecha_fin is not None:

            raise FlowosException(
                message="La participación de la persona ya fue finalizada.",
                code="PARTICIPACION_YA_FINALIZADA",
                status_code=409
            )

        try:

            self.repository.finalizar(
                registro
            )

            self.db.commit()

            return registro

        except Exception:

            self.db.rollback()

            raise