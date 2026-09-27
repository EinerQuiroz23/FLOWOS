from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.persona_habilidad_model import PersonaHabilidad

from app.repositories.persona_habilidad_repository import (
    PersonaHabilidadRepository
)
from app.repositories.persona_repository import PersonaRepository
from app.repositories.habilidad_repository import HabilidadRepository
from app.repositories.nivel_habilidad_repository import (
    NivelHabilidadRepository
)

from app.schemas.persona_habilidad_schema import (
    PersonaHabilidadCreate,
    PersonaHabilidadUpdate
)


class PersonaHabilidadService:

    def __init__(self, db: Session):
        self.db = db

        self.repository = PersonaHabilidadRepository(db)
        self.persona_repository = PersonaRepository(db)
        self.habilidad_repository = HabilidadRepository(db)
        self.nivel_repository = NivelHabilidadRepository(db)

    # =========================================================
    # OBTENER TODOS
    # =========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    # =========================================================
    # OBTENER POR ID
    # =========================================================

    def obtener_por_id(
        self,
        id_persona_habilidad: int,
        id_organizacion: int
    ) -> Optional[PersonaHabilidad]:

        return self.repository.obtener_por_id_y_organizacion(
            id_persona_habilidad,
            id_organizacion
        )

    # =========================================================
    # OBTENER POR PERSONA
    # =========================================================

    def obtener_por_persona(
        self,
        id_persona: int,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        return self.repository.obtener_por_persona_y_organizacion(
            id_persona,
            id_organizacion
        )

    # =========================================================
    # OBTENER POR HABILIDAD
    # =========================================================

    def obtener_por_habilidad(
        self,
        id_habilidad: int,
        id_organizacion: int
    ) -> List[PersonaHabilidad]:

        return self.repository.obtener_por_habilidad_y_organizacion(
            id_habilidad,
            id_organizacion
        )

    # =========================================================
    # CREAR
    # =========================================================

    def crear(
        self,
        datos: PersonaHabilidadCreate,
        id_organizacion: int
    ) -> PersonaHabilidad:

        # -----------------------------------------------------
        # VALIDAR PERSONA Y ORGANIZACIÓN
        # -----------------------------------------------------

        persona = (
            self.persona_repository.obtener_por_id_organizacion(
                datos.id_persona,
                id_organizacion
            )
        )

        if persona is None:
            raise FlowosException(
                message=(
                    "La persona indicada no existe "
                    "en la organización."
                ),
                code="PERSONA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------------------------
        # VALIDAR HABILIDAD
        # -----------------------------------------------------

        habilidad = self.habilidad_repository.obtener_por_id(
            datos.id_habilidad
        )

        if habilidad is None:
            raise FlowosException(
                message="La habilidad indicada no existe.",
                code="HABILIDAD_NO_EXISTE",
                status_code=404
            )

        if not habilidad.estado:
            raise FlowosException(
                message="La habilidad indicada está inactiva.",
                code="HABILIDAD_INACTIVA",
                status_code=400
            )

        # -----------------------------------------------------
        # VALIDAR NIVEL
        # -----------------------------------------------------

        nivel = self.nivel_repository.obtener_por_id(
            datos.id_nivel
        )

        if nivel is None:
            raise FlowosException(
                message="El nivel de habilidad indicado no existe.",
                code="NIVEL_HABILIDAD_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------------------------

        relacion_existente = (
            self.repository
            .obtener_por_persona_y_habilidad_y_organizacion(
                datos.id_persona,
                datos.id_habilidad,
                id_organizacion
            )
        )

        if relacion_existente is not None:
            raise FlowosException(
                message=(
                    "La persona ya tiene registrada "
                    "esta habilidad."
                ),
                code="PERSONA_HABILIDAD_YA_EXISTE",
                status_code=409
            )

        # -----------------------------------------------------
        # CREAR RELACIÓN
        # -----------------------------------------------------

        persona_habilidad = PersonaHabilidad(
            id_persona=datos.id_persona,
            id_habilidad=datos.id_habilidad,
            id_nivel=datos.id_nivel,
            años_experiencia=datos.años_experiencia
        )

        try:
            self.repository.crear(persona_habilidad)

            self.db.commit()
            self.db.refresh(persona_habilidad)

            return persona_habilidad

        except Exception:
            self.db.rollback()
            raise

    # =========================================================
    # ACTUALIZAR
    # =========================================================

    def actualizar(
        self,
        id_persona_habilidad: int,
        datos: PersonaHabilidadUpdate,
        id_organizacion: int
    ) -> PersonaHabilidad:

        # -----------------------------------------------------
        # BUSCAR RELACIÓN DENTRO DE LA ORGANIZACIÓN
        # -----------------------------------------------------

        persona_habilidad = (
            self.repository
            .obtener_por_id_y_organizacion(
                id_persona_habilidad,
                id_organizacion
            )
        )

        if persona_habilidad is None:
            raise FlowosException(
                message=(
                    "La relación persona-habilidad "
                    "no existe en la organización."
                ),
                code="PERSONA_HABILIDAD_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------------------------
        # OBTENER DATOS A ACTUALIZAR
        # -----------------------------------------------------

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # -----------------------------------------------------
        # VALIDAR PERSONA
        # -----------------------------------------------------

        if "id_persona" in datos_actualizados:

            persona = (
                self.persona_repository
                .obtener_por_id_organizacion(
                    datos_actualizados["id_persona"],
                    id_organizacion
                )
            )

            if persona is None:
                raise FlowosException(
                    message=(
                        "La persona indicada no existe "
                        "en la organización."
                    ),
                    code="PERSONA_NO_EXISTE",
                    status_code=404
                )

        # -----------------------------------------------------
        # VALIDAR HABILIDAD
        # -----------------------------------------------------

        if "id_habilidad" in datos_actualizados:

            habilidad = self.habilidad_repository.obtener_por_id(
                datos_actualizados["id_habilidad"]
            )

            if habilidad is None:
                raise FlowosException(
                    message="La habilidad indicada no existe.",
                    code="HABILIDAD_NO_EXISTE",
                    status_code=404
                )

            if not habilidad.estado:
                raise FlowosException(
                    message="La habilidad indicada está inactiva.",
                    code="HABILIDAD_INACTIVA",
                    status_code=400
                )

        # -----------------------------------------------------
        # VALIDAR NIVEL
        # -----------------------------------------------------

        if "id_nivel" in datos_actualizados:

            nivel = self.nivel_repository.obtener_por_id(
                datos_actualizados["id_nivel"]
            )

            if nivel is None:
                raise FlowosException(
                    message=(
                        "El nivel de habilidad indicado "
                        "no existe."
                    ),
                    code="NIVEL_HABILIDAD_NO_EXISTE",
                    status_code=404
                )

        # -----------------------------------------------------
        # DETERMINAR VALORES FINALES
        # -----------------------------------------------------

        id_persona = datos_actualizados.get(
            "id_persona",
            persona_habilidad.id_persona
        )

        id_habilidad = datos_actualizados.get(
            "id_habilidad",
            persona_habilidad.id_habilidad
        )

        # -----------------------------------------------------
        # VALIDAR PERSONA FINAL
        # -----------------------------------------------------

        persona_final = (
            self.persona_repository
            .obtener_por_id_organizacion(
                id_persona,
                id_organizacion
            )
        )

        if persona_final is None:
            raise FlowosException(
                message=(
                    "La persona indicada no pertenece "
                    "a la organización."
                ),
                code="PERSONA_NO_PERTENECE_ORGANIZACION",
                status_code=403
            )

        # -----------------------------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------------------------

        relacion_existente = (
            self.repository
            .obtener_por_persona_y_habilidad_y_organizacion(
                id_persona,
                id_habilidad,
                id_organizacion
            )
        )

        if (
            relacion_existente is not None
            and relacion_existente.id_persona_habilidad
            != id_persona_habilidad
        ):
            raise FlowosException(
                message=(
                    "La persona ya tiene registrada "
                    "esta habilidad."
                ),
                code="PERSONA_HABILIDAD_YA_EXISTE",
                status_code=409
            )

        # -----------------------------------------------------
        # ACTUALIZAR
        # -----------------------------------------------------

        for campo, valor in datos_actualizados.items():
            setattr(
                persona_habilidad,
                campo,
                valor
            )

        try:
            self.repository.actualizar(
                persona_habilidad
            )

            self.db.commit()
            self.db.refresh(persona_habilidad)

            return persona_habilidad

        except Exception:
            self.db.rollback()
            raise
