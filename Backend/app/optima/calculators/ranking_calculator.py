from typing import List


class RankingCalculator:

    def calcular_ranking(self, candidatos: List) -> List:
        if not candidatos:
            return []

        candidatos_validos = [
            candidato
            for candidato in candidatos
            if candidato is not None
        ]

        candidatos_ordenados = sorted(
            candidatos_validos,
            key=self._obtener_clave_ranking,
            reverse=True
        )

        for posicion, candidato in enumerate(
            candidatos_ordenados,
            start=1
        ):
            candidato.ranking = posicion

        return candidatos_ordenados

    def _obtener_clave_ranking(self, candidato):
        elegible = self._obtener_valor(
            candidato,
            "elegible",
            False
        )

        puntuacion_optima = self._obtener_valor(
            candidato,
            "puntuacion_optima",
            0
        )

        compatibilidad = self._obtener_valor(
            candidato,
            "compatibilidad",
            0
        )

        experiencia = self._obtener_valor(
            candidato,
            "experiencia",
            0
        )

        disponibilidad = self._obtener_valor(
            candidato,
            "disponibilidad",
            0
        )

        requisitos_cubiertos = self._obtener_valor(
            candidato,
            "requisitos_cubiertos",
            0
        )

        return (
            1 if elegible else 0,
            float(puntuacion_optima or 0),
            float(compatibilidad or 0),
            float(experiencia or 0),
            float(disponibilidad or 0),
            int(requisitos_cubiertos or 0)
        )

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

    def ordenar(self, candidatos: List) -> List:
        return self.calcular_ranking(candidatos)