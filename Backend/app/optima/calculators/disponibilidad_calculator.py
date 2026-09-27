class DisponibilidadCalculator:

    def calcular(
        self,
        capacidad_horas_semana: float,
        horas_carga_actual: float
    ) -> float:

        if capacidad_horas_semana <= 0:
            return 0.0

        disponibilidad = (
            (
                capacidad_horas_semana
                - horas_carga_actual
            )
            / capacidad_horas_semana
        ) * 100

        return round(
            max(disponibilidad, 0),
            2
        )