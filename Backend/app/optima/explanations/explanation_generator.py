from typing import List, Optional


class ExplanationGenerator:

    # ==========================================================
    # EXPLICACIÓN DE CANDIDATO
    # ==========================================================

    def generar(
        self,
        candidato,
        elegible: Optional[bool] = None
    ) -> str:

        if candidato is None:

            return (
                "No fue posible generar una explicación "
                "porque el candidato no existe."
            )

        if elegible is None:

            elegible = getattr(
                candidato,
                "elegible",
                False
            )

        if not elegible:

            return self._explicar_no_elegible(
                candidato
            )

        return self._explicar_elegible(
            candidato
        )

    # ==========================================================
    # COMPATIBILIDAD CON SERVICIOS ANTERIORES
    # ==========================================================

    def generar_explicacion(
        self,
        candidato
    ) -> str:

        return self.generar(
            candidato
        )

    # ==========================================================
    # EXPLICACIÓN DE PROPUESTA DE EQUIPO
    # ==========================================================

    def generar_propuesta_equipo(
        self,
        integrantes,
        cobertura: float,
        habilidades_faltantes: List[str],
        puede_crearse: bool
    ) -> str:

        cantidad_integrantes = len(
            integrantes or []
        )

        cobertura = float(
            cobertura or 0
        )

        habilidades_faltantes = (
            habilidades_faltantes or []
        )

        if puede_crearse:

            if cobertura >= 100:

                return (
                    f"OPTIMA propone un equipo de "
                    f"{cantidad_integrantes} integrante(s) "
                    "que cubre el 100% de las habilidades "
                    "requeridas para el proyecto."
                )

            return (
                f"OPTIMA propone un equipo de "
                f"{cantidad_integrantes} integrante(s) "
                f"con una cobertura del "
                f"{cobertura:.2f}%."
            )

        if habilidades_faltantes:

            habilidades = ", ".join(
                dict.fromkeys(
                    habilidades_faltantes
                )
            )

            return (
                f"OPTIMA encontró una propuesta de "
                f"{cantidad_integrantes} integrante(s), "
                "pero todavía no se cubren todas las "
                "habilidades requeridas. "
                f"Habilidades faltantes: {habilidades}."
            )

        return (
            f"OPTIMA encontró una propuesta de "
            f"{cantidad_integrantes} integrante(s), "
            "pero las condiciones actuales no permiten "
            "crear el equipo automáticamente."
        )

    # ==========================================================
    # CANDIDATO NO ELEGIBLE
    # ==========================================================

    def _explicar_no_elegible(
        self,
        candidato
    ) -> str:

        razones = []

        compatibilidad = float(
            self._obtener_valor(
                candidato,
                "compatibilidad",
                0
            ) or 0
        )

        disponibilidad = float(
            self._obtener_valor(
                candidato,
                "disponibilidad",
                0
            ) or 0
        )

        habilidades_requeridas = int(
            self._obtener_valor(
                candidato,
                "habilidades_requeridas",
                0
            ) or 0
        )

        habilidades_cumplidas = int(
            self._obtener_valor(
                candidato,
                "habilidades_cumplidas",
                0
            ) or 0
        )

        habilidades_no_registradas = (
            self._convertir_texto_a_lista(
                self._obtener_valor(
                    candidato,
                    "habilidades_no_registradas",
                    None
                )
            )
        )

        habilidades_nivel_insuficiente = (
            self._convertir_texto_a_lista(
                self._obtener_valor(
                    candidato,
                    "habilidades_nivel_insuficiente",
                    None
                )
            )
        )

        # ------------------------------------------------------
        # DISPONIBILIDAD
        # ------------------------------------------------------

        if disponibilidad <= 0:

            razones.append(
                "no cuenta con disponibilidad suficiente"
            )

        # ------------------------------------------------------
        # HABILIDADES
        # ------------------------------------------------------

        if (
            habilidades_requeridas > 0
            and habilidades_cumplidas
            < habilidades_requeridas
        ):

            razones.append(
                "no cumple todos los requisitos de habilidades"
            )

        # ------------------------------------------------------
        # COMPATIBILIDAD
        # ------------------------------------------------------

        if compatibilidad <= 0:

            razones.append(
                "no presenta compatibilidad suficiente "
                "con los requisitos"
            )

        # ------------------------------------------------------
        # RAZÓN GENERAL
        # ------------------------------------------------------

        if not razones:

            razones.append(
                "no cumple las condiciones necesarias "
                "para ser seleccionado"
            )

        mensaje = (
            "La persona no es elegible porque "
            + " y ".join(razones)
            + "."
        )

        # ------------------------------------------------------
        # HABILIDADES NO REGISTRADAS
        # ------------------------------------------------------

        if habilidades_no_registradas:

            habilidades = ", ".join(
                dict.fromkeys(
                    habilidades_no_registradas
                )
            )

            mensaje += (
                " Habilidades no registradas: "
                f"{habilidades}."
            )

        # ------------------------------------------------------
        # NIVEL INSUFICIENTE
        # ------------------------------------------------------

        if habilidades_nivel_insuficiente:

            habilidades = ", ".join(
                dict.fromkeys(
                    habilidades_nivel_insuficiente
                )
            )

            mensaje += (
                " Habilidades con nivel insuficiente: "
                f"{habilidades}."
            )

        return mensaje

    # ==========================================================
    # CANDIDATO ELEGIBLE
    # ==========================================================

    def _explicar_elegible(
        self,
        candidato
    ) -> str:

        partes = []

        habilidades_requeridas = int(
            self._obtener_valor(
                candidato,
                "habilidades_requeridas",
                0
            ) or 0
        )

        habilidades_cumplidas = int(
            self._obtener_valor(
                candidato,
                "habilidades_cumplidas",
                0
            ) or 0
        )

        compatibilidad = float(
            self._obtener_valor(
                candidato,
                "compatibilidad",
                0
            ) or 0
        )

        experiencia = float(
            self._obtener_valor(
                candidato,
                "experiencia",
                0
            ) or 0
        )

        disponibilidad = float(
            self._obtener_valor(
                candidato,
                "disponibilidad",
                0
            ) or 0
        )

        habilidades_ok = (
            self._convertir_texto_a_lista(
                self._obtener_valor(
                    candidato,
                    "habilidades_ok",
                    None
                )
            )
        )

        # ------------------------------------------------------
        # HABILIDADES
        # ------------------------------------------------------

        if habilidades_requeridas > 0:

            partes.append(
                f"cumple {habilidades_cumplidas} de "
                f"{habilidades_requeridas} habilidades requeridas"
            )

        elif habilidades_ok:

            partes.append(
                "cumple con las habilidades requeridas"
            )

        # ------------------------------------------------------
        # DETALLE DE HABILIDADES
        # ------------------------------------------------------

        if habilidades_ok:

            habilidades = ", ".join(
                dict.fromkeys(
                    habilidades_ok
                )
            )

            partes.append(
                f"habilidades cubiertas: {habilidades}"
            )

        # ------------------------------------------------------
        # COMPATIBILIDAD
        # ------------------------------------------------------

        if compatibilidad > 0:

            partes.append(
                f"presenta una compatibilidad del "
                f"{compatibilidad:.2f}%"
            )

        # ------------------------------------------------------
        # EXPERIENCIA
        # ------------------------------------------------------

        if experiencia > 0:

            partes.append(
                f"cuenta con un nivel de experiencia "
                f"de {experiencia:.2f}"
            )

        # ------------------------------------------------------
        # DISPONIBILIDAD
        # ------------------------------------------------------

        if disponibilidad > 0:

            partes.append(
                f"dispone de un "
                f"{disponibilidad:.2f}% de disponibilidad"
            )

        return (
            "La persona es elegible porque "
            + ", ".join(partes)
            + "."
        )

    # ==========================================================
    # CONVERTIR TEXTO A LISTA
    # ==========================================================

    @staticmethod
    def _convertir_texto_a_lista(
        valor
    ) -> List[str]:

        if valor is None:
            return []

        if isinstance(valor, list):
            return [
                str(elemento).strip()
                for elemento in valor
                if str(elemento).strip()
            ]

        if isinstance(valor, tuple):
            return [
                str(elemento).strip()
                for elemento in valor
                if str(elemento).strip()
            ]

        texto = str(valor).strip()

        if not texto:
            return []

        return [
            elemento.strip()
            for elemento in texto.split(",")
            if elemento.strip()
        ]

    # ==========================================================
    # OBTENER ATRIBUTO
    # ==========================================================

    @staticmethod
    def _obtener_valor(
        objeto,
        atributo: str,
        valor_defecto
    ):

        valor = getattr(
            objeto,
            atributo,
            valor_defecto
        )

        if valor is None:
            return valor_defecto

        return valor