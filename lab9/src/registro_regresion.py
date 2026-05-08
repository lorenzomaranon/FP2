from __future__ import annotations

from registro import Registro


class RegistroRegresion(Registro):
    def __init__(self, datos: list[float], objetivo: float) -> None:
        super().__init__(datos)
        self.objetivo = float(objetivo)

