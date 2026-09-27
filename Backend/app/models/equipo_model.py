from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, text , UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Equipo(Base):
    __tablename__ = "equipo"

    id_equipo: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_proyecto: Mapped[int] = mapped_column(
        ForeignKey("proyecto.id_proyecto"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    estado: Mapped[str] = mapped_column(
        nullable=False,
        default="ACTIVO"
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    __table_args__ = (
    UniqueConstraint(
        "id_proyecto",
        "nombre",
        name="uq_equipo_proyecto_nombre"
    ),
)