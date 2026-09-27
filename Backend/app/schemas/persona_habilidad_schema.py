from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PersonaHabilidadCreate(BaseModel):
    id_persona: int = Field(gt=0)
    id_habilidad: int = Field(gt=0)
    id_nivel: int = Field(gt=0)
    años_experiencia: Decimal = Field(ge=0, le=100)


class PersonaHabilidadUpdate(BaseModel):
    id_persona: Optional[int] = Field(default=None, gt=0)
    id_habilidad: Optional[int] = Field(default=None, gt=0)
    id_nivel: Optional[int] = Field(default=None, gt=0)
    años_experiencia: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )


class PersonaHabilidadResponse(BaseModel):
    id_persona_habilidad: int
    id_persona: int
    id_habilidad: int
    id_nivel: int
    años_experiencia: Decimal

    model_config = ConfigDict(from_attributes=True)