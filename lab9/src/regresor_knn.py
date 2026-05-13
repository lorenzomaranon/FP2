from __future__ import annotations

from dataset_regresion import DataSetRegresion
from modelo_regresion import ModeloRegresion
class RegresorKNN(ModeloRegresion):
    def __init__(self, k: int, pesos: list[float] | None = None) -> None:
        super().__init__()
        if k <= 0:
            raise ValueError("El valor de k debe ser mayor que cero.")

        self.k = int(k)
        self.pesos = [float(peso) for peso in pesos] if pesos is not None else None

    def entrenar(self, dataset: DataSetRegresion) -> None:
        super().entrenar(dataset)
        if not dataset.registros:
            raise ValueError("El dataset de entrenamiento no contiene registros.")

        dimension = len(dataset.registros[0].datos)
        if self.pesos is None:
            self.pesos = [1.0] * dimension
        elif len(self.pesos) != dimension:
            raise ValueError("La lista de pesos no coincide con la dimension del dataset.")

    def predecir(self, atributos: list[float]) -> float:
        if self.dataset_entrenamiento is None or self.pesos is None:
            raise ValueError("El modelo debe entrenarse antes de predecir.")

        consulta = [float(valor) for valor in atributos]
        vecinos: list[tuple[float, float]] = []
        limite_vecinos = min(self.k, len(self.dataset_entrenamiento.registros))

        for registro in self.dataset_entrenamiento.registros:
            distancia = 0.0
            for valor_consulta, valor_registro, peso in zip(consulta, registro.datos, self.pesos):
                diferencia = valor_consulta - valor_registro
                distancia += peso * diferencia * diferencia
            candidato = (distancia, float(registro.objetivo))

            if len(vecinos) < limite_vecinos:
                vecinos.append(candidato)
                vecinos.sort(key=lambda elemento: elemento[0], reverse=True)
                continue

            if distancia < vecinos[0][0]:
                vecinos[0] = candidato
                vecinos.sort(key=lambda elemento: elemento[0], reverse=True)

        suma = 0.0
        for _, objetivo in vecinos:
            suma += objetivo

        return suma / float(len(vecinos))
