from types import SimpleNamespace
from typing import List

from sqlalchemy.orm import Session

from app.core.excepcions.base import FlowosException

from app.optima.models.candidato_optima import CandidatoOptima

from app.optima.repositories.optima_repository import (
    OptimaRepository
)

from app.optima.calculators.compatibilidad_calculator import (
    CompatibilidadCalculator
)

from app.optima.calculators.experiencia_calculator import (
    ExperienciaCalculator
)

from app.optima.calculators.disponibilidad_calculator import (
    DisponibilidadCalculator
)

from app.optima.calculators.puntuacion_calculator import (
    PuntuacionCalculator
)

from app.optima.evaluators.elegibilidad_avaluator import (
    ElegibilidadEvaluator
)

from app.optima.calculators.ranking_calculator import (
    RankingCalculator
)

from app.optima.explanations.explanation_generator import (
    ExplanationGenerator
)


class OptimaService:

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

        self.experiencia_calculator = (
            ExperienciaCalculator()
        )

        self.disponibilidad_calculator = (
            DisponibilidadCalculator()
        )

        self.puntuacion_calculator = (
            PuntuacionCalculator()
        )

        self.elegibilidad_evaluator = (
            ElegibilidadEvaluator()
        )

        self.ranking_calculator = (
            RankingCalculator()
        )

        self.explanation_generator = (
            ExplanationGenerator()
        )

    # ==========================================================
    # NORMALIZAR HABILIDADES REQUERIDAS
    # ==========================================================

    def _normalizar_habilidades_requeridas(
        self,
        habilidades
    ):

        resultado = []

        for fila in habilidades:

            entidad = getattr(
                fila,
                "TareaHabilidad",
                None
            )

            # --------------------------------------------------
            # Resultado proveniente de:
            #
            # select(TareaHabilidad, Habilidad.nombre)
            # --------------------------------------------------

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

            # --------------------------------------------------
            # Compatibilidad con resultados ya normalizados
            # --------------------------------------------------

            nombre_habilidad = getattr(
                fila,
                "nombre_habilidad",
                None
            )

            if nombre_habilidad is None:

                nombre_habilidad = getattr(
                    fila,
                    "habilidad",
                    None
                )

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

                    nombre_habilidad=(
                        nombre_habilidad
                    )
                )
            )

        return resultado

    # ==========================================================
    # NORMALIZAR HABILIDADES DE PERSONAS
    # ==========================================================

    def _normalizar_habilidades_personas(
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

            # --------------------------------------------------
            # Resultado proveniente de:
            #
            # select(PersonaHabilidad, Habilidad.nombre)
            # --------------------------------------------------

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
    ):

        if not cargas:

            return {}

        # ------------------------------------------------------
        # El repositorio actual puede devolver:
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
                    carga or 0
                )
                for id_persona, carga
                in cargas.items()
            }

        # ------------------------------------------------------
        # Compatibilidad con resultados de tipo objeto
        # ------------------------------------------------------

        resultado = {}

        for carga in cargas:

            id_persona = getattr(
                carga,
                "id_persona",
                None
            )

            valor = getattr(
                carga,
                "carga_actual",
                None
            )

            if valor is None:

                valor = getattr(
                    carga,
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
    # EVALUAR TAREA
    # ==========================================================

    def evaluar_tarea(
        self,
        id_tarea: int,
        id_organizacion: int
    ) -> List[CandidatoOptima]:

        # ======================================================
        # 1. OBTENER Y VALIDAR TAREA
        # ======================================================

        tarea = (
            self.repository
            .obtener_tarea_por_organizacion(
                id_tarea,
                id_organizacion
            )
        )

        if not tarea:

            raise FlowosException(

                message=(
                    "La tarea no existe o no pertenece "
                    "a la organización del usuario."
                ),

                code="TAREA_NO_AUTORIZADA",

                status_code=404
            )

        # ======================================================
        # 2. VALIDAR ESTADO
        # ======================================================

        if tarea.estado not in {
            "PENDIENTE",
            "EN_PROGRESO"
        }:

            raise FlowosException(

                message=(
                    "La tarea no puede ser analizada "
                    "por OPTIMA porque no se encuentra "
                    "en estado PENDIENTE o EN_PROGRESO."
                ),

                code="TAREA_NO_ANALIZABLE",

                status_code=400
            )

        # ======================================================
        # 3. OBTENER CANDIDATOS
        # ======================================================

        candidatos = (
            self.repository
            .obtener_candidatos_por_tarea(
                id_tarea,
                id_organizacion
            )
        )

        if not candidatos:

            raise FlowosException(

                message=(
                    "No existen integrantes activos "
                    "en el equipo responsable de la tarea."
                ),

                code="CANDIDATOS_NO_ENCONTRADOS",

                status_code=404
            )

        # ======================================================
        # 4. ELIMINAR PERSONAS DUPLICADAS
        # ======================================================

        candidatos_unicos = {}

        for candidato in candidatos:

            if (
                candidato.id_persona
                not in candidatos_unicos
            ):

                candidatos_unicos[
                    candidato.id_persona
                ] = candidato

        candidatos = list(
            candidatos_unicos.values()
        )

        # ======================================================
        # 5. OBTENER HABILIDADES REQUERIDAS
        # ======================================================

        habilidades_requeridas = (
            self.repository
            .obtener_habilidades_requeridas_por_tarea(
                id_tarea
            )
        )

        habilidades_requeridas = (
            self._normalizar_habilidades_requeridas(
                habilidades_requeridas
            )
        )

        if not habilidades_requeridas:

            raise FlowosException(

                message=(
                    "La tarea no tiene habilidades "
                    "requeridas configuradas."
                ),

                code="HABILIDADES_REQUERIDAS_NO_ENCONTRADAS",

                status_code=400
            )

        # ======================================================
        # 6. OBTENER HABILIDADES DE PERSONAS
        # ======================================================

        ids_personas = [
            candidato.id_persona
            for candidato in candidatos
        ]

        habilidades_personas = (
            self.repository
            .obtener_habilidades_por_personas(
                ids_personas
            )
        )

        habilidades_personas = (
            self._normalizar_habilidades_personas(
                habilidades_personas
            )
        )

        # ======================================================
        # 7. OBTENER CARGA ACTUAL
        # ======================================================

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

        # ======================================================
        # 8. INDEXAR HABILIDADES POR PERSONA
        # ======================================================

        habilidades_por_persona = {}

        for habilidad in habilidades_personas:

            habilidades_por_persona.setdefault(
                habilidad.id_persona,
                []
            ).append(
                habilidad
            )

        # ======================================================
        # 9. EVALUAR CADA CANDIDATO
        # ======================================================

        resultados = []

        for candidato in candidatos:

            habilidades_persona = (
                habilidades_por_persona.get(
                    candidato.id_persona,
                    []
                )
            )

            # --------------------------------------------------
            # Variables de evaluación
            # --------------------------------------------------

            habilidades_cumplidas = 0

            habilidades_ok = []

            habilidades_no_registradas = []

            habilidades_nivel_insuficiente = []

            experiencias_relevantes = []

            # ==================================================
            # 10. EVALUAR HABILIDADES
            # ==================================================

            for requerida in (
                habilidades_requeridas
            ):

                habilidad_persona = None

                # --------------------------------------------------
                # Buscar la habilidad correspondiente.
                #
                # Si una persona tiene varias filas para la
                # misma habilidad, conservamos la que tenga
                # mayor nivel.
                # --------------------------------------------------

                for habilidad in (
                    habilidades_persona
                ):

                    if (
                        habilidad.id_habilidad
                        != requerida.id_habilidad
                    ):
                        continue

                    if (
                        habilidad_persona
                        is None
                    ):

                        habilidad_persona = (
                            habilidad
                        )

                        continue

                    if (
                        habilidad.id_nivel
                        > habilidad_persona.id_nivel
                    ):

                        habilidad_persona = (
                            habilidad
                        )

                # --------------------------------------------------
                # Habilidad no registrada
                # --------------------------------------------------

                if habilidad_persona is None:

                    habilidades_no_registradas.append(

                        self._obtener_nombre_habilidad(
                            requerida
                        )
                    )

                    continue

                # --------------------------------------------------
                # Experiencia
                # --------------------------------------------------

                experiencia = float(
                    getattr(
                        habilidad_persona,
                        "años_experiencia",
                        0
                    ) or 0
                )

                if experiencia > 0:

                    experiencias_relevantes.append(
                        experiencia
                    )

                # --------------------------------------------------
                # Nivel suficiente
                # --------------------------------------------------

                if (
                    habilidad_persona.id_nivel
                    >= requerida.id_nivel
                ):

                    habilidades_cumplidas += 1

                    habilidades_ok.append(

                        self._obtener_nombre_habilidad(
                            requerida
                        )
                    )

                else:

                    habilidades_nivel_insuficiente.append(

                        self._obtener_nombre_habilidad(
                            requerida
                        )
                    )

            # ==================================================
            # 11. CANTIDAD DE HABILIDADES
            # ==================================================

            habilidades_requeridas_total = (
                len(
                    habilidades_requeridas
                )
            )

            # ==================================================
            # 12. COMPATIBILIDAD
            # ==================================================

            compatibilidad = (
                self.compatibilidad_calculator.calcular(
                    habilidades_requeridas_total,
                    habilidades_cumplidas
                )
            )

            # ==================================================
            # 13. EXPERIENCIA PROMEDIO
            # ==================================================

            años_experiencia_promedio = (

                sum(
                    experiencias_relevantes
                )
                / len(
                    experiencias_relevantes
                )

                if experiencias_relevantes

                else 0.0
            )

            # ==================================================
            # 14. NIVEL DE EXPERIENCIA
            # ==================================================

            experiencia = (
                self.experiencia_calculator.calcular(
                    años_experiencia_promedio
                )
            )

            # ==================================================
            # 15. CARGA ACTUAL
            # ==================================================

            horas_carga_actual = (
                cargas_por_persona.get(
                    candidato.id_persona,
                    0.0
                )
            )

            # ==================================================
            # 16. DISPONIBILIDAD
            # ==================================================

            disponibilidad = (
                self.disponibilidad_calculator.calcular(

                    float(
                        candidato.capacidad_horas_semana
                        or 0
                    ),

                    horas_carga_actual
                )
            )

            # ==================================================
            # 17. ELEGIBILIDAD
            # ==================================================

            elegible = (
                self.elegibilidad_evaluator.evaluar(

                    compatibilidad,

                    disponibilidad
                )
            )

            # ==================================================
            # 18. PUNTUACIÓN OPTIMA
            # ==================================================

            puntuacion_optima = (
                self.puntuacion_calculator.calcular(

                    compatibilidad,

                    experiencia,

                    disponibilidad
                )
            )

            # ==================================================
            # 19. NOMBRE DE PERSONA
            # ==================================================

            nombre_persona = (
                f"{candidato.nombre} "
                f"{candidato.apellido}"
            )

            # ==================================================
            # 20. CREAR RESULTADO
            # ==================================================

            candidato_optima = CandidatoOptima(

                id_tarea=(
                    id_tarea
                ),

                tarea=(
                    tarea.nombre
                ),

                id_persona=(
                    candidato.id_persona
                ),

                persona=(
                    nombre_persona
                ),

                capacidad_horas_semana=float(
                    candidato.capacidad_horas_semana
                    or 0
                ),

                habilidades_requeridas=(
                    habilidades_requeridas_total
                ),

                habilidades_cumplidas=(
                    habilidades_cumplidas
                ),

                compatibilidad=(
                    compatibilidad
                ),

                años_experiencia_promedio=round(
                    años_experiencia_promedio,
                    2
                ),

                experiencia=(
                    experiencia
                ),

                horas_carga_actual=round(
                    horas_carga_actual,
                    2
                ),

                disponibilidad=(
                    disponibilidad
                ),

                elegible=(
                    elegible
                ),

                # --------------------------------------------------
                # CORRECCIÓN:
                #
                # El modelo usa puntuacion_optima,
                # no puntuacion.
                # --------------------------------------------------

                puntuacion_optima=(
                    puntuacion_optima
                ),

                habilidades_ok=(
                    self._normalizar_lista_texto(
                        habilidades_ok
                    )
                ),

                habilidades_no_registradas=(
                    self._normalizar_lista_texto(
                        habilidades_no_registradas
                    )
                ),

                habilidades_nivel_insuficiente=(
                    self._normalizar_lista_texto(
                        habilidades_nivel_insuficiente
                    )
                )
            )

            # ==================================================
            # 21. EXPLICACIÓN
            # ==================================================

            candidato_optima.explicacion = (

                self.explanation_generator.generar(

                    candidato_optima,

                    candidato_optima.elegible
                )
            )

            resultados.append(
                candidato_optima
            )

        # ======================================================
        # 22. RANKING
        # ======================================================

        resultados = (
            self.ranking_calculator.calcular_ranking(
                resultados
            )
        )

        # ======================================================
        # 23. RETORNAR
        # ======================================================

        return resultados

    # ==========================================================
    # OBTENER NOMBRE DE HABILIDAD
    # ==========================================================

    @staticmethod
    def _obtener_nombre_habilidad(
        habilidad
    ) -> str:

        nombre = getattr(
            habilidad,
            "nombre_habilidad",
            None
        )

        if nombre:

            return str(
                nombre
            ).strip()

        return (
            f"Habilidad "
            f"{getattr(habilidad, 'id_habilidad', '')}"
        )

    # ==========================================================
    # NORMALIZAR LISTA DE TEXTO
    # ==========================================================

    @staticmethod
    def _normalizar_lista_texto(
        valores
    ):

        if not valores:

            return None

        valores_unicos = []

        vistos = set()

        for valor in valores:

            if valor is None:
                continue

            texto = str(
                valor
            ).strip()

            if not texto:
                continue

            if texto in vistos:
                continue

            vistos.add(
                texto
            )

            valores_unicos.append(
                texto
            )

        if not valores_unicos:

            return None

        return ", ".join(
            valores_unicos
        )