from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):

    id_persona: int

    id_rol: int

    nombre_usuario: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    contrasena: str = Field(
        min_length=8,
        max_length=128
    )


class UsuarioUpdate(BaseModel):

    id_rol: Optional[int] = None

    nombre_usuario: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    email: Optional[EmailStr] = None

    estado: Optional[bool] = None


class UsuarioResponse(BaseModel):

    id_usuario: int

    id_organizacion: int

    id_persona: int

    id_rol: int

    nombre_usuario: str

    email: EmailStr

    estado: bool

    fecha_creacion: datetime

    ultimo_acceso: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )