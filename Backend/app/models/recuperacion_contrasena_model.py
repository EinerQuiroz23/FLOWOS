from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class RecuperacionContrasena(Base):

    __tablename__ = "recuperacion_contrasena"

    id_recuperacion: Mapped[int] = mapped_column(
        primary_key=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    fecha_expiracion: Mapped[datetime] = mapped_column(
        nullable=False
    )

    fecha_uso: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    estado: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )