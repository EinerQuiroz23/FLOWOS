from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class EquipoPersonaCreate(BaseModel):
    id_equipo: int = Field(gt=0)

    id_persona: int = Field(gt=0)

    rol_equipo: str = Field(
        min_length=1,
        max_length=100
    )

    dedicacion: Decimal = Field(
        gt=0,
        le=100
    )

    fecha_inicio: date
    fecha_fin: Optional[date] = None 

    @model_validator(mode="after")
    def validar_datos(self):

        if (
            self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de finalización no puede ser anterior "
                "a la fecha de inicio."
            )

        return self


class EquipoPersonaUpdate(BaseModel):
    id_equipo: Optional[int] = Field(
        default=None,
        gt=0
    )

    id_persona: Optional[int] = Field(
        default=None,
        gt=0
    )

    rol_equipo: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    dedicacion: Optional[Decimal] = Field(
        default=None,
        gt=0,
        le=100
    )

    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None

    @model_validator(mode="after")
    def validar_datos(self):

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


class EquipoPersonaResponse(BaseModel):
    id_equipo_persona: int
    id_equipo: int
    id_persona: int
    rol_equipo: str
    dedicacion: Decimal
    fecha_inicio: date
    fecha_fin: Optional[date]  = None

    model_config = ConfigDict(
        from_attributes=True
    ) 