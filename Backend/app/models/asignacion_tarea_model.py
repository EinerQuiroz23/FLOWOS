from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric , UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class AsignacionTarea(Base):
    __tablename__ = "asignacion_tarea"

    id_asignacion: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_tarea: Mapped[int] = mapped_column(
        ForeignKey("tarea.id_tarea"),
        nullable=False
    )

    id_equipo_persona: Mapped[int] = mapped_column(
        ForeignKey("equipo_persona.id_equipo_persona"),
        nullable=False
    )

    fecha_asignacion: Mapped[date] = mapped_column(
        nullable=False
    )

    fecha_inicio: Mapped[date] = mapped_column(
        nullable=False
    )

    fecha_limite: Mapped[date] = mapped_column(
        nullable=False
    )

    dedicacion: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        nullable=False,
        default="ASIGNADA"
    )   

    __table_args__ = (
    UniqueConstraint(
        "id_tarea",
        "id_equipo_persona",
        name="uq_asignacion_tarea_persona"
    ),
)