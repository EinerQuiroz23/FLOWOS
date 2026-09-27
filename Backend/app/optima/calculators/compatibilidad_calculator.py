class CompatibilidadCalculator:

    def calcular(
        self,
        habilidades_requeridas: int,
        habilidades_cumplidas: int
    ) -> float:

        if habilidades_requeridas <= 0:
            return 0.0

        compatibilidad = (
            habilidades_cumplidas
            / habilidades_requeridas
        ) * 100

        return round(compatibilidad, 2)