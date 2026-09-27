from typing import Optional

from pydantic import BaseModel, ConfigDict


class RolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    estado: bool

    model_config = ConfigDict(from_attributes=True)