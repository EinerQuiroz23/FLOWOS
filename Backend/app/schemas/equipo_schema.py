from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EquipoCreate(BaseModel):
    id_proyecto: int = Field(gt=0)

    nombre: str = Field(
        min_length=1,
        max_length=150
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre del equipo no puede estar vacío."
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


class EquipoUpdate(BaseModel):
    id_proyecto: Optional[int] = Field(
        default=None,
        gt=0
    )

    nombre: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500
    )

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
                "El nombre del equipo no puede estar vacío."
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


class EquipoResponse(BaseModel):
    id_equipo: int
    id_proyecto: int
    nombre: str
    descripcion: Optional[str]
    estado: str
    fecha_creacion: datetime

    model_config = ConfigDict(
        from_attributes=True
    )