from __future__ import annotations

import random

from utilidades import acotar


class OptimizadorEvolucionDiferencial:
    def __init__(
        self,
        dimension: int,
        limite_inferior: float = 0.0,
        limite_superior: float = 2.0,
        tam_poblacion: int = 10,
        generaciones: int = 10,
        factor_mutacion: float = 0.7,
        tasa_cruce: float = 0.8,
        semilla: int = 2026,
    ) -> None:
        if dimension <= 0:
            raise ValueError("La dimension debe ser mayor que cero.")
        if tam_poblacion < 4:
            raise ValueError("La poblacion debe tener al menos 4 individuos.")
        if limite_superior < limite_inferior:
            raise ValueError("Los limites del buscador no son validos.")

        self.dimension = int(dimension)
        self.limite_inferior = float(limite_inferior)
        self.limite_superior = float(limite_superior)
        self.tam_poblacion = int(tam_poblacion)
        self.generaciones = int(generaciones)
        self.factor_mutacion = float(factor_mutacion)
        self.tasa_cruce = float(tasa_cruce)
        self.random = random.Random(semilla)

    def optimizar(
        self,
        funcion_objetivo,
        solucion_inicial: list[float] | None = None,
    ) -> tuple[list[float], float]:
        poblacion = self._crear_poblacion(solucion_inicial)
        puntuaciones = [float(funcion_objetivo(individuo)) for individuo in poblacion]

        for _ in range(self.generaciones):
            for indice in range(self.tam_poblacion):
                candidatos = [i for i in range(self.tam_poblacion) if i != indice]
                a, b, c = self.random.sample(candidatos, 3)

                mutante: list[float] = []
                for posicion in range(self.dimension):
                    valor = (
                        poblacion[a][posicion]
                        + self.factor_mutacion
                        * (poblacion[b][posicion] - poblacion[c][posicion])
                    )
                    mutante.append(self._acotar_valor(valor))

                j_aleatorio = self.random.randrange(self.dimension)
                prueba = poblacion[indice][:]

                for posicion in range(self.dimension):
                    if self.random.random() < self.tasa_cruce or posicion == j_aleatorio:
                        prueba[posicion] = mutante[posicion]

                puntuacion_prueba = float(funcion_objetivo(prueba))
                if puntuacion_prueba < puntuaciones[indice]:
                    poblacion[indice] = prueba
                    puntuaciones[indice] = puntuacion_prueba

        mejor_indice = min(range(self.tam_poblacion), key=lambda i: puntuaciones[i])
        return poblacion[mejor_indice][:], puntuaciones[mejor_indice]

    def _crear_poblacion(self, solucion_inicial: list[float] | None) -> list[list[float]]:
        poblacion: list[list[float]] = []

        if solucion_inicial is not None:
            if len(solucion_inicial) != self.dimension:
                raise ValueError("La solucion inicial no coincide con la dimension del problema.")
            poblacion.append([self._acotar_valor(valor) for valor in solucion_inicial])

        while len(poblacion) < self.tam_poblacion:
            if solucion_inicial is None:
                individuo = [
                    self.random.uniform(self.limite_inferior, self.limite_superior)
                    for _ in range(self.dimension)
                ]
            else:
                individuo = []
                for valor in solucion_inicial:
                    rango = self.limite_superior - self.limite_inferior
                    ruido = self.random.uniform(-0.25 * rango, 0.25 * rango)
                    individuo.append(self._acotar_valor(float(valor) + ruido))

            poblacion.append(individuo)

        return poblacion

    def _acotar_valor(self, valor: float) -> float:
        return acotar(float(valor), self.limite_inferior, self.limite_superior)

