from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

LAB9_SRC = Path(__file__).resolve().parents[2] / "lab9" / "src"
if str(LAB9_SRC) not in sys.path:
    sys.path.append(str(LAB9_SRC))

from dataset_regresion import DataSetRegresion
from modelo_regresion import ModeloRegresion


class RegresorLinealVectorizado(ModeloRegresion):
    def __init__(
        self,
        tasa_aprendizaje: float,
        iteraciones: int = 1200,
        normalizador_entradas=None,
        normalizador_objetivo=None,
    ) -> None:
        super().__init__()
        if tasa_aprendizaje <= 0.0:
            raise ValueError("La tasa de aprendizaje debe ser positiva.")
        if iteraciones <= 0:
            raise ValueError("El numero de iteraciones debe ser mayor que cero.")

        self.tasa_aprendizaje = float(tasa_aprendizaje)
        self.iteraciones = int(iteraciones)
        self.normalizador_entradas = normalizador_entradas
        self.normalizador_objetivo = normalizador_objetivo
        self.pesos: list[float] = []
        self.sesgo: float = 0.0

    def entrenar(self, dataset: DataSetRegresion) -> None:
        super().entrenar(dataset)
        matriz = dataset.matriz_atributos()
        objetivos = dataset.objetivos()

        if not matriz:
            raise ValueError("El dataset de entrenamiento no contiene registros.")

        if self.normalizador_entradas is not None:
            self.normalizador_entradas.ajustar_matriz(matriz)
            matriz = self.normalizador_entradas.transformar_matriz(matriz)

        if self.normalizador_objetivo is not None:
            self.normalizador_objetivo.ajustar_valores(objetivos)
            objetivos = self.normalizador_objetivo.transformar_valores(objetivos)

        x = np.array(matriz, dtype=float)
        y = np.array(objetivos, dtype=float)
        total_filas, total_columnas = x.shape
        pesos = np.zeros(total_columnas, dtype=float)
        sesgo = float(np.mean(y))
        factor = 2.0 / float(total_filas)

        for _ in range(self.iteraciones):
            errores = x @ pesos + sesgo - y
            gradiente_pesos = factor * (x.T @ errores)
            gradiente_sesgo = factor * float(np.sum(errores))
            pesos -= self.tasa_aprendizaje * gradiente_pesos
            sesgo -= self.tasa_aprendizaje * gradiente_sesgo

        self.pesos = [float(valor) for valor in pesos]
        self.sesgo = float(sesgo)

    def predecir(self, atributos: list[float]) -> float:
        if not self.pesos:
            raise ValueError("El modelo debe entrenarse antes de predecir.")

        fila = [float(valor) for valor in atributos]
        if self.normalizador_entradas is not None:
            fila = self.normalizador_entradas.transformar_vector(fila)

        prediccion = float(np.dot(np.array(self.pesos), np.array(fila)) + self.sesgo)

        if self.normalizador_objetivo is not None:
            prediccion = self.normalizador_objetivo.inversa_valor(prediccion)

        return prediccion
