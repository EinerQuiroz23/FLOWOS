from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field , field_validator, ConfigDict
from datetime import datetime


class PersonaCreate(BaseModel):

    nombre: str = Field(
        min_length=1,
        max_length=100
    )

    apellido: str = Field(
        min_length=1,
        max_length=100
    )

    email: Optional[EmailStr] = None

    telefono: Optional[str] = Field(
        default=None,
        max_length=30
    )

    capacidad_horas_semana: Decimal = Field(
        gt=0,
        le=168
    )

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre_apellido(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre y apellido no pueden estar vacíos."
            )

        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            return None

        return valor



class PersonaUpdate(BaseModel):
    nombre: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    apellido: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    email: Optional[EmailStr] = None

    telefono: Optional[str] = Field(
        default=None,
        max_length=30
    )

    capacidad_horas_semana: Optional[Decimal] = Field(
        default=None,
        gt=0,
        le=168
    )

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre_apellido(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "El nombre y apellido no pueden estar vacíos."
            )

        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls,valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            return None

        return valor


class PersonaResponse(BaseModel):
    id_persona: int
    nombre: str
    apellido: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    capacidad_horas_semana: Decimal
    estado: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)