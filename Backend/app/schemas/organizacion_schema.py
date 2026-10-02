from datetime import datetime
from typing import Optional, List

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


class AdminResumen(BaseModel):
    id_usuario: int
    nombre_usuario: str
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None


class OrganizacionConAdmin(BaseModel):
    id_organizacion: int
    nombre: str
    descripcion: Optional[str] = None
    codigo: Optional[str] = None
    estado: bool
    fecha_creacion: datetime
    admin: Optional[AdminResumen] = None

    model_config = ConfigDict(from_attributes=True)