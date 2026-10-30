import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.database import get_db
from app.models.usuario_model import Usuario

router = APIRouter(prefix="/chat", tags=["Chat"])

UPLOAD_DIR = Path("uploads/chat")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENTOS = {
    "application/pdf",
    "application/zip",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class MensajeChat(BaseModel):
    id_mensaje: int
    id_equipo: int
    id_persona: int
    nombre: str
    contenido: str
    tipo: str
    nombre_archivo: Optional[str] = None
    tiene_foto: bool = False
    fecha_envio: datetime


def _miembro(db: Session, id_equipo: int, usuario: Usuario) -> None:
    row = db.execute(
        text(
            """
            SELECT e.id_equipo
            FROM equipo e
            JOIN proyecto p ON p.id_proyecto = e.id_proyecto
            WHERE e.id_equipo = :id_equipo
              AND p.id_organizacion = :org
            """
        ),
        {"id_equipo": id_equipo, "org": usuario.id_organizacion},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    if usuario.id_rol in (1, 2, 3):
        return

    miembro = db.execute(
        text(
            """
            SELECT 1 FROM equipo_persona
            WHERE id_equipo = :id_equipo
              AND id_persona = :id_persona
              AND fecha_fin IS NULL
            """
        ),
        {"id_equipo": id_equipo, "id_persona": usuario.id_persona},
    ).first()
    if not miembro:
        raise HTTPException(status_code=403, detail="No perteneces a este equipo")


def _clasificar(mime: str, filename: str = "") -> str:
    base = (mime or "").split(";")[0].strip().lower()
    ext = Path(filename or "").suffix.lower()

    if base.startswith("image/") or ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return "IMAGEN"

    if (
        base.startswith("audio/")
        or base == "video/webm"
        or ext in {".webm", ".mp3", ".wav", ".ogg", ".m4a", ".mp4"}
    ):
        return "AUDIO"

    documentos = {
        "application/pdf",
        "application/zip",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    if base in documentos or ext in {".pdf", ".zip", ".txt", ".doc", ".docx", ".xls", ".xlsx"}:
        return "ARCHIVO"

    raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

@router.get("/equipo/{id_equipo}/bandeja", response_model=list[MensajeChat])
def bandeja(
    id_equipo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    rows = db.execute(
        text(
            """
            SELECT m.id_mensaje, m.id_equipo, m.id_persona,
                   TRIM(p.nombre || ' ' || p.apellido) AS nombre,
                   m.contenido,
                   COALESCE(m.tipo, 'TEXTO') AS tipo,
                   m.nombre_archivo,
                   (p.foto_url IS NOT NULL) AS tiene_foto,
                   m.fecha_envio
            FROM mensaje_equipo m
            JOIN persona p ON p.id_persona = m.id_persona
            WHERE m.id_equipo = :id_equipo
            ORDER BY m.id_mensaje ASC
            """
        ),
        {"id_equipo": id_equipo},
    ).mappings().all()
    return [MensajeChat(**dict(r)) for r in rows]


@router.post("/equipo/{id_equipo}/archivo", response_model=MensajeChat, status_code=201)
async def enviar_archivo(
    id_equipo: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    tipo = _clasificar(archivo.content_type or "", archivo.filename or "")
    data = await archivo.read()
    if not data:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo supera 15 MB")

    ext = Path(archivo.filename or "archivo").suffix.lower()[:10] or ".bin"
    nombre_guardado = f"{uuid.uuid4().hex}{ext}"
    destino = UPLOAD_DIR / nombre_guardado
    destino.write_bytes(data)

    row = db.execute(
        text(
            """
            INSERT INTO mensaje_equipo
              (id_equipo, id_persona, contenido, tipo, nombre_archivo, ruta_archivo)
            VALUES
              (:id_equipo, :id_persona, :contenido, :tipo, :nombre, :ruta)
            RETURNING id_mensaje, fecha_envio
            """
        ),
        {
            "id_equipo": id_equipo,
            "id_persona": usuario.id_persona,
            "contenido": archivo.filename or nombre_guardado,
            "tipo": tipo,
            "nombre": archivo.filename or nombre_guardado,
            "ruta": str(destino),
        },
    ).mappings().first()
    db.commit()

    persona = db.execute(
        text(
            """
            SELECT TRIM(nombre || ' ' || apellido) AS nombre,
                   (foto_url IS NOT NULL) AS tiene_foto
            FROM persona WHERE id_persona = :id
            """
        ),
        {"id": usuario.id_persona},
    ).mappings().first()

    return MensajeChat(
        id_mensaje=row["id_mensaje"],
        id_equipo=id_equipo,
        id_persona=usuario.id_persona,
        nombre=persona["nombre"] if persona else usuario.nombre_usuario,
        contenido=archivo.filename or "",
        tipo=tipo,
        nombre_archivo=archivo.filename,
        tiene_foto=bool(persona["tiene_foto"]) if persona else False,
        fecha_envio=row["fecha_envio"],
    )


@router.get("/archivo/{id_mensaje}")
def descargar_archivo(
    id_mensaje: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    row = db.execute(
        text(
            """
            SELECT id_equipo, ruta_archivo, nombre_archivo, tipo
            FROM mensaje_equipo
            WHERE id_mensaje = :id
            """
        ),
        {"id": id_mensaje},
    ).mappings().first()
    if not row or not row["ruta_archivo"]:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    _miembro(db, row["id_equipo"], usuario)
    path = Path(row["ruta_archivo"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    media = "application/octet-stream"
    if path.suffix.lower() == ".png":
        media = "image/png"
    elif path.suffix.lower() in {".jpg", ".jpeg"}:
        media = "image/jpeg"
    elif path.suffix.lower() == ".pdf":
        media = "application/pdf"
    elif path.suffix.lower() == ".mp3":
        media = "audio/mpeg"
    elif path.suffix.lower() == ".webm":
        media = "audio/webm"

    return FileResponse(
        path,
        media_type=media,
        filename=row["nombre_archivo"] or path.name,
        content_disposition_type="inline",
    )