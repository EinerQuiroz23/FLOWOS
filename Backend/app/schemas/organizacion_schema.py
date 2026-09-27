from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrganizacionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class OrganizacionCreate(OrganizacionBase):
    pass


class OrganizacionResponse(OrganizacionBase):
    id_organizacion: int
    estado: bool
    fecha_creacion: datetime
    codigo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)