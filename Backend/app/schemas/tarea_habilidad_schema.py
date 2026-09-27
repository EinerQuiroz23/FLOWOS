from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TareaHabilidadCreate(BaseModel):
    id_tarea: int = Field(gt=0)

    id_habilidad: int = Field(gt=0)

    id_nivel: int = Field(gt=0)


class TareaHabilidadUpdate(BaseModel):
    id_tarea: Optional[int] = Field(
        default=None,
        gt=0
    )

    id_habilidad: Optional[int] = Field(
        default=None,
        gt=0
    )

    id_nivel: Optional[int] = Field(
        default=None,
        gt=0
    )


class TareaHabilidadResponse(BaseModel):
    id_tarea_habilidad: int
    id_tarea: int
    id_habilidad: int
    id_nivel: int

    model_config = ConfigDict(
        from_attributes=True
    )