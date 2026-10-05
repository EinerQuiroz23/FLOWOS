class DisponibilidadCalculator:

    def calcular(
        self,
        capacidad_horas_semana: float,
        horas_carga_actual: float,
    ) -> float:
        """
        horas_carga_actual hoy es la suma de dedicacion (%) de
        asignaciones ASIGNADA / EN_PROGRESO.

        disponibilidad = 100 - ocupación_porcentual
        """

        if capacidad_horas_semana <= 0:
            return 0.0

        ocupacion_pct = float(horas_carga_actual or 0)

        # No permitir valores negativos de entrada
        if ocupacion_pct < 0:
            ocupacion_pct = 0.0

        disponibilidad = 100.0 - ocupacion_pct

        return round(max(disponibilidad, 0.0), 2)