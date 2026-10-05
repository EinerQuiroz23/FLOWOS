from typing import Optional

from pydantic import BaseModel, Field


class OptimaConfirmarRequest(BaseModel):
    nombre_equipo: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Nombre del equipo a crear. Si no se envía, se genera automático.",
    )


class AsignacionCreadaItem(BaseModel):
    id_asignacion: int
    id_tarea: int
    nombre_tarea: str
    id_persona: int
    persona: str


class OptimaConfirmarResponse(BaseModel):
    id_proyecto: int
    id_equipo: int
    nombre_equipo: str
    id_lider: int | None
    integrantes_agregados: int
    asignaciones_creadas: int
    detalle_asignaciones: list[AsignacionCreadaItem]
    mensaje: str