class PuntuacionCalculator:

    def calcular(
        self,
        compatibilidad: float,
        experiencia: float,
        disponibilidad: float
    ) -> float:

        puntuacion = (
            compatibilidad * 0.50
            + experiencia * 0.20
            + disponibilidad * 0.30
        )

        return round(puntuacion, 2)