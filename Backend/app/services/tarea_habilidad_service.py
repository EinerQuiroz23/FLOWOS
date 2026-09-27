from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.models.tarea_habilidad_model import TareaHabilidad

from app.repositories.tarea_habilidad_repository import (
    TareaHabilidadRepository
)

from app.repositories.tarea_repository import TareaRepository
from app.repositories.habilidad_repository import HabilidadRepository
from app.repositories.nivel_habilidad_repository import (
    NivelHabilidadRepository
)

from app.schemas.tarea_habilidad_schema import (
    TareaHabilidadCreate,
    TareaHabilidadUpdate
)


class TareaHabilidadService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = TareaHabilidadRepository(db)

        self.tarea_repository = TareaRepository(db)
        self.habilidad_repository = HabilidadRepository(db)
        self.nivel_habilidad_repository = NivelHabilidadRepository(db)

    # =========================================================
    # CONSULTAS
    # =========================================================

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    def obtener_por_id(
        self,
        id_tarea_habilidad: int,
        id_organizacion: int
    ) -> Optional[TareaHabilidad]:

        return self.repository.obtener_por_id_y_organizacion(
            id_tarea_habilidad,
            id_organizacion
        )

    def obtener_por_tarea(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        tarea = self.tarea_repository.obtener_por_id_organizacion(
            id_tarea,
            id_organizacion
        )

        if tarea is None:
            raise FlowosException(
                message="La tarea no existe en esta organización.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_tarea_y_organizacion(
            id_tarea,
            id_organizacion
        )

    def obtener_por_habilidad(
        self,
        id_habilidad: int,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        habilidad = self.habilidad_repository.obtener_por_id(
            id_habilidad
        )

        if habilidad is None:
            raise FlowosException(
                message="La habilidad indicada no existe.",
                code="HABILIDAD_NO_EXISTE",
                status_code=404
            )

        return self.repository.obtener_por_habilidad_y_organizacion(
            id_habilidad,
            id_organizacion
        )

    # =========================================================
    # CREAR
    # =========================================================

    def crear(
        self,
        datos: TareaHabilidadCreate,
        id_organizacion: int
    ) -> TareaHabilidad:

        # -----------------------------------
        # VALIDAR TAREA Y ORGANIZACIÓN
        # -----------------------------------

        tarea = self.tarea_repository.obtener_por_id_organizacion(
            datos.id_tarea,
            id_organizacion
        )

        if tarea is None:
            raise FlowosException(
                message="La tarea no existe en esta organización.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR HABILIDAD
        # -----------------------------------

        habilidad = self.habilidad_repository.obtener_por_id(
            datos.id_habilidad
        )

        if habilidad is None:
            raise FlowosException(
                message="La habilidad indicada no existe.",
                code="HABILIDAD_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR NIVEL
        # -----------------------------------

        nivel = self.nivel_habilidad_repository.obtener_por_id(
            datos.id_nivel
        )

        if nivel is None:
            raise FlowosException(
                message="El nivel de habilidad indicado no existe.",
                code="NIVEL_HABILIDAD_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------

        relacion_existente = (
            self.repository
            .obtener_por_tarea_y_habilidad_y_organizacion(
                datos.id_tarea,
                datos.id_habilidad,
                id_organizacion
            )
        )

        if relacion_existente is not None:
            raise FlowosException(
                message=(
                    "La tarea ya tiene registrada "
                    "esta habilidad."
                ),
                code="HABILIDAD_YA_REGISTRADA_EN_TAREA",
                status_code=409
            )

        # -----------------------------------
        # CREAR
        # -----------------------------------

        tarea_habilidad = TareaHabilidad(
            id_tarea=datos.id_tarea,
            id_habilidad=datos.id_habilidad,
            id_nivel=datos.id_nivel
        )

        try:

            self.repository.crear(
                tarea_habilidad
            )

            self.db.commit()

            return tarea_habilidad

        except Exception:

            self.db.rollback()

            raise

    # =========================================================
    # ACTUALIZAR
    # =========================================================

    def actualizar(
        self,
        id_tarea_habilidad: int,
        datos: TareaHabilidadUpdate,
        id_organizacion: int
    ) -> TareaHabilidad:

        # -----------------------------------
        # BUSCAR REGISTRO EN ORGANIZACIÓN
        # -----------------------------------

        registro = (
            self.repository.obtener_por_id_y_organizacion(
                id_tarea_habilidad,
                id_organizacion
            )
        )

        if registro is None:
            raise FlowosException(
                message="El requerimiento de habilidad no existe.",
                code="TAREA_HABILIDAD_NO_EXISTE",
                status_code=404
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        # -----------------------------------
        # DETERMINAR VALORES FINALES
        # -----------------------------------

        id_tarea = datos_actualizados.get(
            "id_tarea",
            registro.id_tarea
        )

        id_habilidad = datos_actualizados.get(
            "id_habilidad",
            registro.id_habilidad
        )

        # -----------------------------------
        # VALIDAR TAREA
        # -----------------------------------

        tarea = self.tarea_repository.obtener_por_id_organizacion(
            id_tarea,
            id_organizacion
        )

        if tarea is None:
            raise FlowosException(
                message="La tarea no existe en esta organización.",
                code="TAREA_NO_EXISTE",
                status_code=404
            )

        # -----------------------------------
        # VALIDAR HABILIDAD
        # -----------------------------------

        if "id_habilidad" in datos_actualizados:

            habilidad = self.habilidad_repository.obtener_por_id(
                id_habilidad
            )

            if habilidad is None:
                raise FlowosException(
                    message="La habilidad indicada no existe.",
                    code="HABILIDAD_NO_EXISTE",
                    status_code=404
                )

        # -----------------------------------
        # VALIDAR NIVEL
        # -----------------------------------

        if "id_nivel" in datos_actualizados:

            nivel = self.nivel_habilidad_repository.obtener_por_id(
                datos_actualizados["id_nivel"]
            )

            if nivel is None:
                raise FlowosException(
                    message="El nivel de habilidad indicado no existe.",
                    code="NIVEL_HABILIDAD_NO_EXISTE",
                    status_code=404
                )

        # -----------------------------------
        # VALIDAR DUPLICADO
        # -----------------------------------

        relacion_existente = (
            self.repository
            .obtener_por_tarea_y_habilidad_y_organizacion(
                id_tarea,
                id_habilidad,
                id_organizacion
            )
        )

        if (
            relacion_existente is not None
            and relacion_existente.id_tarea_habilidad
            != id_tarea_habilidad
        ):
            raise FlowosException(
                message=(
                    "La tarea ya tiene registrada "
                    "esta habilidad."
                ),
                code="HABILIDAD_YA_REGISTRADA_EN_TAREA",
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