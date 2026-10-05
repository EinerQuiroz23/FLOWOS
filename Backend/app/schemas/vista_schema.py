from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class VistaAnalizarRequest(BaseModel):
    id_proyecto: int = Field(gt=0)
    requisitos: str = Field(min_length=20, max_length=20000)


class TareaPropuestaVista(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    prioridad: str = "MEDIA"  # BAJA | MEDIA | ALTA | CRITICA
    horas_estimadas: Decimal
    habilidades_sugeridas: list[str] = []


class VistaAnalizarResponse(BaseModel):
    id_proyecto: int
    proyecto: str
    resumen: str
    tareas_propuestas: list[TareaPropuestaVista]