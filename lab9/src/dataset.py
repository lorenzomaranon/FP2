from __future__ import annotations


class DataSet:
    def __init__(self) -> None:
        self.registros = []
        self.nombres_atributos: list[str] = []
        self.nombre_objetivo: str = "objetivo"

    def establecer_cabeceras(
        self,
        nombres_atributos: list[str],
        nombre_objetivo: str = "objetivo",
    ) -> None:
        self.nombres_atributos = [str(nombre) for nombre in nombres_atributos]
        self.nombre_objetivo = str(nombre_objetivo)

    def __len__(self) -> int:
        return len(self.registros)

