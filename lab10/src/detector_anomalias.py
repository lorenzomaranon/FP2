from __future__ import annotations

from analizador_correlaciones import AnalizadorCorrelaciones
from datos_sensores import DatosSensores
from transformador_diferencias import TransformadorDiferencias


class DetectorAnomalias:
    def __init__(self) -> None:
        self.analizador = AnalizadorCorrelaciones()
        self.transformador = TransformadorDiferencias()

    def minutos_ruptura(
        self,
        datos: DatosSensores,
        dia: int,
        pares: list[tuple[str, str]],
        ventana: int = 60,
        umbral_ruptura: float = 0.1,
        minutos_por_dia: int = 1440,
        usar_diferencias: bool = True,
    ) -> dict[tuple[str, str], list[int]]:
        inicio, fin = datos.rango_dia(dia, minutos_por_dia)
        rupturas: dict[tuple[str, str], list[int]] = {}

        for nombre1, nombre2 in pares:
            valores1 = datos.segmento_variable(nombre1, inicio, fin)
            valores2 = datos.segmento_variable(nombre2, inicio, fin)
            desplazamiento = 0

            if usar_diferencias:
                valores1 = self.transformador.calcular_diferencias(valores1)
                valores2 = self.transformador.calcular_diferencias(valores2)
                desplazamiento = 1

            correlaciones = self.analizador.correlaciones_ventana(
                valores1,
                valores2,
                ventana,
            )
            minutos = [
                indice + desplazamiento
                for indice, correlacion in enumerate(correlaciones)
                if correlacion < umbral_ruptura
            ]

            if minutos:
                rupturas[(nombre1, nombre2)] = minutos

        return rupturas

    def agrupar_minutos(
        self,
        minutos: list[int],
        separacion_maxima: int = 15,
        duracion_minima: int = 3,
    ) -> list[tuple[int, int]]:
        if not minutos:
            return []
        if separacion_maxima < 0:
            raise ValueError("La separacion maxima no puede ser negativa.")
        if duracion_minima <= 0:
            raise ValueError("La duracion minima debe ser positiva.")

        ordenados = sorted(set(int(minuto) for minuto in minutos))
        intervalos: list[tuple[int, int]] = []
        inicio = ordenados[0]
        anterior = ordenados[0]

        for minuto in ordenados[1:]:
            if minuto - anterior <= separacion_maxima:
                anterior = minuto
                continue

            if anterior - inicio + 1 >= duracion_minima:
                intervalos.append((inicio, anterior))
            inicio = minuto
            anterior = minuto

        if anterior - inicio + 1 >= duracion_minima:
            intervalos.append((inicio, anterior))

        return intervalos

    def intervalos_por_par(
        self,
        rupturas: dict[tuple[str, str], list[int]],
        separacion_maxima: int = 15,
        duracion_minima: int = 3,
    ) -> dict[tuple[str, str], list[tuple[int, int]]]:
        intervalos: dict[tuple[str, str], list[tuple[int, int]]] = {}

        for par, minutos in rupturas.items():
            grupos = self.agrupar_minutos(
                minutos,
                separacion_maxima=separacion_maxima,
                duracion_minima=duracion_minima,
            )
            if grupos:
                intervalos[par] = grupos

        return intervalos
