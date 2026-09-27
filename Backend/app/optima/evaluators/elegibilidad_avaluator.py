class ElegibilidadEvaluator:

    def evaluar(
        self,
        compatibilidad: float,
        disponibilidad: float
    ) -> bool:

        return (
            compatibilidad >= 50
            and disponibilidad > 0
        )