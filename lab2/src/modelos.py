from abc import ABC, abstractmethod
from collections import Counter

from dataset import DataSet, DataSetClasificacion, DataSetRegresion
from Registro import Registro


class Modelo(ABC):
    def __init__(self) -> None:
        self.datos_entrenamiento: DataSet | None = None

    def entrenar(self, datos: DataSet) -> None:
        if not isinstance(datos, DataSet):
            raise TypeError("El argumento de entrenar debe ser un objeto DataSet.")
        self.datos_entrenamiento = datos

    @abstractmethod
    def predecir(self, registro: Registro):
        pass


class Clasificador_kNN(Modelo):
    def __init__(
        self,
        k: int,
        distancia: str = "euclidea",
        pesos: list[float] | None = None,
    ) -> None:
        super().__init__()
        if k <= 0:
            raise ValueError("El parametro k debe ser mayor que cero.")

        self.k = k
        self.distancia = distancia
        self.pesos = list(pesos) if pesos is not None else None

    def predecir(self, registro: Registro) -> str:
        if self.datos_entrenamiento is None:
            raise ValueError("El modelo debe entrenarse antes de predecir.")
        if not isinstance(self.datos_entrenamiento, DataSetClasificacion):
            raise TypeError("Clasificador_kNN necesita un DataSetClasificacion entrenado.")
        if not self.datos_entrenamiento.registros:
            raise ValueError("El dataset de entrenamiento no contiene registros.")

        indices = registro.k_vecinos(
            self.datos_entrenamiento.registros,
            k=self.k,
            tipo=self.distancia,
            pesos=self.pesos,
        )

        etiquetas_vecinas = [self.datos_entrenamiento.registros[i].objetivo for i in indices]
        contador = Counter(etiquetas_vecinas)
        etiqueta_mas_comun, _ = contador.most_common(1)[0]
        return etiqueta_mas_comun


class Regresor_kNN(Modelo):
    def __init__(
        self,
        k: int,
        distancia: str = "euclidea",
        pesos: list[float] | None = None,
    ) -> None:
        super().__init__()
        if k <= 0:
            raise ValueError("El parametro k debe ser mayor que cero.")

        self.k = k
        self.distancia = distancia
        self.pesos = list(pesos) if pesos is not None else None

    def predecir(self, registro: Registro) -> float:
        if self.datos_entrenamiento is None:
            raise ValueError("El modelo debe entrenarse antes de predecir.")
        if not isinstance(self.datos_entrenamiento, DataSetRegresion):
            raise TypeError("Regresor_kNN necesita un DataSetRegresion entrenado.")
        if not self.datos_entrenamiento.registros:
            raise ValueError("El dataset de entrenamiento no contiene registros.")

        indices = registro.k_vecinos(
            self.datos_entrenamiento.registros,
            k=self.k,
            tipo=self.distancia,
            pesos=self.pesos,
        )

        valores = [float(self.datos_entrenamiento.registros[i].objetivo) for i in indices]
        return sum(valores) / len(valores)
