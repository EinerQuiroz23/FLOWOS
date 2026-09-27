from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recuperacion_contrasena_model import (
    RecuperacionContrasena
)


class RecuperacionContrasenaRepository:

    def __init__(self, db: Session):

        self.db = db

    def obtener_por_id(
        self,
        id_recuperacion: int
    ) -> Optional[RecuperacionContrasena]:

        return self.db.get(
            RecuperacionContrasena,
            id_recuperacion
        )

    def obtener_por_usuario(
        self,
        id_usuario: int
    ) -> List[RecuperacionContrasena]:

        consulta = select(
            RecuperacionContrasena
        ).where(
            RecuperacionContrasena.id_usuario
            == id_usuario
        )

        return self.db.scalars(
            consulta
        ).all()

    def obtener_token_activo(
        self,
        id_usuario: int,
        token_hash: str
    ) -> Optional[RecuperacionContrasena]:

        consulta = select(
            RecuperacionContrasena
        ).where(
            RecuperacionContrasena.id_usuario == id_usuario,
            RecuperacionContrasena.token_hash == token_hash,
            RecuperacionContrasena.estado.is_(True),
            RecuperacionContrasena.fecha_uso.is_(None),
            RecuperacionContrasena.fecha_expiracion
            > datetime.now()
        )

        return self.db.scalars(
            consulta
        ).first()

    def crear(
        self,
        recuperacion: RecuperacionContrasena
    ) -> RecuperacionContrasena:

        self.db.add(recuperacion)

        self.db.flush()

        return recuperacion

    def marcar_como_usado(
        self,
        recuperacion: RecuperacionContrasena
    ) -> RecuperacionContrasena:

        recuperacion.fecha_uso = datetime.now()

        recuperacion.estado = False

        self.db.flush()

        return recuperacion

    def desactivar_tokens_usuario(
        self,
        id_usuario: int
    ) -> None:

        consulta = select(
            RecuperacionContrasena
        ).where(
            RecuperacionContrasena.id_usuario == id_usuario,
            RecuperacionContrasena.estado.is_(True)
        )

        tokens = self.db.scalars(
            consulta
        ).all()

        for token in tokens:
            token.estado = False

        self.db.flush()