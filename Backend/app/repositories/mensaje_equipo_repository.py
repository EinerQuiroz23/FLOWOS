from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mensaje_equipo_model import MensajeEquipo
from app.models.persona_model import Persona


class MensajeEquipoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar_por_equipo(
        self,
        id_equipo: int,
        limite: int = 100,
    ) -> list[tuple[MensajeEquipo, str]]:
        consulta = (
            select(
                MensajeEquipo,
                (Persona.nombre + " " + Persona.apellido).label(
                    "nombre_persona"
                ),
            )
            .join(
                Persona,
                Persona.id_persona == MensajeEquipo.id_persona,
            )
            .where(MensajeEquipo.id_equipo == id_equipo)
            .order_by(MensajeEquipo.fecha_creacion.asc())
            .limit(limite)
        )
        return list(self.db.execute(consulta).all())

    def crear(self, mensaje: MensajeEquipo) -> MensajeEquipo:
        self.db.add(mensaje)
        self.db.flush()
        return mensaje