from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import enviar_codigo_recuperacion
from app.core.security import (
    create_access_token,
    hash_password,
    hash_reset_token,
    verify_password,
)

from app.models.organizacion_model import Organizacion
from app.models.persona_model import Persona
from app.models.recuperacion_contrasena_model import RecuperacionContrasena
from app.models.usuario_model import Usuario

from app.repositories.organizacion_repository import OrganizacionRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.recuperacion_contrasena_repository import (
    RecuperacionContrasenaRepository,
)
from app.repositories.usuario_repository import UsuarioRepository

from app.schemas.auth_schema import (
    CrearAdminOrganizacionRequest,
    RegistroEmpleadoRequest,
    RegistroOrganizacionRequest,
)

from app.services.organizacion_service import OrganizacionService


class AuthService:

    # =========================================================
    # LOGIN
    # =========================================================

    @staticmethod
    def login(db: Session, email: str, contrasena: str) -> str:
        usuario = UsuarioRepository.obtener_por_email(db, email)

        if not usuario or not usuario.estado:
            raise ValueError("Credenciales inválidas")

        if not verify_password(contrasena, usuario.contrasena_hash):
            raise ValueError("Credenciales inválidas")

        usuario.ultimo_acceso = datetime.now()
        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol,
            }
        )

    # =========================================================
    # REGISTRO ORGANIZACIÓN (legacy / público si lo usas)
    # =========================================================

    @staticmethod
    def registrar_organizacion(
        db: Session,
        datos: RegistroOrganizacionRequest,
    ) -> str:
        nombre_organizacion = datos.nombre_organizacion.strip()
        nombre_usuario = datos.nombre_usuario.strip()

        if not nombre_organizacion:
            raise ValueError("El nombre de la organización es obligatorio")

        if OrganizacionRepository.obtener_por_nombre(db, nombre_organizacion):
            raise ValueError("Ya existe una organización con ese nombre")

        if UsuarioRepository.obtener_por_email(db, datos.email):
            raise ValueError("Ya existe un usuario con ese correo")

        codigo = OrganizacionService._generar_codigo_unico(db)

        organizacion = Organizacion(
            nombre=nombre_organizacion,
            descripcion=datos.descripcion_organizacion,
            codigo=codigo,
        )
        OrganizacionRepository.crear(db, organizacion)
        db.flush()

        persona = Persona(
            id_organizacion=organizacion.id_organizacion,
            nombre=datos.nombre.strip(),
            apellido=datos.apellido.strip(),
            email=datos.email,
            telefono=datos.telefono,
            capacidad_horas_semana=datos.capacidad_horas_semana,
        )
        db.add(persona)
        db.flush()

        usuario = Usuario(
            id_organizacion=organizacion.id_organizacion,
            id_persona=persona.id_persona,
            id_rol=1,
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena),
        )
        UsuarioRepository.crear(db, usuario)
        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol,
            }
        )

    # =========================================================
    # RECUPERAR CONTRASEÑA
    # =========================================================

    @staticmethod
    def solicitar_recuperacion(db: Session, email: str) -> None:
        usuario = UsuarioRepository.obtener_por_email(db, email)

        if not usuario or not usuario.estado:
            return

        repository = RecuperacionContrasenaRepository(db)
        repository.desactivar_tokens_usuario(usuario.id_usuario)

        codigo = f"{random.randint(100000, 999999)}"
        token_hash = hash_reset_token(codigo)

        expiracion = datetime.now() + timedelta(
            minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
        )

        recuperacion = RecuperacionContrasena(
            id_usuario=usuario.id_usuario,
            token_hash=token_hash,
            fecha_expiracion=expiracion,
        )
        repository.crear(recuperacion)
        db.commit()

        try:
            enviar_codigo_recuperacion(email, codigo)
        except Exception as e:
            print(f"Error enviando correo de recuperación: {e}")
            raise ValueError(
                "No se pudo enviar el correo de recuperación. Intenta más tarde."
            )

    @staticmethod
    def restablecer_contrasena(
        db: Session,
        email: str,
        codigo: str,
        nueva_contrasena: str,
    ) -> None:
        usuario = UsuarioRepository.obtener_por_email(db, email)

        if usuario is None or not usuario.estado:
            raise ValueError("El código es inválido o ha expirado")

        token_hash = hash_reset_token(codigo)
        repository = RecuperacionContrasenaRepository(db)

        recuperacion = (
            db.query(RecuperacionContrasena)
            .filter(
                RecuperacionContrasena.id_usuario == usuario.id_usuario,
                RecuperacionContrasena.token_hash == token_hash,
                RecuperacionContrasena.estado.is_(True),
                RecuperacionContrasena.fecha_uso.is_(None),
                RecuperacionContrasena.fecha_expiracion > datetime.now(),
            )
            .first()
        )

        if recuperacion is None:
            raise ValueError("El código es inválido o ha expirado")

        usuario.contrasena_hash = hash_password(nueva_contrasena)
        repository.marcar_como_usado(recuperacion)
        repository.desactivar_tokens_usuario(usuario.id_usuario)
        db.commit()

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _generar_nombre_usuario(db: Session, email: str) -> str:
        base = email.split("@")[0].lower().strip().replace(" ", ".")
        candidato = base
        contador = 1

        while UsuarioRepository.obtener_por_nombre_usuario(db, candidato):
            candidato = f"{base}{contador}"
            contador += 1

        return candidato

    # =========================================================
    # REGISTRO EMPLEADO (código de organización)
    # =========================================================

    @staticmethod
    def registrar_empleado(
        db: Session,
        datos: RegistroEmpleadoRequest,
    ) -> str:
        codigo = datos.codigo_organizacion.strip().upper()

        organizacion = OrganizacionRepository.obtener_por_codigo(db, codigo)

        if organizacion is None or not organizacion.estado:
            raise ValueError(
                "El código de organización no es válido o la organización está inactiva"
            )

        persona_repo = PersonaRepository(db)
        persona = persona_repo.obtener_por_email_organizacion(
            datos.email,
            organizacion.id_organizacion,
        )

        if persona is None:
            raise ValueError(
                "No estás registrado como empleado de esta organización. "
                "Contacta a tu administrador."
            )

        usuario_existente = UsuarioRepository.obtener_por_persona(
            db,
            persona.id_persona,
        )
        if usuario_existente is not None:
            raise ValueError("Ya existe una cuenta asociada a este empleado")

        if UsuarioRepository.obtener_por_email(db, datos.email):
            raise ValueError("Ya existe un usuario con ese correo")

        nombre_usuario = AuthService._generar_nombre_usuario(db, datos.email)

        usuario = Usuario(
            id_organizacion=organizacion.id_organizacion,
            id_persona=persona.id_persona,
            id_rol=4,  # EMPLEADO
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena),
        )
        UsuarioRepository.crear(db, usuario)
        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol,
            }
        )

    # =========================================================
    # CREAR / CAMBIAR ADMIN DE ORGANIZACIÓN (SUPER ADMIN)
    # =========================================================

    @staticmethod
    def crear_admin_organizacion(
        db: Session,
        id_organizacion: int,
        datos: CrearAdminOrganizacionRequest,
    ) -> dict:
        organizacion = OrganizacionRepository.obtener_por_id(
            db, id_organizacion
        )

        if organizacion is None or not organizacion.estado:
            raise ValueError("La organización no existe o está inactiva")

        if UsuarioRepository.obtener_por_email(db, datos.email):
            raise ValueError("Ya existe un usuario con ese correo")

        persona_repo = PersonaRepository(db)
        if persona_repo.obtener_por_email_organizacion(
            datos.email, id_organizacion
        ):
            raise ValueError(
                "Ya existe una persona con ese correo en esta organización"
            )

        # 1) Liberar el cupo de ADMIN (la unique es por id_organizacion + rol 1)
        admins_previos = (
            db.query(Usuario)
            .filter(
                Usuario.id_organizacion == id_organizacion,
                Usuario.id_rol == 1,
            )
            .all()
        )
        for admin_prev in admins_previos:
            admin_prev.id_rol = 4  # EMPLEADO (libera uq_unico_admin_por_organizacion)
            admin_prev.estado = False

        db.flush()  # aplica el cambio ANTES de insertar el nuevo admin

        # 2) Crear persona
        persona = Persona(
            id_organizacion=id_organizacion,
            nombre=datos.nombre.strip(),
            apellido=datos.apellido.strip(),
            email=datos.email,
            telefono=datos.telefono,
            capacidad_horas_semana=datos.capacidad_horas_semana,
            estado=True,
        )
        db.add(persona)
        db.flush()

        # 3) Crear usuario ADMIN
        nombre_usuario = AuthService._generar_nombre_usuario(db, datos.email)

        usuario = Usuario(
            id_organizacion=id_organizacion,
            id_persona=persona.id_persona,
            id_rol=1,  # ADMIN
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena),
            estado=True,
        )
        UsuarioRepository.crear(db, usuario)
        db.commit()

        return {
            "mensaje": "Admin de organización creado/actualizado correctamente",
            "id_usuario": usuario.id_usuario,
            "id_persona": persona.id_persona,
            "email": usuario.email,
            "nombre_usuario": usuario.nombre_usuario,
            "organizacion": organizacion.nombre,
            "codigo_organizacion": getattr(
                organizacion, "codigo", None
            ) or getattr(organizacion, "codigo_organizacion", None),
        }



    @staticmethod
    def promover_admin_organizacion(
        db: Session,
        id_organizacion: int,
        id_persona: int,
        contrasena: str | None = None,
    ) -> dict:
        organizacion = OrganizacionRepository.obtener_por_id(
            db, id_organizacion
        )
        if organizacion is None or not organizacion.estado:
            raise ValueError("La organización no existe o está inactiva")

        persona_repo = PersonaRepository(db)
        persona = persona_repo.obtener_por_id_organizacion(
            id_persona, id_organizacion
        )
        # Si el método se llama distinto en tu repo:
        # persona = persona_repo.obtener_por_id(id_persona)
        # y validar persona.id_organizacion == id_organizacion

        if persona is None:
            raise ValueError(
                "La persona no existe en esta organización"
            )

        # 1) Liberar cupo ADMIN actual
        admins_previos = (
            db.query(Usuario)
            .filter(
                Usuario.id_organizacion == id_organizacion,
                Usuario.id_rol == 1,
            )
            .all()
        )
        for admin_prev in admins_previos:
            admin_prev.id_rol = 4
            admin_prev.estado = False

        db.flush()

        # 2) Usuario de esa persona
        usuario = UsuarioRepository.obtener_por_persona(
            db, id_persona
        )

        if usuario is not None:
            if usuario.id_organizacion != id_organizacion:
                raise ValueError(
                    "El usuario de esa persona pertenece a otra organización"
                )
            usuario.id_rol = 1
            usuario.estado = True
            if contrasena and contrasena.strip():
                usuario.contrasena_hash = hash_password(contrasena.strip())
        else:
            if not contrasena or len(contrasena.strip()) < 8:
                raise ValueError(
                    "Esta persona no tiene cuenta. "
                    "Debes indicar una contraseña (mín. 8 caracteres)."
                )
            if UsuarioRepository.obtener_por_email(db, persona.email):
                raise ValueError(
                    "Ya existe un usuario con el correo de esta persona"
                )

            nombre_usuario = AuthService._generar_nombre_usuario(
                db, persona.email
            )
            usuario = Usuario(
                id_organizacion=id_organizacion,
                id_persona=persona.id_persona,
                id_rol=1,
                nombre_usuario=nombre_usuario,
                email=persona.email,
                contrasena_hash=hash_password(contrasena.strip()),
                estado=True,
            )
            UsuarioRepository.crear(db, usuario)

        db.commit()
        db.refresh(usuario)

        return {
            "mensaje": "Admin actualizado correctamente",
            "id_usuario": usuario.id_usuario,
            "id_persona": persona.id_persona,
            "email": usuario.email,
            "nombre_usuario": usuario.nombre_usuario,
            "organizacion": organizacion.nombre,
            "codigo_organizacion": getattr(
                organizacion, "codigo", None
            )
            or getattr(organizacion, "codigo_organizacion", None),
        }