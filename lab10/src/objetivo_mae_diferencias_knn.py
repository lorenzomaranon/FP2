from __future__ import annotations

import sys
from pathlib import Path

LAB9_SRC = Path(__file__).resolve().parents[2] / "lab9" / "src"
if str(LAB9_SRC) not in sys.path:
    sys.path.append(str(LAB9_SRC))

from dataset_regresion import DataSetRegresion
from evaluador_mae import EvaluadorMAE
from predictor_serie_temporal import PredictorSerieTemporal
from regresor_knn import RegresorKNN
from transformador_diferencias import TransformadorDiferencias


class ObjetivoMAEDiferenciasKNN:
    def __init__(
        self,
        dataset_entrenamiento: DataSetRegresion,
        historial_diferencias: list[float],
        valor_inicial_original: float,
        valores_reales_originales: list[float],
        ph: int,
        k: int,
    ) -> None:
        self.dataset_entrenamiento = dataset_entrenamiento
        self.historial_diferencias = [float(valor) for valor in historial_diferencias]
        self.valor_inicial_original = float(valor_inicial_original)
        self.valores_reales_originales = [
            float(valor) for valor in valores_reales_originales
        ]
        self.ph = int(ph)
        self.k = int(k)
        self.predictor = PredictorSerieTemporal()
        self.evaluador = EvaluadorMAE()
        self.transformador = TransformadorDiferencias()

    def evaluar(self, pesos: list[float]) -> float:
        modelo = RegresorKNN(self.k, pesos=pesos)
        modelo.entrenar(self.dataset_entrenamiento)
        predicciones_diferencias = self.predictor.predecir(
            modelo,
            self.historial_diferencias,
            self.ph,
            len(self.valores_reales_originales),
        )
        predicciones_originales = self.transformador.reconstruir_desde_diferencias(
            self.valor_inicial_original,
            predicciones_diferencias,
        )
        return self.evaluador.calcular(
            self.valores_reales_originales,
            predicciones_originales,
        )
