from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tarea_model import Tarea
from app.models.proyecto_model import Proyecto


class TareaRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # OBTENER TODAS
    # ==========================================================

    def obtener_todos(self) -> List[Tarea]:

        consulta = select(Tarea)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================

    def obtener_por_id(
        self,
        id_tarea: int
    ) -> Optional[Tarea]:

        return self.db.get(
            Tarea,
            id_tarea
        )

    # ==========================================================
    # OBTENER POR PROYECTO
    # ==========================================================

    def obtener_por_proyecto(
        self,
        id_proyecto: int
    ) -> List[Tarea]:

        consulta = select(Tarea).where(
            Tarea.id_proyecto == id_proyecto
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # OBTENER POR EQUIPO
    # ==========================================================

    def obtener_por_equipo(
        self,
        id_equipo: int
    ) -> List[Tarea]:

        consulta = select(Tarea).where(
            Tarea.id_equipo == id_equipo
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # OBTENER POR ORGANIZACIÓN
    # ==========================================================

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[Tarea]:

        consulta = (
            select(Tarea)
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

    # ==========================================================
    # OBTENER POR ID + ORGANIZACIÓN
    # ==========================================================

    def obtener_por_id_organizacion(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> Optional[Tarea]:

        consulta = (
            select(Tarea)
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Tarea.id_tarea == id_tarea,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    # ==========================================================
    # OBTENER POR PROYECTO + ORGANIZACIÓN
    # ==========================================================

    def obtener_por_proyecto_organizacion(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> List[Tarea]:

        consulta = (
            select(Tarea)
            .join(
                Proyecto,
                Tarea.id_proyecto == Proyecto.id_proyecto
            )
            .where(
                Tarea.id_proyecto == id_proyecto,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # CREAR
    # ==========================================================

    def crear(
        self,
        tarea: Tarea
    ) -> Tarea:

        self.db.add(tarea)

        self.db.flush()

        return tarea

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================

    def actualizar(
        self,
        tarea: Tarea
    ) -> Tarea:

        self.db.flush()

        return tarea

    # ==========================================================
    # CAMBIAR ESTADO
    # ==========================================================

    def cambiar_estado(
        self,
        tarea: Tarea,
        nuevo_estado: str
    ) -> Tarea:

        tarea.estado = nuevo_estado

        self.db.flush()

        return tarea