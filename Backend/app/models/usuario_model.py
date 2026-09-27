from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_organizacion: Mapped[int] = mapped_column(
        ForeignKey("organizacion.id_organizacion"),
        nullable=False
    )

    id_rol: Mapped[int] = mapped_column(
        ForeignKey("rol.id_rol"),
        nullable=False
    )

    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"),
        nullable=False,
        unique=True
    )

    nombre_usuario: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    contrasena_hash: Mapped[str] = mapped_column(
        "contraseña_hash",
        String(255),
        nullable=False
    )

    estado: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )