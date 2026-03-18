from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

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


@dataclass(frozen=True)
class ResultadoJugadorDecadas:
    jugador: str
    decadas: list[int]


@dataclass(frozen=True)
class ResultadoTemporadaEquipos:
    temporada: str
    num_equipos: int
    equipos: list[str]


@dataclass(frozen=True)
class ResultadoEquipoValor:
    equipo: str
    valor: int


@dataclass(frozen=True)
class ResultadoTemporadaMediaGoles:
    temporada: str
    goles: int
    partidos: int
    media_goles: float


@dataclass(frozen=True)
class ResultadoEquiposCompartidos:
    equipo_1: str
    equipo_2: str
    num_jugadores: int
    ejemplos: list[str]


@dataclass(frozen=True)
class ResultadoPromedioMinutos:
    jugador: str
    temporadas: int
    minutos_totales: int
    promedio_minutos: float


@dataclass(frozen=True)
class ResultadoRegresoEquipo:
    jugador: str
    equipo: str
    anios_fuera: int


class RepositorioPlantillas:
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

    def __init__(self, ruta_excel: str | Path) -> None:
        self.ruta_excel = Path(ruta_excel)

    def cargar(self) -> pd.DataFrame:
        if not self.ruta_excel.exists():
            raise FileNotFoundError(f"No existe el archivo: {self.ruta_excel}")

        try:
            tabla = pd.read_excel(self.ruta_excel)
        except ImportError as exc:
            raise ImportError(
                "No se puede leer .xls sin xlrd. Instala: pip install xlrd"
            ) from exc

        faltantes = self.COLUMNAS_ESPERADAS.difference(set(tabla.columns))
        if faltantes:
            faltantes_txt = ", ".join(sorted(faltantes))
            raise ValueError(f"Faltan columnas requeridas: {faltantes_txt}")

        tabla = tabla.copy()
        tabla["TEMPORADA"] = tabla["TEMPORADA"].astype(str)
        tabla["ANIO_INICIO"] = tabla["TEMPORADA"].str.slice(0, 4).astype(int)
        return tabla


