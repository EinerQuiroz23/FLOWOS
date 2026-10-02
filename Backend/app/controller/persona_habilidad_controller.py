from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.authorization import require_any_role

from app.models.usuario_model import Usuario

from app.schemas.persona_habilidad_schema import (
    PersonaHabilidadCreate,
    PersonaHabilidadResponse,
    PersonaHabilidadUpdate
)

from app.services.persona_habilidad_service import (
    PersonaHabilidadService
)


router = APIRouter(
    prefix="/personas-habilidades",
    tags=["Personas - Habilidades"]
)


# =========================================================
# MIS HABILIDADES (empleado / usuario logueado)
# =========================================================

@router.get(
    "/me",
    response_model=List[PersonaHabilidadResponse]
)
def obtener_mis_habilidades(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.obtener_por_persona(
        usuario.id_persona,
        usuario.id_organizacion
    )


@router.post(
    "/me",
    response_model=PersonaHabilidadResponse,
    status_code=201
)
def crear_mi_habilidad(
    datos: PersonaHabilidadCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    # Empleado: solo su persona
    if usuario.id_rol == 4 and datos.id_persona != usuario.id_persona:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes registrar habilidades para tu propio perfil."
        )

    if usuario.id_rol == 4:
        datos = datos.model_copy(
            update={"id_persona": usuario.id_persona}
        )

    service = PersonaHabilidadService(db)

    return service.crear(
        datos,
        usuario.id_organizacion
    )


@router.put(
    "/me/{id_persona_habilidad}",
    response_model=PersonaHabilidadResponse
)
def actualizar_mi_habilidad(
    id_persona_habilidad: int,
    datos: PersonaHabilidadUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    registro = service.obtener_por_id(
        id_persona_habilidad,
        usuario.id_organizacion
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="El registro de persona-habilidad no existe."
        )

    if usuario.id_rol == 4 and registro.id_persona != usuario.id_persona:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes editar tus propias habilidades."
        )

    # Empleado no puede cambiar a otra persona
    if usuario.id_rol == 4 and datos.id_persona is not None:
        if datos.id_persona != usuario.id_persona:
            raise HTTPException(
                status_code=403,
                detail="No puedes asignar la habilidad a otra persona."
            )

    return service.actualizar(
        id_persona_habilidad,
        datos,
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR POR PERSONA
# =========================================================

@router.get(
    "/persona/{id_persona}",
    response_model=List[PersonaHabilidadResponse]
)
def obtener_por_persona(
    id_persona: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.obtener_por_persona(
        id_persona,
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR POR HABILIDAD
# =========================================================

@router.get(
    "/habilidad/{id_habilidad}",
    response_model=List[PersonaHabilidadResponse]
)
def obtener_por_habilidad(
    id_habilidad: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.obtener_por_habilidad(
        id_habilidad,
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR TODOS
# =========================================================

@router.get(
    "/",
    response_model=List[PersonaHabilidadResponse]
)
def obtener_registros(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.obtener_todos(
        usuario.id_organizacion
    )


# =========================================================
# CONSULTAR POR ID
# =========================================================

@router.get(
    "/{id_persona_habilidad}",
    response_model=PersonaHabilidadResponse
)
def obtener_registro_por_id(
    id_persona_habilidad: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "LIDER_PROYECTO",
            "SECRETARIO",
            "EMPLEADO"
        )
    )
):
    service = PersonaHabilidadService(db)

    registro = service.obtener_por_id(
        id_persona_habilidad,
        usuario.id_organizacion
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="El registro de persona-habilidad no existe."
        )

    return registro


# =========================================================
# CREAR (Admin / Secretaria)
# =========================================================

@router.post(
    "/",
    response_model=PersonaHabilidadResponse,
    status_code=201
)
def crear_registro(
    datos: PersonaHabilidadCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.crear(
        datos,
        usuario.id_organizacion
    )


# =========================================================
# ACTUALIZAR (Admin / Secretaria)
# =========================================================

@router.put(
    "/{id_persona_habilidad}",
    response_model=PersonaHabilidadResponse
)
def actualizar_registro(
    id_persona_habilidad: int,
    datos: PersonaHabilidadUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        require_any_role(
            "ADMIN",
            "SECRETARIO"
        )
    )
):
    service = PersonaHabilidadService(db)

    return service.actualizar(
        id_persona_habilidad,
        datos,
        usuario.id_organizacion
    )