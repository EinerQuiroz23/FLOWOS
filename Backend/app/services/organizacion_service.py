import random
import string

from sqlalchemy.orm import Session

from app.models.organizacion_model import Organizacion
from app.repositories.organizacion_repository import OrganizacionRepository
from app.schemas.organizacion_schema import OrganizacionCreate


class OrganizacionService:

    @staticmethod
    def _generar_codigo_unico(db: Session) -> str:
        """
        Genera un código único con formato: FLOW-XXXX-XXXXX
        Ejemplo: FLOW-ACME-8X29K
        """
        while True:
            letras = ''.join(random.choices(string.ascii_uppercase, k=4))
            alfanumerico = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=5)
            )
            codigo = f"FLOW-{letras}-{alfanumerico}"

            # Verificar que no exista
            existente = OrganizacionRepository.obtener_por_codigo(db, codigo)
            if existente is None:
                return codigo

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_organizacion: int
    ) -> Organizacion:

        organizacion = OrganizacionRepository.obtener_por_id(
            db,
            id_organizacion
        )

        if organizacion is None or not organizacion.estado:
            raise ValueError(
                "La organización no existe o está inactiva"
            )

        return organizacion

    @staticmethod
    def obtener_por_codigo(
        db: Session,
        codigo: str
    ) -> Organizacion:

        organizacion = OrganizacionRepository.obtener_por_codigo(
            db,
            codigo.strip().upper()
        )

        if organizacion is None or not organizacion.estado:
            raise ValueError(
                "El código de organización no es válido o la organización está inactiva"
            )

        return organizacion

    @staticmethod
    def crear(
        db: Session,
        datos: OrganizacionCreate
    ) -> Organizacion:

        nombre = datos.nombre.strip()

        if not nombre:
            raise ValueError(
                "El nombre de la organización es obligatorio"
            )

        existente = OrganizacionRepository.obtener_por_nombre(
            db,
            nombre
        )

        if existente is not None:
            raise ValueError(
                "Ya existe una organización con ese nombre"
            )

        codigo = OrganizacionService._generar_codigo_unico(db)

        organizacion = Organizacion(
            nombre=nombre,
            descripcion=datos.descripcion,
            codigo=codigo
        )

        return OrganizacionRepository.crear(
            db,
            organizacion
        )