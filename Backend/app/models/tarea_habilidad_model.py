from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class TareaHabilidad(Base):
    __tablename__ = "tarea_habilidad"

    id_tarea_habilidad: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_tarea: Mapped[int] = mapped_column(
        ForeignKey("tarea.id_tarea"),
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
    __table_args__ = (
    UniqueConstraint(
        "id_tarea",
        "id_habilidad",
        name="uq_tarea_habilidad"
    ),
)