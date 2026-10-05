from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class MensajeEquipo(Base):
    __tablename__ = "mensaje_equipo"

    id_mensaje: Mapped[int] = mapped_column(primary_key=True)

    id_equipo: Mapped[int] = mapped_column(
        ForeignKey("equipo.id_equipo"),
        nullable=False,
    )

    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona"),
        nullable=False,
    )

    contenido: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )