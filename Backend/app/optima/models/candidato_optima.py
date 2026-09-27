from typing import Optional

from pydantic import BaseModel


class CandidatoOptima(BaseModel):

    id_tarea: int
    tarea: str

    id_persona: int
    persona: str

    capacidad_horas_semana: float

    habilidades_requeridas: int
    habilidades_cumplidas: int

    compatibilidad: Optional[float] = None

    años_experiencia_promedio: Optional[float] = None
    experiencia: Optional[float] = None

    horas_carga_actual: Optional[float] = None
    disponibilidad: Optional[float] = None

    elegible: Optional[bool] = None
    puntuacion_optima: Optional[float] = None

    habilidades_ok: Optional[str] = None
    habilidades_no_registradas: Optional[str] = None
    habilidades_nivel_insuficiente: Optional[str] = None

    ranking: Optional[int] = None
    explicacion: Optional[str] = None