class AnalizadorBoletin4:
    def __init__(self, tabla: pd.DataFrame) -> None:
        self.tabla = tabla.copy()

    @classmethod
    def desde_excel(cls, ruta_excel: str | Path) -> "AnalizadorBoletin4":
        repo = RepositorioPlantillas(ruta_excel)
        return cls(repo.cargar())

    @staticmethod
    def _racha_consecutiva_maxima(anios: list[int]) -> int:
        if not anios:
            return 0

        mejor = 1
        actual = 1
        for i in range(1, len(anios)):
            if anios[i] == anios[i - 1] + 1:
                actual += 1
            else:
                actual = 1
            if actual > mejor:
                mejor = actual
        return mejor

    def _equipos_ordenados(self, jugador: str, solo_con_goles: bool = False) -> list[str]:
        subset = self.tabla[self.tabla["JUGADOR"] == jugador]
        if solo_con_goles:
            subset = subset[subset["GOLES"] > 0]

        equipos = (
            subset.groupby("EQUIPO", as_index=False)
            .agg(partidos=("PJUGADOS", "sum"), anio_min=("ANIO_INICIO", "min"))
            .sort_values(["partidos", "anio_min", "EQUIPO"], ascending=[False, True, True])
        )
        return equipos["EQUIPO"].tolist()

    @staticmethod
    def _temporadas_ordenadas(tabla: pd.DataFrame) -> list[str]:
        temporadas = tabla["TEMPORADA"].astype(str).unique().tolist()
        return sorted(temporadas, key=lambda temporada: int(temporada[:4]))

    @staticmethod
    def _primera_aparicion_equipo(tabla: pd.DataFrame) -> pd.Series:
        return tabla.reset_index().groupby("EQUIPO")["index"].min()

    @staticmethod
    def _racha_consecutiva_detallada(anios: list[int]) -> tuple[int, int]:
        if not anios:
            return 0, 0

        anios_ordenados = sorted(set(anios))
        mejor_longitud = 1
        mejor_inicio = anios_ordenados[0]
        longitud_actual = 1
        inicio_actual = anios_ordenados[0]

        for indice in range(1, len(anios_ordenados)):
            anio = anios_ordenados[indice]
            anio_previo = anios_ordenados[indice - 1]

            if anio == anio_previo + 1:
                longitud_actual += 1
            else:
                longitud_actual = 1
                inicio_actual = anio

            if longitud_actual > mejor_longitud:
                mejor_longitud = longitud_actual
                mejor_inicio = inicio_actual
            elif longitud_actual == mejor_longitud and inicio_actual < mejor_inicio:
                mejor_inicio = inicio_actual

        return mejor_longitud, mejor_inicio

    def _transiciones_temporada(self) -> list[tuple[str, str, list[str], list[str]]]:
        temporadas = self._temporadas_ordenadas(self.tabla)
        equipos_por_temporada = {
            temporada: set(self.tabla[self.tabla["TEMPORADA"] == temporada]["EQUIPO"].unique())
            for temporada in temporadas
        }

        transiciones: list[tuple[str, str, list[str], list[str]]] = []
        for temporada_actual, temporada_siguiente in zip(temporadas, temporadas[1:]):
            equipos_actual = equipos_por_temporada[temporada_actual]
            equipos_siguiente = equipos_por_temporada[temporada_siguiente]
            descendidos = sorted(equipos_actual - equipos_siguiente)
            ascendidos = sorted(equipos_siguiente - equipos_actual)
            transiciones.append((temporada_actual, temporada_siguiente, descendidos, ascendidos))

        return transiciones

    def ejercicio_1(self) -> ResultadoJugadorTemporada:
        fila = self.tabla.loc[self.tabla["GOLES"].idxmax()]
        return ResultadoJugadorTemporada(
            jugador=str(fila["JUGADOR"]),
            equipo=str(fila["EQUIPO"]),
            temporada=str(fila["TEMPORADA"]),
            partidos=int(fila["PJUGADOS"]),
            goles=int(fila["GOLES"]),
        )

    def ejercicio_2(self) -> ResultadoJugadorValor:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(goles=("GOLES", "sum"))
            .sort_values(["goles", "JUGADOR"], ascending=[False, True])
        )
        top = ranking.iloc[0]
        return ResultadoJugadorValor(jugador=str(top["JUGADOR"]), valor=int(top["goles"]))

    def ejercicio_3(self) -> ResultadoJugadorEquipos:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(num_equipos=("EQUIPO", "nunique"))
            .sort_values(["num_equipos", "JUGADOR"], ascending=[False, True])
        )
        jugador = str(ranking.iloc[0]["JUGADOR"])
        return ResultadoJugadorEquipos(jugador=jugador, equipos=self._equipos_ordenados(jugador))

    def ejercicio_4(self) -> ResultadoJugadorEquipoValor:
        ranking = (
            self.tabla.groupby(["JUGADOR", "EQUIPO"], as_index=False)
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
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(minutos=("MINUTOS", "sum"))
            .sort_values(["minutos", "JUGADOR"], ascending=[False, True])
        )
        top = ranking.iloc[0]
        return ResultadoJugadorValor(jugador=str(top["JUGADOR"]), valor=int(top["minutos"]))

    def ejercicio_6(self, top_n: int = 3) -> list[ResultadoJugadorEquipos]:
        con_goles = self.tabla[self.tabla["GOLES"] > 0]
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
        filas: list[tuple[str, str, int]] = []
        for (jugador, equipo), subset in self.tabla.groupby(["JUGADOR", "EQUIPO"]):
            anios = sorted(subset["ANIO_INICIO"].unique().tolist())
            racha = self._racha_consecutiva_maxima(anios)
            filas.append((str(jugador), str(equipo), int(racha)))

        ranking = pd.DataFrame(filas, columns=["JUGADOR", "EQUIPO", "RACHA"]).sort_values(
            ["RACHA", "JUGADOR", "EQUIPO"], ascending=[False, True, True]
        )

        return [
            ResultadoJugadorEquipoValor(
                jugador=row["JUGADOR"],
                equipo=row["EQUIPO"],
                valor=int(row["RACHA"]),
            )
            for _, row in ranking.head(top_n).iterrows()
        ]

    def ejercicio_8(self, top_n: int = 10) -> list[ResultadoParejaEquipo]:
        minutos_por_pareja: dict[tuple[str, str, str], int] = defaultdict(int)

        for (equipo, temporada), subset in self.tabla.groupby(["EQUIPO", "TEMPORADA"], sort=False):
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
        # El boletin usa resultados de la etapa moderna: desde 1980, jugadores sin goles
        # y con todos sus partidos jugados de forma completa.
        moderna = self.tabla[self.tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(partidos=("PJUGADOS", "sum"), completos=("PCOMPLETOS", "sum"), goles=("GOLES", "sum"))
            .query("partidos == completos and goles == 0")
            .sort_values(["completos", "JUGADOR"], ascending=[False, True])
            .head(top_n)
        )

        return [
            ResultadoJugadorValor(jugador=str(row["JUGADOR"]), valor=int(row["completos"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_10(self, top_n: int = 3) -> list[ResultadoEquipoTemporadaValor]:
        ranking = (
            self.tabla.groupby(["EQUIPO", "TEMPORADA"], as_index=False)
            .agg(tarjetas=("TARJETAS", "sum"), expulsiones=("EXPULSIONES", "sum"))
        )
        ranking["tarjetas_conjuntas"] = ranking["tarjetas"] + ranking["expulsiones"]
        ranking = (
            ranking.sort_values(
                ["tarjetas_conjuntas", "TEMPORADA", "EQUIPO"], ascending=[False, True, True]
            )
            .head(top_n)
        )

        return [
            ResultadoEquipoTemporadaValor(
                equipo=str(row["EQUIPO"]),
                temporada=str(row["TEMPORADA"]),
                valor=int(row["tarjetas_conjuntas"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_11(self, top_n: int = 3, min_goles: int = 10) -> list[ResultadoRevulsivo]:
        moderna = self.tabla[self.tabla["ANIO_INICIO"] >= 1980]
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
                jugador=str(row["JUGADOR"]),
                goles=int(row["goles"]),
                minutos_por_gol=float(row["minutos_por_gol"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_12(self, top_n: int = 5) -> list[ResultadoActividad]:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(inicio=("ANIO_INICIO", "min"), fin=("ANIO_INICIO", "max"))
        )
        ranking["anios_activo"] = ranking["fin"] - ranking["inicio"]
        ranking = ranking.sort_values(
            ["anios_activo", "inicio", "JUGADOR"], ascending=[False, True, True]
        ).head(top_n)

        return [
            ResultadoActividad(
                jugador=str(row["JUGADOR"]),
                inicio=int(row["inicio"]),
                fin=int(row["fin"]) + 1,
                anios_activo=int(row["anios_activo"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_13(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        # En el boletin se toman temporadas desde 1980 para tarjetas/expulsiones.
        moderna = self.tabla[self.tabla["ANIO_INICIO"] >= 1980]
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
            ResultadoJugadorValor(jugador=str(row["JUGADOR"]), valor=int(row["partidos"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_14(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        moderna = self.tabla[self.tabla["ANIO_INICIO"] >= 1980].copy()
        moderna["cambiado"] = moderna["PTITULAR"] - moderna["PCOMPLETOS"]
        ranking = (
            moderna.groupby("JUGADOR", as_index=False)
            .agg(cambios=("cambiado", "sum"))
            .sort_values(["cambios", "JUGADOR"], ascending=[False, True])
            .head(top_n)
        )

        return [
            ResultadoJugadorValor(jugador=str(row["JUGADOR"]), valor=int(row["cambios"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_15(self, top_n: int = 4) -> list[ResultadoUnaTemporada]:
        totales = self.tabla.groupby("JUGADOR", as_index=False).agg(goles_totales=("GOLES", "sum"))
        idx_temporada_max = self.tabla.groupby("JUGADOR")["GOLES"].idxmax()
        temporada_pico = self.tabla.loc[idx_temporada_max, ["JUGADOR", "TEMPORADA", "GOLES"]].rename(
            columns={"GOLES": "goles_temporada"}
        )

        ranking = totales.merge(temporada_pico, on="JUGADOR", how="inner")
        ranking = ranking.query("goles_totales == goles_temporada")
        ranking = ranking.sort_values(
            ["goles_totales", "TEMPORADA", "JUGADOR"], ascending=[False, True, True]
        ).head(top_n)

        return [
            ResultadoUnaTemporada(
                jugador=str(row["JUGADOR"]),
                goles=int(row["goles_totales"]),
                temporada=str(row["TEMPORADA"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_16(self, top_n: int = 10, min_goles: int = 50) -> list[ResultadoEficienciaGol]:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(goles=("GOLES", "sum"), minutos=("MINUTOS", "sum"))
            .query("goles >= @min_goles")
        )
        ranking["minutos_por_gol"] = ranking["minutos"] / ranking["goles"]
        ranking = ranking.sort_values(
            ["minutos_por_gol", "goles", "JUGADOR"], ascending=[True, False, True]
        ).head(top_n)

        return [
            ResultadoEficienciaGol(
                jugador=str(row["JUGADOR"]),
                goles=int(row["goles"]),
                minutos_por_gol=float(row["minutos_por_gol"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_17(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(partidos=("PJUGADOS", "sum"), goles=("GOLES", "sum"))
            .query("goles == 0")
            .sort_values(["partidos", "JUGADOR"], ascending=[False, True])
            .head(top_n)
        )

        return [
            ResultadoJugadorValor(jugador=str(row["JUGADOR"]), valor=int(row["partidos"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_18(self, top_n: int = 5) -> list[ResultadoJugadorDecadas]:
        con_goles = self.tabla[self.tabla["GOLES"] > 0].copy()
        con_goles["DECADE"] = (con_goles["ANIO_INICIO"] // 10) * 10
        primera_aparicion = con_goles.reset_index().groupby("JUGADOR")["index"].min()
        decadas_por_jugador = con_goles.groupby("JUGADOR")["DECADE"].apply(
            lambda serie: sorted({int(valor) for valor in serie.tolist()})
        )

        filas: list[tuple[str, list[int], int]] = []
        for jugador, decadas in decadas_por_jugador.items():
            filas.append((str(jugador), decadas, int(primera_aparicion.loc[jugador])))

        ranking = sorted(filas, key=lambda fila: (-len(fila[1]), fila[2], fila[0]))[:top_n]
        return [ResultadoJugadorDecadas(jugador=fila[0], decadas=fila[1]) for fila in ranking]

    def ejercicio_19(self, min_descensos: int = 4) -> list[ResultadoTemporadaEquipos]:
        resultados: list[ResultadoTemporadaEquipos] = []
        for temporada, _, descendidos, _ in self._transiciones_temporada():
            if len(descendidos) >= min_descensos:
                resultados.append(
                    ResultadoTemporadaEquipos(
                        temporada=temporada,
                        num_equipos=len(descendidos),
                        equipos=descendidos,
                    )
                )
        return resultados

    def ejercicio_20(self, top_n: int = 3) -> list[ResultadoEquipoValor]:
        descensos_por_equipo: dict[str, int] = defaultdict(int)
        primer_descenso: dict[str, int] = {}

        for temporada, _, descendidos, _ in self._transiciones_temporada():
            anio = int(temporada[:4])
            for equipo in descendidos:
                descensos_por_equipo[equipo] += 1
                if equipo not in primer_descenso:
                    primer_descenso[equipo] = anio

        ranking = sorted(
            descensos_por_equipo.items(),
            key=lambda item: (-item[1], primer_descenso[item[0]], item[0]),
        )[:top_n]

        return [ResultadoEquipoValor(equipo=equipo, valor=int(valor)) for equipo, valor in ranking]

    def ejercicio_21(self, min_ascensos: int = 4) -> list[ResultadoTemporadaEquipos]:
        resultados: list[ResultadoTemporadaEquipos] = []
        for _, temporada, _, ascendidos in self._transiciones_temporada():
            if len(ascendidos) >= min_ascensos:
                resultados.append(
                    ResultadoTemporadaEquipos(
                        temporada=temporada,
                        num_equipos=len(ascendidos),
                        equipos=ascendidos,
                    )
                )
        return resultados

    def ejercicio_22(self, top_n: int = 1) -> list[ResultadoEquipoValor]:
        ascensos_por_equipo: dict[str, int] = defaultdict(int)
        primer_ascenso: dict[str, int] = {}

        for _, temporada, _, ascendidos in self._transiciones_temporada():
            anio = int(temporada[:4])
            for equipo in ascendidos:
                ascensos_por_equipo[equipo] += 1
                if equipo not in primer_ascenso:
                    primer_ascenso[equipo] = anio

        ranking = sorted(
            ascensos_por_equipo.items(),
            key=lambda item: (-item[1], primer_ascenso[item[0]], item[0]),
        )[:top_n]

        return [ResultadoEquipoValor(equipo=equipo, valor=int(valor)) for equipo, valor in ranking]

    def ejercicio_23(self, top_n: int = 10) -> list[ResultadoEquipoValor]:
        primera_aparicion = self._primera_aparicion_equipo(self.tabla).rename("first_idx")
        ranking = (
            self.tabla.groupby("EQUIPO", as_index=False)
            .agg(temporadas=("TEMPORADA", "nunique"))
            .merge(primera_aparicion, on="EQUIPO", how="left")
            .sort_values(["temporadas", "first_idx", "EQUIPO"], ascending=[False, True, True])
            .head(top_n)
        )

        return [
            ResultadoEquipoValor(equipo=str(row["EQUIPO"]), valor=int(row["temporadas"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_24(self, top_n: int = 10) -> list[ResultadoEquipoValor]:
        primera_aparicion = self._primera_aparicion_equipo(self.tabla).rename("first_idx")
        ranking = (
            self.tabla.groupby("EQUIPO", as_index=False)
            .agg(temporadas=("TEMPORADA", "nunique"))
            .merge(primera_aparicion, on="EQUIPO", how="left")
            .sort_values(["temporadas", "first_idx", "EQUIPO"], ascending=[True, True, True])
            .head(top_n)
        )

        return [
            ResultadoEquipoValor(equipo=str(row["EQUIPO"]), valor=int(row["temporadas"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_25(self, top_n: int = 10) -> list[ResultadoEquipoValor]:
        primera_aparicion = self._primera_aparicion_equipo(self.tabla).rename("first_idx")
        ranking = (
            self.tabla.groupby("EQUIPO", as_index=False)
            .agg(goles=("GOLES", "sum"))
            .merge(primera_aparicion, on="EQUIPO", how="left")
            .sort_values(["goles", "first_idx", "EQUIPO"], ascending=[False, True, True])
            .head(top_n)
        )

        return [
            ResultadoEquipoValor(equipo=str(row["EQUIPO"]), valor=int(row["goles"]))
            for _, row in ranking.iterrows()
        ]

    def ejercicio_26(self, top_n: int = 10) -> list[ResultadoEquipoValor]:
        primera_aparicion = self._primera_aparicion_equipo(self.tabla).rename("first_idx")
        ranking_baja = (
            self.tabla.groupby("EQUIPO", as_index=False)
            .agg(goles=("GOLES", "sum"))
            .merge(primera_aparicion, on="EQUIPO", how="left")
            .sort_values(["goles", "first_idx", "EQUIPO"], ascending=[True, True, True])
            .head(top_n)
        )
        ranking_baja = ranking_baja.sort_values(
            ["goles", "first_idx", "EQUIPO"], ascending=[False, True, True]
        )

        return [
            ResultadoEquipoValor(equipo=str(row["EQUIPO"]), valor=int(row["goles"]))
            for _, row in ranking_baja.iterrows()
        ]

    def ejercicio_27(self, min_media: float = 4.0) -> list[ResultadoTemporadaMediaGoles]:
        ranking = (
            self.tabla.groupby("TEMPORADA", as_index=False)
            .agg(goles=("GOLES", "sum"), equipos=("EQUIPO", "nunique"))
            .sort_values(["TEMPORADA"], ascending=[True])
        )
        ranking["partidos"] = ranking["equipos"] * (ranking["equipos"] - 1)
        ranking["media"] = ranking["goles"] / ranking["partidos"]
        ranking = ranking[ranking["media"] >= min_media]

        return [
            ResultadoTemporadaMediaGoles(
                temporada=str(row["TEMPORADA"]),
                goles=int(row["goles"]),
                partidos=int(row["partidos"]),
                media_goles=float(row["media"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_28(self) -> list[ResultadoTemporadaEquipos]:
        ranking = (
            self.tabla.reset_index()
            .groupby(["TEMPORADA", "EQUIPO"], as_index=False)
            .agg(goles=("GOLES", "sum"), first_idx=("index", "min"))
        )

        resultados: list[ResultadoTemporadaEquipos] = []
        for temporada, subset in ranking.groupby("TEMPORADA", sort=True):
            maximo = subset["goles"].max()
            equipos = (
                subset[subset["goles"] == maximo]
                .sort_values(["first_idx", "EQUIPO"], ascending=[True, True])["EQUIPO"]
                .tolist()
            )
            if len(equipos) > 1:
                resultados.append(
                    ResultadoTemporadaEquipos(
                        temporada=str(temporada),
                        num_equipos=len(equipos),
                        equipos=[str(equipo) for equipo in equipos],
                    )
                )
        return resultados

    def ejercicio_29(self, top_n: int = 3) -> list[ResultadoEquipoValor]:
        ranking = (
            self.tabla.groupby(["TEMPORADA", "EQUIPO"], as_index=False)
            .agg(goles=("GOLES", "sum"))
        )
        ranking["ANIO_INICIO"] = ranking["TEMPORADA"].str.slice(0, 4).astype(int)

        temporadas_top_por_equipo: dict[str, list[int]] = defaultdict(list)
        for _, subset in ranking.groupby("TEMPORADA", sort=True):
            maximo = subset["goles"].max()
            for _, fila in subset[subset["goles"] == maximo].iterrows():
                temporadas_top_por_equipo[str(fila["EQUIPO"])].append(int(fila["ANIO_INICIO"]))

        filas: list[tuple[str, int, int]] = []
        for equipo, anios in temporadas_top_por_equipo.items():
            racha = self._racha_consecutiva_maxima(sorted(set(anios)))
            temporadas_como_top = len(set(anios))
            filas.append((equipo, racha, temporadas_como_top))

        filas = sorted(filas, key=lambda fila: (-fila[1], -fila[2], fila[0]))[:top_n]
        return [ResultadoEquipoValor(equipo=equipo, valor=racha) for equipo, racha, _ in filas]

    def ejercicio_30(
        self,
        equipo_1: str = "Sevilla F.C.",
        equipo_2: str = "Real Betis B. S.",
        ejemplos_n: int = 5,
    ) -> ResultadoEquiposCompartidos:
        jugadores_1 = set(self.tabla[self.tabla["EQUIPO"] == equipo_1]["JUGADOR"].unique())
        jugadores_2 = set(self.tabla[self.tabla["EQUIPO"] == equipo_2]["JUGADOR"].unique())
        compartidos = sorted(jugadores_1.intersection(jugadores_2))
        return ResultadoEquiposCompartidos(
            equipo_1=equipo_1,
            equipo_2=equipo_2,
            num_jugadores=len(compartidos),
            ejemplos=[str(nombre) for nombre in compartidos[:ejemplos_n]],
        )

    def ejercicio_31(self, top_n: int = 5, temporadas_objetivo: int = 8) -> list[ResultadoPromedioMinutos]:
        ranking = (
            self.tabla.groupby("JUGADOR", as_index=False)
            .agg(temporadas=("TEMPORADA", "nunique"), minutos_totales=("MINUTOS", "sum"))
            .query("temporadas == @temporadas_objetivo")
        )
        ranking["promedio"] = ranking["minutos_totales"] / ranking["temporadas"]
        ranking = ranking.sort_values(["promedio", "JUGADOR"], ascending=[True, True]).head(top_n)

        return [
            ResultadoPromedioMinutos(
                jugador=str(row["JUGADOR"]),
                temporadas=int(row["temporadas"]),
                minutos_totales=int(row["minutos_totales"]),
                promedio_minutos=float(row["promedio"]),
            )
            for _, row in ranking.iterrows()
        ]

    def ejercicio_32(self, top_n: int = 5) -> list[ResultadoRegresoEquipo]:
        filas: list[tuple[str, str, int, int]] = []

        for (jugador, equipo), subset in self.tabla.groupby(["JUGADOR", "EQUIPO"]):
            anios = sorted({int(valor) for valor in subset["ANIO_INICIO"].tolist()})
            if len(anios) < 2:
                continue

            mejor_gap = 0
            inicio_gap = anios[0]
            for previo, siguiente in zip(anios, anios[1:]):
                gap = siguiente - previo
                if gap > mejor_gap:
                    mejor_gap = gap
                    inicio_gap = previo
                elif gap == mejor_gap and previo < inicio_gap:
                    inicio_gap = previo

            if mejor_gap > 1:
                filas.append((str(jugador), str(equipo), int(mejor_gap), int(inicio_gap)))

        filas = sorted(filas, key=lambda fila: (-fila[2], fila[3], fila[0], fila[1]))[:top_n]
        return [
            ResultadoRegresoEquipo(jugador=jugador, equipo=equipo, anios_fuera=anios_fuera)
            for jugador, equipo, anios_fuera, _ in filas
        ]

    def ejercicio_33(self, top_n: int = 3) -> list[ResultadoJugadorValor]:
        moderna = self.tabla[self.tabla["ANIO_INICIO"] >= 1980]
        ranking = (
            moderna.groupby(["JUGADOR", "ANIO_INICIO"], as_index=False)
            .agg(tarjetas=("TARJETAS", "sum"), expulsiones=("EXPULSIONES", "sum"))
        )
        ranking["limpio"] = (ranking["tarjetas"] == 0) & (ranking["expulsiones"] == 0)

        filas: list[tuple[str, int, int]] = []
        for jugador, subset in ranking.groupby("JUGADOR"):
            anios_limpios = subset[subset["limpio"]]["ANIO_INICIO"].astype(int).tolist()
            racha, inicio = self._racha_consecutiva_detallada(anios_limpios)
            if racha > 0:
                filas.append((str(jugador), int(racha), int(inicio)))

        filas = sorted(filas, key=lambda fila: (-fila[1], fila[2], fila[0]))[:top_n]
        return [ResultadoJugadorValor(jugador=jugador, valor=racha) for jugador, racha, _ in filas]
