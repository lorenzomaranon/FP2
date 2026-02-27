from abc import ABC, abstractmethod

from Registro import Registro, RegistroClasificacion, RegistroRegresion


class DataSet(ABC):
    def __init__(self) -> None:
        self.registros: list[Registro] = []
        self.nombres_atributos: list[str] = []

    def set_cabeceras(self, cabeceras: list[str]) -> None:
        self.nombres_atributos = [str(valor) for valor in cabeceras[:-1]]

    @abstractmethod
    def agregar_registro(self, registro: Registro) -> None:
        pass

    def calcular_min_max(self) -> tuple[list[float], list[float]]:
        if not self.registros:
            return [], []

        primera_dimension = len(self.registros[0].datos)
        minimos = self.registros[0].datos.copy()
        maximos = self.registros[0].datos.copy()

        for registro in self.registros[1:]:
            if len(registro.datos) != primera_dimension:
                raise ValueError("Todos los registros del dataset deben tener la misma dimension.")

            for indice, valor in enumerate(registro.datos):
                if valor < minimos[indice]:
                    minimos[indice] = valor
                if valor > maximos[indice]:
                    maximos[indice] = valor

        return minimos, maximos

    def crear_subconjunto(self, registros: list[Registro]) -> "DataSet":
        subconjunto = self.__class__()
        subconjunto.nombres_atributos = self.nombres_atributos.copy()

        for registro in registros:
            subconjunto.agregar_registro(registro)

        return subconjunto


class DataSetClasificacion(DataSet):
    def agregar_registro(self, registro: RegistroClasificacion) -> None:
        if not isinstance(registro, RegistroClasificacion):
            raise TypeError("DataSetClasificacion solo admite objetos RegistroClasificacion.")
        self.registros.append(registro)


class DataSetRegresion(DataSet):
    def agregar_registro(self, registro: RegistroRegresion) -> None:
        if not isinstance(registro, RegistroRegresion):
            raise TypeError("DataSetRegresion solo admite objetos RegistroRegresion.")
        self.registros.append(registro)
