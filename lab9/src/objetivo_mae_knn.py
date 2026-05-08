from __future__ import annotations

from dataset_regresion import DataSetRegresion
from evaluador_mae import EvaluadorMAE
from predictor_serie_temporal import PredictorSerieTemporal
from regresor_knn import RegresorKNN


class ObjetivoMAEKNN:
    def __init__(
        self,
        dataset_entrenamiento: DataSetRegresion,
        historial_inicial: list[float],
        valores_reales: list[float],
        ph: int,
        k: int,
    ) -> None:
        self.dataset_entrenamiento = dataset_entrenamiento
        self.historial_inicial = [float(valor) for valor in historial_inicial]
        self.valores_reales = [float(valor) for valor in valores_reales]
        self.ph = int(ph)
        self.k = int(k)
        self.predictor = PredictorSerieTemporal()
        self.evaluador = EvaluadorMAE()

    def evaluar(self, pesos: list[float]) -> float:
        modelo = RegresorKNN(self.k, pesos=pesos)
        modelo.entrenar(self.dataset_entrenamiento)
        predicciones = self.predictor.predecir(
            modelo,
            self.historial_inicial,
            self.ph,
            len(self.valores_reales),
        )
        return self.evaluador.calcular(self.valores_reales, predicciones)

