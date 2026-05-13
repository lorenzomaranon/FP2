from __future__ import annotations


class ObservacionSerieTemporal:
    def __init__(self, fecha, valor: float) -> None:
        self.fecha = fecha
        self.valor = float(valor)

