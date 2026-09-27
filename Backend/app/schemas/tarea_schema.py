from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class TareaCreate(BaseModel):
    id_proyecto: int
    id_equipo: int
    nombre: str
    descripcion: Optional[str] = None
    prioridad: str = "MEDIA"
    horas_estimadas: Decimal
    fecha_inicio: date
    fecha_limite: date

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, valor: str) -> str:
        valor = valor.strip().upper()

        prioridades_validas = {
            "BAJA",
            "MEDIA",
            "ALTA",
            "CRITICA"
        }

        if valor not in prioridades_validas:
            raise ValueError(
                "La prioridad debe ser BAJA, MEDIA, ALTA o CRITICA."
            )

        return valor

    @field_validator("horas_estimadas")
    @classmethod
    def validar_horas_estimadas(cls, valor: Decimal) -> Decimal:
        if valor <= 0:
            raise ValueError(
                "Las horas estimadas deben ser mayores que 0."
            )

        return valor

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_limite < self.fecha_inicio:
            raise ValueError(
                "La fecha límite no puede ser anterior a la fecha de inicio."
            )

        return self


class TareaUpdate(BaseModel):
    id_proyecto: Optional[int] = None
    id_equipo: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    horas_estimadas: Optional[Decimal] = None
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return valor

        valor = valor.strip().upper()

        prioridades_validas = {
            "BAJA",
            "MEDIA",
            "ALTA",
            "CRITICA"
        }

        if valor not in prioridades_validas:
            raise ValueError(
                "La prioridad debe ser BAJA, MEDIA, ALTA o CRITICA."
            )

        return valor

    @field_validator("horas_estimadas")
    @classmethod
    def validar_horas_estimadas(
        cls,
        valor: Optional[Decimal]
    ) -> Optional[Decimal]:
        if valor is not None and valor <= 0:
            raise ValueError(
                "Las horas estimadas deben ser mayores que 0."
            )

        return valor


class TareaResponse(BaseModel):
    id_tarea: int
    id_proyecto: int
    id_equipo: int
    nombre: str
    descripcion: Optional[str]
    prioridad: str
    horas_estimadas: Decimal
    fecha_inicio: date
    fecha_limite: date
    estado: str
    fecha_creacion: datetime

    model_config = ConfigDict(
        from_attributes=True
    )