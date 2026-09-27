from typing import List
 
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asignacion_tarea_model import AsignacionTarea
from app.models.equipo_model import Equipo
from app.models.equipo_persona_model import EquipoPersona
from app.models.habilidad_model import Habilidad
from app.models.persona_habilidad_model import PersonaHabilidad
from app.models.persona_model import Persona
from app.models.proyecto_model import Proyecto
from app.models.tarea_habilidad_model import TareaHabilidad
from app.models.tarea_model import Tarea


class OptimaRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # TAREA
    # ==========================================================

    def obtener_tarea_por_organizacion(
        self,
        id_tarea: int,
        id_organizacion: int
    ):
        consulta = (
            select(Tarea)
            .join(
                Proyecto,
                Proyecto.id_proyecto == Tarea.id_proyecto
            )
            .where(
                Tarea.id_tarea == id_tarea,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalar(consulta)

    # ==========================================================
    # CANDIDATOS PARA UNA TAREA
    # ==========================================================

    def obtener_candidatos_por_tarea(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[Persona]:

        consulta = (
            select(Persona)
            .join(
                EquipoPersona,
                EquipoPersona.id_persona == Persona.id_persona
            )
            .join(
                Equipo,
                Equipo.id_equipo == EquipoPersona.id_equipo
            )
            .join(
                Tarea,
                Tarea.id_equipo == Equipo.id_equipo
            )
            .join(
                Proyecto,
                Proyecto.id_proyecto == Tarea.id_proyecto
            )
            .where(
                Tarea.id_tarea == id_tarea,
                Proyecto.id_organizacion == id_organizacion,
                Persona.id_organizacion == id_organizacion,

                # Persona activa
                Persona.estado.is_(True),

                # Equipo activo
                Equipo.estado == "ACTIVO",

                # La persona sigue perteneciendo al equipo
                EquipoPersona.fecha_fin.is_(None)
            )
            .distinct()
        )

        return self.db.scalars(consulta).all()

    # ==========================================================
    # HABILIDADES REQUERIDAS POR TAREA
    # ==========================================================

    def obtener_habilidades_requeridas_por_tarea(
        self,
        id_tarea: int
    ):
        consulta = (
            select(
                TareaHabilidad,
                Habilidad.nombre.label("nombre_habilidad")
            )
            .join(
                Habilidad,
                Habilidad.id_habilidad
                == TareaHabilidad.id_habilidad
            )
            .where(
                TareaHabilidad.id_tarea == id_tarea,
                Habilidad.estado.is_(True)
            )
        )

        return self.db.execute(consulta).all()

    # ==========================================================
    # HABILIDADES DE LAS PERSONAS
    # ==========================================================

    def obtener_habilidades_por_personas(
        self,
        ids_personas: List[int]
    ):

        if not ids_personas:
            return []

        consulta = (
            select(
                PersonaHabilidad,
                Habilidad.nombre.label("nombre_habilidad")
            )
            .join(
                Habilidad,
                Habilidad.id_habilidad
                == PersonaHabilidad.id_habilidad
            )
            .where(
                PersonaHabilidad.id_persona.in_(ids_personas),
                Habilidad.estado.is_(True)
            )
        )

        return self.db.execute(consulta).all()

    # ==========================================================
    # CARGA ACTUAL
    # ==========================================================

    def obtener_carga_actual_por_personas(
        self,
        ids_personas: List[int]
    ):

        if not ids_personas:
            return {}

        consulta = (
            select(
                EquipoPersona.id_persona,
                func.coalesce(
                    func.sum(AsignacionTarea.dedicacion),
                    0
                ).label("carga_actual")
            )
            .join(
                AsignacionTarea,
                AsignacionTarea.id_equipo_persona
                == EquipoPersona.id_equipo_persona
            )
            .where(
                EquipoPersona.id_persona.in_(ids_personas),
                AsignacionTarea.estado.in_(
                    ["ASIGNADA", "EN_PROGRESO"]
                )
            )
            .group_by(
                EquipoPersona.id_persona
            )
        )

        resultados = self.db.execute(consulta).all()

        return {
            fila.id_persona: float(
                fila.carga_actual or 0
            )
            for fila in resultados
        }

    # ==========================================================
    # PROYECTO
    # ==========================================================

    def obtener_proyecto_por_organizacion(
        self,
        id_proyecto: int,
        id_organizacion: int
    ):
        consulta = (
            select(Proyecto)
            .where(
                Proyecto.id_proyecto == id_proyecto,
                Proyecto.id_organizacion == id_organizacion
            )
        )

        return self.db.scalar(consulta)

    # ==========================================================
    # TAREAS ACTIVAS DE UN PROYECTO
    # ==========================================================

    def obtener_tareas_activas_por_proyecto(
        self,
        id_proyecto: int
    ) -> List[Tarea]:

        consulta = (
            select(Tarea)
            .where(
                Tarea.id_proyecto == id_proyecto,
                Tarea.estado.in_(
                    ["PENDIENTE", "EN_PROGRESO"]
                )
            )
        )

        return self.db.scalars(consulta).all()

    # ==========================================================
    # PERSONAS ACTIVAS DEL PROYECTO
    # ==========================================================

    def obtener_personas_activas_proyecto(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> List[Persona]:

        consulta = (
            select(Persona)
            .join(
                EquipoPersona,
                EquipoPersona.id_persona
                == Persona.id_persona
            )
            .join(
                Equipo,
                Equipo.id_equipo
                == EquipoPersona.id_equipo
            )
            .where(
                Persona.id_organizacion == id_organizacion,

                # Persona activa
                Persona.estado.is_(True),

                # Equipo perteneciente al proyecto
                Equipo.id_proyecto == id_proyecto,

                # Equipo activo
                Equipo.estado == "ACTIVO",

                # Pertenencia actual al equipo
                EquipoPersona.fecha_fin.is_(None)
            )
            .distinct()
        )

        return self.db.scalars(consulta).all()