import json
import re
from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.proyecto_repository import ProyectoRepository  # ajusta si tu path es otro
from app.schemas.vista_schema import (
    VistaAnalizarRequest,
    VistaAnalizarResponse,
    TareaPropuestaVista,
)


PROMPT_SISTEMA = """
Eres VISTA, el motor de análisis de requisitos de FlowOS.
Analizas la descripción de un proyecto de software y propones tareas concretas para el equipo.

Responde SOLO con JSON válido, sin markdown, con esta forma exacta:
{
  "resumen": "texto corto del análisis",
  "tareas": [
    {
      "nombre": "string",
      "descripcion": "string",
      "prioridad": "BAJA|MEDIA|ALTA|CRITICA",
      "horas_estimadas": number,
      "habilidades_sugeridas": ["Python", "React"]
    }
  ]
}

Reglas:
- Entre 4 y 12 tareas.
- Prioridades solo: BAJA, MEDIA, ALTA, CRITICA.
- horas_estimadas > 0.
- Nombres claros y accionables.
- Idioma: español.
"""


class VistaService:

    @staticmethod
    def analizar(
        db: Session,
        datos: VistaAnalizarRequest,
        id_organizacion: int,
    ) -> VistaAnalizarResponse:

        if not settings.XAI_API_KEY:
            raise ValueError(
                "XAI_API_KEY no está configurada en el servidor."
            )

        # --- Proyecto (ajusta el método a tu repository) ---
        proyecto = None
        try:
            proyecto = ProyectoRepository.obtener_por_id(
                db, datos.id_proyecto
            )
        except Exception:
            # Si tu repo es por organización:
            # proyecto = ProyectoRepository.obtener_por_id_y_organizacion(...)
            pass

        if proyecto is None:
            # Fallback: query directa si hace falta
            from app.models.proyecto_model import Proyecto
            proyecto = (
                db.query(Proyecto)
                .filter(Proyecto.id_proyecto == datos.id_proyecto)
                .first()
            )

        if proyecto is None:
            raise ValueError("El proyecto no existe.")

        # Validar organización si el modelo la tiene
        if hasattr(proyecto, "id_organizacion"):
            if proyecto.id_organizacion != id_organizacion:
                raise ValueError("No puedes analizar un proyecto de otra organización.")

        nombre_proyecto = getattr(proyecto, "nombre", f"Proyecto {datos.id_proyecto}")

        user_content = (
            f"Proyecto: {nombre_proyecto}\n\n"
            f"Requisitos / descripción:\n{datos.requisitos.strip()}"
        )

        payload = {
            "model": settings.XAI_MODEL,
            "messages": [
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {settings.XAI_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=90.0) as client:
                response = client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Error de xAI ({e.response.status_code}): no se pudo analizar."
            )
        except Exception as e:
            raise ValueError(f"No se pudo contactar a Grok/xAI: {e}")

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError("Respuesta inválida de Grok.")

        data = VistaService._parsear_json(content)

        tareas_raw = data.get("tareas") or data.get("tareas_propuestas") or []
        tareas: list[TareaPropuestaVista] = []

        for t in tareas_raw:
            prioridad = str(t.get("prioridad", "MEDIA")).strip().upper()
            if prioridad not in {"BAJA", "MEDIA", "ALTA", "CRITICA"}:
                prioridad = "MEDIA"

            try:
                horas = Decimal(str(t.get("horas_estimadas", 8)))
            except Exception:
                horas = Decimal("8")

            if horas <= 0:
                horas = Decimal("8")

            habilidades = t.get("habilidades_sugeridas") or []
            if not isinstance(habilidades, list):
                habilidades = []

            tareas.append(
                TareaPropuestaVista(
                    nombre=str(t.get("nombre", "Tarea sin nombre"))[:150],
                    descripcion=(str(t["descripcion"]) if t.get("descripcion") else None),
                    prioridad=prioridad,
                    horas_estimadas=horas,
                    habilidades_sugeridas=[str(h) for h in habilidades][:10],
                )
            )

        if not tareas:
            raise ValueError("VISTA no generó tareas. Intenta con más detalle en los requisitos.")

        return VistaAnalizarResponse(
            id_proyecto=datos.id_proyecto,
            proyecto=nombre_proyecto,
            resumen=str(data.get("resumen", "Análisis generado por VISTA.")),
            tareas_propuestas=tareas,
        )

    @staticmethod
    def _parsear_json(content: str) -> dict:
        text = content.strip()

        # Quitar fences ```json ... ```
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence:
            text = fence.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Intentar extraer el primer objeto { ... }
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Grok no devolvió JSON válido.")