from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):

    email: EmailStr

    contrasena: str


class RegistroOrganizacionRequest(BaseModel):

    nombre_organizacion: str = Field(
        min_length=2,
        max_length=150
    )

    descripcion_organizacion: str | None = Field(
        default=None,
        max_length=255
    )

    nombre: str = Field(
        min_length=1,
        max_length=100
    )

    apellido: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    telefono: str | None = Field(
        default=None,
        max_length=30
    )

    capacidad_horas_semana: float = Field(
        gt=0,
        le=168
    )

    nombre_usuario: str = Field(
        min_length=3,
        max_length=100
    )

    contrasena: str = Field(
        min_length=8,
        max_length=128
    )


class RecuperarContrasenaRequest(BaseModel):

    email: EmailStr


class RestablecerContrasenaRequest(BaseModel):

    email: EmailStr

    codigo: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )

    nueva_contrasena: str = Field(
        min_length=8,
        max_length=128
    )


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

class RegistroEmpleadoRequest(BaseModel):

    codigo_organizacion: str = Field(
        min_length=5,
        max_length=20
    )

    email: EmailStr

    contrasena: str = Field(
        min_length=8,
        max_length=128
    )

    nombre_usuario: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

class RegistroEmpleadoRequest(BaseModel):

    codigo_organizacion: str = Field(
        min_length=5,
        max_length=20
    )

    email: EmailStr

    contrasena: str = Field(
        min_length=8,
        max_length=128
    )


class CrearAdminOrganizacionRequest(BaseModel):

    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    capacidad_horas_semana: float = Field(default=40, gt=0, le=168)
    contrasena: str = Field(min_length=8, max_length=128)



class PromoverAdminRequest(BaseModel):
    id_persona: int = Field(gt=0)
    # Solo obligatorio si la persona aún no tiene usuario
    contrasena: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )