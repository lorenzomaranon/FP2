from __future__ import annotations

import csv
from pathlib import Path

from datos_sensores import DatosSensores


class FactoriaDatosSensores:
    def leer_csv(self, ruta_csv: str | Path) -> DatosSensores:
        ruta = Path(ruta_csv)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el fichero: {ruta}")

        with ruta.open("r", encoding="utf-8-sig", newline="") as fichero:
            lector = csv.DictReader(fichero)
            if lector.fieldnames is None:
                raise ValueError("El CSV no contiene cabecera.")

            nombres_variables = [
                nombre for nombre in lector.fieldnames if nombre != "Minuto"
            ]
            datos = {nombre: [] for nombre in nombres_variables}
            minutos: list[int] = []

            for fila in lector:
                minutos.append(int(float(fila["Minuto"])))
                for nombre in nombres_variables:
                    datos[nombre].append(float(fila[nombre]))

        return DatosSensores(minutos, datos)
