from __future__ import annotations


class EscaladorMinMax:
    def __init__(self) -> None:
        self.minimos: list[float] = []
        self.maximos: list[float] = []

    def ajustar_matriz(self, matriz: list[list[float]]) -> None:
        if not matriz:
            raise ValueError("Se requiere una matriz no vacia para ajustar el escalador.")

        total_columnas = len(matriz[0])
        self.minimos = [float("inf")] * total_columnas
        self.maximos = [float("-inf")] * total_columnas

        for fila in matriz:
            if len(fila) != total_columnas:
                raise ValueError("Todas las filas deben tener la misma longitud.")
            for indice, valor in enumerate(fila):
                valor = float(valor)
                if valor < self.minimos[indice]:
                    self.minimos[indice] = valor
                if valor > self.maximos[indice]:
                    self.maximos[indice] = valor

    def transformar_matriz(self, matriz: list[list[float]]) -> list[list[float]]:
        return [self.transformar_vector(fila) for fila in matriz]

    def transformar_vector(self, vector: list[float]) -> list[float]:
        if len(vector) != len(self.minimos):
            raise ValueError("La dimension del vector no coincide con la del escalador.")

        vector_transformado: list[float] = []
        for indice, valor in enumerate(vector):
            minimo = self.minimos[indice]
            maximo = self.maximos[indice]
            rango = maximo - minimo

            if rango == 0.0:
                vector_transformado.append(0.0)
            else:
                vector_transformado.append((float(valor) - minimo) / rango)

        return vector_transformado

    def ajustar_valores(self, valores: list[float]) -> None:
        if not valores:
            raise ValueError("Se requiere al menos un valor para ajustar el escalador.")
        self.minimos = [min(float(valor) for valor in valores)]
        self.maximos = [max(float(valor) for valor in valores)]

    def transformar_valores(self, valores: list[float]) -> list[float]:
        return [self.transformar_valor(valor) for valor in valores]

    def transformar_valor(self, valor: float) -> float:
        if not self.minimos or not self.maximos:
            raise ValueError("El escalador debe ajustarse antes de usarse.")
        minimo = self.minimos[0]
        maximo = self.maximos[0]
        rango = maximo - minimo

        if rango == 0.0:
            return 0.0

        return (float(valor) - minimo) / rango

    def inversa_valor(self, valor: float) -> float:
        if not self.minimos or not self.maximos:
            raise ValueError("El escalador debe ajustarse antes de usarse.")
        minimo = self.minimos[0]
        maximo = self.maximos[0]
        return float(valor) * (maximo - minimo) + minimo

