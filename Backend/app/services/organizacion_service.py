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
    


    @staticmethod
    def listar_con_admin(db: Session) -> list[dict]:
        from app.models.usuario_model import Usuario
        from app.models.persona_model import Persona

        organizaciones = (
            db.query(Organizacion)
            .order_by(Organizacion.id_organizacion.asc())
            .all()
        )

        resultado = []

        for org in organizaciones:
            admin_usuario = (
                db.query(Usuario)
                .filter(
                    Usuario.id_organizacion == org.id_organizacion,
                    Usuario.id_rol == 1,
                )
                .first()
            )

            admin_data = None
            if admin_usuario is not None:
                persona = (
                    db.query(Persona)
                    .filter(Persona.id_persona == admin_usuario.id_persona)
                    .first()
                )
                admin_data = {
                    "id_usuario": admin_usuario.id_usuario,
                    "nombre_usuario": admin_usuario.nombre_usuario,
                    "email": admin_usuario.email,
                    "nombre": getattr(persona, "nombre", None) if persona else None,
                    "apellido": getattr(persona, "apellido", None) if persona else None,
                    "telefono": getattr(persona, "telefono", None) if persona else None,
                }

            resultado.append({
                "id_organizacion": org.id_organizacion,
                "nombre": org.nombre,
                "descripcion": org.descripcion,
                "codigo": org.codigo,
                "estado": bool(org.estado),
                "fecha_creacion": org.fecha_creacion,
                "admin": admin_data,
            })

        return resultado

    @staticmethod
    def desactivar(db: Session, id_organizacion: int) -> Organizacion:
        organizacion = OrganizacionRepository.obtener_por_id(db, id_organizacion)

        if organizacion is None:
            raise ValueError("La organización no existe")

        # No permitir desactivar la org del Super Admin / plataforma
        if organizacion.codigo == "FLOW-PLATFORM-0001":
            raise ValueError("No se puede desactivar la organización de la plataforma")

        return OrganizacionRepository.desactivar(db, organizacion)


    @staticmethod
    def activar(db: Session, id_organizacion: int) -> Organizacion:
        organizacion = OrganizacionRepository.obtener_por_id(db, id_organizacion)

        if organizacion is None:
            raise ValueError("La organización no existe")

        return OrganizacionRepository.activar(db, organizacion)