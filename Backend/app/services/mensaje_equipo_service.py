from sqlalchemy.orm import Session

from app.models.mensaje_equipo_model import MensajeEquipo
from app.models.equipo_model import Equipo
from app.models.equipo_persona_model import EquipoPersona
from app.models.persona_model import Persona
from app.models.proyecto_model import Proyecto

from app.repositories.mensaje_equipo_repository import (
    MensajeEquipoRepository,
)
from app.schemas.mensaje_equipo_schema import (
    MensajeEquipoCreate,
    MensajeEquipoResponse,
)


class MensajeEquipoService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = MensajeEquipoRepository(db)

    def _equipo_de_organizacion(
        self,
        id_equipo: int,
        id_organizacion: int,
    ) -> Equipo:
        equipo = (
            self.db.query(Equipo)
            .join(Proyecto, Proyecto.id_proyecto == Equipo.id_proyecto)
            .filter(
                Equipo.id_equipo == id_equipo,
                Proyecto.id_organizacion == id_organizacion,
            )
            .first()
        )
        if equipo is None:
            raise ValueError("El equipo no existe en tu organización.")
        return equipo

    def _es_miembro_o_admin(
        self,
        id_equipo: int,
        id_persona: int,
        id_rol: int,
    ) -> bool:
        # ADMIN org = 1 → acceso
        if id_rol == 1:
            return True

        miembro = (
            self.db.query(EquipoPersona)
            .filter(
                EquipoPersona.id_equipo == id_equipo,
                EquipoPersona.id_persona == id_persona,
                EquipoPersona.fecha_fin.is_(None),
            )
            .first()
        )
        return miembro is not None

    def listar(
        self,
        id_equipo: int,
        id_organizacion: int,
        id_persona: int,
        id_rol: int,
    ) -> list[MensajeEquipoResponse]:
        self._equipo_de_organizacion(id_equipo, id_organizacion)

        if not self._es_miembro_o_admin(id_equipo, id_persona, id_rol):
            raise ValueError("No perteneces a este equipo.")

        filas = self.repo.listar_por_equipo(id_equipo)
        resultado: list[MensajeEquipoResponse] = []

        for mensaje, nombre in filas:
            resultado.append(
                MensajeEquipoResponse(
                    id_mensaje=mensaje.id_mensaje,
                    id_equipo=mensaje.id_equipo,
                    id_persona=mensaje.id_persona,
                    nombre_persona=nombre or "Usuario",
                    contenido=mensaje.contenido,
                    fecha_creacion=mensaje.fecha_creacion,
                )
            )
        return resultado

    def crear(
        self,
        id_equipo: int,
        datos: MensajeEquipoCreate,
        id_organizacion: int,
        id_persona: int,
        id_rol: int,
    ) -> MensajeEquipoResponse:
        self._equipo_de_organizacion(id_equipo, id_organizacion)

        if not self._es_miembro_o_admin(id_equipo, id_persona, id_rol):
            raise ValueError("No perteneces a este equipo.")

        texto = datos.contenido.strip()
        if not texto:
            raise ValueError("El mensaje no puede estar vacío.")

        mensaje = MensajeEquipo(
            id_equipo=id_equipo,
            id_persona=id_persona,
            contenido=texto,
        )
        self.repo.crear(mensaje)
        self.db.commit()
        self.db.refresh(mensaje)

        persona = self.db.get(Persona, id_persona)
        nombre = (
            f"{persona.nombre} {persona.apellido}"
            if persona
            else "Usuario"
        )

        return MensajeEquipoResponse(
            id_mensaje=mensaje.id_mensaje,
            id_equipo=mensaje.id_equipo,
            id_persona=mensaje.id_persona,
            nombre_persona=nombre,
            contenido=mensaje.contenido,
            fecha_creacion=mensaje.fecha_creacion,
        )