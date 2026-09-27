from types import SimpleNamespace

from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.optima.calculators.compatibilidad_calculator import (
    CompatibilidadCalculator
)

from app.optima.calculators.disponibilidad_calculator import (
    DisponibilidadCalculator
)

from app.optima.calculators.experiencia_calculator import (
    ExperienciaCalculator
)

from app.optima.calculators.puntuacion_calculator import (
    PuntuacionCalculator
)

from app.optima.calculators.liderazgo_calculator import (
    LiderazgoCalculator
)

from app.optima.models.integrante_propuesta import (
    IntegrantePropuesto
)

from app.optima.models.lider_propuesto import (
    LiderPropuesto
)

from app.optima.models.propuesta_equipo import (
    PropuestaEquipo
)

from app.optima.repositories.optima_repository import (
    OptimaRepository
)


class OptimaTeamService:

    # ==========================================================
    # CONFIGURACIÓN
    # ==========================================================

    MAX_INTEGRANTES = 6

    # Una persona solo puede ser recomendada si tiene
    # disponibilidad estrictamente mayor que 0%.
    DISPONIBILIDAD_MINIMA = 0.0

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(
        self,
        db: Session
    ):

        self.repository = (
            OptimaRepository(db)
        )

        self.compatibilidad_calculator = (
            CompatibilidadCalculator()
        )

        self.disponibilidad_calculator = (
            DisponibilidadCalculator()
        )

        self.experiencia_calculator = (
            ExperienciaCalculator()
        )

        self.puntuacion_calculator = (
            PuntuacionCalculator()
        )

        self.liderazgo_calculator = (
            LiderazgoCalculator()
        )

    # ==========================================================
    # NORMALIZAR REQUISITOS
    # ==========================================================

    def _normalizar_requisitos(
        self,
        requisitos
    ):

        resultado = []

        for fila in requisitos:

            entidad = getattr(
                fila,
                "TareaHabilidad",
                None
            )

            if entidad is not None:

                resultado.append(
                    SimpleNamespace(

                        id_tarea_habilidad=(
                            entidad.id_tarea_habilidad
                        ),

                        id_tarea=(
                            entidad.id_tarea
                        ),

                        id_habilidad=(
                            entidad.id_habilidad
                        ),

                        id_nivel=(
                            entidad.id_nivel
                        ),

                        nombre_habilidad=(
                            getattr(
                                fila,
                                "nombre_habilidad",
                                None
                            )
                        )
                    )
                )

                continue

            resultado.append(
                SimpleNamespace(

                    id_tarea_habilidad=getattr(
                        fila,
                        "id_tarea_habilidad",
                        None
                    ),

                    id_tarea=getattr(
                        fila,
                        "id_tarea",
                        None
                    ),

                    id_habilidad=getattr(
                        fila,
                        "id_habilidad",
                        None
                    ),

                    id_nivel=getattr(
                        fila,
                        "id_nivel",
                        None
                    ),

                    nombre_habilidad=getattr(
                        fila,
                        "nombre_habilidad",
                        None
                    )
                )
            )

        return resultado

    # ==========================================================
    # NORMALIZAR HABILIDADES
    # ==========================================================

    def _normalizar_habilidades(
        self,
        habilidades
    ):

        resultado = []

        for fila in habilidades:

            entidad = getattr(
                fila,
                "PersonaHabilidad",
                None
            )

            if entidad is not None:

                resultado.append(
                    SimpleNamespace(

                        id_persona=(
                            entidad.id_persona
                        ),

                        id_habilidad=(
                            entidad.id_habilidad
                        ),

                        id_nivel=(
                            entidad.id_nivel
                        ),

                        años_experiencia=float(
                            getattr(
                                entidad,
                                "años_experiencia",
                                0
                            ) or 0
                        ),

                        nombre_habilidad=(
                            getattr(
                                fila,
                                "nombre_habilidad",
                                None
                            )
                        )
                    )
                )

                continue

            resultado.append(
                fila
            )

        return resultado

    # ==========================================================
    # NORMALIZAR CARGAS
    # ==========================================================

    def _normalizar_cargas(
        self,
        cargas
    ) -> Dict[int, float]:

        if not cargas:
            return {}

        # ------------------------------------------------------
        # EL REPOSITORIO ACTUAL DEVUELVE:
        #
        # {
        #     id_persona: carga_actual
        # }
        # ------------------------------------------------------

        if isinstance(
            cargas,
            dict
        ):

            return {
                int(id_persona): float(
                    valor or 0
                )
                for id_persona, valor
                in cargas.items()
            }

        # ------------------------------------------------------
        # COMPATIBILIDAD CON VERSIONES ANTERIORES
        # ------------------------------------------------------

        resultado = {}

        for fila in cargas:

            id_persona = getattr(
                fila,
                "id_persona",
                None
            )

            valor = getattr(
                fila,
                "carga_actual",
                None
            )

            if valor is None:

                valor = getattr(
                    fila,
                    "horas_carga_actual",
                    0
                )

            if id_persona is not None:

                resultado[
                    int(id_persona)
                ] = float(
                    valor or 0
                )

        return resultado

    # ==========================================================
    # NORMALIZAR NOMBRE
    # ==========================================================

    @staticmethod
    def _nombre_habilidad(
        requisito
    ) -> str:

        return (
            getattr(
                requisito,
                "nombre_habilidad",
                None
            )
            or f"Habilidad {requisito.id_habilidad}"
        )

    # ==========================================================
    # PROPONER EQUIPO
    # ==========================================================

    def proponer_equipo(
        self,
        id_proyecto: int,
        id_organizacion: int
    ) -> PropuestaEquipo:

        # ------------------------------------------------------
        # 1. VALIDAR PROYECTO
        # ------------------------------------------------------

        proyecto = (
            self.repository
            .obtener_proyecto_por_organizacion(
                id_proyecto,
                id_organizacion
            )
        )

        if not proyecto:

            raise FlowosException(
                message=(
                    "El proyecto no existe o no pertenece "
                    "a la organización del usuario."
                ),
                code="PROYECTO_NO_AUTORIZADO",
                status_code=404
            )

        # ------------------------------------------------------
        # 2. OBTENER TAREAS
        # ------------------------------------------------------

        tareas = (
            self.repository
            .obtener_tareas_activas_por_proyecto(
                id_proyecto
            )
        )

        if not tareas:

            raise FlowosException(
                message=(
                    "El proyecto no tiene tareas activas "
                    "para analizar."
                ),
                code="TAREAS_NO_ENCONTRADAS",
                status_code=400
            )

        # ------------------------------------------------------
        # 3. PERSONAS ACTIVAS
        # ------------------------------------------------------

        personas = (
            self.repository
            .obtener_personas_activas_proyecto(
                id_proyecto,
                id_organizacion
            )
        )

        if not personas:

            raise FlowosException(
                message=(
                    "No existen personas activas en los "
                    "equipos del proyecto."
                ),
                code="PERSONAS_NO_ENCONTRADAS",
                status_code=404
            )

        # ------------------------------------------------------
        # ELIMINAR DUPLICADOS
        # ------------------------------------------------------

        personas_unicas = {}

        for persona in personas:

            if persona.id_persona not in personas_unicas:

                personas_unicas[
                    persona.id_persona
                ] = persona

        personas = list(
            personas_unicas.values()
        )

        # ------------------------------------------------------
        # 4. HABILIDADES Y CARGAS
        # ------------------------------------------------------

        ids_personas = [
            persona.id_persona
            for persona in personas
        ]

        habilidades_personas = (
            self.repository
            .obtener_habilidades_por_personas(
                ids_personas
            )
        )

        habilidades_personas = (
            self._normalizar_habilidades(
                habilidades_personas
            )
        )

        cargas = (
            self.repository
            .obtener_carga_actual_por_personas(
                ids_personas
            )
        )

        cargas_por_persona = (
            self._normalizar_cargas(
                cargas
            )
        )

        habilidades_por_persona = {}

        for habilidad in habilidades_personas:

            habilidades_por_persona.setdefault(
                habilidad.id_persona,
                []
            ).append(
                habilidad
            )

        # ------------------------------------------------------
        # 5. CONSTRUIR REQUISITOS DEL PROYECTO
        # ------------------------------------------------------

        requisitos_proyecto = []

        for tarea in tareas:

            filas = (
                self.repository
                .obtener_habilidades_requeridas_por_tarea(
                    tarea.id_tarea
                )
            )

            requisitos = (
                self._normalizar_requisitos(
                    filas
                )
            )

            requisitos_proyecto.extend(
                requisitos
            )

        if not requisitos_proyecto:

            raise FlowosException(
                message=(
                    "Las tareas activas del proyecto no "
                    "tienen habilidades requeridas."
                ),
                code="REQUISITOS_NO_ENCONTRADOS",
                status_code=400
            )

        # ------------------------------------------------------
        # 6. ELIMINAR DUPLICADOS TAREA + HABILIDAD
        # ------------------------------------------------------

        requisitos_por_clave = {}

        for requisito in requisitos_proyecto:

            clave = (
                requisito.id_tarea,
                requisito.id_habilidad
            )

            existente = (
                requisitos_por_clave.get(
                    clave
                )
            )

            if (
                existente is None
                or requisito.id_nivel
                > existente.id_nivel
            ):

                requisitos_por_clave[
                    clave
                ] = requisito

        requisitos_proyecto = list(
            requisitos_por_clave.values()
        )

        # ------------------------------------------------------
        # 7. HABILIDADES ÚNICAS DEL PROYECTO
        #
        # Si una habilidad aparece en varias tareas,
        # se conserva el mayor nivel requerido.
        # ------------------------------------------------------

        requisitos_unicos_por_habilidad = {}

        for requisito in requisitos_proyecto:

            id_habilidad = (
                requisito.id_habilidad
            )

            existente = (
                requisitos_unicos_por_habilidad
                .get(id_habilidad)
            )

            if (
                existente is None
                or requisito.id_nivel
                > existente.id_nivel
            ):

                requisitos_unicos_por_habilidad[
                    id_habilidad
                ] = requisito

        requisitos_unicos_proyecto = list(
            requisitos_unicos_por_habilidad.values()
        )

        if not requisitos_unicos_proyecto:

            raise FlowosException(
                message=(
                    "No existen habilidades únicas "
                    "requeridas para el proyecto."
                ),
                code="HABILIDADES_PROYECTO_NO_ENCONTRADAS",
                status_code=400
            )

        # ------------------------------------------------------
        # 8. EVALUAR PERSONAS
        # ------------------------------------------------------

        resultados = []

        for persona in personas:

            habilidades_persona = (
                habilidades_por_persona.get(
                    persona.id_persona,
                    []
                )
            )
            carga = (
                cargas_por_persona.get(
                    persona.id_persona,
                    0.0
                )
            )

            capacidad = float(
                persona.capacidad_horas_semana
                or 0
            )

            disponibilidad = (
                self.disponibilidad_calculator.calcular(
                    capacidad,
                    carga
                )
            )

            evaluacion = (
                self._evaluar_persona_proyecto(
                    habilidades_persona=(
                        habilidades_persona
                    ),
                    requisitos_proyecto=(
                        requisitos_proyecto
                    ),
                    requisitos_unicos_proyecto=(
                        requisitos_unicos_proyecto
                    )
                )
            )

            puntuacion = (
                self.puntuacion_calculator.calcular(
                    evaluacion[
                        "compatibilidad"
                    ],
                    evaluacion[
                        "experiencia"
                    ],
                    disponibilidad
                )
            )

            resultados.append(
                IntegrantePropuesto(

                    id_persona=(
                        persona.id_persona
                    ),

                    persona=(
                        f"{persona.nombre} "
                        f"{persona.apellido}"
                    ),

                    capacidad_horas_semana=(
                        capacidad
                    ),

                    horas_carga_actual=round(
                        carga,
                        2
                    ),

                    disponibilidad=(
                        disponibilidad
                    ),

                    habilidades_requeridas=(
                        evaluacion[
                            "habilidades_requeridas"
                        ]
                    ),

                    habilidades_cumplidas=(
                        evaluacion[
                            "habilidades_cumplidas"
                        ]
                    ),

                    compatibilidad=(
                        evaluacion[
                            "compatibilidad"
                        ]
                    ),

                    años_experiencia_promedio=round(
                        evaluacion[
                            "promedio_experiencia"
                        ],
                        2
                    ),

                    experiencia=(
                        evaluacion[
                            "experiencia"
                        ]
                    ),

                    puntuacion_equipo=(
                        puntuacion
                    ),

                    habilidades_ok=(
                        ", ".join(
                            evaluacion[
                                "habilidades_ok"
                            ]
                        )
                        if evaluacion[
                            "habilidades_ok"
                        ]
                        else None
                    ),

                    habilidades_no_registradas=(
                        ", ".join(
                            evaluacion[
                                "habilidades_no_registradas"
                            ]
                        )
                        if evaluacion[
                            "habilidades_no_registradas"
                        ]
                        else None
                    ),

                    habilidades_nivel_insuficiente=(
                        ", ".join(
                            evaluacion[
                                "habilidades_nivel_insuficiente"
                            ]
                        )
                        if evaluacion[
                            "habilidades_nivel_insuficiente"
                        ]
                        else None
                    ),

                    contribucion=(
                        self._generar_contribucion(
                            evaluacion[
                                "habilidades_ok"
                            ]
                        )
                    ),

                    requisitos_cubiertos=[
                        self._crear_clave_requisito(
                            id_tarea,
                            id_habilidad
                        )
                        for (
                            id_tarea,
                            id_habilidad
                        )
                        in evaluacion[
                            "requisitos_cubiertos"
                        ]
                    ]
                )
            )

        # ------------------------------------------------------
        # 9. SOLO CANDIDATOS ASIGNABLES
        #
        # Las personas con 0% pueden ser analizadas,
        # pero nunca recomendadas.
        # ------------------------------------------------------

        candidatos_utiles = [
            candidato
            for candidato in resultados
            if (
                candidato.requisitos_cubiertos
                and self._es_asignable(
                    candidato
                )
            )
        ]

        # ------------------------------------------------------
        # 10. SI NO HAY CANDIDATOS
        # ------------------------------------------------------

        if not candidatos_utiles:

            personas_con_habilidades = [
                candidato
                for candidato in resultados
                if candidato.requisitos_cubiertos
            ]

            if personas_con_habilidades:

                explicacion = (
                    "OPTIMA encontró personas que cubren "
                    "habilidades requeridas, pero ninguna "
                    "cuenta actualmente con disponibilidad "
                    "suficiente para integrar el equipo."
                )

            else:

                explicacion = (
                    "OPTIMA analizó las personas activas "
                    "del proyecto, pero ninguna cubre "
                    "las habilidades requeridas."
                )

            habilidades_faltantes = (
                self._obtener_habilidades_faltantes_unicas(
                    requisitos_unicos_proyecto,
                    set()
                )
            )

            return PropuestaEquipo(
                id_proyecto=proyecto.id_proyecto,
                proyecto=proyecto.nombre,
                cobertura=0.0,
                integrantes_recomendados=0,
                integrantes_analizados=len(personas),
                lider=None,
                lider_alternativo=None,
                integrantes=[],
                habilidades_requeridas=len(requisitos_unicos_proyecto),
                habilidades_cubiertas=0,
                habilidades_faltantes=(
                    ", ".join(habilidades_faltantes)
                    if habilidades_faltantes
                    else None
                ),
                explicacion=explicacion,
                puede_crearse=False,
                confianza_liderazgo=None,
                riesgos_detectados=[
                    "No se encontraron candidatos con disponibilidad "
                    "y habilidades suficientes."
                ],
                recomendaciones=[
                    "Revisar la carga de trabajo del personal o "
                    "ampliar el pool de personas del proyecto."
                ]
            )

        # ------------------------------------------------------
        # 11. SELECCIONAR INTEGRANTES
        # ------------------------------------------------------

        integrantes = (
            self._seleccionar_integrantes(
                candidatos_utiles,
                requisitos_unicos_proyecto
            )
        )

        # ------------------------------------------------------
        # 12. COBERTURA ÚNICA REAL
        # ------------------------------------------------------

        ids_habilidades_cubiertas = (
            self._obtener_ids_habilidades_cubiertas(
                integrantes,
                requisitos_unicos_proyecto
            )
        )

        habilidades_cubiertas = len(
            ids_habilidades_cubiertas
        )

        habilidades_requeridas = len(
            requisitos_unicos_proyecto
        )

        cobertura = (
            self.compatibilidad_calculator.calcular(
                habilidades_requeridas,
                habilidades_cubiertas
            )
        )

        # ------------------------------------------------------
        # 13. HABILIDADES FALTANTES
        # ------------------------------------------------------

        habilidades_faltantes = (
            self._obtener_habilidades_faltantes_unicas(
                requisitos_unicos_proyecto,
                ids_habilidades_cubiertas
            )
        )

        # ------------------------------------------------------
        # 14. LÍDER (solo se propone si cobertura >= 60%)
        # ------------------------------------------------------

        lider = None
        lider_alternativo = None
        confianza_liderazgo = None

        if cobertura >= 60 and integrantes:
            lider, lider_alternativo = self._seleccionar_lider(
                integrantes=integrantes,
                cobertura_equipo=cobertura,
                habilidades_requeridas=habilidades_requeridas
            )

            if lider:
                confianza_liderazgo = lider.confianza

        # ------------------------------------------------------
        # 15. DISPONIBILIDAD DEL EQUIPO
        # ------------------------------------------------------

        equipo_disponible = all(
            integrante.disponibilidad
            > self.DISPONIBILIDAD_MINIMA
            for integrante in integrantes
        )

        lider_disponible = (
            lider is not None
            and lider.disponibilidad
            > self.DISPONIBILIDAD_MINIMA
        )

        puede_crearse = (
            len(integrantes) > 0
            and cobertura >= 100
            and lider is not None
            and equipo_disponible
            and lider_disponible
        )

        # ------------------------------------------------------
        # 16. RIESGOS Y RECOMENDACIONES
        # ------------------------------------------------------

        riesgos, recomendaciones = self._generar_riesgos_y_recomendaciones(
            cobertura=cobertura,
            integrantes=integrantes,
            lider=lider,
            habilidades_faltantes=habilidades_faltantes,
            puede_crearse=puede_crearse
        )

        # ------------------------------------------------------
        # 17. EXPLICACIÓN
        # ------------------------------------------------------

        explicacion = self._generar_explicacion(
            cobertura=cobertura,
            integrantes=integrantes,
            lider=lider,
            habilidades_faltantes=habilidades_faltantes,
            puede_crearse=puede_crearse,
            confianza_liderazgo=confianza_liderazgo
        )

        # ------------------------------------------------------
        # 18. RESPUESTA
        # ------------------------------------------------------

        return PropuestaEquipo(
            id_proyecto=proyecto.id_proyecto,
            proyecto=proyecto.nombre,
            cobertura=cobertura,
            integrantes_recomendados=len(integrantes),
            integrantes_analizados=len(personas),
            lider=lider,
            lider_alternativo=lider_alternativo,
            integrantes=integrantes,
            habilidades_requeridas=habilidades_requeridas,
            habilidades_cubiertas=habilidades_cubiertas,
            habilidades_faltantes=(
                ", ".join(habilidades_faltantes)
                if habilidades_faltantes
                else None
            ),
            explicacion=explicacion,
            puede_crearse=puede_crearse,
            confianza_liderazgo=confianza_liderazgo,
            riesgos_detectados=riesgos,
            recomendaciones=recomendaciones
        )

    # ==========================================================
    # EVALUAR PERSONA
    # ==========================================================

    def _evaluar_persona_proyecto(
        self,
        habilidades_persona,
        requisitos_proyecto,
        requisitos_unicos_proyecto
    ) -> dict:

        habilidades_persona_map = {
            habilidad.id_habilidad: habilidad
            for habilidad
            in habilidades_persona
        }

        habilidades_cumplidas = 0

        habilidades_ok = set()

        habilidades_no_registradas = set()

        habilidades_nivel_insuficiente = set()

        experiencias = []

        requisitos_cubiertos = set()

        # ------------------------------------------------------
        # HABILIDADES ÚNICAS
        # ------------------------------------------------------

        for requisito in requisitos_unicos_proyecto:

            habilidad_persona = (
                habilidades_persona_map.get(
                    requisito.id_habilidad
                )
            )

            nombre = (
                self._nombre_habilidad(
                    requisito
                )
            )

            if habilidad_persona is None:

                habilidades_no_registradas.add(
                    nombre
                )

                continue

            experiencia = float(
                getattr(
                    habilidad_persona,
                    "años_experiencia",
                    0
                ) or 0
            )

            if experiencia > 0:

                experiencias.append(
                    experiencia
                )

            if (
                habilidad_persona.id_nivel
                >= requisito.id_nivel
            ):

                habilidades_cumplidas += 1

                habilidades_ok.add(
                    nombre
                )

            else:

                habilidades_nivel_insuficiente.add(
                    nombre
                )

        # ------------------------------------------------------
        # REQUISITOS ESPECÍFICOS
        # ------------------------------------------------------

        for requisito in requisitos_proyecto:

            habilidad_persona = (
                habilidades_persona_map.get(
                    requisito.id_habilidad
                )
            )

            if habilidad_persona is None:
                continue

            if (
                habilidad_persona.id_nivel
                >= requisito.id_nivel
            ):

                requisitos_cubiertos.add(
                    (
                        requisito.id_tarea,
                        requisito.id_habilidad
                    )
                )

        # ------------------------------------------------------
        # COMPATIBILIDAD
        # ------------------------------------------------------

        total_habilidades = len(
            requisitos_unicos_proyecto
        )

        compatibilidad = (
            self.compatibilidad_calculator.calcular(
                total_habilidades,
                habilidades_cumplidas
            )
        )

        # ------------------------------------------------------
        # EXPERIENCIA
        # ------------------------------------------------------

        promedio_experiencia = (
            sum(experiencias)
            / len(experiencias)
            if experiencias
            else 0.0
        )

        experiencia = (
            self.experiencia_calculator.calcular(
                promedio_experiencia
            )
        )

        return {

            "habilidades_requeridas": (
                total_habilidades
            ),

            "habilidades_cumplidas": (
                habilidades_cumplidas
            ),

            "compatibilidad": (
                compatibilidad
            ),

            "promedio_experiencia": (
                promedio_experiencia
            ),

            "experiencia": (
                experiencia
            ),

            "habilidades_ok": sorted(
                habilidades_ok
            ),

            "habilidades_no_registradas": sorted(
                habilidades_no_registradas
            ),

            "habilidades_nivel_insuficiente": sorted(
                habilidades_nivel_insuficiente
            ),

            "requisitos_cubiertos": (
                requisitos_cubiertos
            )
        }

    # ==========================================================
    # VALIDAR SI ES ASIGNABLE
    # ==========================================================

    def _es_asignable(
        self,
        candidato: IntegrantePropuesto
    ) -> bool:

        try:

            disponibilidad = float(
                candidato.disponibilidad
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return False

        return (
            disponibilidad
            > self.DISPONIBILIDAD_MINIMA
        )

    # ==========================================================
    # CLAVE DE REQUISITO
    # ==========================================================

    @staticmethod
    def _crear_clave_requisito(
        id_tarea: int,
        id_habilidad: int
    ) -> str:

        return (
            f"{id_tarea}:{id_habilidad}"
        )

    # ==========================================================
    # SELECCIONAR INTEGRANTES
    # ==========================================================

    def _seleccionar_integrantes(
        self,
        candidatos: List[
            IntegrantePropuesto
        ],
        requisitos_unicos_proyecto: list
    ) -> List[
        IntegrantePropuesto
    ]:

        if not candidatos:
            return []

        candidatos_unicos = {}

        for candidato in candidatos:

            if not self._es_asignable(
                candidato
            ):
                continue

            if (
                candidato.id_persona
                not in candidatos_unicos
            ):

                candidatos_unicos[
                    candidato.id_persona
                ] = candidato

        candidatos_restantes = list(
            candidatos_unicos.values()
        )

        seleccionados = []

        habilidades_cubiertas = set()

        requisitos_cubiertos = set()

        habilidades_objetivo = {
            requisito.id_habilidad
            for requisito
            in requisitos_unicos_proyecto
        }

        while (
            candidatos_restantes
            and len(seleccionados)
            < self.MAX_INTEGRANTES
        ):

            mejor = None

            mejor_clave = None

            mejor_habilidades = set()

            mejor_requisitos = set()

            for candidato in (
                candidatos_restantes
            ):

                nuevas_habilidades = set()

                nuevos_requisitos = set()

                for clave in (
                    candidato.requisitos_cubiertos
                ):

                    partes = (
                        clave.split(":")
                    )

                    if len(partes) != 2:
                        continue

                    try:

                        id_habilidad = int(
                            partes[1]
                        )

                    except ValueError:

                        continue

                    if (
                        id_habilidad
                        in habilidades_objetivo
                        and id_habilidad
                        not in habilidades_cubiertas
                    ):

                        nuevas_habilidades.add(
                            id_habilidad
                        )

                    if (
                        clave
                        not in requisitos_cubiertos
                    ):

                        nuevos_requisitos.add(
                            clave
                        )

                if (
                    not nuevas_habilidades
                    and not nuevos_requisitos
                ):

                    continue

                clave_comparacion = (

                    len(
                        nuevas_habilidades
                    ),

                    len(
                        nuevos_requisitos
                    ),

                    float(
                        candidato.compatibilidad
                        or 0
                    ),

                    float(
                        candidato.experiencia
                        or 0
                    ),

                    float(
                        candidato.disponibilidad
                        or 0
                    ),

                    float(
                        candidato.puntuacion_equipo
                        or 0
                    )
                )

                if (
                    mejor_clave is None
                    or clave_comparacion
                    > mejor_clave
                ):

                    mejor = candidato

                    mejor_clave = (
                        clave_comparacion
                    )

                    mejor_habilidades = (
                        nuevas_habilidades
                    )

                    mejor_requisitos = (
                        nuevos_requisitos
                    )

            if mejor is None:
                break

            seleccionados.append(
                mejor
            )

            habilidades_cubiertas.update(
                mejor_habilidades
            )

            requisitos_cubiertos.update(
                mejor_requisitos
            )

            candidatos_restantes.remove(
                mejor
            )

            if (
                habilidades_cubiertas
                >= habilidades_objetivo
            ):

                break

        return seleccionados

    # ==========================================================
    # IDS HABILIDADES CUBIERTAS
    # ==========================================================

    def _obtener_ids_habilidades_cubiertas(
        self,
        integrantes: List[
            IntegrantePropuesto
        ],
        requisitos_unicos_proyecto: list
    ) -> set:

        habilidades_requeridas = {
            requisito.id_habilidad
            for requisito
            in requisitos_unicos_proyecto
        }

        ids_cubiertos = set()

        for integrante in integrantes:

            for clave in (
                integrante.requisitos_cubiertos
            ):

                partes = (
                    clave.split(":")
                )

                if len(partes) != 2:
                    continue

                try:

                    id_habilidad = int(
                        partes[1]
                    )

                except ValueError:

                    continue

                if (
                    id_habilidad
                    in habilidades_requeridas
                ):

                    ids_cubiertos.add(
                        id_habilidad
                    )

        return ids_cubiertos

    # ==========================================================
    # HABILIDADES FALTANTES
    # ==========================================================

    def _obtener_habilidades_faltantes_unicas(
        self,
        requisitos_unicos_proyecto: list,
        ids_habilidades_cubiertas: set
    ) -> list:

        faltantes = []

        habilidades_vistas = set()

        for requisito in (
            requisitos_unicos_proyecto
        ):

            id_habilidad = (
                requisito.id_habilidad
            )

            if (
                id_habilidad
                in ids_habilidades_cubiertas
            ):

                continue

            if (
                id_habilidad
                in habilidades_vistas
            ):

                continue

            habilidades_vistas.add(
                id_habilidad
            )

            faltantes.append(
                self._nombre_habilidad(
                    requisito
                )
            )

        return faltantes

    # ==========================================================
    # SELECCIONAR LÍDER
    # ==========================================================

    def _seleccionar_lider(
        self,
        integrantes: List[IntegrantePropuesto],
        cobertura_equipo: float = 0.0,
        habilidades_requeridas: int = 1
    ) -> tuple[LiderPropuesto | None, LiderPropuesto | None]:
        """
        Selecciona el mejor líder y un líder alternativo.
        Retorna (lider_principal, lider_alternativo)
        """

        if not integrantes:
            return None, None

        candidatos_lider = []

        for integrante in integrantes:

            if integrante.disponibilidad <= self.DISPONIBILIDAD_MINIMA:
                continue

            # Cobertura individual de habilidades
            cobertura_individual = 0.0
            if habilidades_requeridas > 0:
                cobertura_individual = (
                    integrante.habilidades_cumplidas
                    / habilidades_requeridas
                ) * 100

            # Detectar si aporta habilidades únicas (simplificado)
            es_unico = cobertura_individual >= 40

            score = self.liderazgo_calculator.calcular(
                compatibilidad=integrante.compatibilidad,
                experiencia=integrante.experiencia,
                disponibilidad=integrante.disponibilidad,
                cobertura_habilidades=cobertura_individual,
                es_unico_en_habilidades=es_unico
            )

            candidatos_lider.append({
                "integrante": integrante,
                "score": score,
                "cobertura_individual": cobertura_individual
            })

        if not candidatos_lider:
            return None, None

        # Ordenar por score descendente
        candidatos_lider.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        mejor = candidatos_lider[0]
        alternativo = candidatos_lider[1] if len(candidatos_lider) > 1 else None

        def _construir_lider(item, es_principal: bool = True) -> LiderPropuesto:
            integrante = item["integrante"]
            score = item["score"]

            confianza = self.liderazgo_calculator.determinar_confianza(
                score=score,
                compatibilidad=integrante.compatibilidad,
                cobertura_equipo=cobertura_equipo
            )

            if es_principal:
                explicacion = (
                    f"OPTIMA propone a {integrante.persona} como líder "
                    f"porque combina la mejor puntuación de liderazgo "
                    f"({score:.1f}). "
                    f"Compatibilidad técnica: {integrante.compatibilidad:.0f}%, "
                    f"experiencia: {integrante.experiencia:.0f}%, "
                    f"disponibilidad: {integrante.disponibilidad:.0f}%. "
                    f"Nivel de confianza: {confianza}."
                )
            else:
                explicacion = (
                    f"Alternativa de liderazgo. "
                    f"Puntuación: {score:.1f}. "
                    f"Puede ser considerada si se busca un perfil diferente."
                )

            return LiderPropuesto(
                id_persona=integrante.id_persona,
                persona=integrante.persona,
                compatibilidad=integrante.compatibilidad,
                experiencia=integrante.experiencia,
                disponibilidad=integrante.disponibilidad,
                puntuacion_liderazgo=score,
                confianza=confianza,
                habilidades_ok=integrante.habilidades_ok,
                habilidades_no_registradas=integrante.habilidades_no_registradas,
                habilidades_nivel_insuficiente=integrante.habilidades_nivel_insuficiente,
                explicacion=explicacion
            )

        lider_principal = _construir_lider(mejor, es_principal=True)
        lider_alternativo = (
            _construir_lider(alternativo, es_principal=False)
            if alternativo else None
        )

        return lider_principal, lider_alternativo

    # ==========================================================
    # CONTRIBUCIÓN
    # ==========================================================

    @staticmethod
    def _generar_contribucion(
        habilidades_ok: list
    ) -> str | None:

        if not habilidades_ok:
            return None

        return (
            "Cubre las habilidades: "
            + ", ".join(
                habilidades_ok
            )
            + "."
        )

    # ==========================================================
    # EXPLICACIÓN DE PROPUESTA
    # ==========================================================

    def _generar_explicacion(
        self,
        cobertura: float,
        integrantes: List[IntegrantePropuesto],
        lider: LiderPropuesto | None,
        habilidades_faltantes: list,
        puede_crearse: bool,
        confianza_liderazgo: str | None = None
    ) -> str:

        if not integrantes:
            return (
                "OPTIMA no pudo construir una propuesta de equipo "
                "con las personas disponibles actualmente."
            )

        partes = []

        partes.append(
            f"OPTIMA propone {len(integrantes)} integrante(s) "
            f"con una cobertura del {cobertura:.1f}%."
        )

        if habilidades_faltantes:
            partes.append(
                f"Aún faltan habilidades clave: "
                f"{', '.join(habilidades_faltantes)}."
            )

        if lider:
            nivel = confianza_liderazgo or lider.confianza or "Media"
            partes.append(
                f"Se recomienda a {lider.persona} como líder "
                f"(confianza: {nivel}, score: {lider.puntuacion_liderazgo:.1f})."
            )
        else:
            if cobertura < 60:
                partes.append(
                    "No se propone líder porque la cobertura del equipo "
                    "aún es insuficiente (< 60%)."
                )
            else:
                partes.append(
                    "No se encontró un perfil adecuado para el liderazgo "
                    "con la disponibilidad actual."
                )

        if puede_crearse:
            partes.append(
                "El equipo cumple todas las condiciones y puede crearse."
            )
        else:
            partes.append(
                "La propuesta requiere ajustes antes de poder crear el equipo."
            )

        return " ".join(partes)

    # ==========================================================
    # RIESGOS Y RECOMENDACIONES
    # ==========================================================

    def _generar_riesgos_y_recomendaciones(
        self,
        cobertura: float,
        integrantes: List[IntegrantePropuesto],
        lider: LiderPropuesto | None,
        habilidades_faltantes: list,
        puede_crearse: bool
    ) -> tuple[list[str], list[str]]:

        riesgos = []
        recomendaciones = []

        if cobertura < 50:
            riesgos.append(
                f"Cobertura muy baja ({cobertura:.0f}%). El equipo no cubre "
                "la mitad de las habilidades requeridas."
            )
            recomendaciones.append(
                "Incorporar perfiles con las habilidades faltantes antes "
                "de formalizar el equipo."
            )
        elif cobertura < 80:
            riesgos.append(
                f"Cobertura parcial ({cobertura:.0f}%). Existen habilidades "
                "sin cobertura."
            )
            recomendaciones.append(
                "Buscar refuerzos en las habilidades que aún faltan."
            )

        if habilidades_faltantes:
            criticas = [
                h for h in habilidades_faltantes
                if any(palabra in h.lower() for palabra in [
                    "inteligencia artificial", "machine learning",
                    "análisis de datos", "data", "ia", "ml"
                ])
            ]
            if criticas:
                riesgos.append(
                    f"Faltan habilidades críticas de alto valor: "
                    f"{', '.join(criticas)}."
                )
                recomendaciones.append(
                    "Priorizar la incorporación de un perfil de Data Science "
                    "o Inteligencia Artificial."
                )

        if lider:
            if lider.compatibilidad < 40:
                riesgos.append(
                    f"El líder propuesto ({lider.persona}) tiene baja "
                    f"compatibilidad técnica ({lider.compatibilidad:.0f}%)."
                )
                recomendaciones.append(
                    "Considerar al líder alternativo o reforzar el equipo "
                    "con alguien de mayor dominio técnico."
                )

            if lider.confianza == "Baja":
                riesgos.append(
                    "El nivel de confianza en el liderazgo propuesto es Bajo."
                )
        else:
            if cobertura >= 60:
                riesgos.append(
                    "No se pudo proponer un líder con disponibilidad suficiente."
                )
                recomendaciones.append(
                    "Revisar la carga de trabajo de los integrantes mejor "
                    "evaluados para liberar disponibilidad de liderazgo."
                )

        if 0 < len(integrantes) < 3 and cobertura < 100:
            riesgos.append(
                "El equipo propuesto es pequeño y aún no cubre todas "
                "las habilidades."
            )

        if puede_crearse and not riesgos:
            recomendaciones.append(
                "El equipo está listo para ser creado. Se recomienda "
                "formalizar la asignación y comunicar al líder propuesto."
            )

        return riesgos, recomendaciones
    