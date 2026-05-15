from __future__ import annotations

from pathlib import Path

from analizador_correlaciones import AnalizadorCorrelaciones
from detector_anomalias import DetectorAnomalias
from escritor_lab10 import EscritorLab10
from exportador_entrega import ExportadorEntrega
from experimento_prediccion_diferencias import ExperimentoPrediccionDiferencias
from factoria_datos_sensores import FactoriaDatosSensores
from graficador_series import GraficadorSeries


class Laboratorio10App:
    def __init__(
        self,
        lab9_data_dir: str | Path,
        lab10_data_dir: str | Path,
    ) -> None:
        self.lab9_data_dir = Path(lab9_data_dir)
        self.lab10_data_dir = Path(lab10_data_dir)
        self.experimento_diferencias = ExperimentoPrediccionDiferencias(
            self.lab9_data_dir,
        )
        self.factoria_sensores = FactoriaDatosSensores()
        self.analizador = AnalizadorCorrelaciones()
        self.detector = DetectorAnomalias()
        self.graficador = GraficadorSeries()
        self.escritor = EscritorLab10()
        self.exportador = ExportadorEntrega()

    def ejecutar(self) -> None:
        self.lab10_data_dir.mkdir(parents=True, exist_ok=True)
        resultados_prediccion = self.experimento_diferencias.ejecutar()
        fechas_test = self.experimento_diferencias.fechas_test()
        valores_test = self.experimento_diferencias.valores_test()

        ruta_resumen = self.lab10_data_dir / "resultados_lab10.txt"
        ruta_predicciones = self.lab10_data_dir / "predicciones_diferencias_lab10.csv"
        ruta_markdown = self.lab10_data_dir / "tablas_entrega_lab10.md"

        self.escritor.guardar_resumen_prediccion(
            ruta_resumen,
            resultados_prediccion,
        )
        self.escritor.guardar_predicciones(
            ruta_predicciones,
            fechas_test,
            valores_test,
            resultados_prediccion,
        )
        self.escritor.guardar_tabla_markdown(
            ruta_markdown,
            resultados_prediccion,
        )

        ruta_csv = self.lab10_data_dir / "reto_4_dias.csv"
        datos = self.factoria_sensores.leer_csv(ruta_csv)
        graficas_originales = self.graficador.graficar_series_originales(
            datos,
            self.lab10_data_dir,
        )
        graficas_diferencias = self.graficador.graficar_series_diferencias(
            datos,
            self.lab10_data_dir,
        )
        pares = self.analizador.pares_correlacionados(
            datos,
            umbral=0.8,
            dia=1,
            usar_diferencias=True,
        )
        resultados_anomalias = self._ejecutar_anomalias(datos, pares)
        ruta_anomalias = self.lab10_data_dir / "anomalias_lab10.txt"
        self.escritor.guardar_anomalias(
            ruta_anomalias,
            pares,
            resultados_anomalias,
            graficas_originales + graficas_diferencias,
        )
        ruta_word, ruta_excel = self.exportador.exportar(self.lab10_data_dir)

        self._mostrar_resumen(
            ruta_resumen,
            ruta_predicciones,
            ruta_markdown,
            ruta_anomalias,
            ruta_word,
            ruta_excel,
            graficas_originales + graficas_diferencias,
            pares,
        )

    def _ejecutar_anomalias(self, datos, pares: list[tuple[str, str]]) -> list[dict]:
        resultados: list[dict] = []

        for umbral_ruptura in (0.15, 0.0):
            for separacion_maxima in (15, 20):
                for duracion_minima in (3, 5):
                    dias = {}
                    for dia in (2, 3, 4):
                        rupturas = self.detector.minutos_ruptura(
                            datos,
                            dia=dia,
                            pares=pares,
                            ventana=60,
                            umbral_ruptura=umbral_ruptura,
                            usar_diferencias=True,
                        )
                        dias[dia] = self.detector.intervalos_por_par(
                            rupturas,
                            separacion_maxima=separacion_maxima,
                            duracion_minima=duracion_minima,
                        )

                    resultados.append(
                        {
                            "umbral_ruptura": umbral_ruptura,
                            "separacion_maxima": separacion_maxima,
                            "duracion_minima": duracion_minima,
                            "dias": dias,
                        },
                    )

        return resultados

    def _mostrar_resumen(
        self,
        ruta_resumen: Path,
        ruta_predicciones: Path,
        ruta_markdown: Path,
        ruta_anomalias: Path,
        ruta_word: Path,
        ruta_excel: Path,
        graficas: list[Path],
        pares: list[tuple[str, str]],
    ) -> None:
        print("Resultados guardados en:")
        print(f"  {ruta_resumen}")
        print(f"  {ruta_predicciones}")
        print(f"  {ruta_markdown}")
        print(f"  {ruta_anomalias}")
        print(f"  {ruta_word}")
        print(f"  {ruta_excel}")
        print(f"Graficas exportadas: {len(graficas)} ficheros PNG en {self.lab10_data_dir}")
        print(f"Pares correlacionados del dia 1: {len(pares)}")
