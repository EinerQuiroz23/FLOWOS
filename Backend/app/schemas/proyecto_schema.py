from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProyectoCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500
    )

    fecha_inicio: date
    fecha_limite: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre del proyecto no puede estar vacío."
            )

        return valor

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(
        cls,
        valor: Optional[str]
    ) -> Optional[str]:

        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            return None

        return valor

    @field_validator("fecha_limite")
    @classmethod
    def validar_fecha_limite(
        cls,
        valor: date,
        info
    ) -> date:

        fecha_inicio = info.data.get("fecha_inicio")

        if (
            fecha_inicio is not None
            and valor < fecha_inicio
        ):
            raise ValueError(
                "La fecha límite no puede ser anterior "
                "a la fecha de inicio."
            )

        return valor


class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500
    )

    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(
        cls,
        valor: Optional[str]
    ) -> Optional[str]:

        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre del proyecto no puede estar vacío."
            )

        return valor

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(
        cls,
        valor: Optional[str]
    ) -> Optional[str]:

        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            return None

        return valor


class ProyectoResponse(BaseModel):
    id_proyecto: int
    nombre: str
    descripcion: Optional[str]
    fecha_inicio: date
    fecha_limite: date
    estado: str
    fecha_creacion: datetime

    model_config = ConfigDict(
        from_attributes=True
    )