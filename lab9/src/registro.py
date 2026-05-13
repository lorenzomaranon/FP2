from __future__ import annotations

import math


class Registro:
    def __init__(self, datos: list[float]) -> None:
        self.datos = [float(valor) for valor in datos]

    def distancia_ponderada(self, otro: "Registro", pesos: list[float]) -> float:
        if len(self.datos) != len(otro.datos):
            raise ValueError("Los registros deben tener la misma dimension.")
        if len(pesos) != len(self.datos):
            raise ValueError("La lista de pesos debe coincidir con la dimension de los registros.")

        suma = 0.0
        for valor_propio, valor_otro, peso in zip(self.datos, otro.datos, pesos):
            diferencia = valor_propio - valor_otro
            suma += max(0.0, float(peso)) * diferencia * diferencia

        return math.sqrt(suma)

