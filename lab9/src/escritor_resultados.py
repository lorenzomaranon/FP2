from __future__ import annotations

import csv
from pathlib import Path

from resultado_experimento import ResultadoExperimento


class EscritorResultados:
    def guardar_resumen(
        self,
        ruta_salida: str | Path,
        resultados_lineales: list[ResultadoExperimento],
        resultados_knn_correlacion: list[ResultadoExperimento],
        resultados_knn_heuristicos: list[ResultadoExperimento],
        mejor_lineal: ResultadoExperimento,
        mejor_knn_correlacion: ResultadoExperimento,
        mejor_knn_heuristico: ResultadoExperimento,
    ) -> None:
        ruta = Path(ruta_salida)
        lineas: list[str] = []
        mejor_lineal_test = min(resultados_lineales, key=lambda resultado: resultado.mae_test)
        mejor_knn_correlacion_test = min(
            resultados_knn_correlacion,
            key=lambda resultado: resultado.mae_test,
        )
        mejor_knn_heuristico_test = min(
            resultados_knn_heuristicos,
            key=lambda resultado: resultado.mae_test,
        )

        lineas.append("LABORATORIO 9 - PREDICCION DE SERIES TEMPORALES")
        lineas.append("")
        lineas.append("Criterio de seleccion del mejor modelo: MAE de validacion temporal interna")
        lineas.append("Validacion interna: ultimas 24 horas del 28/12/2026")
        lineas.append("Metrica entregable: MAE sobre FH=24 del 29/12/2026")
        lineas.append("")

        lineas.append("RECTA DE REGRESION")
        lineas.append(self._tabla_recta_regresion(resultados_lineales))
        lineas.append("")
        lineas.append(
            "Mejor recta segun validacion: "
            f"PH={mejor_lineal.ph}, lr={self._texto(mejor_lineal.tasa_aprendizaje)}, "
            f"normalizacion={self._texto(mejor_lineal.normalizacion)}, "
            f"MAE validacion={mejor_lineal.mae_validacion:.6f}, "
            f"MAE test={mejor_lineal.mae_test:.6f}"
        )
        lineas.append(
            "Mejor MAE test en recta: "
            f"PH={mejor_lineal_test.ph}, lr={self._texto(mejor_lineal_test.tasa_aprendizaje)}, "
            f"normalizacion={self._texto(mejor_lineal_test.normalizacion)}, "
            f"MAE test={mejor_lineal_test.mae_test:.6f}"
        )
        lineas.append("")

        lineas.append("KNN PONDERADO CON CORRELACION")
        lineas.append(self._tabla_knn(resultados_knn_correlacion))
        lineas.append("")
        lineas.append(
            "Mejor kNN con correlacion segun validacion: "
            f"PH={mejor_knn_correlacion.ph}, k={self._texto(mejor_knn_correlacion.k)}, "
            f"MAE validacion={mejor_knn_correlacion.mae_validacion:.6f}, "
            f"MAE test={mejor_knn_correlacion.mae_test:.6f}"
        )
        lineas.append(
            "Mejor MAE test en kNN con correlacion: "
            f"PH={mejor_knn_correlacion_test.ph}, k={self._texto(mejor_knn_correlacion_test.k)}, "
            f"MAE test={mejor_knn_correlacion_test.mae_test:.6f}"
        )
        lineas.append("")

        lineas.append("KNN CON HEURISTICA")
        lineas.append(self._tabla_knn(resultados_knn_heuristicos))
        lineas.append("")
        lineas.append(
            "Mejor kNN con heuristica segun validacion: "
            f"PH={mejor_knn_heuristico.ph}, k={self._texto(mejor_knn_heuristico.k)}, "
            f"MAE validacion={mejor_knn_heuristico.mae_validacion:.6f}, "
            f"MAE test={mejor_knn_heuristico.mae_test:.6f}"
        )
        lineas.append(
            "Mejor MAE test en kNN con heuristica: "
            f"PH={mejor_knn_heuristico_test.ph}, k={self._texto(mejor_knn_heuristico_test.k)}, "
            f"MAE test={mejor_knn_heuristico_test.mae_test:.6f}"
        )

        ruta.write_text("\n".join(lineas), encoding="utf-8")

    def guardar_predicciones(
        self,
        ruta_salida: str | Path,
        fechas: list,
        reales: list[float],
        mejor_lineal: ResultadoExperimento,
        mejor_knn_correlacion: ResultadoExperimento,
        mejor_knn_heuristico: ResultadoExperimento,
    ) -> None:
        ruta = Path(ruta_salida)

        with ruta.open("w", encoding="utf-8", newline="") as descriptor:
            escritor = csv.writer(descriptor)
            escritor.writerow(
                [
                    "fecha",
                    "valor_real",
                    "pred_recta_mejor",
                    "pred_knn_correlacion_mejor",
                    "pred_knn_heuristica_mejor",
                ]
            )

            for indice, fecha in enumerate(fechas):
                escritor.writerow(
                    [
                        fecha,
                        reales[indice],
                        mejor_lineal.predicciones_test[indice],
                        mejor_knn_correlacion.predicciones_test[indice],
                        mejor_knn_heuristico.predicciones_test[indice],
                    ]
                )

    def _tabla_recta_regresion(self, resultados: list[ResultadoExperimento]) -> str:
        cabecera = (
            f"{'PH':>4} {'Tasa':>12} {'Min-Max':>8} {'Z-Score':>8} "
            f"{'MAE val':>12} {'MAE test':>12}"
        )
        filas = [cabecera]

        for resultado in resultados:
            usa_min_max = "Si" if resultado.normalizacion == "minmax" else "No"
            usa_z_score = "Si" if resultado.normalizacion == "zscore" else "No"
            filas.append(
                f"{resultado.ph:>4} {self._texto(resultado.tasa_aprendizaje):>12} "
                f"{usa_min_max:>8} {usa_z_score:>8} "
                f"{resultado.mae_validacion:>12.6f} {resultado.mae_test:>12.6f}"
            )

        return "\n".join(filas)

    def _tabla_knn(self, resultados: list[ResultadoExperimento]) -> str:
        cabecera = f"{'PH':>4} {'K':>4} {'MAE val':>12} {'MAE test':>12}"
        filas = [cabecera]

        for resultado in resultados:
            filas.append(
                f"{resultado.ph:>4} {self._texto(resultado.k):>4} "
                f"{resultado.mae_validacion:>12.6f} {resultado.mae_test:>12.6f}"
            )

        return "\n".join(filas)

    def _texto(self, valor) -> str:
        if valor is None:
            return "-"
        return str(valor)
