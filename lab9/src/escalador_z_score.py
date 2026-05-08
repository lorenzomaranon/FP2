from __future__ import annotations

from utilidades import desviacion_tipica, media


class EscaladorZScore:
    def __init__(self) -> None:
        self.medias: list[float] = []
        self.desviaciones: list[float] = []

    def ajustar_matriz(self, matriz: list[list[float]]) -> None:
        if not matriz:
            raise ValueError("Se requiere una matriz no vacia para ajustar el escalador.")

        total_columnas = len(matriz[0])
        self.medias = []
        self.desviaciones = []

        for indice in range(total_columnas):
            columna = [float(fila[indice]) for fila in matriz]
            self.medias.append(media(columna))
            desviacion = desviacion_tipica(columna)
            self.desviaciones.append(desviacion if desviacion != 0.0 else 1.0)

    def transformar_matriz(self, matriz: list[list[float]]) -> list[list[float]]:
        return [self.transformar_vector(fila) for fila in matriz]

    def transformar_vector(self, vector: list[float]) -> list[float]:
        if len(vector) != len(self.medias):
            raise ValueError("La dimension del vector no coincide con la del escalador.")

        transformado: list[float] = []
        for indice, valor in enumerate(vector):
            media_columna = self.medias[indice]
            desviacion = self.desviaciones[indice]
            transformado.append((float(valor) - media_columna) / desviacion)

        return transformado

    def ajustar_valores(self, valores: list[float]) -> None:
        if not valores:
            raise ValueError("Se requiere al menos un valor para ajustar el escalador.")
        promedio = media([float(valor) for valor in valores])
        desviacion = desviacion_tipica([float(valor) for valor in valores])
        self.medias = [promedio]
        self.desviaciones = [desviacion if desviacion != 0.0 else 1.0]

    def transformar_valores(self, valores: list[float]) -> list[float]:
        return [self.transformar_valor(valor) for valor in valores]

    def transformar_valor(self, valor: float) -> float:
        if not self.medias or not self.desviaciones:
            raise ValueError("El escalador debe ajustarse antes de usarse.")
        return (float(valor) - self.medias[0]) / self.desviaciones[0]

    def inversa_valor(self, valor: float) -> float:
        if not self.medias or not self.desviaciones:
            raise ValueError("El escalador debe ajustarse antes de usarse.")
        return float(valor) * self.desviaciones[0] + self.medias[0]

