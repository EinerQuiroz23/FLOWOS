from typing import Optional

from pydantic import BaseModel


class LiderPropuesto(BaseModel):

    id_persona: int
    persona: str

    compatibilidad: float
    experiencia: float
    disponibilidad: float

    puntuacion_liderazgo: float

    confianza: Optional[str] = None  # "Alta" | "Media" | "Baja"

    habilidades_ok: Optional[str] = None
    habilidades_no_registradas: Optional[str] = None
    habilidades_nivel_insuficiente: Optional[str] = None

    explicacion: Optional[str] = None