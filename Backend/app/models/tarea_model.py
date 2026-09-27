from datetime import date, datetime 
from decimal import Decimal
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Tarea(Base):
    __tablename__ = "tarea"

    id_tarea: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_proyecto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("proyecto.id_proyecto"),
        nullable=False
    )

    id_equipo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("equipo.id_equipo"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descripcion: Mapped[Optional[str ]] = mapped_column(
        Text,
        nullable=True
    )

    prioridad: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIA"
    )

    horas_estimadas: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    fecha_limite: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDIENTE"
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default= func.current_timestamp()
    )