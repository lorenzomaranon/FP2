from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Iterator

import pandas as pd


@dataclass(frozen=True)
class ResultadoJugadorTemporada:
    jugador: str
    equipo: str
    temporada: str
    partidos: int
    goles: int


@dataclass(frozen=True)
class ResultadoJugadorValor:
    jugador: str
    valor: float


@dataclass(frozen=True)
class ResultadoJugadorEquipos:
    jugador: str
    equipos: list[str]


@dataclass(frozen=True)
class ResultadoJugadorEquipoValor:
    jugador: str
    equipo: str
    valor: int


@dataclass(frozen=True)
class ResultadoParejaEquipo:
    jugador_1: str
    jugador_2: str
    equipo: str
    minutos_juntos: int


@dataclass(frozen=True)
class ResultadoEquipoTemporadaValor:
    equipo: str
    temporada: str
    valor: int


@dataclass(frozen=True)
class ResultadoRevulsivo:
    jugador: str
    goles: int
    minutos_por_gol: float


@dataclass(frozen=True)
class ResultadoActividad:
    jugador: str
    inicio: int
    fin: int
    anios_activo: int


@dataclass(frozen=True)
class ResultadoUnaTemporada:
    jugador: str
    goles: int
    temporada: str


@dataclass(frozen=True)
class ResultadoEficienciaGol:
    jugador: str
    goles: int
    minutos_por_gol: float


class ValidacionDatosError(ValueError):
    def __init__(self, errores: list[str]) -> None:
        mensaje = "Se encontraron errores de validacion en el Excel:\n- " + "\n- ".join(errores)
        super().__init__(mensaje)
        self.errores = errores


@dataclass(frozen=True)
class Jugador:
    nombre: str
    liga: str
    partidos_jugados: int
    partidos_completos: int
    partidos_titular: int
    partidos_suplente: int
    minutos: int
    lesiones: int
    tarjetas: int
    expulsiones: int
    goles: int
    penalties_fallados: int

    @property
    def tarjetas_totales(self) -> int:
        return self.tarjetas + self.expulsiones

    @property
    def veces_sustituido(self) -> int:
        return self.partidos_titular - self.partidos_completos

    @property
    def goles_por_minuto(self) -> float:
        if self.minutos <= 0:
            return 0.0
        return self.goles / self.minutos

    @property
    def es_revulsivo(self) -> bool:
        return self.partidos_suplente > self.partidos_titular


@dataclass
class Equipo:
    nombre: str
    temporada_id: str
    jugadores: list[Jugador] = field(default_factory=list)

    def agregar_jugador(self, jugador: Jugador) -> None:
        self.jugadores.append(jugador)

    @property
    def goles_marcados(self) -> int:
        return sum(jugador.goles for jugador in self.jugadores)

    @property
    def num_jugadores(self) -> int:
        return len(self.jugadores)

    @property
    def partidos_jugados(self) -> int:
        if not self.jugadores:
            return 0
        return max(jugador.partidos_jugados for jugador in self.jugadores)

    @property
    def total_tarjetas(self) -> int:
        return sum(jugador.tarjetas_totales for jugador in self.jugadores)


@dataclass
class Temporada:
    identificador: str
    equipos: dict[str, Equipo] = field(default_factory=dict)

    def agregar_equipo(self, equipo: Equipo) -> None:
        self.equipos[equipo.nombre] = equipo

    def obtener_o_crear_equipo(self, nombre_equipo: str) -> Equipo:
        equipo = self.equipos.get(nombre_equipo)
        if equipo is None:
            equipo = Equipo(nombre=nombre_equipo, temporada_id=self.identificador)
            self.agregar_equipo(equipo)
        return equipo

    @property
    def num_equipos(self) -> int:
        return len(self.equipos)

    @property
    def num_partidos(self) -> int:
        if not self.equipos:
            return 0
        return sum(equipo.partidos_jugados for equipo in self.equipos.values()) // 2

    @property
    def partidos_por_equipo(self) -> int:
        if not self.equipos:
            return 0
        return max(equipo.partidos_jugados for equipo in self.equipos.values())

    @property
    def goles_totales(self) -> int:
        return sum(equipo.goles_marcados for equipo in self.equipos.values())

    @property
    def media_goles_por_partido(self) -> float:
        if self.num_partidos <= 0:
            return 0.0
        return self.goles_totales / self.num_partidos

    @property
    def anio_inicio(self) -> int:
        return int(self.identificador[:4])


