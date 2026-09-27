from typing import Optional, List

from pydantic import BaseModel, Field

from app.optima.models.integrante_propuesta import IntegrantePropuesto
from app.optima.models.lider_propuesto import LiderPropuesto


class PropuestaEquipo(BaseModel):

    id_proyecto: int
    proyecto: str

    cobertura: float

    integrantes_recomendados: int
    integrantes_analizados: int

    lider: Optional[LiderPropuesto] = None
    lider_alternativo: Optional[LiderPropuesto] = None

    integrantes: list[IntegrantePropuesto]

    habilidades_requeridas: int
    habilidades_cubiertas: int

    habilidades_faltantes: Optional[str] = None

    explicacion: str

    puede_crearse: bool

    # Nuevos campos profesionales
    confianza_liderazgo: Optional[str] = None          # "Alta" | "Media" | "Baja"
    riesgos_detectados: List[str] = Field(default_factory=list)
    recomendaciones: List[str] = Field(default_factory=list)