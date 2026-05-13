from __future__ import annotations

from dataset_regresion import DataSetRegresion
from utilidades import correlacion_pearson_absoluta


class CalculadoraPesosCorrelacion:
    def calcular(self, dataset: DataSetRegresion) -> list[float]:
        matriz = dataset.matriz_atributos()
        objetivos = dataset.objetivos()

        if not matriz:
            raise ValueError("El dataset no contiene registros para calcular correlaciones.")

        total_columnas = len(matriz[0])
        pesos: list[float] = []

        for indice in range(total_columnas):
            columna = [fila[indice] for fila in matriz]
            peso = correlacion_pearson_absoluta(columna, objetivos)
            pesos.append(max(peso, 1e-8))

        return pesos

