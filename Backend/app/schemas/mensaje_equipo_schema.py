from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MensajeEquipoCreate(BaseModel):
    contenido: str = Field(min_length=1, max_length=2000)


class MensajeEquipoResponse(BaseModel):
    id_mensaje: int
    id_equipo: int
    id_persona: int
    nombre_persona: str
    contenido: str
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)