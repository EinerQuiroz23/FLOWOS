from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AsignacionTareaCreate(BaseModel):
    id_tarea: int = Field(gt=0)

    id_equipo_persona: int = Field(gt=0)

    fecha_asignacion: date

    fecha_inicio: date
    fecha_limite: date

    dedicacion: Decimal = Field(
        gt=0,
        le=100
    )

    @model_validator(mode="after")
    def validar_datos(self):

        if self.fecha_limite < self.fecha_inicio:
            raise ValueError(
                "La fecha límite no puede ser anterior "
                "a la fecha de inicio."
            )

        return self


class AsignacionTareaUpdate(BaseModel):
    id_tarea: Optional[int] = Field(
        default=None,
        gt=0
    )

    id_equipo_persona: Optional[int] = Field(
        default=None,
        gt=0
    )

    fecha_asignacion: Optional[date] = None

    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None

    dedicacion: Optional[Decimal] = Field(
        default=None,
        gt=0,
        le=100
    )

    @model_validator(mode="after")
    def validar_datos(self):

        if (
            self.fecha_inicio is not None
            and self.fecha_limite is not None
            and self.fecha_limite < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha límite no puede ser anterior "
                "a la fecha de inicio."
            )

        return self


class AsignacionTareaResponse(BaseModel):
    id_asignacion: int
    id_tarea: int
    id_equipo_persona: int
    fecha_asignacion: date
    fecha_inicio: date
    fecha_limite: date
    dedicacion: Decimal
    estado: str

    model_config = ConfigDict(
        from_attributes=True
    )