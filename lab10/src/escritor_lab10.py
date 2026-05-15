from __future__ import annotations

from pathlib import Path


class EscritorLab10:
    def guardar_resumen_prediccion(
        self,
        ruta: str | Path,
        resultados: dict[str, list],
    ) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        with ruta.open("w", encoding="utf-8") as fichero:
            fichero.write("LABORATORIO 10 - SERIES DE DIFERENCIAS\n\n")
            fichero.write(
                "Los MAE se calculan sobre la serie original reconstruida, "
                "no sobre la serie de diferencias.\n\n"
            )

            self._escribir_tabla_recta(fichero, resultados["recta_regresion"])
            self._escribir_tabla_knn(
                fichero,
                "KNN PONDERADO CON CORRELACION SOBRE DIFERENCIAS",
                resultados["knn_correlacion"],
            )
            self._escribir_tabla_knn(
                fichero,
                "KNN CON HEURISTICA SOBRE DIFERENCIAS",
                resultados["knn_heuristica"],
            )
            self._escribir_comparacion_mejores(fichero, resultados)

    def guardar_tabla_markdown(
        self,
        ruta: str | Path,
        resultados: dict[str, list],
    ) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        with ruta.open("w", encoding="utf-8") as fichero:
            fichero.write("# Laboratorio 10 - Resultados\n\n")
            fichero.write("## Comparacion de mejores modelos\n\n")
            fichero.write(
                "| Modelo | Mejor lab9 original | MAE lab9 | "
                "Mejor lab10 diferencias | MAE lab10 | Mejora? |\n"
            )
            fichero.write("|---|---:|---:|---:|---:|:---:|\n")
            for fila in self._filas_comparacion_mejores(resultados):
                fichero.write(
                    f"| {fila['modelo']} | {fila['config_original']} | "
                    f"{self._formatear(fila['mae_original'])} | "
                    f"{fila['config_diferencias']} | "
                    f"{self._formatear(fila['mae_diferencias'])} | "
                    f"{fila['mejora']} |\n"
                )

    def guardar_predicciones(
        self,
        ruta: str | Path,
        fechas: list,
        valores_reales: list[float],
        resultados: dict[str, list],
    ) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        mejores = self._mejores_por_modelo(resultados)

        with ruta.open("w", encoding="utf-8") as fichero:
            fichero.write(
                "Fecha,Real,Recta_diferencias,KNN_correlacion_diferencias,"
                "KNN_heuristica_diferencias\n",
            )
            for indice, real in enumerate(valores_reales):
                fila = [
                    str(fechas[indice]),
                    f"{float(real):.10f}",
                    f"{mejores['recta_regresion'].predicciones_test[indice]:.10f}",
                    f"{mejores['knn_correlacion'].predicciones_test[indice]:.10f}",
                    f"{mejores['knn_heuristica'].predicciones_test[indice]:.10f}",
                ]
                fichero.write(",".join(fila) + "\n")

    def guardar_anomalias(
        self,
        ruta: str | Path,
        pares: list[tuple[str, str]],
        resultados_anomalias: list[dict],
        graficas: list[Path],
    ) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        with ruta.open("w", encoding="utf-8") as fichero:
            fichero.write("LABORATORIO 10 - DETECCION DE ANOMALIAS\n\n")
            fichero.write(f"Pares correlacionados en el dia 1: {len(pares)}\n")
            for nombre1, nombre2 in pares:
                fichero.write(f"  - {nombre1} / {nombre2}\n")
            fichero.write("\nGraficas exportadas:\n")
            for ruta_grafica in graficas:
                fichero.write(f"  - {ruta_grafica}\n")

            for configuracion in resultados_anomalias:
                fichero.write("\n")
                fichero.write(
                    "Umbral ruptura="
                    f"{configuracion['umbral_ruptura']}, "
                    "separacion="
                    f"{configuracion['separacion_maxima']}, "
                    "duracion_minima="
                    f"{configuracion['duracion_minima']}\n"
                )
                for dia, intervalos_por_par in configuracion["dias"].items():
                    total_intervalos = sum(
                        len(intervalos)
                        for intervalos in intervalos_por_par.values()
                    )
                    fichero.write(
                        f"  Dia {dia}: {total_intervalos} intervalos detectados\n",
                    )
                    if total_intervalos == 0:
                        continue
                    for par, intervalos in intervalos_por_par.items():
                        texto_intervalos = ", ".join(
                            f"{inicio}-{fin}" for inicio, fin in intervalos
                        )
                        fichero.write(
                            f"    {par[0]} / {par[1]}: {texto_intervalos}\n",
                        )

    def _escribir_tabla_recta(self, fichero, resultados: list) -> None:
        fichero.write("RECTA DE REGRESION SOBRE DIFERENCIAS\n")
        fichero.write(
            f"{'PH':>4} {'Tasa':>12} {'Normalizacion':>15} "
            f"{'MAE val':>12} {'MAE test':>12} {'MAE lab9':>12}\n"
        )
        for resultado in resultados:
            mae_original = self._mae_lab9_configuracion(resultado)
            fichero.write(
                f"{resultado.ph:>4} {resultado.tasa_aprendizaje:>12g} "
                f"{resultado.normalizacion:>15} "
                f"{resultado.mae_validacion:>12.6f} "
                f"{resultado.mae_test:>12.6f} "
                f"{self._formatear(mae_original):>12}\n"
            )
        fichero.write("\n")

    def _escribir_tabla_knn(self, fichero, titulo: str, resultados: list) -> None:
        fichero.write(titulo + "\n")
        fichero.write(
            f"{'PH':>4} {'K':>4} {'MAE val':>12} "
            f"{'MAE test':>12} {'MAE lab9':>12}\n"
        )
        for resultado in resultados:
            mae_original = self._mae_lab9_configuracion(resultado)
            fichero.write(
                f"{resultado.ph:>4} {resultado.k:>4} "
                f"{resultado.mae_validacion:>12.6f} "
                f"{resultado.mae_test:>12.6f} "
                f"{self._formatear(mae_original):>12}\n"
            )
        fichero.write("\n")

    def _escribir_comparacion_mejores(self, fichero, resultados: dict[str, list]) -> None:
        fichero.write("COMPARACION DE MEJORES MODELOS POR VALIDACION\n")
        fichero.write(
            f"{'Modelo':<22} {'Original lab9':>18} {'MAE lab9':>12} "
            f"{'Diferencias':>22} {'MAE lab10':>12} {'Mejora':>8}\n"
        )
        for fila in self._filas_comparacion_mejores(resultados):
            fichero.write(
                f"{fila['modelo']:<22} {fila['config_original']:>18} "
                f"{self._formatear(fila['mae_original']):>12} "
                f"{fila['config_diferencias']:>22} "
                f"{self._formatear(fila['mae_diferencias']):>12} "
                f"{fila['mejora']:>8}\n"
            )
        fichero.write("\n")

    def _mejores_por_modelo(self, resultados: dict[str, list]) -> dict[str, object]:
        return {
            clave: min(lista, key=lambda resultado: resultado.mae_validacion)
            for clave, lista in resultados.items()
        }

    def _filas_comparacion_mejores(self, resultados: dict[str, list]) -> list[dict]:
        mejores = self._mejores_por_modelo(resultados)
        originales = {
            "recta_regresion": ("PH=12, lr=0.05, zscore", 14.041879),
            "knn_correlacion": ("PH=48, k=5", 6.845120),
            "knn_heuristica": ("PH=48, k=5", 6.491298),
        }
        nombres = {
            "recta_regresion": "Recta regresion",
            "knn_correlacion": "kNN correlacion",
            "knn_heuristica": "kNN heuristica",
        }
        filas: list[dict] = []

        for clave, resultado in mejores.items():
            configuracion_original, mae_original = originales[clave]
            mae_diferencias = resultado.mae_test
            filas.append(
                {
                    "modelo": nombres[clave],
                    "config_original": configuracion_original,
                    "mae_original": mae_original,
                    "config_diferencias": self._configuracion(resultado),
                    "mae_diferencias": mae_diferencias,
                    "mejora": "Si" if mae_diferencias < mae_original else "No",
                },
            )

        return filas

    def _mae_lab9_configuracion(self, resultado) -> float | None:
        mapa = {
            ("recta_regresion_diferencias", 12, "1e-07", "ninguna", None): 16.807851,
            ("recta_regresion_diferencias", 24, "1e-07", "ninguna", None): 13.816402,
            ("recta_regresion_diferencias", 12, "0.03", "minmax", None): 14.305248,
            ("recta_regresion_diferencias", 24, "0.03", "minmax", None): 12.093180,
            ("recta_regresion_diferencias", 12, "0.05", "zscore", None): 14.041879,
            ("recta_regresion_diferencias", 24, "0.05", "zscore", None): 8.826340,
            ("knn_correlacion_diferencias", 6, None, None, 1): 21.460553,
            ("knn_correlacion_diferencias", 6, None, None, 3): 24.942604,
            ("knn_correlacion_diferencias", 6, None, None, 5): 21.023249,
            ("knn_correlacion_diferencias", 12, None, None, 1): 21.460553,
            ("knn_correlacion_diferencias", 12, None, None, 3): 22.220398,
            ("knn_correlacion_diferencias", 12, None, None, 5): 18.774739,
            ("knn_correlacion_diferencias", 24, None, None, 1): 6.418939,
            ("knn_correlacion_diferencias", 24, None, None, 3): 20.264276,
            ("knn_correlacion_diferencias", 24, None, None, 5): 19.523289,
            ("knn_correlacion_diferencias", 48, None, None, 1): 6.418939,
            ("knn_correlacion_diferencias", 48, None, None, 3): 6.231750,
            ("knn_correlacion_diferencias", 48, None, None, 5): 6.845120,
            ("knn_heuristica_diferencias", 48, None, None, 1): 9.675892,
            ("knn_heuristica_diferencias", 48, None, None, 3): 6.275080,
            ("knn_heuristica_diferencias", 48, None, None, 5): 6.491298,
        }
        tasa = None
        if resultado.tasa_aprendizaje is not None:
            tasa = f"{resultado.tasa_aprendizaje:g}"
        clave = (
            resultado.modelo,
            resultado.ph,
            tasa,
            resultado.normalizacion,
            resultado.k,
        )
        return mapa.get(clave)

    def _configuracion(self, resultado) -> str:
        if resultado.tasa_aprendizaje is not None:
            return (
                f"PH={resultado.ph}, lr={resultado.tasa_aprendizaje:g}, "
                f"{resultado.normalizacion}"
            )
        return f"PH={resultado.ph}, k={resultado.k}"

    def _formatear(self, valor: float | None) -> str:
        if valor is None:
            return "-"
        return f"{float(valor):.6f}"
