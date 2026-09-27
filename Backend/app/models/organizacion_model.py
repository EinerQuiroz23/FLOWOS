from datetime import datetime
from typing import Optional

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Organizacion(Base):
    __tablename__ = "organizacion"

    id_organizacion: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    estado: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    codigo: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )