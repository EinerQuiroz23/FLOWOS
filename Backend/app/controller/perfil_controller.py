import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.database import get_db
from app.models.usuario_model import Usuario

router = APIRouter(prefix="/personas", tags=["Perfil"])

FOTO_DIR = Path("uploads/perfiles")
FOTO_DIR.mkdir(parents=True, exist_ok=True)

ROLES = ("ADMIN", "LIDER_PROYECTO", "SECRETARIO", "EMPLEADO")


@router.post("/mi-foto")
async def subir_mi_foto(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_any_role(*ROLES)),
):
    base = (archivo.content_type or "").split(";")[0].strip().lower()
    if base not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="La foto debe ser JPG, PNG o WEBP")
    data = await archivo.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La foto supera 5 MB")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[base]
    destino = FOTO_DIR / f"{usuario.id_persona}_{uuid.uuid4().hex}{ext}"
    destino.write_bytes(data)
    anterior = db.execute(
        text("SELECT foto_url FROM persona WHERE id_persona = :id"),
        {"id": usuario.id_persona},
    ).scalar()
    db.execute(
        text("UPDATE persona SET foto_url = :ruta WHERE id_persona = :id"),
        {"ruta": str(destino), "id": usuario.id_persona},
    )
    db.commit()
    if anterior:
        vieja = Path(str(anterior))
        if vieja.exists():
            vieja.unlink()
    return {"ok": True}


@router.get("/foto/{id_persona}")
def ver_foto(
    id_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_any_role(*ROLES)),
):
    row = db.execute(
        text(
            """
            SELECT foto_url FROM persona
            WHERE id_persona = :id AND id_organizacion = :org
            """
        ),
        {"id": id_persona, "org": usuario.id_organizacion},
    ).mappings().first()
    if not row or not row["foto_url"]:
        raise HTTPException(status_code=404, detail="Sin foto")
    path = Path(row["foto_url"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sin foto")
    media = "image/jpeg"
    if path.suffix.lower() == ".png":
        media = "image/png"
    elif path.suffix.lower() == ".webp":
        media = "image/webp"
    return FileResponse(path, media_type=media)