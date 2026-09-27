from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Persona(Base):
    __tablename__ = "persona"

    id_persona: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_organizacion: Mapped[int] = mapped_column(
        ForeignKey("organizacion.id_organizacion"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        nullable=False
    )

    apellido: Mapped[str] = mapped_column(
        nullable=False
    )

    email: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    capacidad_horas_semana: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
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