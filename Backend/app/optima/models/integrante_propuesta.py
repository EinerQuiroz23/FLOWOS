from typing import Optional

from pydantic import BaseModel, Field


class IntegrantePropuesto(BaseModel):
    id_persona: int
    persona: str

    capacidad_horas_semana: float
    horas_carga_actual: float
    disponibilidad: float

    habilidades_requeridas: int
    habilidades_cumplidas: int
    compatibilidad: float

    años_experiencia_promedio: float
    experiencia: float

    puntuacion_equipo: float

    habilidades_ok: Optional[str] = None
    habilidades_no_registradas: Optional[str] = None
    habilidades_nivel_insuficiente: Optional[str] = None

    contribucion: Optional[str] = None

    # Uso interno de OPTIMA para identificar exactamente
    # qué requisitos de las tareas cubre la persona.
    # No se devuelve en la respuesta de la API.
    requisitos_cubiertos: list[str] = Field(
        default_factory=list,
        exclude=True
    )