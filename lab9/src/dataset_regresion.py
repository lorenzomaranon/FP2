from __future__ import annotations

from dataset import DataSet
from registro_regresion import RegistroRegresion


class DataSetRegresion(DataSet):
    def agregar_registro(self, registro: RegistroRegresion) -> None:
        if not isinstance(registro, RegistroRegresion):
            raise TypeError("DataSetRegresion solo admite objetos RegistroRegresion.")
        self.registros.append(registro)

    def ultimos_registros(self, cantidad: int | None) -> "DataSetRegresion":
        if cantidad is None or cantidad >= len(self.registros):
            registros_seleccionados = self.registros
        else:
            registros_seleccionados = self.registros[-cantidad:]

        nuevo_dataset = DataSetRegresion()
        nuevo_dataset.nombres_atributos = self.nombres_atributos[:]
        nuevo_dataset.nombre_objetivo = self.nombre_objetivo

        for registro in registros_seleccionados:
            nuevo_dataset.agregar_registro(registro)

        return nuevo_dataset

    def matriz_atributos(self) -> list[list[float]]:
        return [registro.datos[:] for registro in self.registros]

    def objetivos(self) -> list[float]:
        return [float(registro.objetivo) for registro in self.registros]

