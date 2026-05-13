from __future__ import annotations

from abc import ABC, abstractmethod

from dataset_regresion import DataSetRegresion


class ModeloRegresion(ABC):
    def __init__(self) -> None:
        self.dataset_entrenamiento: DataSetRegresion | None = None

    def entrenar(self, dataset: DataSetRegresion) -> None:
        if not isinstance(dataset, DataSetRegresion):
            raise TypeError("El modelo requiere un DataSetRegresion.")
        self.dataset_entrenamiento = dataset

    @abstractmethod
    def predecir(self, atributos: list[float]) -> float:
        raise NotImplementedError

