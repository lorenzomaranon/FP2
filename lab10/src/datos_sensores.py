from __future__ import annotations


class DatosSensores:
    def __init__(self, minutos: list[int], datos: dict[str, list[float]]) -> None:
        if not minutos:
            raise ValueError("La lista de minutos no puede estar vacia.")

        total = len(minutos)
        for nombre, valores in datos.items():
            if len(valores) != total:
                raise ValueError(
                    f"La variable {nombre} no tiene el mismo tamano que Minuto.",
                )

        self.minutos = minutos[:]
        self.datos = {nombre: valores[:] for nombre, valores in datos.items()}

    def nombres_variables(self) -> list[str]:
        return list(self.datos.keys())

    def total_muestras(self) -> int:
        return len(self.minutos)

    def valores_variable(self, nombre: str) -> list[float]:
        if nombre not in self.datos:
            raise KeyError(f"No existe la variable {nombre}.")
        return self.datos[nombre][:]

    def segmento_variable(self, nombre: str, inicio: int, fin: int) -> list[float]:
        return self.valores_variable(nombre)[inicio:fin]

    def rango_dia(self, dia: int, minutos_por_dia: int = 1440) -> tuple[int, int]:
        if dia <= 0:
            raise ValueError("El dia debe empezar en 1.")
        inicio = (dia - 1) * minutos_por_dia
        fin = inicio + minutos_por_dia
        if inicio >= self.total_muestras():
            raise ValueError(f"El dia {dia} queda fuera de los datos.")
        return inicio, min(fin, self.total_muestras())
