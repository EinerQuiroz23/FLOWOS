from datetime import date, datetime
from typing import Optional

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Proyecto(Base):
    __tablename__ = "proyecto"

    id_proyecto: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_organizacion: Mapped[int] = mapped_column(
        ForeignKey("organizacion.id_organizacion"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    fecha_inicio: Mapped[date] = mapped_column(
        nullable=False
    )

    fecha_limite: Mapped[date] = mapped_column(
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        nullable=False,
        default="PLANIFICACION"
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )