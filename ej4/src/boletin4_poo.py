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
