from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PersonaCargoCreate(BaseModel):
    id_persona: int = Field(gt=0)
    id_cargo: int = Field(gt=0)
    fecha_inicio: date
    fecha_fin: Optional[date] = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de finalización no puede ser anterior "
                "a la fecha de inicio."
            )

        return self


class PersonaCargoUpdate(BaseModel):
    id_persona: Optional[int] = Field(
        default=None,
        gt=0
    )

    id_cargo: Optional[int] = Field(
        default=None,
        gt=0
    )

    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de finalización no puede ser anterior "
                "a la fecha de inicio."
            )

        return self


class PersonaCargoResponse(BaseModel):
    id_persona_cargo: int
    id_persona: int
    id_cargo: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None

    model_config = ConfigDict(
        from_attributes=True
    )