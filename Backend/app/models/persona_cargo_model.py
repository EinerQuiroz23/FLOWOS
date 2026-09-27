from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.core.base import Base


class PersonaCargo(Base):
    __tablename__ = "persona_cargo"

    id_persona_cargo: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"),
        nullable=False
    )

    id_cargo: Mapped[int] = mapped_column(
        ForeignKey("cargo.id_cargo"),
        nullable=False
    )

    fecha_inicio: Mapped[date] = mapped_column(
        nullable=False
    )

    fecha_fin: Mapped[Optional[date]] = mapped_column(
        nullable=True
    )
    