from __future__ import annotations

from dataset_regresion import DataSetRegresion
from modelo_regresion import ModeloRegresion
from utilidades import media


class RegresorLineal(ModeloRegresion):
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
            matriz_entrenamiento = self.normalizador_entradas.transformar_matriz(matriz)
        else:
            matriz_entrenamiento = [fila[:] for fila in matriz]

        if self.normalizador_objetivo is not None:
            self.normalizador_objetivo.ajustar_valores(objetivos)
            objetivos_entrenamiento = self.normalizador_objetivo.transformar_valores(objetivos)
        else:
            objetivos_entrenamiento = objetivos[:]

        total_filas = len(matriz_entrenamiento)
        total_columnas = len(matriz_entrenamiento[0])
        self.pesos = [0.0] * total_columnas
        self.sesgo = media(objetivos_entrenamiento)

        for _ in range(self.iteraciones):
            gradiente_pesos = [0.0] * total_columnas
            gradiente_sesgo = 0.0

            for fila, objetivo in zip(matriz_entrenamiento, objetivos_entrenamiento):
                prediccion = self._predecir_normalizado(fila)
                error = prediccion - objetivo
                gradiente_sesgo += error

                for indice, valor in enumerate(fila):
                    gradiente_pesos[indice] += error * valor

            factor = 2.0 / float(total_filas)
            for indice in range(total_columnas):
                self.pesos[indice] -= self.tasa_aprendizaje * factor * gradiente_pesos[indice]

            self.sesgo -= self.tasa_aprendizaje * factor * gradiente_sesgo

    def predecir(self, atributos: list[float]) -> float:
        if not self.pesos:
            raise ValueError("El modelo debe entrenarse antes de predecir.")

        fila = [float(valor) for valor in atributos]
        if self.normalizador_entradas is not None:
            fila = self.normalizador_entradas.transformar_vector(fila)

        prediccion = self._predecir_normalizado(fila)

        if self.normalizador_objetivo is not None:
            prediccion = self.normalizador_objetivo.inversa_valor(prediccion)

        return float(prediccion)

    def _predecir_normalizado(self, fila: list[float]) -> float:
        suma = self.sesgo
        for peso, valor in zip(self.pesos, fila):
            suma += peso * valor
        return suma

