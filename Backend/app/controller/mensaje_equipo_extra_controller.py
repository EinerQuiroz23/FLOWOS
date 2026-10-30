import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.database import get_db
from app.models.usuario_model import Usuario

router = APIRouter(prefix="/chat", tags=["Chat"])

UPLOAD_DIR = Path("uploads/chat")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

TIPOS_OK = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "audio/mpeg",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
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
    fecha_envio: datetime


class MensajeTexto(BaseModel):
    contenido: str = Field(min_length=1, max_length=2000)


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


def _fila(r) -> MensajeChat:
    return MensajeChat(
        id_mensaje=r["id_mensaje"],
        id_equipo=r["id_equipo"],
        id_persona=r["id_persona"],
        nombre=r["nombre"],
        contenido=r["contenido"] or "",
        tipo=r["tipo"] or "TEXTO",
        nombre_archivo=r["nombre_archivo"],
        fecha_envio=r["fecha_envio"],
    )

@router.get("/mis-equipos")
def mis_equipos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    rows = db.execute(
        text(
            """
            SELECT e.id_equipo, e.id_proyecto, e.nombre, e.descripcion, e.estado
            FROM equipo e
            JOIN proyecto p ON p.id_proyecto = e.id_proyecto
            JOIN equipo_persona ep ON ep.id_equipo = e.id_equipo
            WHERE p.id_organizacion = :org
              AND ep.id_persona = :id_persona
              AND ep.fecha_fin IS NULL
            ORDER BY e.nombre
            """
        ),
        {
            "org": usuario.id_organizacion,
            "id_persona": usuario.id_persona,
        },
    ).mappings().all()
    return [dict(r) for r in rows]

@router.get("/equipo/{id_equipo}/bandeja", response_model=list[MensajeChat])
def bandeja(
    id_equipo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    rows = (
        db.execute(
            text(
                """
                SELECT m.id_mensaje, m.id_equipo, m.id_persona,
                       TRIM(p.nombre || ' ' || p.apellido) AS nombre,
                       m.contenido,
                       COALESCE(m.tipo, 'TEXTO') AS tipo,
                       m.nombre_archivo,
                       m.fecha_envio as fecha_envio
                FROM mensaje_equipo m
                JOIN persona p ON p.id_persona = m.id_persona
                WHERE m.id_equipo = :id_equipo
                  AND NOT EXISTS (
                    SELECT 1 FROM mensaje_equipo_oculto o
                    WHERE o.id_mensaje = m.id_mensaje
                      AND o.id_persona = :id_persona
                  )
                ORDER BY m.id_mensaje ASC
                """
            ),
            {"id_equipo": id_equipo, "id_persona": usuario.id_persona},
        )
        .mappings()
        .all()
    )
    return [_fila(r) for r in rows]


@router.post(
    "/equipo/{id_equipo}/bandeja",
    response_model=MensajeChat,
    status_code=201,
)
def enviar_texto(
    id_equipo: int,
    datos: MensajeTexto,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    contenido = datos.contenido.strip()
    if not contenido:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    row = (
        db.execute(
            text(
                """
                INSERT INTO mensaje_equipo
                  (id_equipo, id_persona, contenido, tipo)
                VALUES
                  (:id_equipo, :id_persona, :contenido, 'TEXTO')
                RETURNING id_mensaje, fecha_envio as fecha_envio
                """
            ),
            {
                "id_equipo": id_equipo,
                "id_persona": usuario.id_persona,
                "contenido": contenido,
            },
        )
        .mappings()
        .first()
    )
    db.commit()

    persona = (
        db.execute(
            text(
                """
                SELECT TRIM(nombre || ' ' || apellido) AS nombre
                FROM persona
                WHERE id_persona = :id
                """
            ),
            {"id": usuario.id_persona},
        )
        .mappings()
        .first()
    )

    return MensajeChat(
        id_mensaje=row["id_mensaje"],
        id_equipo=id_equipo,
        id_persona=usuario.id_persona,
        nombre=persona["nombre"] if persona else usuario.nombre_usuario,
        contenido=contenido,
        tipo="TEXTO",
        fecha_envio=row["fecha_envio"],
    )


@router.post(
    "/equipo/{id_equipo}/archivo",
    response_model=MensajeChat,
    status_code=201,
)
async def enviar_archivo(
    id_equipo: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    tipo_mime = archivo.content_type or ""
    if tipo_mime not in TIPOS_OK:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    data = await archivo.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo supera 15 MB")

    if tipo_mime.startswith("image/"):
        tipo = "IMAGEN"
    elif tipo_mime.startswith("audio/"):
        tipo = "AUDIO"
    else:
        tipo = "ARCHIVO"

    ext = Path(archivo.filename or "archivo").suffix.lower()[:10]
    nombre_guardado = f"{uuid.uuid4().hex}{ext}"
    destino = UPLOAD_DIR / nombre_guardado
    destino.write_bytes(data)

    row = (
        db.execute(
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
        )
        .mappings()
        .first()
    )
    db.commit()

    persona = (
        db.execute(
            text(
                """
                SELECT TRIM(nombre || ' ' || apellido) AS nombre
                FROM persona
                WHERE id_persona = :id
                """
            ),
            {"id": usuario.id_persona},
        )
        .mappings()
        .first()
    )

    return MensajeChat(
        id_mensaje=row["id_mensaje"],
        id_equipo=id_equipo,
        id_persona=usuario.id_persona,
        nombre=persona["nombre"] if persona else usuario.nombre_usuario,
        contenido=archivo.filename or "",
        tipo=tipo,
        nombre_archivo=archivo.filename,
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
    row = (
        db.execute(
            text(
                """
                SELECT m.id_equipo, m.ruta_archivo, m.nombre_archivo
                FROM mensaje_equipo m
                WHERE m.id_mensaje = :id
                """
            ),
            {"id": id_mensaje},
        )
        .mappings()
        .first()
    )
    if not row or not row["ruta_archivo"]:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    _miembro(db, row["id_equipo"], usuario)
    path = Path(row["ruta_archivo"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(path, filename=row["nombre_archivo"] or path.name)


@router.delete("/equipo/{id_equipo}/para-mi", status_code=204)
def borrar_conversacion_para_mi(
    id_equipo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")
    ),
):
    _miembro(db, id_equipo, usuario)
    db.execute(
        text(
            """
            INSERT INTO mensaje_equipo_oculto (id_mensaje, id_persona)
            SELECT m.id_mensaje, :id_persona
            FROM mensaje_equipo m
            WHERE m.id_equipo = :id_equipo
            ON CONFLICT DO NOTHING
            """
        ),
        {"id_equipo": id_equipo, "id_persona": usuario.id_persona},
    )
    db.commit()