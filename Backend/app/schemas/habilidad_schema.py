from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabilidadCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=100
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=255
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre de la habilidad no puede estar vacío."
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

class HabilidadUpdate(BaseModel):
    nombre: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=255
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
                "El nombre de la habilidad no puede estar vacío."
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


class HabilidadResponse(BaseModel):
    id_habilidad: int
    nombre: str
    descripcion: Optional[str]
    estado: bool
    fecha_creacion: datetime

    model_config = ConfigDict(
        from_attributes=True
    )