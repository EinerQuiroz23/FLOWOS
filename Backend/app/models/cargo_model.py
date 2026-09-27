from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Cargo(Base):
    __tablename__ = "cargo"

    id_cargo: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
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