class Liga:
    def __init__(self) -> None:
        self.temporadas: dict[str, Temporada] = {}
        self._tabla_cache: pd.DataFrame | None = None

    def agregar_temporada(self, temporada: Temporada) -> None:
        self.temporadas[temporada.identificador] = temporada
        self._tabla_cache = None

    def obtener_o_crear_temporada(self, identificador: str) -> Temporada:
        temporada = self.temporadas.get(identificador)
        if temporada is None:
            temporada = Temporada(identificador=identificador)
            self.agregar_temporada(temporada)
        return temporada

    @property
    def num_temporadas(self) -> int:
        return len(self.temporadas)

    @property
    def num_temporadas_no_jugadas(self) -> int:
        if not self.temporadas:
            return 0
        anios = sorted(temporada.anio_inicio for temporada in self.temporadas.values())
        huecos = 0
        for actual, siguiente in zip(anios, anios[1:]):
            huecos += max(0, siguiente - actual - 1)
        return huecos

    def _iterar_historial(self) -> Iterator[tuple[Temporada, Equipo, Jugador]]:
        for temporada in self.temporadas.values():
            for equipo in temporada.equipos.values():
                for jugador in equipo.jugadores:
                    yield temporada, equipo, jugador

    def maximo_goleador_temporada(self) -> Jugador | None:
        max_jugador: Jugador | None = None
        max_goles = -1
        for _, _, jugador in self._iterar_historial():
            if jugador.goles > max_goles:
                max_goles = jugador.goles
                max_jugador = jugador
        return max_jugador

    def maximo_goleador_historico(self) -> ResultadoJugadorValor:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby("JUGADOR", as_index=False)
            .agg(goles=("GOLES", "sum"))
            .sort_values(["goles", "JUGADOR"], ascending=[False, True])
        )
        top = ranking.iloc[0]
        return ResultadoJugadorValor(jugador=str(top["JUGADOR"]), valor=int(top["goles"]))

    def _tabla_historial(self) -> pd.DataFrame:
        if self._tabla_cache is not None:
            return self._tabla_cache.copy()

        filas: list[dict[str, object]] = []
        for temporada, equipo, jugador in self._iterar_historial():
            filas.append(
                {
                    "TEMPORADA": temporada.identificador,
                    "ANIO_INICIO": temporada.anio_inicio,
                    "EQUIPO": equipo.nombre,
                    "JUGADOR": jugador.nombre,
                    "LIGA": jugador.liga,
                    "PJUGADOS": jugador.partidos_jugados,
                    "PCOMPLETOS": jugador.partidos_completos,
                    "PTITULAR": jugador.partidos_titular,
                    "PSUPLENTE": jugador.partidos_suplente,
                    "MINUTOS": jugador.minutos,
                    "LESIONES": jugador.lesiones,
                    "TARJETAS": jugador.tarjetas,
                    "EXPULSIONES": jugador.expulsiones,
                    "TARJETAS_TOTALES": jugador.tarjetas_totales,
                    "GOLES": jugador.goles,
                    "PENALTIES_FALLADOS": jugador.penalties_fallados,
                    "VECES_SUSTITUIDO": jugador.veces_sustituido,
                    "GOLES_POR_MINUTO": jugador.goles_por_minuto,
                    "ES_REVULSIVO": jugador.es_revulsivo,
                }
            )

        self._tabla_cache = pd.DataFrame(filas)
        return self._tabla_cache.copy()

    @staticmethod
    def _racha_consecutiva_maxima(anios: list[int]) -> int:
        if not anios:
            return 0

        mejor = 1
        actual = 1
        for indice in range(1, len(anios)):
            if anios[indice] == anios[indice - 1] + 1:
                actual += 1
            else:
                actual = 1
            if actual > mejor:
                mejor = actual
        return mejor

    def _equipos_ordenados(self, jugador: str, solo_con_goles: bool = False) -> list[str]:
        tabla = self._tabla_historial()
        subset = tabla[tabla["JUGADOR"] == jugador]
        if solo_con_goles:
            subset = subset[subset["GOLES"] > 0]

        equipos = (
            subset.groupby("EQUIPO", as_index=False)
            .agg(partidos=("PJUGADOS", "sum"), anio_min=("ANIO_INICIO", "min"))
            .sort_values(["partidos", "anio_min", "EQUIPO"], ascending=[False, True, True])
        )
        return equipos["EQUIPO"].tolist()

    def ejercicio_1(self) -> ResultadoJugadorTemporada:
        tabla = self._tabla_historial()
        fila = tabla.loc[tabla["GOLES"].idxmax()]
        return ResultadoJugadorTemporada(
            jugador=str(fila["JUGADOR"]),
            equipo=str(fila["EQUIPO"]),
            temporada=str(fila["TEMPORADA"]),
            partidos=int(fila["PJUGADOS"]),
            goles=int(fila["GOLES"]),
        )

    def ejercicio_2(self) -> ResultadoJugadorValor:
        return self.maximo_goleador_historico()

    def ejercicio_3(self) -> ResultadoJugadorEquipos:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby("JUGADOR", as_index=False)
            .agg(num_equipos=("EQUIPO", "nunique"))
            .sort_values(["num_equipos", "JUGADOR"], ascending=[False, True])
        )
        jugador = str(ranking.iloc[0]["JUGADOR"])
        return ResultadoJugadorEquipos(jugador=jugador, equipos=self._equipos_ordenados(jugador))

    def ejercicio_4(self) -> ResultadoJugadorEquipoValor:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby(["JUGADOR", "EQUIPO"], as_index=False)
            .agg(partidos=("PJUGADOS", "sum"))
            .sort_values(["partidos", "JUGADOR"], ascending=[False, True])
        )
        top = ranking.iloc[0]
        return ResultadoJugadorEquipoValor(
            jugador=str(top["JUGADOR"]),
            equipo=str(top["EQUIPO"]),
            valor=int(top["partidos"]),
        )

    def ejercicio_5(self) -> ResultadoJugadorValor:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby("JUGADOR", as_index=False)
            .agg(minutos=("MINUTOS", "sum"))
            .sort_values(["minutos", "JUGADOR"], ascending=[False, True])
        )
        top = ranking.iloc[0]
        return ResultadoJugadorValor(jugador=str(top["JUGADOR"]), valor=int(top["minutos"]))

    def ejercicio_6(self, top_n: int = 3) -> list[ResultadoJugadorEquipos]:
        tabla = self._tabla_historial()
        con_goles = tabla[tabla["GOLES"] > 0]
        ranking = (
            con_goles.groupby("JUGADOR", as_index=False)
            .agg(equipos_con_gol=("EQUIPO", "nunique"), goles=("GOLES", "sum"))
            .query("equipos_con_gol == 6")
            .sort_values(["equipos_con_gol", "goles", "JUGADOR"], ascending=[False, False, True])
            .head(top_n)
        )

        resultados: list[ResultadoJugadorEquipos] = []
        for jugador in ranking["JUGADOR"].tolist():
            resultados.append(
                ResultadoJugadorEquipos(
                    jugador=str(jugador),
                    equipos=self._equipos_ordenados(str(jugador), solo_con_goles=True),
                )
            )
        return resultados

    def ejercicio_7(self, top_n: int = 5) -> list[ResultadoJugadorEquipoValor]:
        tabla = self._tabla_historial()
        filas: list[tuple[str, str, int]] = []
        for (jugador, equipo), subset in tabla.groupby(["JUGADOR", "EQUIPO"]):
            anios = sorted(subset["ANIO_INICIO"].unique().tolist())
            racha = self._racha_consecutiva_maxima(anios)
            filas.append((str(jugador), str(equipo), int(racha)))

        ranking = pd.DataFrame(filas, columns=["JUGADOR", "EQUIPO", "RACHA"]).sort_values(
            ["RACHA", "JUGADOR", "EQUIPO"], ascending=[False, True, True]
        )

        return [
            ResultadoJugadorEquipoValor(
                jugador=str(fila["JUGADOR"]),
                equipo=str(fila["EQUIPO"]),
                valor=int(fila["RACHA"]),
            )
            for _, fila in ranking.head(top_n).iterrows()
        ]

    def ejercicio_8(self, top_n: int = 10) -> list[ResultadoParejaEquipo]:
        tabla = self._tabla_historial()
        minutos_por_pareja: dict[tuple[str, str, str], int] = defaultdict(int)

        for (equipo, temporada), subset in tabla.groupby(["EQUIPO", "TEMPORADA"], sort=False):
            jugadores = list(zip(subset["JUGADOR"].tolist(), subset["MINUTOS"].tolist()))
            for (jugador_1, minutos_1), (jugador_2, minutos_2) in combinations(jugadores, 2):
                j1, j2 = sorted((str(jugador_1), str(jugador_2)))
                minutos_por_pareja[(j1, j2, str(equipo))] += int(minutos_1) + int(minutos_2)

        ranking = sorted(
            minutos_por_pareja.items(),
            key=lambda item: (-item[1], item[0][2], item[0][0], item[0][1]),
        )[:top_n]

        return [
            ResultadoParejaEquipo(
                jugador_1=clave[0],
                jugador_2=clave[1],
                equipo=clave[2],
                minutos_juntos=int(valor),
            )
            for clave, valor in ranking
        ]

    def ejercicio_9(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        tabla = self._tabla_historial()
        moderna = tabla[tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(partidos=("PJUGADOS", "sum"), completos=("PCOMPLETOS", "sum"), goles=("GOLES", "sum"))
            .query("partidos == completos and goles == 0")
            .sort_values(["completos", "JUGADOR"], ascending=[False, True])
            .head(top_n)
        )
        return [
            ResultadoJugadorValor(jugador=str(fila["JUGADOR"]), valor=int(fila["completos"]))
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_10(self, top_n: int = 3) -> list[ResultadoEquipoTemporadaValor]:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby(["EQUIPO", "TEMPORADA"], as_index=False)
            .agg(tarjetas_conjuntas=("TARJETAS_TOTALES", "sum"))
            .sort_values(["tarjetas_conjuntas", "TEMPORADA", "EQUIPO"], ascending=[False, True, True])
            .head(top_n)
        )

        return [
            ResultadoEquipoTemporadaValor(
                equipo=str(fila["EQUIPO"]),
                temporada=str(fila["TEMPORADA"]),
                valor=int(fila["tarjetas_conjuntas"]),
            )
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_11(self, top_n: int = 3, min_goles: int = 10) -> list[ResultadoRevulsivo]:
        tabla = self._tabla_historial()
        moderna = tabla[tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(
                goles=("GOLES", "sum"),
                minutos=("MINUTOS", "sum"),
                titularidades=("PTITULAR", "sum"),
                suplencias=("PSUPLENTE", "sum"),
            )
            .query("goles >= @min_goles and suplencias > titularidades")
        )
        ranking["minutos_por_gol"] = ranking["minutos"] / ranking["goles"]
        ranking = ranking.sort_values(
            ["minutos_por_gol", "goles", "JUGADOR"], ascending=[True, False, True]
        ).head(top_n)

        return [
            ResultadoRevulsivo(
                jugador=str(fila["JUGADOR"]),
                goles=int(fila["goles"]),
                minutos_por_gol=float(fila["minutos_por_gol"]),
            )
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_12(self, top_n: int = 5) -> list[ResultadoActividad]:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby("JUGADOR", as_index=False)
            .agg(inicio=("ANIO_INICIO", "min"), fin=("ANIO_INICIO", "max"))
            .sort_values(["inicio", "JUGADOR"], ascending=[True, True])
        )
        ranking["anios_activo"] = ranking["fin"] - ranking["inicio"]
        ranking = ranking.sort_values(
            ["anios_activo", "inicio", "JUGADOR"], ascending=[False, True, True]
        ).head(top_n)

        return [
            ResultadoActividad(
                jugador=str(fila["JUGADOR"]),
                inicio=int(fila["inicio"]),
                fin=int(fila["fin"]) + 1,
                anios_activo=int(fila["anios_activo"]),
            )
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_13(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        tabla = self._tabla_historial()
        moderna = tabla[tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(
                partidos=("PJUGADOS", "sum"),
                tarjetas=("TARJETAS", "sum"),
                expulsiones=("EXPULSIONES", "sum"),
                fin=("ANIO_INICIO", "max"),
            )
            .query("tarjetas == 0 and expulsiones == 0")
            .sort_values(["partidos", "fin", "JUGADOR"], ascending=[False, False, True])
            .head(top_n)
        )

        return [
            ResultadoJugadorValor(jugador=str(fila["JUGADOR"]), valor=int(fila["partidos"]))
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_14(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        tabla = self._tabla_historial()
        moderna = tabla[tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(cambios=("VECES_SUSTITUIDO", "sum"))
            .sort_values(["cambios", "JUGADOR"], ascending=[False, True])
            .head(top_n)
        )

        return [
            ResultadoJugadorValor(jugador=str(fila["JUGADOR"]), valor=int(fila["cambios"]))
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_15(self, top_n: int = 4) -> list[ResultadoUnaTemporada]:
        tabla = self._tabla_historial()
        totales = tabla.groupby("JUGADOR", as_index=False).agg(goles_totales=("GOLES", "sum"))
        idx_temporada_max = tabla.groupby("JUGADOR")["GOLES"].idxmax()
        temporada_pico = tabla.loc[idx_temporada_max, ["JUGADOR", "TEMPORADA", "GOLES"]].rename(
            columns={"GOLES": "goles_temporada"}
        )

        ranking = totales.merge(temporada_pico, on="JUGADOR", how="inner")
        ranking = ranking.query("goles_totales == goles_temporada")
        ranking = ranking.sort_values(
            ["goles_totales", "TEMPORADA", "JUGADOR"], ascending=[False, True, True]
        ).head(top_n)

        return [
            ResultadoUnaTemporada(
                jugador=str(fila["JUGADOR"]),
                goles=int(fila["goles_totales"]),
                temporada=str(fila["TEMPORADA"]),
            )
            for _, fila in ranking.iterrows()
        ]

    def ejercicio_16(self, top_n: int = 10, min_goles: int = 50) -> list[ResultadoEficienciaGol]:
        tabla = self._tabla_historial()
        ranking = (
            tabla.groupby("JUGADOR", as_index=False)
            .agg(goles=("GOLES", "sum"), minutos=("MINUTOS", "sum"))
            .query("goles >= @min_goles")
        )
        ranking["minutos_por_gol"] = ranking["minutos"] / ranking["goles"]
        ranking = ranking.sort_values(
            ["minutos_por_gol", "goles", "JUGADOR"], ascending=[True, False, True]
        ).head(top_n)

        return [
            ResultadoEficienciaGol(
                jugador=str(fila["JUGADOR"]),
                goles=int(fila["goles"]),
                minutos_por_gol=float(fila["minutos_por_gol"]),
            )
            for _, fila in ranking.iterrows()
        ]


class FactoriaLiga:
    COLUMNAS_ESPERADAS = {
        "TEMPORADA",
        "LIGA",
        "EQUIPO",
        "JUGADOR",
        "PJUGADOS",
        "PCOMPLETOS",
        "PTITULAR",
        "PSUPLENTE",
        "MINUTOS",
        "LESIONES",
        "TARJETAS",
        "EXPULSIONES",
        "GOLES",
        "PENALTIES FALLADOS",
    }
    COLUMNAS_TEXTO = ("TEMPORADA", "LIGA", "EQUIPO", "JUGADOR")
    COLUMNAS_NUMERICAS = (
        "PJUGADOS",
        "PCOMPLETOS",
        "PTITULAR",
        "PSUPLENTE",
        "MINUTOS",
        "LESIONES",
        "TARJETAS",
        "EXPULSIONES",
        "GOLES",
        "PENALTIES_FALLADOS",
    )
    REGEX_TEMPORADA = re.compile(r"^(\d{4})-(\d{2})$")
    LIMITE_ERRORES = 25

    @classmethod
    def desde_excel(cls, ruta_excel: str | Path) -> Liga:
        tabla = cls._leer_excel(ruta_excel)
        cls._validar(tabla)
        return cls._construir_liga(tabla)

    @classmethod
    def _leer_excel(cls, ruta_excel: str | Path) -> pd.DataFrame:
        ruta = Path(ruta_excel)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        try:
            tabla = pd.read_excel(ruta)
        except ImportError as exc:
            raise ImportError("No se puede leer .xls sin xlrd. Instala: pip install xlrd") from exc

        tabla = tabla.copy()
        tabla.columns = [str(columna).strip() for columna in tabla.columns]

        faltantes = cls.COLUMNAS_ESPERADAS.difference(set(tabla.columns))
        if faltantes:
            faltantes_txt = ", ".join(sorted(faltantes))
            raise ValueError(f"Faltan columnas requeridas: {faltantes_txt}")

        columnas_ordenadas = [
            "TEMPORADA",
            "LIGA",
            "EQUIPO",
            "JUGADOR",
            "PJUGADOS",
            "PCOMPLETOS",
            "PTITULAR",
            "PSUPLENTE",
            "MINUTOS",
            "LESIONES",
            "TARJETAS",
            "EXPULSIONES",
            "GOLES",
            "PENALTIES FALLADOS",
        ]
        tabla = tabla[columnas_ordenadas]
        tabla = tabla.rename(columns={"PENALTIES FALLADOS": "PENALTIES_FALLADOS"})

        for columna in cls.COLUMNAS_TEXTO:
            tabla[columna] = tabla[columna].astype(str).str.strip()

        for columna in cls.COLUMNAS_NUMERICAS:
            tabla[columna] = pd.to_numeric(tabla[columna], errors="coerce")
        tabla[list(cls.COLUMNAS_NUMERICAS)] = tabla[list(cls.COLUMNAS_NUMERICAS)].fillna(0)

        return tabla

    @classmethod
    def _validar(cls, tabla: pd.DataFrame) -> None:
        errores: list[str] = []
        errores.extend(cls._validar_valores_obligatorios(tabla))
        errores.extend(cls._validar_temporadas(tabla))
        errores.extend(cls._validar_no_negativos(tabla))
        errores.extend(cls._validar_relaciones_partidos(tabla))
        errores.extend(cls._validar_minutos(tabla))
        errores.extend(cls._validar_partidos_temporada(tabla))

        if errores:
            if len(errores) > cls.LIMITE_ERRORES:
                visibles = errores[: cls.LIMITE_ERRORES]
                restantes = len(errores) - cls.LIMITE_ERRORES
                visibles.append(f"... y {restantes} errores mas.")
                raise ValidacionDatosError(visibles)
            raise ValidacionDatosError(errores)

    @classmethod
    def _validar_valores_obligatorios(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []
        for columna in cls.COLUMNAS_TEXTO:
            mascara_vacios = tabla[columna].isna() | (tabla[columna].astype(str).str.strip() == "")
            for indice in tabla.index[mascara_vacios].tolist()[:5]:
                errores.append(f"Fila {indice + 2}: {columna} vacio")

        for columna in cls.COLUMNAS_NUMERICAS:
            mascara_nan = tabla[columna].isna()
            for indice in tabla.index[mascara_nan].tolist()[:5]:
                errores.append(f"Fila {indice + 2}: {columna} no numerico o vacio")
        return errores

    @classmethod
    def _validar_temporadas(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []
        for indice, temporada in tabla["TEMPORADA"].items():
            match = cls.REGEX_TEMPORADA.fullmatch(temporada)
            if not match:
                errores.append(f"Fila {indice + 2}: TEMPORADA invalida ({temporada})")
                continue

            anio_inicio = int(match.group(1))
            anio_fin_2d = int(match.group(2))
            if (anio_inicio + 1) % 100 != anio_fin_2d:
                errores.append(
                    f"Fila {indice + 2}: TEMPORADA incoherente ({temporada}), "
                    f"deberia terminar en {(anio_inicio + 1) % 100:02d}"
                )
        return errores

    @classmethod
    def _validar_no_negativos(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []
        mascara = (tabla[list(cls.COLUMNAS_NUMERICAS)] < 0).any(axis=1)
        for indice in tabla.index[mascara].tolist()[:10]:
            errores.append(f"Fila {indice + 2}: hay cantidades negativas")
        return errores

    @classmethod
    def _validar_relaciones_partidos(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []

        mascara_completos = tabla["PCOMPLETOS"] > tabla["PTITULAR"]
        for indice in tabla.index[mascara_completos].tolist()[:10]:
            errores.append(f"Fila {indice + 2}: PCOMPLETOS > PTITULAR")

        mascara_partidos = tabla["PJUGADOS"] != (tabla["PTITULAR"] + tabla["PSUPLENTE"])
        for indice in tabla.index[mascara_partidos].tolist()[:10]:
            errores.append(f"Fila {indice + 2}: PJUGADOS != PTITULAR + PSUPLENTE")

        return errores

    @classmethod
    def _validar_minutos(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []
        mascara = tabla["MINUTOS"] > (tabla["PJUGADOS"] * 90)
        for indice in tabla.index[mascara].tolist()[:10]:
            errores.append(f"Fila {indice + 2}: MINUTOS > PJUGADOS * 90")
        return errores

    @classmethod
    def _validar_partidos_temporada(cls, tabla: pd.DataFrame) -> list[str]:
        errores: list[str] = []

        equipos_por_temporada = tabla.groupby("TEMPORADA")["EQUIPO"].nunique()
        partidos_regulares = (equipos_por_temporada - 1) * 2
        maximo_equipo = tabla.groupby(["TEMPORADA", "EQUIPO"])["PJUGADOS"].max()
        partidos_por_temporada: dict[str, int] = {}

        for temporada, partidos_teoricos in partidos_regulares.items():
            maximos_temp = maximo_equipo.loc[temporada]
            maximo_real = int(maximos_temp.max())

            if maximo_real > int(partidos_teoricos):
                if not (maximos_temp > partidos_teoricos).all():
                    errores.append(
                        f"Temporada {temporada}: formato irregular en partidos jugados por equipo"
                    )
                    continue
                partidos_por_temporada[temporada] = maximo_real
            else:
                partidos_por_temporada[temporada] = int(partidos_teoricos)

        partidos_esperados = tabla["TEMPORADA"].map(partidos_por_temporada)
        mascara = tabla["PJUGADOS"] > partidos_esperados
        for indice in tabla.index[mascara].tolist()[:10]:
            limite = int(partidos_esperados.loc[indice])
            valor = int(tabla.loc[indice, "PJUGADOS"])
            errores.append(
                f"Fila {indice + 2}: PJUGADOS ({valor}) supera partidos de temporada ({limite})"
            )
        return errores

    @classmethod
    def _construir_liga(cls, tabla: pd.DataFrame) -> Liga:
        liga = Liga()
        ordenada = tabla.copy()
        ordenada["ANIO_INICIO"] = ordenada["TEMPORADA"].str.slice(0, 4).astype(int)
        ordenada = ordenada.sort_values(["ANIO_INICIO", "TEMPORADA", "EQUIPO", "JUGADOR"])

        for fila in ordenada.itertuples(index=False):
            temporada = liga.obtener_o_crear_temporada(str(fila.TEMPORADA))
            equipo = temporada.obtener_o_crear_equipo(str(fila.EQUIPO))
            equipo.agregar_jugador(
                Jugador(
                    nombre=str(fila.JUGADOR),
                    liga=str(fila.LIGA),
                    partidos_jugados=int(fila.PJUGADOS),
                    partidos_completos=int(fila.PCOMPLETOS),
                    partidos_titular=int(fila.PTITULAR),
                    partidos_suplente=int(fila.PSUPLENTE),
                    minutos=int(fila.MINUTOS),
                    lesiones=int(fila.LESIONES),
                    tarjetas=int(fila.TARJETAS),
                    expulsiones=int(fila.EXPULSIONES),
                    goles=int(fila.GOLES),
                    penalties_fallados=int(fila.PENALTIES_FALLADOS),
                )
            )
        return liga
