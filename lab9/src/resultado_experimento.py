from __future__ import annotations


class ResultadoExperimento:
    def __init__(
        self,
        modelo: str,
        ph: int,
        mae_validacion: float,
        mae_test: float,
        tasa_aprendizaje: float | None = None,
        normalizacion: str | None = None,
        k: int | None = None,
        estrategia_pesos: str | None = None,
        pesos: list[float] | None = None,
        predicciones_test: list[float] | None = None,
    ) -> None:
        self.modelo = modelo
        self.ph = int(ph)
        self.mae_validacion = float(mae_validacion)
        self.mae_test = float(mae_test)
        self.tasa_aprendizaje = tasa_aprendizaje
        self.normalizacion = normalizacion
        self.k = k
        self.estrategia_pesos = estrategia_pesos
        self.pesos = pesos[:] if pesos is not None else None
        self.predicciones_test = predicciones_test[:] if predicciones_test is not None else []

