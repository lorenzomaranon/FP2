from __future__ import annotations

import sys
from pathlib import Path

LAB9_SRC = Path(__file__).resolve().parents[2] / "lab9" / "src"
if str(LAB9_SRC) not in sys.path:
    sys.path.append(str(LAB9_SRC))

from calculadora_pesos_correlacion import CalculadoraPesosCorrelacion
from escalador_min_max import EscaladorMinMax
from escalador_z_score import EscaladorZScore
from evaluador_mae import EvaluadorMAE
from factoria_serie_temporal import FactoriaSerieTemporal
from observacion_serie_temporal import ObservacionSerieTemporal
from optimizador_evolucion_diferencial import OptimizadorEvolucionDiferencial
from predictor_serie_temporal import PredictorSerieTemporal
from regresor_knn import RegresorKNN
from resultado_experimento import ResultadoExperimento
from serie_temporal import SerieTemporal

from objetivo_mae_diferencias_knn import ObjetivoMAEDiferenciasKNN
from regresor_lineal_vectorizado import RegresorLinealVectorizado
from transformador_diferencias import TransformadorDiferencias


class ExperimentoPrediccionDiferencias:
    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.factoria = FactoriaSerieTemporal()
        self.predictor = PredictorSerieTemporal()
        self.evaluador = EvaluadorMAE()
        self.calculadora_pesos = CalculadoraPesosCorrelacion()
        self.transformador = TransformadorDiferencias()
        self.max_registros_entrenamiento = 1000
        self.horizonte = 24

    def ejecutar(self) -> dict[str, list[ResultadoExperimento]]:
        ruta_train = self.data_dir / "serie_temporal_alumnos.xlsx"
        ruta_test = self.data_dir / "serie_temporal_test.xlsx"

        serie_train = self.factoria.leer_excel(ruta_train)
        serie_test = self.factoria.leer_excel(ruta_test)
        valores_test = serie_test.primeros_valores(self.horizonte)

        resultados_lineales = self._ejecutar_recta_regresion(
            serie_train,
            valores_test,
        )
        resultados_knn_correlacion = self._ejecutar_knn_correlacion(
            serie_train,
            valores_test,
        )
        mejor_knn_correlacion = min(
            resultados_knn_correlacion,
            key=lambda resultado: resultado.mae_validacion,
        )
        resultados_knn_heuristicos = self._ejecutar_knn_heuristico(
            serie_train,
            valores_test,
            mejor_knn_correlacion.ph,
        )

        return {
            "recta_regresion": resultados_lineales,
            "knn_correlacion": resultados_knn_correlacion,
            "knn_heuristica": resultados_knn_heuristicos,
        }

    def fechas_test(self) -> list:
        ruta_test = self.data_dir / "serie_temporal_test.xlsx"
        serie_test = self.factoria.leer_excel(ruta_test)
        return serie_test.primeras_fechas(self.horizonte)

    def valores_test(self) -> list[float]:
        ruta_test = self.data_dir / "serie_temporal_test.xlsx"
        serie_test = self.factoria.leer_excel(ruta_test)
        return serie_test.primeros_valores(self.horizonte)

    def _ejecutar_recta_regresion(
        self,
        serie_train: SerieTemporal,
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
            modelo_validacion = self._crear_regresor_lineal(configuracion)
            mae_validacion, _ = self._evaluar_validacion(
                serie_train,
                ph,
                modelo_validacion,
            )

            modelo_test = self._crear_regresor_lineal(configuracion)
            mae_test, predicciones_test = self._evaluar_test(
                serie_train,
                valores_test,
                ph,
                modelo_test,
            )

            resultados.append(
                ResultadoExperimento(
                    modelo="recta_regresion_diferencias",
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
        serie_train: SerieTemporal,
        valores_test: list[float],
    ) -> list[ResultadoExperimento]:
        resultados: list[ResultadoExperimento] = []

        for ph in (6, 12, 24, 48):
            for k in (1, 3, 5):
                dataset_validacion, historial_validacion, inicial_validacion = (
                    self._datos_validacion_diferencias(serie_train, ph)
                )
                pesos_validacion = self.calculadora_pesos.calcular(dataset_validacion)
                modelo_validacion = RegresorKNN(k, pesos=pesos_validacion)
                mae_validacion, _ = self._evaluar_validacion(
                    serie_train,
                    ph,
                    modelo_validacion,
                    dataset_preparado=dataset_validacion,
                    historial_preparado=historial_validacion,
                    inicial_preparado=inicial_validacion,
                )

                dataset_test, historial_test, inicial_test = (
                    self._datos_test_diferencias(serie_train, ph)
                )
                pesos_test = self.calculadora_pesos.calcular(dataset_test)
                modelo_test = RegresorKNN(k, pesos=pesos_test)
                mae_test, predicciones_test = self._evaluar_test(
                    serie_train,
                    valores_test,
                    ph,
                    modelo_test,
                    dataset_preparado=dataset_test,
                    historial_preparado=historial_test,
                    inicial_preparado=inicial_test,
                )

                resultados.append(
                    ResultadoExperimento(
                        modelo="knn_correlacion_diferencias",
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
        serie_train: SerieTemporal,
        valores_test: list[float],
        ph: int,
    ) -> list[ResultadoExperimento]:
        resultados: list[ResultadoExperimento] = []
        dataset_validacion, historial_validacion, inicial_validacion = (
            self._datos_validacion_diferencias(serie_train, ph)
        )
        pesos_iniciales = self.calculadora_pesos.calcular(dataset_validacion)
        valores_validacion = serie_train.ultimos_valores(self.horizonte)

        objetivo = ObjetivoMAEDiferenciasKNN(
            dataset_entrenamiento=dataset_validacion,
            historial_diferencias=historial_validacion,
            valor_inicial_original=inicial_validacion,
            valores_reales_originales=valores_validacion,
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
                semilla=3026 + k + ph,
            )
            mejores_pesos, mae_validacion = optimizador.optimizar(
                objetivo.evaluar,
                solucion_inicial=pesos_iniciales,
            )

            dataset_test, historial_test, inicial_test = self._datos_test_diferencias(
                serie_train,
                ph,
            )
            modelo_test = RegresorKNN(k, pesos=mejores_pesos)
            mae_test, predicciones_test = self._evaluar_test(
                serie_train,
                valores_test,
                ph,
                modelo_test,
                dataset_preparado=dataset_test,
                historial_preparado=historial_test,
                inicial_preparado=inicial_test,
            )

            resultados.append(
                ResultadoExperimento(
                    modelo="knn_heuristica_diferencias",
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

    def _evaluar_validacion(
        self,
        serie_train: SerieTemporal,
        ph: int,
        modelo,
        dataset_preparado=None,
        historial_preparado: list[float] | None = None,
        inicial_preparado: float | None = None,
    ) -> tuple[float, list[float]]:
        if dataset_preparado is None or historial_preparado is None or inicial_preparado is None:
            dataset_preparado, historial_preparado, inicial_preparado = (
                self._datos_validacion_diferencias(serie_train, ph)
            )

        modelo.entrenar(dataset_preparado)
        predicciones_diferencias = self.predictor.predecir(
            modelo,
            historial_preparado,
            ph,
            self.horizonte,
        )
        predicciones_originales = self.transformador.reconstruir_desde_diferencias(
            inicial_preparado,
            predicciones_diferencias,
        )
        reales_validacion = serie_train.ultimos_valores(self.horizonte)
        mae_validacion = self.evaluador.calcular(
            reales_validacion,
            predicciones_originales,
        )
        return mae_validacion, predicciones_originales

    def _evaluar_test(
        self,
        serie_train: SerieTemporal,
        valores_test: list[float],
        ph: int,
        modelo,
        dataset_preparado=None,
        historial_preparado: list[float] | None = None,
        inicial_preparado: float | None = None,
    ) -> tuple[float, list[float]]:
        if dataset_preparado is None or historial_preparado is None or inicial_preparado is None:
            dataset_preparado, historial_preparado, inicial_preparado = (
                self._datos_test_diferencias(serie_train, ph)
            )

        modelo.entrenar(dataset_preparado)
        predicciones_diferencias = self.predictor.predecir(
            modelo,
            historial_preparado,
            ph,
            self.horizonte,
        )
        predicciones_originales = self.transformador.reconstruir_desde_diferencias(
            inicial_preparado,
            predicciones_diferencias,
        )
        mae_test = self.evaluador.calcular(valores_test, predicciones_originales)
        return mae_test, predicciones_originales

    def _datos_validacion_diferencias(self, serie_train: SerieTemporal, ph: int):
        serie_base = serie_train.sin_ultimos(self.horizonte)
        serie_diferencias = self._crear_serie_diferencias(serie_base)
        dataset = self.factoria.crear_dataset_regresion_desde_serie(
            serie_diferencias,
            ph,
            max_registros=self.max_registros_entrenamiento,
        )
        historial = serie_diferencias.ultimos_valores(ph)
        valor_inicial = serie_base.ultimos_valores(1)[0]
        return dataset, historial, valor_inicial

    def _datos_test_diferencias(self, serie_train: SerieTemporal, ph: int):
        serie_diferencias = self._crear_serie_diferencias(serie_train)
        dataset = self.factoria.crear_dataset_regresion_desde_serie(
            serie_diferencias,
            ph,
            max_registros=self.max_registros_entrenamiento,
        )
        historial = serie_diferencias.ultimos_valores(ph)
        valor_inicial = serie_train.ultimos_valores(1)[0]
        return dataset, historial, valor_inicial

    def _crear_serie_diferencias(self, serie: SerieTemporal) -> SerieTemporal:
        valores = serie.valores()
        fechas = serie.fechas()
        diferencias = self.transformador.calcular_diferencias(valores)
        serie_diferencias = SerieTemporal()

        for fecha, diferencia in zip(fechas[1:], diferencias):
            serie_diferencias.agregar_observacion(
                ObservacionSerieTemporal(fecha, diferencia),
            )

        return serie_diferencias

    def _crear_regresor_lineal(self, configuracion: dict) -> RegresorLinealVectorizado:
        normalizacion = str(configuracion["normalizacion"])
        normalizador_entradas = None
        normalizador_objetivo = None

        if normalizacion == "minmax":
            normalizador_entradas = EscaladorMinMax()
            normalizador_objetivo = EscaladorMinMax()
        elif normalizacion == "zscore":
            normalizador_entradas = EscaladorZScore()
            normalizador_objetivo = EscaladorZScore()

        return RegresorLinealVectorizado(
            tasa_aprendizaje=float(configuracion["tasa"]),
            iteraciones=int(configuracion["iteraciones"]),
            normalizador_entradas=normalizador_entradas,
            normalizador_objetivo=normalizador_objetivo,
        )
