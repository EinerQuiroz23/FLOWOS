from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric , UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class PersonaHabilidad(Base):
    __tablename__ = "persona_habilidad"

    id_persona_habilidad: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"),
        nullable=False
    )

    id_habilidad: Mapped[int] = mapped_column(
        ForeignKey("habilidad.id_habilidad"),
        nullable=False
    )

    id_nivel: Mapped[int] = mapped_column(
        ForeignKey("nivel_habilidad.id_nivel"),
        nullable=False
    )

    años_experiencia: Mapped[Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "id_persona",
            "id_habilidad",
            name="uq_persona_habilidad"
        ),
    )