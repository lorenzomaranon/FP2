from __future__ import annotations

from pathlib import Path

from calculadora_pesos_correlacion import CalculadoraPesosCorrelacion
from escalador_min_max import EscaladorMinMax
from escalador_z_score import EscaladorZScore
from escritor_resultados import EscritorResultados
from evaluador_mae import EvaluadorMAE
from factoria_serie_temporal import FactoriaSerieTemporal
from objetivo_mae_knn import ObjetivoMAEKNN
from optimizador_evolucion_diferencial import OptimizadorEvolucionDiferencial
from predictor_serie_temporal import PredictorSerieTemporal
from regresor_knn import RegresorKNN
from regresor_lineal import RegresorLineal
from resultado_experimento import ResultadoExperimento


class Laboratorio9App:
    def __init__(self, data_dir: str | Path, output_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.factoria = FactoriaSerieTemporal()
        self.predictor = PredictorSerieTemporal()
        self.evaluador = EvaluadorMAE()
        self.calculadora_pesos = CalculadoraPesosCorrelacion()
        self.escritor = EscritorResultados()
        self.max_registros_entrenamiento = 1000
        self.horizonte = 24

    def ejecutar(self) -> None:
        ruta_train = self.data_dir / "serie_temporal_alumnos.xlsx"
        ruta_test = self.data_dir / "serie_temporal_test.xlsx"

        serie_train = self.factoria.leer_excel(ruta_train)
        serie_test = self.factoria.leer_excel(ruta_test)
        valores_test = serie_test.primeros_valores(self.horizonte)
        fechas_test = serie_test.primeras_fechas(self.horizonte)

        resultados_lineales = self._ejecutar_recta_regresion(serie_train, valores_test)
        mejor_lineal = min(resultados_lineales, key=lambda resultado: resultado.mae_validacion)
        mejor_lineal_test = min(resultados_lineales, key=lambda resultado: resultado.mae_test)

        resultados_knn_correlacion = self._ejecutar_knn_correlacion(serie_train, valores_test)
        mejor_knn_correlacion = min(
            resultados_knn_correlacion,
            key=lambda resultado: resultado.mae_validacion,
        )
        mejor_knn_correlacion_test = min(
            resultados_knn_correlacion,
            key=lambda resultado: resultado.mae_test,
        )

        resultados_knn_heuristicos = self._ejecutar_knn_heuristico(
            serie_train,
            valores_test,
            mejor_knn_correlacion.ph,
        )
        mejor_knn_heuristico = min(
            resultados_knn_heuristicos,
            key=lambda resultado: resultado.mae_validacion,
        )
        mejor_knn_heuristico_test = min(
            resultados_knn_heuristicos,
            key=lambda resultado: resultado.mae_test,
        )

        ruta_resumen = self.output_dir / "resultados_lab9.txt"
        ruta_predicciones = self.output_dir / "predicciones_lab9.csv"

        self.escritor.guardar_resumen(
            ruta_resumen,
            resultados_lineales,
            resultados_knn_correlacion,
            resultados_knn_heuristicos,
            mejor_lineal,
            mejor_knn_correlacion,
            mejor_knn_heuristico,
        )
        self.escritor.guardar_predicciones(
            ruta_predicciones,
            fechas_test,
            valores_test,
            mejor_lineal,
            mejor_knn_correlacion,
            mejor_knn_heuristico,
        )

        print("Resultados guardados en:")
        print(f"  {ruta_resumen}")
        print(f"  {ruta_predicciones}")
        print("")
        print(
            "Mejor recta segun validacion: "
            f"PH={mejor_lineal.ph}, lr={mejor_lineal.tasa_aprendizaje}, "
            f"normalizacion={mejor_lineal.normalizacion}, "
            f"MAE test={mejor_lineal.mae_test:.6f}"
        )
        print(
            "Mejor MAE test en recta: "
            f"PH={mejor_lineal_test.ph}, lr={mejor_lineal_test.tasa_aprendizaje}, "
            f"normalizacion={mejor_lineal_test.normalizacion}, "
            f"MAE test={mejor_lineal_test.mae_test:.6f}"
        )
        print(
            "Mejor kNN correlacion segun validacion: "
            f"PH={mejor_knn_correlacion.ph}, k={mejor_knn_correlacion.k}, "
            f"MAE test={mejor_knn_correlacion.mae_test:.6f}"
        )
        print(
            "Mejor MAE test en kNN correlacion: "
            f"PH={mejor_knn_correlacion_test.ph}, k={mejor_knn_correlacion_test.k}, "
            f"MAE test={mejor_knn_correlacion_test.mae_test:.6f}"
        )
        print(
            "Mejor kNN heuristica segun validacion: "
            f"PH={mejor_knn_heuristico.ph}, k={mejor_knn_heuristico.k}, "
            f"MAE test={mejor_knn_heuristico.mae_test:.6f}"
        )
        print(
            "Mejor MAE test en kNN heuristica: "
            f"PH={mejor_knn_heuristico_test.ph}, k={mejor_knn_heuristico_test.k}, "
            f"MAE test={mejor_knn_heuristico_test.mae_test:.6f}"
        )

    def _ejecutar_recta_regresion(
        self,
        serie_train,
        valores_test: list[float],
    ) -> list[ResultadoExperimento]:
        configuraciones = [
            {"ph": 12, "tasa": 0.0000001, "normalizacion": "ninguna", "iteraciones": 2500},
            {"ph": 24, "tasa": 0.0000001, "normalizacion": "ninguna", "iteraciones": 2500},
            {"ph": 12, "tasa": 0.03, "normalizacion": "minmax", "iteraciones": 1500},
            {"ph": 24, "tasa": 0.03, "normalizacion": "minmax", "iteraciones": 1500},
            {"ph": 12, "tasa": 0.05, "normalizacion": "zscore", "iteraciones": 1500},
            {"ph": 24, "tasa": 0.05, "normalizacion": "zscore", "iteraciones": 1500},
        ]

        resultados: list[ResultadoExperimento] = []

        for configuracion in configuraciones:
            ph = int(configuracion["ph"])
            dataset_validacion = self._dataset_para_validacion(serie_train, ph)
            modelo_validacion = self._crear_regresor_lineal(configuracion)
            modelo_validacion.entrenar(dataset_validacion)
            predicciones_validacion = self.predictor.predecir(
                modelo_validacion,
                serie_train.sin_ultimos(self.horizonte).ultimos_valores(ph),
                ph,
                self.horizonte,
            )
            reales_validacion = serie_train.ultimos_valores(self.horizonte)
            mae_validacion = self.evaluador.calcular(reales_validacion, predicciones_validacion)

            dataset_test = self._dataset_para_test(serie_train, ph)
            modelo_test = self._crear_regresor_lineal(configuracion)
            modelo_test.entrenar(dataset_test)
            predicciones_test = self.predictor.predecir(
                modelo_test,
                serie_train.ultimos_valores(ph),
                ph,
                self.horizonte,
            )
            mae_test = self.evaluador.calcular(valores_test, predicciones_test)

            resultados.append(
                ResultadoExperimento(
                    modelo="recta_regresion",
                    ph=ph,
                    mae_validacion=mae_validacion,
                    mae_test=mae_test,
                    tasa_aprendizaje=float(configuracion["tasa"]),
                    normalizacion=str(configuracion["normalizacion"]),
                    predicciones_test=predicciones_test,
                )
            )

        return resultados

    def _ejecutar_knn_correlacion(
        self,
        serie_train,
        valores_test: list[float],
    ) -> list[ResultadoExperimento]:
        resultados: list[ResultadoExperimento] = []

        for ph in (6, 12, 24, 48):
            for k in (1, 3, 5):
                dataset_validacion = self._dataset_para_validacion(serie_train, ph)
                pesos_validacion = self.calculadora_pesos.calcular(dataset_validacion)
                modelo_validacion = RegresorKNN(k, pesos=pesos_validacion)
                modelo_validacion.entrenar(dataset_validacion)
                predicciones_validacion = self.predictor.predecir(
                    modelo_validacion,
                    serie_train.sin_ultimos(self.horizonte).ultimos_valores(ph),
                    ph,
                    self.horizonte,
                )
                reales_validacion = serie_train.ultimos_valores(self.horizonte)
                mae_validacion = self.evaluador.calcular(reales_validacion, predicciones_validacion)

                dataset_test = self._dataset_para_test(serie_train, ph)
                pesos_test = self.calculadora_pesos.calcular(dataset_test)
                modelo_test = RegresorKNN(k, pesos=pesos_test)
                modelo_test.entrenar(dataset_test)
                predicciones_test = self.predictor.predecir(
                    modelo_test,
                    serie_train.ultimos_valores(ph),
                    ph,
                    self.horizonte,
                )
                mae_test = self.evaluador.calcular(valores_test, predicciones_test)

                resultados.append(
                    ResultadoExperimento(
                        modelo="knn_correlacion",
                        ph=ph,
                        mae_validacion=mae_validacion,
                        mae_test=mae_test,
                        k=k,
                        estrategia_pesos="correlacion",
                        pesos=pesos_test,
                        predicciones_test=predicciones_test,
                    )
                )

        return resultados

    def _ejecutar_knn_heuristico(
        self,
        serie_train,
        valores_test: list[float],
        ph: int,
    ) -> list[ResultadoExperimento]:
        resultados: list[ResultadoExperimento] = []

        dataset_validacion = self._dataset_para_validacion(serie_train, ph)
        pesos_iniciales = self.calculadora_pesos.calcular(dataset_validacion)
        objetivo = ObjetivoMAEKNN(
            dataset_entrenamiento=dataset_validacion,
            historial_inicial=serie_train.sin_ultimos(self.horizonte).ultimos_valores(ph),
            valores_reales=serie_train.ultimos_valores(self.horizonte),
            ph=ph,
            k=1,
        )

        for k in (1, 3, 5):
            objetivo.k = k
            optimizador = OptimizadorEvolucionDiferencial(
                dimension=ph,
                limite_inferior=0.0,
                limite_superior=2.0,
                tam_poblacion=6,
                generaciones=4,
                factor_mutacion=0.7,
                tasa_cruce=0.8,
                semilla=2026 + k + ph,
            )
            mejores_pesos, mae_validacion = optimizador.optimizar(
                objetivo.evaluar,
                solucion_inicial=pesos_iniciales,
            )

            dataset_test = self._dataset_para_test(serie_train, ph)
            modelo_test = RegresorKNN(k, pesos=mejores_pesos)
            modelo_test.entrenar(dataset_test)
            predicciones_test = self.predictor.predecir(
                modelo_test,
                serie_train.ultimos_valores(ph),
                ph,
                self.horizonte,
            )
            mae_test = self.evaluador.calcular(valores_test, predicciones_test)

            resultados.append(
                ResultadoExperimento(
                    modelo="knn_heuristica",
                    ph=ph,
                    mae_validacion=mae_validacion,
                    mae_test=mae_test,
                    k=k,
                    estrategia_pesos="evolucion_diferencial",
                    pesos=mejores_pesos,
                    predicciones_test=predicciones_test,
                )
            )

        return resultados

    def _crear_regresor_lineal(self, configuracion: dict) -> RegresorLineal:
        normalizacion = str(configuracion["normalizacion"])
        normalizador_entradas = None
        normalizador_objetivo = None

        if normalizacion == "minmax":
            normalizador_entradas = EscaladorMinMax()
            normalizador_objetivo = EscaladorMinMax()
        elif normalizacion == "zscore":
            normalizador_entradas = EscaladorZScore()
            normalizador_objetivo = EscaladorZScore()

        return RegresorLineal(
            tasa_aprendizaje=float(configuracion["tasa"]),
            iteraciones=int(configuracion["iteraciones"]),
            normalizador_entradas=normalizador_entradas,
            normalizador_objetivo=normalizador_objetivo,
        )

    def _dataset_para_validacion(self, serie_train, ph: int):
        serie_base = serie_train.sin_ultimos(self.horizonte)
        return self.factoria.crear_dataset_regresion_desde_serie(
            serie_base,
            ph,
            max_registros=self.max_registros_entrenamiento,
        )

    def _dataset_para_test(self, serie_train, ph: int):
        return self.factoria.crear_dataset_regresion_desde_serie(
            serie_train,
            ph,
            max_registros=self.max_registros_entrenamiento,
        )
