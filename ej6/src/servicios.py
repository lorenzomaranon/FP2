from __future__ import annotations

from itertools import combinations

try:
    from .modelos import (
        Coalicion,
        Circunscripcion,
        EleccionGeneral,
        ResultadoUltimoEscano,
        ResultadoVotosPorEscano,
    )
except ImportError:
    from modelos import Coalicion, Circunscripcion, EleccionGeneral, ResultadoUltimoEscano, ResultadoVotosPorEscano


class RepartidorDhondt:
    def __init__(self, umbral_minimo: float = 0.03) -> None:
        self.umbral_minimo = umbral_minimo

    def _partidos_elegibles(self, circunscripcion: Circunscripcion) -> list[tuple[str, int]]:
        minimo = circunscripcion.votos_validos * self.umbral_minimo
        elegibles = [
            (clave, resultado.votos)
            for clave, resultado in circunscripcion.resultados_partido.items()
            if resultado.votos >= minimo
        ]
        if not elegibles:
            elegibles = [
                (clave, resultado.votos) for clave, resultado in circunscripcion.resultados_partido.items()
            ]
        return elegibles

    def ranking_cocientes(self, circunscripcion: Circunscripcion) -> list[tuple[float, int, str, int]]:
        tabla: list[tuple[float, int, str, int]] = []
        diputados = max(circunscripcion.diputados, 0)
        if diputados <= 0:
            return tabla

        for clave_partido, votos in self._partidos_elegibles(circunscripcion):
            for divisor in range(1, diputados + 1):
                tabla.append((votos / divisor, votos, clave_partido, divisor))

        tabla.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
        return tabla

    def repartir(self, circunscripcion: Circunscripcion) -> dict[str, int]:
        escanos: dict[str, int] = {clave: 0 for clave in circunscripcion.resultados_partido}
        diputados = max(circunscripcion.diputados, 0)
        if diputados <= 0:
            return escanos

        ranking = self.ranking_cocientes(circunscripcion)
        for _, _, clave_partido, _ in ranking[:diputados]:
            escanos[clave_partido] = escanos.get(clave_partido, 0) + 1
        return escanos

    def repartir_y_actualizar(self, circunscripcion: Circunscripcion) -> dict[str, int]:
        escanos = self.repartir(circunscripcion)
        for clave, resultado in circunscripcion.resultados_partido.items():
            resultado.escanos_dhondt = escanos.get(clave, 0)
        return escanos


class ValidadorEscanosOficiales:
    def __init__(self, repartidor: RepartidorDhondt | None = None) -> None:
        self.repartidor = repartidor or RepartidorDhondt()

    def comprobar(self, eleccion: EleccionGeneral, actualizar_dhondt: bool = True) -> list[str]:
        errores: list[str] = []
        for circ in eleccion.iter_circunscripciones():
            reparto = self.repartidor.repartir(circ)
            if actualizar_dhondt:
                for clave, resultado in circ.resultados_partido.items():
                    resultado.escanos_dhondt = reparto.get(clave, 0)

            for clave, resultado in circ.resultados_partido.items():
                oficial = resultado.escanos_oficiales
                calculado = reparto.get(clave, 0)
                if oficial != calculado:
                    errores.append(
                        f"{circ.nombre_provincia}: {clave} oficial={oficial}, dhondt={calculado}"
                    )

            if sum(reparto.values()) != circ.diputados:
                errores.append(
                    f"{circ.nombre_provincia}: suma reparto dhondt ({sum(reparto.values())}) "
                    f"!= diputados ({circ.diputados})"
                )
        return errores


