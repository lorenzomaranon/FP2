from __future__ import annotations

import math

from datos_sensores import DatosSensores
from transformador_diferencias import TransformadorDiferencias


class AnalizadorCorrelaciones:
    def __init__(self) -> None:
        self.transformador = TransformadorDiferencias()

    def correlacion_pearson(self, lista1: list[float], lista2: list[float]) -> float:
        if len(lista1) != len(lista2):
            raise ValueError("Las listas deben tener la misma longitud.")
        if not lista1:
            return 0.0

        valores1 = [float(valor) for valor in lista1]
        valores2 = [float(valor) for valor in lista2]
        media1 = sum(valores1) / float(len(valores1))
        media2 = sum(valores2) / float(len(valores2))

        numerador = 0.0
        suma1 = 0.0
        suma2 = 0.0
        for valor1, valor2 in zip(valores1, valores2):
            delta1 = valor1 - media1
            delta2 = valor2 - media2
            numerador += delta1 * delta2
            suma1 += delta1 * delta1
            suma2 += delta2 * delta2

        if suma1 == 0.0 or suma2 == 0.0:
            return 0.0

        return numerador / math.sqrt(suma1 * suma2)

    def correlaciones_ventana(
        self,
        lista1: list[float],
        lista2: list[float],
        tamano_ventana: int,
    ) -> list[float]:
        if tamano_ventana <= 1:
            raise ValueError("La ventana debe ser mayor que 1.")
        if len(lista1) != len(lista2):
            raise ValueError("Las listas deben tener la misma longitud.")

        resultado: list[float] = []
        for indice in range(len(lista1)):
            if indice + 1 < tamano_ventana:
                resultado.append(1.0)
                continue

            inicio = indice - tamano_ventana + 1
            resultado.append(
                self.correlacion_pearson(
                    lista1[inicio : indice + 1],
                    lista2[inicio : indice + 1],
                ),
            )

        return resultado

    def pares_correlacionados(
        self,
        datos: DatosSensores,
        umbral: float = 0.8,
        dia: int = 1,
        minutos_por_dia: int = 1440,
        usar_diferencias: bool = True,
    ) -> list[tuple[str, str]]:
        inicio, fin = datos.rango_dia(dia, minutos_por_dia)
        nombres = datos.nombres_variables()
        pares: list[tuple[str, str]] = []

        for indice1 in range(len(nombres)):
            nombre1 = nombres[indice1]
            valores1 = datos.segmento_variable(nombre1, inicio, fin)
            if usar_diferencias:
                valores1 = self.transformador.calcular_diferencias(valores1)

            for indice2 in range(indice1 + 1, len(nombres)):
                nombre2 = nombres[indice2]
                valores2 = datos.segmento_variable(nombre2, inicio, fin)
                if usar_diferencias:
                    valores2 = self.transformador.calcular_diferencias(valores2)

                correlacion = self.correlacion_pearson(valores1, valores2)
                if correlacion >= umbral:
                    pares.append((nombre1, nombre2))

        return pares
