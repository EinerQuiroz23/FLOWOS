from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(50),
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