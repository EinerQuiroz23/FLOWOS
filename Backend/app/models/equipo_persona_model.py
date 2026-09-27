from datetime import date

from sqlalchemy import ForeignKey, Numeric , UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class EquipoPersona(Base):
    __tablename__ = "equipo_persona"

    id_equipo_persona: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_equipo: Mapped[int] = mapped_column(
        ForeignKey("equipo.id_equipo"),
        nullable=False
    )

    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"),
        nullable=False
    )

    rol_equipo: Mapped[str] = mapped_column(
        nullable=False
    )

    dedicacion: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    fecha_inicio: Mapped[date] = mapped_column(
        nullable=False
    )

    fecha_fin: Mapped[date | None] = mapped_column(
        nullable=True
    )
    __table_args__ = (
    UniqueConstraint(
        "id_equipo",
        "id_persona",
        name="uq_equipo_persona"
    ),
)