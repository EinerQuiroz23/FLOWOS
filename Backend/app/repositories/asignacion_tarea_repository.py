from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asignacion_tarea_model import AsignacionTarea
from app.models.tarea_model import Tarea
from app.models.equipo_model import Equipo
from app.models.proyecto_model import Proyecto
from app.models.equipo_persona_model import EquipoPersona


class AsignacionTareaRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # CONSULTAS GENERALES
    # ==========================================================

    def obtener_todos(self) -> List[AsignacionTarea]:

        consulta = select(AsignacionTarea)

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id(
        self,
        id_asignacion: int
    ) -> Optional[AsignacionTarea]:

        return self.db.get(
            AsignacionTarea,
            id_asignacion
        )

    def obtener_por_tarea(
        self,
        id_tarea: int
    ) -> List[AsignacionTarea]:

        consulta = select(AsignacionTarea).where(
            AsignacionTarea.id_tarea == id_tarea
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_equipo_persona(
        self,
        id_equipo_persona: int
    ) -> List[AsignacionTarea]:

        consulta = select(AsignacionTarea).where(
            AsignacionTarea.id_equipo_persona
            == id_equipo_persona
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_activas_por_equipo_persona(
        self,
        id_equipo_persona: int
    ) -> List[AsignacionTarea]:

        consulta = select(AsignacionTarea).where(
            AsignacionTarea.id_equipo_persona
            == id_equipo_persona,
            AsignacionTarea.estado.in_([
                "ASIGNADA",
                "EN_PROGRESO"
            ])
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_tarea_y_persona(
        self,
        id_tarea: int,
        id_equipo_persona: int
    ) -> Optional[AsignacionTarea]:

        consulta = select(AsignacionTarea).where(
            AsignacionTarea.id_tarea == id_tarea,
            AsignacionTarea.id_equipo_persona
            == id_equipo_persona
        )

        return self.db.scalars(consulta).first()

    # ==========================================================
    # AISLAMIENTO POR ORGANIZACIÓN
    # ==========================================================

    def obtener_por_organizacion(
        self,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        consulta = (
            select(AsignacionTarea)
            .join(
                Tarea,
                AsignacionTarea.id_tarea
                == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto
                == Proyecto.id_proyecto
            )
            .where(
                Proyecto.id_organizacion
                == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_id_y_organizacion(
        self,
        id_asignacion: int,
        id_organizacion: int
    ) -> Optional[AsignacionTarea]:

        consulta = (
            select(AsignacionTarea)
            .join(
                Tarea,
                AsignacionTarea.id_tarea
                == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto
                == Proyecto.id_proyecto
            )
            .where(
                AsignacionTarea.id_asignacion
                == id_asignacion,
                Proyecto.id_organizacion
                == id_organizacion
            )
        )

        return self.db.scalars(consulta).first()

    def obtener_por_tarea_y_organizacion(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        consulta = (
            select(AsignacionTarea)
            .join(
                Tarea,
                AsignacionTarea.id_tarea
                == Tarea.id_tarea
            )
            .join(
                Proyecto,
                Tarea.id_proyecto
                == Proyecto.id_proyecto
            )
            .where(
                AsignacionTarea.id_tarea == id_tarea,
                Proyecto.id_organizacion
                == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    def obtener_por_equipo_persona_y_organizacion(
        self,
        id_equipo_persona: int,
        id_organizacion: int
    ) -> List[AsignacionTarea]:

        consulta = (
            select(AsignacionTarea)
            .join(
                EquipoPersona,
                AsignacionTarea.id_equipo_persona
                == EquipoPersona.id_equipo_persona
            )
            .join(
                Equipo,
                EquipoPersona.id_equipo
                == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Equipo.id_proyecto
                == Proyecto.id_proyecto
            )
            .where(
                AsignacionTarea.id_equipo_persona
                == id_equipo_persona,
                Proyecto.id_organizacion
                == id_organizacion
            )
        )

        resultado = self.db.scalars(consulta)

        return resultado.all()

    # ==========================================================
    # PERSISTENCIA
    # ==========================================================

    def crear(
        self,
        asignacion: AsignacionTarea
    ) -> AsignacionTarea:

        self.db.add(asignacion)

        self.db.flush()

        return asignacion

    def actualizar(
        self,
        asignacion: AsignacionTarea
    ) -> AsignacionTarea:

        self.db.flush()

        return asignacion

    def cambiar_estado(
        self,
        asignacion: AsignacionTarea,
        nuevo_estado: str
    ) -> AsignacionTarea:

        asignacion.estado = nuevo_estado

        self.db.flush()

        return asignacion