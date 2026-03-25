from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class Partido:
    siglas: str
    nombre: str

    @property
    def clave(self) -> str:
        return self.siglas or self.nombre


@dataclass
class ResultadoPartidoCircunscripcion:
    partido: Partido
    votos: int
    escanos_oficiales: int = 0
    escanos_dhondt: int = 0


@dataclass
class Circunscripcion:
    nombre_comunidad: str
    codigo_provincia: str
    nombre_provincia: str
    poblacion: int
    numero_mesas: int
    censo_sin_cera: int
    censo_cera: int
    censo_total: int
    votantes_cer: int
    votantes_cera: int
    votantes_total: int
    votos_validos: int
    votos_candidaturas: int
    votos_blanco: int
    votos_nulos: int
    diputados: int
    resultados_partido: dict[str, ResultadoPartidoCircunscripcion] = field(default_factory=dict)

    def agregar_resultado(self, resultado: ResultadoPartidoCircunscripcion) -> None:
        self.resultados_partido[resultado.partido.clave] = resultado

    @property
    def total_votos_partidos(self) -> int:
        return sum(resultado.votos for resultado in self.resultados_partido.values())

    @property
    def total_escanos_oficiales(self) -> int:
        return sum(resultado.escanos_oficiales for resultado in self.resultados_partido.values())

    @property
    def porcentaje_nulos(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return (self.votos_nulos / self.votantes_total) * 100.0

    @property
    def porcentaje_blanco(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return (self.votos_blanco / self.votantes_total) * 100.0

    @property
    def porcentaje_nulos_blanco(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return ((self.votos_nulos + self.votos_blanco) / self.votantes_total) * 100.0

    @property
    def porcentaje_participacion_cera(self) -> float:
        if self.censo_cera <= 0:
            return 0.0
        return (self.votantes_cera / self.censo_cera) * 100.0

    @property
    def ratio_cera_poblacion(self) -> float:
        if self.poblacion <= 0:
            return 0.0
        return (self.votantes_cera / self.poblacion) * 100.0

    @property
    def votos_por_diputado(self) -> float:
        if self.diputados <= 0:
            return float("inf")
        return self.votos_candidaturas / self.diputados


@dataclass
class ComunidadAutonoma:
    nombre: str
    circunscripciones: dict[str, Circunscripcion] = field(default_factory=dict)

    def agregar_circunscripcion(self, circunscripcion: Circunscripcion) -> None:
        self.circunscripciones[circunscripcion.nombre_provincia] = circunscripcion

    def iter_circunscripciones(self) -> Iterator[Circunscripcion]:
        return iter(self.circunscripciones.values())

    @property
    def poblacion(self) -> int:
        return sum(c.poblacion for c in self.circunscripciones.values())

    @property
    def censo_cera(self) -> int:
        return sum(c.censo_cera for c in self.circunscripciones.values())

    @property
    def votantes_cera(self) -> int:
        return sum(c.votantes_cera for c in self.circunscripciones.values())

    @property
    def votantes_total(self) -> int:
        return sum(c.votantes_total for c in self.circunscripciones.values())

    @property
    def votos_nulos(self) -> int:
        return sum(c.votos_nulos for c in self.circunscripciones.values())

    @property
    def votos_blanco(self) -> int:
        return sum(c.votos_blanco for c in self.circunscripciones.values())

    @property
    def votos_candidaturas(self) -> int:
        return sum(c.votos_candidaturas for c in self.circunscripciones.values())

    @property
    def diputados(self) -> int:
        return sum(c.diputados for c in self.circunscripciones.values())

    @property
    def porcentaje_nulos(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return (self.votos_nulos / self.votantes_total) * 100.0

    @property
    def porcentaje_blanco(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return (self.votos_blanco / self.votantes_total) * 100.0

    @property
    def porcentaje_nulos_blanco(self) -> float:
        if self.votantes_total <= 0:
            return 0.0
        return ((self.votos_nulos + self.votos_blanco) / self.votantes_total) * 100.0

    @property
    def porcentaje_participacion_cera(self) -> float:
        if self.censo_cera <= 0:
            return 0.0
        return (self.votantes_cera / self.censo_cera) * 100.0

    @property
    def ratio_cera_poblacion(self) -> float:
        if self.poblacion <= 0:
            return 0.0
        return (self.votantes_cera / self.poblacion) * 100.0


@dataclass
class EleccionGeneral:
    anio: int
    comunidades: dict[str, ComunidadAutonoma] = field(default_factory=dict)
    partidos: dict[str, Partido] = field(default_factory=dict)
    totales_oficiales_nacionales: dict[str, int] = field(default_factory=dict)
    totales_oficiales_nacionales_partidos: dict[str, tuple[int, int]] = field(default_factory=dict)

    def obtener_o_crear_partido(self, siglas: str, nombre: str) -> Partido:
        clave = (siglas or nombre).strip()
        partido = self.partidos.get(clave)
        if partido is None:
            partido = Partido(siglas=siglas.strip(), nombre=nombre.strip())
            self.partidos[clave] = partido
        return partido

    def agregar_circunscripcion(self, circunscripcion: Circunscripcion) -> None:
        comunidad = self.comunidades.get(circunscripcion.nombre_comunidad)
        if comunidad is None:
            comunidad = ComunidadAutonoma(nombre=circunscripcion.nombre_comunidad)
            self.comunidades[circunscripcion.nombre_comunidad] = comunidad
        comunidad.agregar_circunscripcion(circunscripcion)

    def iter_circunscripciones(self) -> Iterator[Circunscripcion]:
        for comunidad in self.comunidades.values():
            yield from comunidad.iter_circunscripciones()

    def obtener_circunscripcion(self, nombre_provincia: str) -> Circunscripcion | None:
        nombre_objetivo = nombre_provincia.strip().lower()
        for circunscripcion in self.iter_circunscripciones():
            if circunscripcion.nombre_provincia.strip().lower() == nombre_objetivo:
                return circunscripcion
        return None

    @property
    def total_diputados_nacional(self) -> int:
        return sum(c.diputados for c in self.iter_circunscripciones())

    @property
    def total_votantes_nacional(self) -> int:
        return sum(c.votantes_total for c in self.iter_circunscripciones())

    def votos_nacionales_por_partido(self) -> dict[str, int]:
        acumulado: dict[str, int] = {}
        for circ in self.iter_circunscripciones():
            for clave, resultado in circ.resultados_partido.items():
                acumulado[clave] = acumulado.get(clave, 0) + resultado.votos
        return acumulado

    def escanos_oficiales_por_partido(self) -> dict[str, int]:
        acumulado: dict[str, int] = {}
        for circ in self.iter_circunscripciones():
            for clave, resultado in circ.resultados_partido.items():
                acumulado[clave] = acumulado.get(clave, 0) + resultado.escanos_oficiales
        return acumulado


class ValidacionDatosError(ValueError):
    def __init__(self, errores: list[str]) -> None:
        mensaje = "Se detectaron incoherencias en los datos:\n- " + "\n- ".join(errores)
        super().__init__(mensaje)
        self.errores = errores


@dataclass(frozen=True)
class ResultadoUltimoEscano:
    circunscripcion: str
    partido_ultimo_escano: str
    partido_casi_gana: str | None
    votos_que_faltaron: int | None


@dataclass(frozen=True)
class ResultadoVotosPorEscano:
    ambito: str
    partido: str
    votos_totales: int
    escanos_totales: int
    votos_por_escano: float


@dataclass(frozen=True)
class Coalicion:
    partidos: tuple[str, ...]
    diputados: int