class AnalizadorParticipacion:
    @staticmethod
    def top_circunscripciones_nulos(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(c.nombre_provincia, c.porcentaje_nulos) for c in eleccion.iter_circunscripciones()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_ccaa_nulos(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(ccaa.nombre, ccaa.porcentaje_nulos) for ccaa in eleccion.comunidades.values()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_circunscripciones_blanco(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(c.nombre_provincia, c.porcentaje_blanco) for c in eleccion.iter_circunscripciones()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_ccaa_blanco(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(ccaa.nombre, ccaa.porcentaje_blanco) for ccaa in eleccion.comunidades.values()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_circunscripciones_nulos_blanco(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(c.nombre_provincia, c.porcentaje_nulos_blanco) for c in eleccion.iter_circunscripciones()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_ccaa_nulos_blanco(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(ccaa.nombre, ccaa.porcentaje_nulos_blanco) for ccaa in eleccion.comunidades.values()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_circunscripciones_participacion_cera(
        eleccion: EleccionGeneral, top_n: int = 5
    ) -> list[tuple[str, float]]:
        datos = [(c.nombre_provincia, c.porcentaje_participacion_cera) for c in eleccion.iter_circunscripciones()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_ccaa_participacion_cera(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(ccaa.nombre, ccaa.porcentaje_participacion_cera) for ccaa in eleccion.comunidades.values()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]

    @staticmethod
    def top_ccaa_ratio_cera_poblacion(eleccion: EleccionGeneral, top_n: int = 5) -> list[tuple[str, float]]:
        datos = [(ccaa.nombre, ccaa.ratio_cera_poblacion) for ccaa in eleccion.comunidades.values()]
        return sorted(datos, key=lambda item: (-item[1], item[0]))[:top_n]


class AnalizadorPartidos:
    @staticmethod
    def partidos_en_exactamente_n_circunscripciones(eleccion: EleccionGeneral, n: int) -> list[str]:
        conteo: dict[str, int] = {}
        for circ in eleccion.iter_circunscripciones():
            for clave in circ.resultados_partido:
                conteo[clave] = conteo.get(clave, 0) + 1
        return sorted([clave for clave, valor in conteo.items() if valor == n])

    @staticmethod
    def partido_mas_votado_sin_escano(eleccion: EleccionGeneral) -> tuple[str, str, int] | None:
        mejor: tuple[str, str, int] | None = None
        for circ in eleccion.iter_circunscripciones():
            for clave, resultado in circ.resultados_partido.items():
                if resultado.votos <= 0:
                    continue
                if resultado.escanos_oficiales > 0:
                    continue
                actual = (circ.nombre_provincia, clave, resultado.votos)
                if mejor is None or actual[2] > mejor[2]:
                    mejor = actual
        return mejor

    @staticmethod
    def n_parejas_partido_circunscripcion_menos_votos_positivos(
        eleccion: EleccionGeneral, n: int
    ) -> list[tuple[str, str, int]]:
        pares: list[tuple[str, str, int]] = []
        for circ in eleccion.iter_circunscripciones():
            for clave, resultado in circ.resultados_partido.items():
                if resultado.votos > 0:
                    pares.append((clave, circ.nombre_provincia, resultado.votos))
        pares.sort(key=lambda item: (item[2], item[0], item[1]))
        return pares[:n]


class AnalizadorEscanos:
    def __init__(self, repartidor: RepartidorDhondt | None = None) -> None:
        self.repartidor = repartidor or RepartidorDhondt()

    def escanos_nacionales(self, eleccion: EleccionGeneral, usar_oficiales: bool = True) -> dict[str, int]:
        acumulado: dict[str, int] = {}
        for circ in eleccion.iter_circunscripciones():
            if usar_oficiales:
                for clave, resultado in circ.resultados_partido.items():
                    acumulado[clave] = acumulado.get(clave, 0) + resultado.escanos_oficiales
                continue
            reparto = self.repartidor.repartir(circ)
            for clave, escanos in reparto.items():
                acumulado[clave] = acumulado.get(clave, 0) + escanos
        return acumulado

    def ultimo_escano_y_segundo_por_circunscripcion(
        self, eleccion: EleccionGeneral
    ) -> list[ResultadoUltimoEscano]:
        resultados: list[ResultadoUltimoEscano] = []
        for circ in eleccion.iter_circunscripciones():
            ranking = self.repartidor.ranking_cocientes(circ)
            if not ranking or circ.diputados <= 0:
                continue

            ganadores = ranking[: circ.diputados]
            ultimo = ganadores[-1]
            primer_perdedor = ranking[circ.diputados] if len(ranking) > circ.diputados else None

            partido_ultimo = ultimo[2]
            partido_casi = None
            votos_faltan = None

            if primer_perdedor is not None:
                partido_casi = primer_perdedor[2]
                votos_ultimo = ultimo[1]
                divisor_ultimo = ultimo[3]
                votos_perdedor = primer_perdedor[1]
                divisor_perdedor = primer_perdedor[3]

                # Necesitamos: (votos_perdedor + x) / divisor_perdedor > votos_ultimo / divisor_ultimo
                votos_objetivo = (votos_ultimo * divisor_perdedor) // divisor_ultimo + 1
                votos_faltan = max(votos_objetivo - votos_perdedor, 1)

            resultados.append(
                ResultadoUltimoEscano(
                    circunscripcion=circ.nombre_provincia,
                    partido_ultimo_escano=partido_ultimo,
                    partido_casi_gana=partido_casi,
                    votos_que_faltaron=votos_faltan,
                )
            )
        return resultados

    def partidos_escanos_mas_baratos_nacional(
        self, eleccion: EleccionGeneral, top_n: int = 10, usar_oficiales: bool = True
    ) -> list[ResultadoVotosPorEscano]:
        votos = eleccion.votos_nacionales_por_partido()
        escanos = self.escanos_nacionales(eleccion, usar_oficiales=usar_oficiales)
        resultados: list[ResultadoVotosPorEscano] = []
        for partido, votos_totales in votos.items():
            escanos_totales = escanos.get(partido, 0)
            if escanos_totales <= 0:
                continue
            ratio = votos_totales / escanos_totales
            resultados.append(
                ResultadoVotosPorEscano(
                    ambito="Nacional",
                    partido=partido,
                    votos_totales=votos_totales,
                    escanos_totales=escanos_totales,
                    votos_por_escano=ratio,
                )
            )
        resultados.sort(key=lambda item: (item.votos_por_escano, item.partido))
        return resultados[:top_n]

    def partidos_escanos_mas_caros_nacional(
        self, eleccion: EleccionGeneral, top_n: int = 10, usar_oficiales: bool = True
    ) -> list[ResultadoVotosPorEscano]:
        votos = eleccion.votos_nacionales_por_partido()
        escanos = self.escanos_nacionales(eleccion, usar_oficiales=usar_oficiales)
        resultados: list[ResultadoVotosPorEscano] = []
        for partido, votos_totales in votos.items():
            escanos_totales = escanos.get(partido, 0)
            if escanos_totales <= 0:
                continue
            ratio = votos_totales / escanos_totales
            resultados.append(
                ResultadoVotosPorEscano(
                    ambito="Nacional",
                    partido=partido,
                    votos_totales=votos_totales,
                    escanos_totales=escanos_totales,
                    votos_por_escano=ratio,
                )
            )
        resultados.sort(key=lambda item: (-item.votos_por_escano, item.partido))
        return resultados[:top_n]

    def partidos_escanos_mas_baratos_por_circunscripcion(
        self, eleccion: EleccionGeneral, usar_oficiales: bool = True
    ) -> list[ResultadoVotosPorEscano]:
        mejores: list[ResultadoVotosPorEscano] = []
        for circ in eleccion.iter_circunscripciones():
            mejor: ResultadoVotosPorEscano | None = None
            reparto = self.repartidor.repartir(circ) if not usar_oficiales else None
            for clave, resultado in circ.resultados_partido.items():
                escanos = resultado.escanos_oficiales if usar_oficiales else reparto.get(clave, 0)
                if escanos <= 0:
                    continue
                ratio = resultado.votos / escanos
                actual = ResultadoVotosPorEscano(
                    ambito=circ.nombre_provincia,
                    partido=clave,
                    votos_totales=resultado.votos,
                    escanos_totales=escanos,
                    votos_por_escano=ratio,
                )
                if mejor is None or actual.votos_por_escano < mejor.votos_por_escano:
                    mejor = actual
            if mejor is not None:
                mejores.append(mejor)
        mejores.sort(key=lambda item: (item.votos_por_escano, item.ambito))
        return mejores

    def partidos_escanos_mas_caros_por_circunscripcion(
        self, eleccion: EleccionGeneral, usar_oficiales: bool = True
    ) -> list[ResultadoVotosPorEscano]:
        peores: list[ResultadoVotosPorEscano] = []
        for circ in eleccion.iter_circunscripciones():
            peor: ResultadoVotosPorEscano | None = None
            reparto = self.repartidor.repartir(circ) if not usar_oficiales else None
            for clave, resultado in circ.resultados_partido.items():
                escanos = resultado.escanos_oficiales if usar_oficiales else reparto.get(clave, 0)
                if escanos <= 0:
                    continue
                ratio = resultado.votos / escanos
                actual = ResultadoVotosPorEscano(
                    ambito=circ.nombre_provincia,
                    partido=clave,
                    votos_totales=resultado.votos,
                    escanos_totales=escanos,
                    votos_por_escano=ratio,
                )
                if peor is None or actual.votos_por_escano > peor.votos_por_escano:
                    peor = actual
            if peor is not None:
                peores.append(peor)
        peores.sort(key=lambda item: (-item.votos_por_escano, item.ambito))
        return peores

    @staticmethod
    def circunscripciones_con_menos_votos_para_diputado(
        eleccion: EleccionGeneral, top_n: int = 10
    ) -> list[tuple[str, float]]:
        datos = [(circ.nombre_provincia, circ.votos_por_diputado) for circ in eleccion.iter_circunscripciones()]
        return sorted(datos, key=lambda item: (item[1], item[0]))[:top_n]


class Pactometro:
    def __init__(self, analizador_escanos: AnalizadorEscanos | None = None) -> None:
        self.analizador_escanos = analizador_escanos or AnalizadorEscanos()

    def combinaciones_minimo_diputados(
        self, eleccion: EleccionGeneral, n: int, usar_oficiales: bool = True
    ) -> list[Coalicion]:
        escanos = self.analizador_escanos.escanos_nacionales(eleccion, usar_oficiales=usar_oficiales)
        partidos_con_escanos = sorted([(partido, valor) for partido, valor in escanos.items() if valor > 0])

        resultados: list[Coalicion] = []
        for tam in range(1, len(partidos_con_escanos) + 1):
            for combo in combinations(partidos_con_escanos, tam):
                total = sum(valor for _, valor in combo)
                if total >= n:
                    resultados.append(Coalicion(partidos=tuple(partido for partido, _ in combo), diputados=total))

        resultados.sort(key=lambda item: (item.diputados, len(item.partidos), item.partidos))
        return resultados


class VisualizadorResultados:
    def __init__(self) -> None:
        self._plt = None

    def _obtener_matplotlib(self):
        if self._plt is None:
            try:
                import matplotlib

                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
            except ImportError as exc:
                raise ImportError(
                    "No se pudo importar matplotlib. Instala la libreria para generar graficos."
                ) from exc
            self._plt = plt
        return self._plt

    @staticmethod
    def _agrupar_otros(datos: dict[str, int], top_n: int) -> dict[str, int]:
        ordenado = sorted(datos.items(), key=lambda item: (-item[1], item[0]))
        if top_n <= 0 or len(ordenado) <= top_n:
            return dict(ordenado)
        principales = ordenado[:top_n]
        resto = ordenado[top_n:]
        agrupado = dict(principales)
        agrupado["OTROS"] = sum(valor for _, valor in resto)
        return agrupado

    @staticmethod
    def _buscar_ccaa(eleccion: EleccionGeneral, nombre: str):
        objetivo = nombre.strip().lower()
        for ccaa in eleccion.comunidades.values():
            if ccaa.nombre.strip().lower() == objetivo:
                return ccaa
        return None

    @staticmethod
    def _datos_votos(eleccion: EleccionGeneral, nivel: str, ambito: str | None = None) -> dict[str, int]:
        nivel_norm = nivel.strip().lower()
        if nivel_norm == "nacional":
            return eleccion.votos_nacionales_por_partido()

        if nivel_norm == "ccaa":
            if ambito is None:
                raise ValueError("Para nivel CCAA debes indicar el nombre de la comunidad en 'ambito'.")
            ccaa = VisualizadorResultados._buscar_ccaa(eleccion, ambito)
            if ccaa is None:
                raise ValueError(f"No existe la CCAA: {ambito}")
            acumulado: dict[str, int] = {}
            for circ in ccaa.iter_circunscripciones():
                for clave, resultado in circ.resultados_partido.items():
                    acumulado[clave] = acumulado.get(clave, 0) + resultado.votos
            return acumulado

        if nivel_norm == "circunscripcion":
            if ambito is None:
                raise ValueError(
                    "Para nivel circunscripcion debes indicar el nombre de provincia en 'ambito'."
                )
            circ = eleccion.obtener_circunscripcion(ambito)
            if circ is None:
                raise ValueError(f"No existe la circunscripcion: {ambito}")
            return {clave: resultado.votos for clave, resultado in circ.resultados_partido.items()}

        raise ValueError("Nivel no valido. Usa: 'circunscripcion', 'ccaa' o 'nacional'.")

    def _datos_escanos(
        self,
        eleccion: EleccionGeneral,
        nivel: str,
        ambito: str | None = None,
        usar_oficiales: bool = True,
    ) -> dict[str, int]:
        repartidor = RepartidorDhondt()
        analizador = AnalizadorEscanos(repartidor)
        nivel_norm = nivel.strip().lower()

        if nivel_norm == "nacional":
            return analizador.escanos_nacionales(eleccion, usar_oficiales=usar_oficiales)

        if nivel_norm == "ccaa":
            if ambito is None:
                raise ValueError("Para nivel CCAA debes indicar el nombre de la comunidad en 'ambito'.")
            ccaa = self._buscar_ccaa(eleccion, ambito)
            if ccaa is None:
                raise ValueError(f"No existe la CCAA: {ambito}")
            acumulado: dict[str, int] = {}
            for circ in ccaa.iter_circunscripciones():
                if usar_oficiales:
                    for clave, resultado in circ.resultados_partido.items():
                        acumulado[clave] = acumulado.get(clave, 0) + resultado.escanos_oficiales
                else:
                    reparto = repartidor.repartir(circ)
                    for clave, valor in reparto.items():
                        acumulado[clave] = acumulado.get(clave, 0) + valor
            return acumulado

        if nivel_norm == "circunscripcion":
            if ambito is None:
                raise ValueError(
                    "Para nivel circunscripcion debes indicar el nombre de provincia en 'ambito'."
                )
            circ = eleccion.obtener_circunscripcion(ambito)
            if circ is None:
                raise ValueError(f"No existe la circunscripcion: {ambito}")
            if usar_oficiales:
                return {clave: resultado.escanos_oficiales for clave, resultado in circ.resultados_partido.items()}
            return repartidor.repartir(circ)

        raise ValueError("Nivel no valido. Usa: 'circunscripcion', 'ccaa' o 'nacional'.")

    def graficar_barras(
        self,
        datos: dict[str, int],
        titulo: str,
        top_n: int = 15,
        mostrar: bool = True,
        guardar_en: str | None = None,
    ) -> None:
        plt = self._obtener_matplotlib()
        datos_plot = self._agrupar_otros(datos, top_n=top_n)
        etiquetas = list(datos_plot.keys())
        valores = list(datos_plot.values())

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(etiquetas, valores, color="#1f77b4")
        ax.set_title(titulo)
        ax.set_ylabel("Valor")
        ax.tick_params(axis="x", labelrotation=75)
        fig.tight_layout()
        if guardar_en:
            fig.savefig(guardar_en, dpi=150)
        if mostrar:
            plt.show()
        else:
            plt.close(fig)

    def graficar_sectores(
        self,
        datos: dict[str, int],
        titulo: str,
        top_n: int = 12,
        mostrar: bool = True,
        guardar_en: str | None = None,
    ) -> None:
        plt = self._obtener_matplotlib()
        datos_plot = self._agrupar_otros(datos, top_n=top_n)
        etiquetas = list(datos_plot.keys())
        valores = list(datos_plot.values())

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(valores, labels=etiquetas, autopct="%1.1f%%", startangle=90)
        ax.set_title(titulo)
        ax.axis("equal")
        fig.tight_layout()
        if guardar_en:
            fig.savefig(guardar_en, dpi=150)
        if mostrar:
            plt.show()
        else:
            plt.close(fig)

    def graficar_votos(
        self,
        eleccion: EleccionGeneral,
        nivel: str,
        ambito: str | None = None,
        tipo: str = "barras",
        top_n: int = 15,
        mostrar: bool = True,
        guardar_en: str | None = None,
    ) -> None:
        datos = self._datos_votos(eleccion, nivel=nivel, ambito=ambito)
        titulo = f"Votos por partido ({nivel}{' - ' + ambito if ambito else ''})"
        if tipo == "barras":
            self.graficar_barras(datos, titulo=titulo, top_n=top_n, mostrar=mostrar, guardar_en=guardar_en)
            return
        if tipo == "sectores":
            self.graficar_sectores(datos, titulo=titulo, top_n=top_n, mostrar=mostrar, guardar_en=guardar_en)
            return
        raise ValueError("Tipo de grafico no valido. Usa 'barras' o 'sectores'.")

    def graficar_escanos(
        self,
        eleccion: EleccionGeneral,
        nivel: str,
        ambito: str | None = None,
        usar_oficiales: bool = True,
        tipo: str = "barras",
        top_n: int = 15,
        mostrar: bool = True,
        guardar_en: str | None = None,
    ) -> None:
        datos = self._datos_escanos(eleccion, nivel=nivel, ambito=ambito, usar_oficiales=usar_oficiales)
        titulo = f"Escanos por partido ({nivel}{' - ' + ambito if ambito else ''})"
        if tipo == "barras":
            self.graficar_barras(datos, titulo=titulo, top_n=top_n, mostrar=mostrar, guardar_en=guardar_en)
            return
        if tipo == "sectores":
            self.graficar_sectores(datos, titulo=titulo, top_n=top_n, mostrar=mostrar, guardar_en=guardar_en)
            return
        raise ValueError("Tipo de grafico no valido. Usa 'barras' o 'sectores'.")


class ResolutorBoletin6:
    def __init__(self) -> None:
        self.repartidor = RepartidorDhondt()
        self.validador_escanos = ValidadorEscanosOficiales(self.repartidor)
        self.analizador_participacion = AnalizadorParticipacion()
        self.analizador_partidos = AnalizadorPartidos()
        self.analizador_escanos = AnalizadorEscanos(self.repartidor)
        self.servicio_pactometro = Pactometro(self.analizador_escanos)
        self.visualizador = VisualizadorResultados()

    # 1) Graficos de votos
    def representar_votos(
        self, eleccion: EleccionGeneral, nivel: str, ambito: str | None = None, tipo: str = "barras"
    ) -> None:
        self.visualizador.graficar_votos(eleccion=eleccion, nivel=nivel, ambito=ambito, tipo=tipo)

    # 2) Circunscripciones/CCAA con mayor porcentaje de nulos o blanco
    def mayor_porcentaje_nulos_blanco(
        self, eleccion: EleccionGeneral, top_n: int = 5
    ) -> dict[str, list[tuple[str, float]]]:
        return {
            "circunscripciones_nulos": self.analizador_participacion.top_circunscripciones_nulos(eleccion, top_n),
            "circunscripciones_blanco": self.analizador_participacion.top_circunscripciones_blanco(eleccion, top_n),
            "circunscripciones_nulos_blanco": self.analizador_participacion.top_circunscripciones_nulos_blanco(
                eleccion, top_n
            ),
            "ccaa_nulos": self.analizador_participacion.top_ccaa_nulos(eleccion, top_n),
            "ccaa_blanco": self.analizador_participacion.top_ccaa_blanco(eleccion, top_n),
            "ccaa_nulos_blanco": self.analizador_participacion.top_ccaa_nulos_blanco(eleccion, top_n),
        }

    # 3) Mayor participacion CERA
    def mayor_participacion_cera(self, eleccion: EleccionGeneral, top_n: int = 5) -> dict[str, list[tuple[str, float]]]:
        return {
            "circunscripciones": self.analizador_participacion.top_circunscripciones_participacion_cera(eleccion, top_n),
            "ccaa": self.analizador_participacion.top_ccaa_participacion_cera(eleccion, top_n),
        }

    # 4) Partidos presentados exactamente en n circunscripciones
    def partidos_exactamente_n_circunscripciones(self, eleccion: EleccionGeneral, n: int) -> list[str]:
        return self.analizador_partidos.partidos_en_exactamente_n_circunscripciones(eleccion, n)

    # 5) CCAA con mayor CERA / poblacion
    def ccaa_mayor_ratio_cera_poblacion(
        self, eleccion: EleccionGeneral, top_n: int = 5
    ) -> list[tuple[str, float]]:
        return self.analizador_participacion.top_ccaa_ratio_cera_poblacion(eleccion, top_n)

    # 6) D'Hondt por circunscripcion
    def escanos_por_dhondt(self, circunscripcion: Circunscripcion) -> dict[str, int]:
        return self.repartidor.repartir(circunscripcion)

    # 7) Comprobar coincidencia con Excel
    def comprobar_resultados_escanos(self, eleccion: EleccionGeneral) -> list[str]:
        return self.validador_escanos.comprobar(eleccion, actualizar_dhondt=True)

    # 8) Graficos de escanos
    def representar_escanos(
        self,
        eleccion: EleccionGeneral,
        nivel: str,
        ambito: str | None = None,
        usar_oficiales: bool = True,
        tipo: str = "barras",
    ) -> None:
        self.visualizador.graficar_escanos(
            eleccion=eleccion,
            nivel=nivel,
            ambito=ambito,
            usar_oficiales=usar_oficiales,
            tipo=tipo,
        )

    # 9) Ultimo escano y casi ganador
    def ultimo_escano_y_casi_ganador(self, eleccion: EleccionGeneral) -> list[ResultadoUltimoEscano]:
        return self.analizador_escanos.ultimo_escano_y_segundo_por_circunscripcion(eleccion)

    # 10) Escanos mas baratos
    def escanos_mas_baratos(
        self, eleccion: EleccionGeneral, top_n: int = 10
    ) -> dict[str, list[ResultadoVotosPorEscano]]:
        return {
            "nacional": self.analizador_escanos.partidos_escanos_mas_baratos_nacional(eleccion, top_n),
            "circunscripcion": self.analizador_escanos.partidos_escanos_mas_baratos_por_circunscripcion(eleccion),
        }

    # 11) Escanos mas caros
    def escanos_mas_caros(
        self, eleccion: EleccionGeneral, top_n: int = 10
    ) -> dict[str, list[ResultadoVotosPorEscano]]:
        return {
            "nacional": self.analizador_escanos.partidos_escanos_mas_caros_nacional(eleccion, top_n),
            "circunscripcion": self.analizador_escanos.partidos_escanos_mas_caros_por_circunscripcion(eleccion),
        }

    # 12) Circunscripciones con menos votos por diputado
    def circunscripciones_menos_votos_por_diputado(
        self, eleccion: EleccionGeneral, top_n: int = 10
    ) -> list[tuple[str, float]]:
        return self.analizador_escanos.circunscripciones_con_menos_votos_para_diputado(eleccion, top_n)

    # 13) Partido mas votado sin escano
    def partido_mas_votado_sin_escano(self, eleccion: EleccionGeneral) -> tuple[str, str, int] | None:
        return self.analizador_partidos.partido_mas_votado_sin_escano(eleccion)

    # 14) n parejas (partido-circunscripcion) con menos votos > 0
    def n_parejas_menos_votos_positivos(
        self, eleccion: EleccionGeneral, n: int
    ) -> list[tuple[str, str, int]]:
        return self.analizador_partidos.n_parejas_partido_circunscripcion_menos_votos_positivos(eleccion, n)

    # 15) Pactometro
    def pactometro(self, eleccion: EleccionGeneral, n: int) -> list[Coalicion]:
        return self.servicio_pactometro.combinaciones_minimo_diputados(
            eleccion, n, usar_oficiales=True
        )
