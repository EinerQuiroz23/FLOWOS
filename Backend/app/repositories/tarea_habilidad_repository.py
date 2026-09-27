from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tarea_habilidad_model import TareaHabilidad
from app.models.tarea_model import Tarea
from app.models.proyecto_model import Proyecto


class TareaHabilidadRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> List[TareaHabilidad]:
        consulta = select(TareaHabilidad)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_tarea_habilidad: int
    ) -> Optional[TareaHabilidad]:

        return self.db.get(
            TareaHabilidad,
            id_tarea_habilidad
        )

    def obtener_por_tarea(
        self,
        id_tarea: int
    ) -> List[TareaHabilidad]:

        consulta = select(TareaHabilidad).where(
            TareaHabilidad.id_tarea == id_tarea
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_habilidad(
        self,
        id_habilidad: int
    ) -> List[TareaHabilidad]:

        consulta = select(TareaHabilidad).where(
            TareaHabilidad.id_habilidad == id_habilidad
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_tarea_y_habilidad(
        self,
        id_tarea: int,
        id_habilidad: int
    ) -> Optional[TareaHabilidad]:

        consulta = select(TareaHabilidad).where(
            TareaHabilidad.id_tarea == id_tarea,
            TareaHabilidad.id_habilidad == id_habilidad
        )

        return self.db.scalars(consulta).first()

    # =========================================================
    # MÉTODOS AISLADOS POR ORGANIZACIÓN
    # =========================================================

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        consulta = (
            select(TareaHabilidad)
            .join(
                Tarea,
                TareaHabilidad.id_tarea == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_y_organizacion(
        self,
        id_tarea_habilidad: int,
        id_organizacion: int
    ) -> Optional[TareaHabilidad]:

        consulta = (
            select(TareaHabilidad)
            .join(
                Tarea,
                TareaHabilidad.id_tarea == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                TareaHabilidad.id_tarea_habilidad
                == id_tarea_habilidad,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_tarea_y_organizacion(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        consulta = (
            select(TareaHabilidad)
            .join(
                Tarea,
                TareaHabilidad.id_tarea == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                TareaHabilidad.id_tarea == id_tarea,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_habilidad_y_organizacion(
        self,
        id_habilidad: int,
        id_organizacion: int
    ) -> List[TareaHabilidad]:

        consulta = (
            select(TareaHabilidad)
            .join(
                Tarea,
                TareaHabilidad.id_tarea == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                TareaHabilidad.id_habilidad == id_habilidad,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_tarea_y_habilidad_y_organizacion(
        self,
        id_tarea: int,
        id_habilidad: int,
        id_organizacion: int
    ) -> Optional[TareaHabilidad]:

        consulta = (
            select(TareaHabilidad)
            .join(
                Tarea,
                TareaHabilidad.id_tarea == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                TareaHabilidad.id_tarea == id_tarea,
                TareaHabilidad.id_habilidad == id_habilidad,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    # =========================================================
    # PERSISTENCIA
    # =========================================================

    def crear(
        self,
        tarea_habilidad: TareaHabilidad
    ) -> TareaHabilidad:

        self.db.add(tarea_habilidad)

        self.db.flush()

        return tarea_habilidad

    def actualizar(
        self,
        tarea_habilidad: TareaHabilidad
    ) -> TareaHabilidad:

        self.db.flush()

        return tarea_habilidad