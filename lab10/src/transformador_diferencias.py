from __future__ import annotations


class TransformadorDiferencias:
    def calcular_diferencias(self, valores: list[float]) -> list[float]:
        if len(valores) < 2:
            return []

        diferencias: list[float] = []
        for indice in range(1, len(valores)):
            diferencias.append(float(valores[indice]) - float(valores[indice - 1]))

        return diferencias

    def reconstruir_desde_diferencias(
        self,
        valor_inicial: float,
        diferencias: list[float],
    ) -> list[float]:
        valor_actual = float(valor_inicial)
        reconstruida: list[float] = []

        for diferencia in diferencias:
            valor_actual += float(diferencia)
            reconstruida.append(valor_actual)

        return reconstruida
