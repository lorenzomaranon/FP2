from __future__ import annotations

from modelo_regresion import ModeloRegresion


class PredictorSerieTemporal:
    def predecir(
        self,
        modelo: ModeloRegresion,
        historial_valores: list[float],
        ph: int,
        fh: int,
    ) -> list[float]:
        if ph <= 0:
            raise ValueError("PH debe ser mayor que cero.")
        if fh <= 0:
            return []
        if len(historial_valores) < ph:
            raise ValueError("No hay suficientes valores historicos para iniciar la prediccion.")

        ventana = [float(valor) for valor in historial_valores[-ph:]]
        predicciones: list[float] = []

        for _ in range(fh):
            siguiente_valor = float(modelo.predecir(ventana))
            predicciones.append(siguiente_valor)
            ventana = ventana[1:] + [siguiente_valor]

        return predicciones

