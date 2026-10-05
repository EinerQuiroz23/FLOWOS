from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.usuario_model import Usuario
from app.schemas.mensaje_equipo_schema import MensajeEquipoCreate
from app.services.mensaje_equipo_service import MensajeEquipoService

router = APIRouter(tags=["Chat WS"])


class ConnectionManager:
    def __init__(self):
        # id_equipo -> lista de websockets
        self.salas: dict[int, list[WebSocket]] = {}

    async def connect(self, id_equipo: int, websocket: WebSocket):
        await websocket.accept()
        self.salas.setdefault(id_equipo, []).append(websocket)

    def disconnect(self, id_equipo: int, websocket: WebSocket):
        if id_equipo in self.salas:
            self.salas[id_equipo] = [
                ws for ws in self.salas[id_equipo] if ws != websocket
            ]

    async def broadcast(self, id_equipo: int, data: dict):
        for ws in list(self.salas.get(id_equipo, [])):
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(id_equipo, ws)


manager = ConnectionManager()


def _usuario_desde_token(token: str, db: Session) -> Usuario | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        sub = payload.get("sub")
        if sub is None:
            return None
        return db.query(Usuario).filter(Usuario.id_usuario == int(sub)).first()
    except (JWTError, ValueError):
        return None


@router.websocket("/ws/chat/{id_equipo}")
async def chat_websocket(
    websocket: WebSocket,
    id_equipo: int,
    token: str = Query(...),
):
    db = SessionLocal()
    try:
        usuario = _usuario_desde_token(token, db)
        if usuario is None or not usuario.estado:
            await websocket.close(code=4401)
            return

        service = MensajeEquipoService(db)
        try:
            # Valida org + membresía (o admin)
            service.listar(
                id_equipo=id_equipo,
                id_organizacion=usuario.id_organizacion,
                id_persona=usuario.id_persona,
                id_rol=usuario.id_rol,
            )
        except ValueError:
            await websocket.close(code=4403)
            return

        await manager.connect(id_equipo, websocket)

        while True:
            data = await websocket.receive_json()
            contenido = (data.get("contenido") or "").strip()
            if not contenido:
                continue

            try:
                mensaje = service.crear(
                    id_equipo=id_equipo,
                    datos=MensajeEquipoCreate(contenido=contenido),
                    id_organizacion=usuario.id_organizacion,
                    id_persona=usuario.id_persona,
                    id_rol=usuario.id_rol,
                )
                await manager.broadcast(
                    id_equipo,
                    {
                        "id_mensaje": mensaje.id_mensaje,
                        "id_equipo": mensaje.id_equipo,
                        "id_persona": mensaje.id_persona,
                        "nombre_persona": mensaje.nombre_persona,
                        "contenido": mensaje.contenido,
                        "fecha_creacion": mensaje.fecha_creacion.isoformat(),
                    },
                )
            except ValueError as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        manager.disconnect(id_equipo, websocket)
    finally:
        db.close()