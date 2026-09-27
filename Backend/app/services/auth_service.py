from datetime import datetime, timedelta
import email
from email.mime import base

from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password
)

from app.models.organizacion_model import Organizacion
from app.models.persona_model import Persona
from app.models.recuperacion_contrasena_model import (
    RecuperacionContrasena
)
from app.models.usuario_model import Usuario

from app.repositories.organizacion_repository import (
    OrganizacionRepository
)

from app.repositories.recuperacion_contrasena_repository import (
    RecuperacionContrasenaRepository
)

from app.repositories.usuario_repository import (
    UsuarioRepository
)

from app.schemas.auth_schema import (
    CrearAdminOrganizacionRequest,
    RegistroOrganizacionRequest,
    RegistroEmpleadoRequest

)

from app.services.organizacion_service import (
    OrganizacionService 
)

import random
from datetime import datetime, timedelta

from app.core.email import enviar_codigo_recuperacion
from app.core.security import hash_password, hash_reset_token


class AuthService:

    @staticmethod
    def login(
        db: Session,
        email: str,
        contrasena: str
    ) -> str:

        usuario = UsuarioRepository.obtener_por_email(
            db,
            email
        )

        if not usuario or not usuario.estado:
            raise ValueError(
                "Credenciales inválidas"
            )

        if not verify_password(
            contrasena,
            usuario.contrasena_hash
        ):
            raise ValueError(
                "Credenciales inválidas"
            )

        usuario.ultimo_acceso = datetime.now()

        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol
            }
        )

    @staticmethod
    def registrar_organizacion(
        db: Session,
        datos: RegistroOrganizacionRequest
    ) -> str:

        nombre_organizacion = (
            datos.nombre_organizacion.strip()
        )

        nombre_usuario = (
            datos.nombre_usuario.strip()
        )

        if not nombre_organizacion:
            raise ValueError(
                "El nombre de la organización es obligatorio"
            )

        if OrganizacionRepository.obtener_por_nombre(
            db,
            nombre_organizacion
        ):
            raise ValueError(
                "Ya existe una organización con ese nombre"
            )

        # El correo debe ser único dentro de la
        # organización que se está creando.
        #
        # Como todavía no existe organización,
        # aquí no necesitamos consultar por organización.
        if UsuarioRepository.obtener_por_email(
            db,
            datos.email
        ):
            raise ValueError(
                "Ya existe un usuario con ese correo"
            )

        codigo = OrganizacionService._generar_codigo_unico(db)

        organizacion = Organizacion(
            nombre=nombre_organizacion,
            descripcion=datos.descripcion_organizacion,
            codigo = codigo
        )

        OrganizacionRepository.crear(
            db,
            organizacion
        )

        db.flush()

        persona = Persona(
            id_organizacion=organizacion.id_organizacion,
            nombre=datos.nombre.strip(),
            apellido=datos.apellido.strip(),
            email=datos.email,
            telefono=datos.telefono,
            capacidad_horas_semana=(
                datos.capacidad_horas_semana
            )
        )

        db.add(persona)

        db.flush()

        usuario = Usuario(
            id_organizacion=organizacion.id_organizacion,
            id_persona=persona.id_persona,
            id_rol=1,
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(
                datos.contrasena
            )
        )

        UsuarioRepository.crear(
            db,
            usuario
        )

        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol
            }
        )

    @staticmethod
    def solicitar_recuperacion(
        db: Session,
        email: str
    ) -> None:

        usuario = UsuarioRepository.obtener_por_email(db, email)

        # Por seguridad no revelamos si el correo existe o no
        if not usuario or not usuario.estado:
            return

        repository = RecuperacionContrasenaRepository(db)
        repository.desactivar_tokens_usuario(usuario.id_usuario)

    # Generar código de 6 dígitos
        codigo = f"{random.randint(100000, 999999)}"
        token_hash = hash_reset_token(codigo)

        expiracion = datetime.now() + timedelta(
            minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
        )

        recuperacion = RecuperacionContrasena(
            id_usuario=usuario.id_usuario,
            token_hash=token_hash,
            fecha_expiracion=expiracion
        )

        repository.crear(recuperacion)
        db.commit()

    # Enviar el código por correo
        try:
            enviar_codigo_recuperacion(email, codigo)
        except Exception as e:
            # Loguear el error, pero no revelar detalles al cliente
            print(f"Error enviando correo de recuperación: {e}")
            raise ValueError(
                "No se pudo enviar el correo de recuperación. Intenta más tarde."
            )


    @staticmethod
    def restablecer_contrasena(
        db: Session,
        email: str,
        codigo: str,
        nueva_contrasena: str
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
                RecuperacionContrasena.fecha_expiracion > datetime.now()
            )
            .first()
        )

        if recuperacion is None:
            raise ValueError("El código es inválido o ha expirado")

        usuario.contrasena_hash = hash_password(nueva_contrasena)

        repository.marcar_como_usado(recuperacion)
        repository.desactivar_tokens_usuario(usuario.id_usuario)

        db.commit()

    @staticmethod
    def _generar_nombre_usuario(db: Session, email: str) -> str:
        """
        Genera un nombre de usuario único a partir del email.
        Ejemplo: sofia.torres@empresa.com → sofia.torres
        """
        base = email.split("@")[0].lower().strip()
        base = base.replace(" ", ".")

        candidato = base
        contador = 1

        while UsuarioRepository.obtener_por_nombre_usuario(db, candidato):
            candidato = f"{base}{contador}"
            contador += 1

        return candidato


    @staticmethod
    def registrar_empleado(
        db: Session,
        datos: RegistroEmpleadoRequest
    ) -> str:

        codigo = datos.codigo_organizacion.strip().upper()

        # 1. Validar organización por código
        organizacion = OrganizacionRepository.obtener_por_codigo(db, codigo)

        if organizacion is None or not organizacion.estado:
            raise ValueError(
                "El código de organización no es válido o la organización está inactiva"
            )

        # 2. Buscar si existe la persona con ese email en la organización
        from app.repositories.persona_repository import PersonaRepository

        persona = PersonaRepository.obtener_por_email_y_organizacion(
            db,
            datos.email,
            organizacion.id_organizacion
        )

        if persona is None:
            raise ValueError(
                "No estás registrado como empleado de esta organización. "
                "Contacta a tu administrador."
            )

        # 3. Verificar que la persona aún no tenga usuario
        usuario_existente = UsuarioRepository.obtener_por_persona(
            db,
            persona.id_persona
        )

        if usuario_existente is not None:
            raise ValueError(
                "Ya existe una cuenta asociada a este empleado"
            )

        # 4. Verificar que el email no esté ya usado como usuario
        if UsuarioRepository.obtener_por_email(db, datos.email):
            raise ValueError(
                "Ya existe un usuario con ese correo"
            )

        # 5. Generar nombre de usuario automático
        nombre_usuario = AuthService._generar_nombre_usuario(db, datos.email)

        # 6. Crear el usuario (rol EMPLEADO = 4)
        usuario = Usuario(
            id_organizacion=organizacion.id_organizacion,
            id_persona=persona.id_persona,
            id_rol=4,  # EMPLEADO
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena)
        )

        UsuarioRepository.crear(db, usuario)
        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol
            }
        )

    @staticmethod
    def _generar_nombre_usuario(db: Session, email: str) -> str:
        """
        Genera un nombre de usuario único a partir del email.
        Ejemplo: sofia.torres@empresa.com → sofia.torres
        """
        base = email.split("@")[0].lower().strip()
        base = base.replace(" ", ".")

        candidato = base
        contador = 1

        while UsuarioRepository.obtener_por_nombre_usuario(db, candidato):
            candidato = f"{base}{contador}"
            contador += 1

        return candidato


    @staticmethod
    def registrar_empleado(
        db: Session,
        datos: RegistroEmpleadoRequest
    ) -> str:

        from app.repositories.persona_repository import PersonaRepository
        from app.schemas.auth_schema import RegistroEmpleadoRequest

        codigo = datos.codigo_organizacion.strip().upper()

        # 1. Validar organización por código
        organizacion = OrganizacionRepository.obtener_por_codigo(db, codigo)

        if organizacion is None or not organizacion.estado:
            raise ValueError(
                "El código de organización no es válido o la organización está inactiva"
            )

        # 2. Buscar si existe la persona con ese email en la organización
        persona_repo = PersonaRepository(db)

        persona = persona_repo.obtener_por_email_organizacion(
            datos.email,
            organizacion.id_organizacion
        )

        if persona is None:
            raise ValueError(
                "No estás registrado como empleado de esta organización. "
                "Contacta a tu administrador."
            )

        # 3. Verificar que la persona aún no tenga usuario
        usuario_existente = UsuarioRepository.obtener_por_persona(
            db,
            persona.id_persona
        )

        if usuario_existente is not None:
            raise ValueError(
                "Ya existe una cuenta asociada a este empleado"
            )

        # 4. Verificar que el email no esté ya usado como usuario
        if UsuarioRepository.obtener_por_email(db, datos.email):
            raise ValueError(
                "Ya existe un usuario con ese correo"
            )

        # 5. Generar nombre de usuario automático
        nombre_usuario = AuthService._generar_nombre_usuario(db, datos.email)

        # 6. Crear el usuario (rol EMPLEADO = 4)
        usuario = Usuario(
            id_organizacion=organizacion.id_organizacion,
            id_persona=persona.id_persona,
            id_rol=4,  # EMPLEADO
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena)
        )

        UsuarioRepository.crear(db, usuario)
        db.commit()

        return create_access_token(
            {
                "sub": str(usuario.id_usuario),
                "id_organizacion": usuario.id_organizacion,
                "id_rol": usuario.id_rol
            }
        )
    


    @staticmethod
    def crear_admin_organizacion(
        db: Session,
        id_organizacion: int,
        datos: CrearAdminOrganizacionRequest
    ) -> dict:

        from app.repositories.persona_repository import PersonaRepository

        # 1. Validar que la organización exista
        organizacion = OrganizacionRepository.obtener_por_id(db, id_organizacion)

        if organizacion is None or not organizacion.estado:
            raise ValueError("La organización no existe o está inactiva")

            # 2. Verificar que el email no esté usado
            if UsuarioRepository.obtener_por_email(db, datos.email):
                raise ValueError("Ya existe un usuario con ese correo")

        persona_repo = PersonaRepository(db)
        if persona_repo.obtener_por_email_organizacion(datos.email, id_organizacion):
            raise ValueError("Ya existe una persona con ese correo en esta organización")

        # 3. Crear Persona
        persona = Persona(
            id_organizacion=id_organizacion,
            nombre=datos.nombre.strip(),
            apellido=datos.apellido.strip(),
            email=datos.email,
            telefono=datos.telefono,
            capacidad_horas_semana=datos.capacidad_horas_semana,
            estado=True
        )
        db.add(persona)
        db.flush()

        # 4. Generar nombre de usuario
        nombre_usuario = AuthService._generar_nombre_usuario(db, datos.email)

    #    5. Crear Usuario con rol ADMIN (1)
        usuario = Usuario(
            id_organizacion=id_organizacion,
            id_persona=persona.id_persona,
            id_rol=1,  # ADMIN
            nombre_usuario=nombre_usuario,
            email=datos.email,
            contrasena_hash=hash_password(datos.contrasena),
            estado=True
        )
        UsuarioRepository.crear(db, usuario)
        db.commit()

        return {
            "mensaje": "Admin de organización creado correctamente",
            "id_usuario": usuario.id_usuario,
            "id_persona": persona.id_persona,
            "email": usuario.email,
            "nombre_usuario": usuario.nombre_usuario,
            "organizacion": organizacion.nombre,
            "codigo_organizacion": organizacion.codigo
        }