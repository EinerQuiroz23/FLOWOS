from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class NivelHabilidad(Base):
    __tablename__ = "nivel_habilidad"

    id_nivel: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )