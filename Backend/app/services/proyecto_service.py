from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.proyecto_model import Proyecto
from app.repositories.proyecto_repository import ProyectoRepository
from app.schemas.proyecto_schema import (
    ProyectoCreate,
    ProyectoUpdate
)


class ProyectoService:

    ESTADOS_VALIDOS = {
        "PLANIFICACION",
        "ACTIVO",
        "PAUSADO",
        "FINALIZADO",
        "CANCELADO"
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProyectoRepository(db)

    def obtener_todos(
        self,
        id_organizacion: int
    ) -> List[Proyecto]:

        return self.repository.obtener_por_organizacion(
            id_organizacion
        )

    def obtener_por_id(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> Optional[Proyecto]:

        return self.repository.obtener_por_id_organizacion(
            id_proyecto,
            id_organizacion
        )

    def crear(
        self,
        datos: ProyectoCreate,
        id_organizacion: int
    ) -> Proyecto:

        proyectos = self.repository.obtener_por_organizacion(
            id_organizacion
        )

        for proyecto_existente in proyectos:
            if proyecto_existente.nombre == datos.nombre:
                raise ValueError(
                    "Ya existe un proyecto con ese nombre."
                )

        proyecto = Proyecto(
            id_organizacion=id_organizacion,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            fecha_inicio=datos.fecha_inicio,
            fecha_limite=datos.fecha_limite
        )

        try:
            self.repository.crear(proyecto)
            self.db.commit()

            return proyecto

        except Exception:
            self.db.rollback()
            raise

    def actualizar(
        self,
        id_proyecto: int,
        datos: ProyectoUpdate,
        id_organizacion: int
    ) -> Proyecto:

        proyecto = self.repository.obtener_por_id_organizacion(
            id_proyecto,
            id_organizacion
        )

        if proyecto is None:
            raise ValueError(
                "El proyecto no existe."
            )

        datos_actualizados = datos.model_dump(
            exclude_unset=True
        )

        for campo, valor in datos_actualizados.items():
            setattr(proyecto, campo, valor)

        try:
            self.repository.actualizar(proyecto)
            self.db.commit()

            return proyecto

        except Exception:
            self.db.rollback()
            raise

    def cambiar_estado(
        self,
        id_proyecto: int,
        nuevo_estado: str,
        id_organizacion: int
    ) -> Proyecto:

        proyecto = self.repository.obtener_por_id_organizacion(
            id_proyecto,
            id_organizacion
        )

        if proyecto is None:
            raise ValueError(
                "El proyecto no existe."
            )

        nuevo_estado = nuevo_estado.strip().upper()

        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "El estado del proyecto no es válido."
            )

        try:
            self.repository.cambiar_estado(
                proyecto,
                nuevo_estado
            )

            self.db.commit()

            return proyecto

        except Exception:
            self.db.rollback()
            raise