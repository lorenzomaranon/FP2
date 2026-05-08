from __future__ import annotations

from observacion_serie_temporal import ObservacionSerieTemporal


class SerieTemporal:
    def __init__(self) -> None:
        self._observaciones: list[ObservacionSerieTemporal] = []

    @classmethod
    def desde_observaciones(
        cls,
        observaciones: list[ObservacionSerieTemporal],
    ) -> "SerieTemporal":
        serie = cls()
        for observacion in observaciones:
            serie.agregar_observacion(observacion)
        return serie

    def agregar_observacion(self, observacion: ObservacionSerieTemporal) -> None:
        if not isinstance(observacion, ObservacionSerieTemporal):
            raise TypeError("La serie solo admite objetos ObservacionSerieTemporal.")
        self._observaciones.append(observacion)

    def valores(self) -> list[float]:
        return [observacion.valor for observacion in self._observaciones]

    def fechas(self) -> list:
        return [observacion.fecha for observacion in self._observaciones]

    def primeros_valores(self, cantidad: int) -> list[float]:
        return self.valores()[:cantidad]

    def primeras_fechas(self, cantidad: int) -> list:
        return self.fechas()[:cantidad]

    def ultimos_valores(self, cantidad: int) -> list[float]:
        if cantidad <= 0:
            return []
        return self.valores()[-cantidad:]

    def sin_ultimos(self, cantidad: int) -> "SerieTemporal":
        if cantidad <= 0:
            return SerieTemporal.desde_observaciones(self._observaciones[:])
        return SerieTemporal.desde_observaciones(self._observaciones[:-cantidad])

    def __len__(self) -> int:
        return len(self._observaciones)

