from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from datos_sensores import DatosSensores
from transformador_diferencias import TransformadorDiferencias


class GraficadorSeries:
    def __init__(self) -> None:
        self.transformador = TransformadorDiferencias()

    def graficar_series_originales(
        self,
        datos: DatosSensores,
        salida_dir: str | Path,
        variables_por_grafica: int = 4,
    ) -> list[Path]:
        return self._graficar(
            datos,
            salida_dir,
            variables_por_grafica,
            usar_diferencias=False,
            prefijo="series_originales",
            titulo_base="Series originales",
        )

    def graficar_series_diferencias(
        self,
        datos: DatosSensores,
        salida_dir: str | Path,
        variables_por_grafica: int = 4,
    ) -> list[Path]:
        return self._graficar(
            datos,
            salida_dir,
            variables_por_grafica,
            usar_diferencias=True,
            prefijo="series_diferencias",
            titulo_base="Series de diferencias",
        )

    def _graficar(
        self,
        datos: DatosSensores,
        salida_dir: str | Path,
        variables_por_grafica: int,
        usar_diferencias: bool,
        prefijo: str,
        titulo_base: str,
    ) -> list[Path]:
        salida = Path(salida_dir)
        salida.mkdir(parents=True, exist_ok=True)
        nombres = datos.nombres_variables()
        rutas: list[Path] = []

        for indice in range(0, len(nombres), variables_por_grafica):
            grupo = nombres[indice : indice + variables_por_grafica]
            figura, eje = plt.subplots(figsize=(13, 6))

            for nombre in grupo:
                valores = datos.valores_variable(nombre)
                minutos = datos.minutos
                if usar_diferencias:
                    valores = self.transformador.calcular_diferencias(valores)
                    minutos = minutos[1:]
                eje.plot(minutos, valores, linewidth=0.9, label=nombre)

            for limite in (1440, 2880, 4320):
                eje.axvline(limite, color="#666666", linestyle="--", linewidth=0.8)

            eje.set_title(f"{titulo_base} - grupo {indice // variables_por_grafica + 1}")
            eje.set_xlabel("Minuto")
            eje.set_ylabel("Valor")
            eje.grid(True, alpha=0.25)
            eje.legend(loc="best", fontsize=8)
            figura.tight_layout()

            ruta = salida / f"{prefijo}_grupo_{indice // variables_por_grafica + 1:02d}.png"
            figura.savefig(ruta, dpi=150)
            plt.close(figura)
            rutas.append(ruta)

        return rutas
