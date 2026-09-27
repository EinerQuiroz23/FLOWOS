class ExperienciaCalculator:

    def calcular(
        self,
        años_experiencia_promedio: float
    ) -> float:

        if años_experiencia_promedio <= 0:
            return 0.0

        experiencia = (
            años_experiencia_promedio / 5
        ) * 100

        return round(
            min(experiencia, 100),
            2
        )