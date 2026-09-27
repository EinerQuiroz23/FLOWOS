from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.organizacion_model import Organizacion
from app.models.persona_model import Persona
from app.models.usuario_model import Usuario

db = SessionLocal()

try:
    # 1. Crear organización de la plataforma
    organizacion = Organizacion(
        nombre="FlowOS Platform",
        descripcion="Organización del sistema - Super Admin",
        estado=True,
        codigo="FLOW-PLATFORM-0001"
    )
    db.add(organizacion)
    db.flush()

    print(f"Organización creada → id: {organizacion.id_organizacion}")

    # 2. Crear persona
    persona = Persona(
        id_organizacion=organizacion.id_organizacion,
        nombre="Einer",
        apellido="Quiroz",
        email="flowos.optima@gmail.com",
        capacidad_horas_semana=40,
        estado=True
    )
    db.add(persona)
    db.flush()

    print(f"Persona creada → id: {persona.id_persona}")

    # 3. Crear usuario Super Admin
    usuario = Usuario(
        id_organizacion=organizacion.id_organizacion,
        id_persona=persona.id_persona,
        id_rol=5,  # SUPER_ADMIN
        nombre_usuario="einer.quiroz",
        email="flowos.optima@gmail.com",
        contrasena_hash=hash_password("SuperAdmin.00"),
        estado=True
    )
    db.add(usuario)
    db.commit()

    print(f"Super Admin creado → id: {usuario.id_usuario}")
    print("Listo. Ya puedes iniciar sesión con:")
    print("  Email: flowos.optima@gmail.com")
    print("  Contraseña: SuperAdmin.00")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()