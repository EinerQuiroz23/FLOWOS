class LiderazgoCalculator:
    """
    Calcula el score de liderazgo de forma multidimensional.

    Factores considerados:
    - Compatibilidad técnica
    - Experiencia
    - Disponibilidad
    - Cobertura de habilidades del proyecto
    - Bonus si cubre habilidades únicas / difíciles
    """

    def calcular(
        self,
        compatibilidad: float,
        experiencia: float,
        disponibilidad: float,
        cobertura_habilidades: float = 0.0,
        es_unico_en_habilidades: bool = False
    ) -> float:
        """
        Retorna un score de 0 a 100.
        """

        # Pesos equilibrados y profesionales
        puntuacion = (
            compatibilidad * 0.30
            + experiencia * 0.30
            + disponibilidad * 0.25
            + cobertura_habilidades * 0.15
        )

        # Bonus por cubrir habilidades que pocos tienen
        if es_unico_en_habilidades:
            puntuacion += 8.0

        # Nunca superar 100
        puntuacion = min(puntuacion, 100.0)

        return round(puntuacion, 2)

    def determinar_confianza(
        self,
        score: float,
        compatibilidad: float,
        cobertura_equipo: float
    ) -> str:
        """
        Determina el nivel de confianza del liderazgo propuesto.
        """

        if score >= 75 and compatibilidad >= 60 and cobertura_equipo >= 80:
            return "Alta"

        if score >= 55 and compatibilidad >= 35 and cobertura_equipo >= 50:
            return "Media"

        return "Baja"