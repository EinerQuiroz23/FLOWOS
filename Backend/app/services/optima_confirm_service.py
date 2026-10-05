from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.equipo_model import Equipo
from app.models.equipo_persona_model import EquipoPersona
from app.models.asignacion_tarea_model import AsignacionTarea
from app.models.tarea_model import Tarea

from app.optima.service.optima_team_service import OptimaTeamService
from app.optima.service.optima_service import OptimaService

from app.schemas.optima_confirm_schema import (
    OptimaConfirmarResponse,
    AsignacionCreadaItem,
)


class OptimaConfirmService:

    def __init__(self, db: Session):
        self.db = db

    def confirmar(
        self,
        id_proyecto: int,
        id_organizacion: int,
        nombre_equipo: str | None = None,
    ) -> OptimaConfirmarResponse:

        # 1) Propuesta OPTIMA
        team_service = OptimaTeamService(self.db)
        propuesta = team_service.proponer_equipo(
            id_proyecto=id_proyecto,
            id_organizacion=id_organizacion,
        )

        if not propuesta.integrantes:
            raise ValueError("OPTIMA no propuso integrantes para este proyecto.")

        # 2) Crear equipo
        nombre = (nombre_equipo or f"OPTIMA - {propuesta.proyecto}").strip()[:150]

        equipo = Equipo(
            id_proyecto=id_proyecto,
            nombre=nombre,
            descripcion="Equipo generado automáticamente por OPTIMA",
            estado="ACTIVO",
        )
        self.db.add(equipo)
        self.db.flush()

        # 3) Agregar personas al equipo
        mapa_ep: dict[int, EquipoPersona] = {}
        id_lider = propuesta.lider.id_persona if propuesta.lider else None

        for integ in propuesta.integrantes:
            rol = "LIDER" if id_lider and integ.id_persona == id_lider else "INTEGRANTE"

            ep = EquipoPersona(
                id_equipo=equipo.id_equipo,
                id_persona=integ.id_persona,
                rol_equipo=rol,
                dedicacion=Decimal("50.00"),
                fecha_inicio=date.today(),
                fecha_fin=None,
            )
            self.db.add(ep)
            self.db.flush()
            mapa_ep[integ.id_persona] = ep

        # Si el líder no vino en integrantes (raro), agregarlo
        if id_lider and id_lider not in mapa_ep and propuesta.lider:
            ep = EquipoPersona(
                id_equipo=equipo.id_equipo,
                id_persona=id_lider,
                rol_equipo="LIDER",
                dedicacion=Decimal("50.00"),
                fecha_inicio=date.today(),
                fecha_fin=None,
            )
            self.db.add(ep)
            self.db.flush()
            mapa_ep[id_lider] = ep

        # 4) Tareas del proyecto → pasarlas a este equipo
        tareas = (
            self.db.query(Tarea)
            .filter(Tarea.id_proyecto == id_proyecto)
            .all()
        )

        # Filtrar por organización si tu modelo de tarea/proyecto lo permite
        for tarea in tareas:
            tarea.id_equipo = equipo.id_equipo

        self.db.flush()

        # 5) Asignar cada tarea al mejor candidato OPTIMA (modo tarea)
        optima = OptimaService(self.db)
        detalle: list[AsignacionCreadaItem] = []
        hoy = date.today()

        for tarea in tareas:
            try:
                candidatos = optima.evaluar_tarea(
                    id_tarea=tarea.id_tarea,
                    id_organizacion=id_organizacion,
                )
            except Exception:
                candidatos = []

            # Preferir elegibles que estén en el equipo OPTIMA
            ids_equipo = set(mapa_ep.keys())
            ordenados = sorted(
                [c for c in candidatos if c.id_persona in ids_equipo],
                key=lambda c: (
                    0 if getattr(c, "elegible", False) else 1,
                    getattr(c, "ranking", 999) or 999,
                    -(getattr(c, "puntuacion_optima", 0) or 0),
                ),
            )

            if not ordenados:
                # fallback: primer integrante del equipo
                persona_id = next(iter(mapa_ep.keys()))
            else:
                persona_id = ordenados[0].id_persona

            ep = mapa_ep[persona_id]

            # Evitar duplicado
            existe = (
                self.db.query(AsignacionTarea)
                .filter(
                    AsignacionTarea.id_tarea == tarea.id_tarea,
                    AsignacionTarea.id_equipo_persona == ep.id_equipo_persona,
                )
                .first()
            )
            if existe:
                continue

            fecha_inicio = tarea.fecha_inicio or hoy
            fecha_limite = tarea.fecha_limite or hoy

            asignacion = AsignacionTarea(
                id_tarea=tarea.id_tarea,
                id_equipo_persona=ep.id_equipo_persona,
                fecha_asignacion=hoy,
                fecha_inicio=fecha_inicio,
                fecha_limite=fecha_limite,
                dedicacion=Decimal("50.00"),
                estado="ASIGNADA",
            )
            self.db.add(asignacion)
            self.db.flush()

            nombre_persona = next(
                (i.persona for i in propuesta.integrantes if i.id_persona == persona_id),
                f"Persona {persona_id}",
            )
            if propuesta.lider and propuesta.lider.id_persona == persona_id:
                nombre_persona = propuesta.lider.persona

            detalle.append(
                AsignacionCreadaItem(
                    id_asignacion=asignacion.id_asignacion,
                    id_tarea=tarea.id_tarea,
                    nombre_tarea=tarea.nombre,
                    id_persona=persona_id,
                    persona=nombre_persona,
                )
            )

            integrantes = getattr(propuesta, "integrantes", None) or []
            if isinstance(propuesta, dict):
                integrantes = propuesta.get("integrantes") or []

            if not integrantes:
                raise ValueError("OPTIMA no propuso integrantes para este proyecto.")

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise ValueError("No se pudo confirmar la propuesta de OPTIMA.")

        return OptimaConfirmarResponse(
            id_proyecto=id_proyecto,
            id_equipo=equipo.id_equipo,
            nombre_equipo=nombre,
            id_lider=id_lider,
            integrantes_agregados=len(mapa_ep),
            asignaciones_creadas=len(detalle),
            detalle_asignaciones=detalle,
            mensaje=(
                f"Equipo '{nombre}' creado con {len(mapa_ep)} integrante(s). "
                f"Se generaron {len(detalle)} asignación(es)."
            ),
        )