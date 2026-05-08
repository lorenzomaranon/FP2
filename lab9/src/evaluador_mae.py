from __future__ import annotations

from utilidades import mae


class EvaluadorMAE:
    def calcular(self, reales: list[float], predicciones: list[float]) -> float:
        return mae(reales, predicciones)

