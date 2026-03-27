from __future__ import annotations

from typing import Iterator

try:
    from .areas import MACROAREAS, area_de_subarea, macroarea_de_area
    from .proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
except ImportError:
    from areas import MACROAREAS, area_de_subarea, macroarea_de_area
    from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato


class Gestor_Proyectos:
    def __init__(self) -> None:
        self._proyectos: list[Proyecto] = []
        self._por_referencia: dict[str, Proyecto] = {}

    def agregar(self, proyecto: Proyecto) -> None:
        referencia = proyecto.referencia
        if referencia in self._por_referencia:
            raise ValueError(f"La referencia {referencia} ya existe en el gestor.")
        self._proyectos.append(proyecto)
        self._por_referencia[referencia] = proyecto

    def obtener(self, referencia: str) -> Proyecto | None:
        return self._por_referencia.get(referencia)

    def conteo_por_ccaa(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.ccaa] = conteo.get(proyecto.ccaa, 0) + 1
        return conteo

    def conteo_por_entidad(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.entidad] = conteo.get(proyecto.entidad, 0) + 1
        return conteo

    def conteo_por_area(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            conteo[area] = conteo.get(area, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def conteo_por_macroarea(self) -> dict[str, int]:
        conteo: dict[str, int] = {codigo_macro: 0 for codigo_macro in MACROAREAS}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            macroarea = macroarea_de_area(area)
            conteo[macroarea] = conteo.get(macroarea, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def tasa_exito_por_ccaa(self, gestor_exitos) -> dict[str, float]:
        total_por_ccaa = self.conteo_por_ccaa()
        exitos_por_ccaa = gestor_exitos.conteo_por_ccaa()
        tasas: dict[str, float] = {}

        for ccaa, total in total_por_ccaa.items():
            if total <= 0:
                tasas[ccaa] = 0.0
                continue
            tasas[ccaa] = (exitos_por_ccaa.get(ccaa, 0) / total) * 100.0

        return dict(sorted(tasas.items(), key=lambda item: item[0]))

    def tasa_exito_por_area(self, gestor_exitos) -> dict[str, float]:
        total_por_area = self.conteo_por_area()
        exitos_por_area = gestor_exitos.conteo_por_area()
        tasas: dict[str, float] = {}

        for area, total in total_por_area.items():
            if total <= 0:
                tasas[area] = 0.0
                continue
            tasas[area] = (exitos_por_area.get(area, 0) / total) * 100.0

        return dict(sorted(tasas.items(), key=lambda item: item[0]))

    def tasa_exito_por_macroarea(self, gestor_exitos) -> dict[str, float]:
        total_por_macroarea = self.conteo_por_macroarea()
        exitos_por_macroarea = gestor_exitos.conteo_por_macroarea()
        tasas: dict[str, float] = {}

        for macroarea, total in total_por_macroarea.items():
            if total <= 0:
                tasas[macroarea] = 0.0
                continue
            tasas[macroarea] = (exitos_por_macroarea.get(macroarea, 0) / total) * 100.0

        return dict(sorted(tasas.items(), key=lambda item: item[0]))

    def top_n_entidades_por_tasa_exito(
        self, gestor_exitos, n: int
    ) -> list[tuple[str, float, int, int]]:
        if n <= 0:
            return []

        total_por_entidad = self.conteo_por_entidad()
        exitos_por_entidad = gestor_exitos.conteo_por_entidad()
        ranking: list[tuple[str, float, int, int]] = []

        for entidad, total in total_por_entidad.items():
            exitos = exitos_por_entidad.get(entidad, 0)
            tasa = 0.0 if total <= 0 else (exitos / total) * 100.0
            ranking.append((entidad, tasa, exitos, total))

        ranking.sort(key=lambda fila: (-fila[1], -fila[2], -fila[3], fila[0]))
        return ranking[:n]

    @property
    def proyectos(self) -> list[Proyecto]:
        return list(self._proyectos)

    def __len__(self) -> int:
        return len(self._proyectos)

    def __iter__(self) -> Iterator[Proyecto]:
        return iter(self._proyectos)


class Gestor_ProyectosConcedidos:
    def __init__(self) -> None:
        self._proyectos: list[ProyectoConcedido] = []
        self._por_referencia: dict[str, ProyectoConcedido] = {}

    def agregar(self, proyecto: ProyectoConcedido) -> None:
        referencia = proyecto.referencia
        if referencia in self._por_referencia:
            raise ValueError(f"La referencia {referencia} ya existe en el gestor.")
        self._proyectos.append(proyecto)
        self._por_referencia[referencia] = proyecto

    def obtener(self, referencia: str) -> ProyectoConcedido | None:
        return self._por_referencia.get(referencia)

    def conteo_por_ccaa(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.ccaa] = conteo.get(proyecto.ccaa, 0) + 1
        return conteo

    def conteo_por_entidad(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.entidad] = conteo.get(proyecto.entidad, 0) + 1
        return conteo

    def conteo_por_area(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            conteo[area] = conteo.get(area, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def conteo_por_macroarea(self) -> dict[str, int]:
        conteo: dict[str, int] = {codigo_macro: 0 for codigo_macro in MACROAREAS}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            macroarea = macroarea_de_area(area)
            conteo[macroarea] = conteo.get(macroarea, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def tasa_exito_por_ccaa(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_ccaa(self)

    def tasa_exito_por_area(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_area(self)

    def tasa_exito_por_macroarea(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_macroarea(self)

    def top_n_entidades_por_tasa_exito(
        self, gestor_solicitados: Gestor_Proyectos, n: int
    ) -> list[tuple[str, float, int, int]]:
        return gestor_solicitados.top_n_entidades_por_tasa_exito(self, n)

    def presupuesto_total_por_ccaa(self) -> dict[str, float]:
        presupuesto_por_ccaa: dict[str, float] = {}
        for proyecto in self._proyectos:
            presupuesto_por_ccaa[proyecto.ccaa] = (
                presupuesto_por_ccaa.get(proyecto.ccaa, 0.0) + proyecto.presupuesto
            )
        return dict(sorted(presupuesto_por_ccaa.items(), key=lambda item: item[0]))

    def financiacion_por_habitante(self, habitantes_por_ccaa: dict[str, int]) -> dict[str, float]:
        presupuesto_por_ccaa = self.presupuesto_total_por_ccaa()
        ccaa_con_presupuesto = set(presupuesto_por_ccaa)
        ccaa_con_habitantes = set(habitantes_por_ccaa)
        faltantes = sorted(ccaa_con_presupuesto - ccaa_con_habitantes)
        if faltantes:
            raise ValueError(
                "Faltan habitantes para estas CCAA: " + ", ".join(faltantes)
            )

        tasas: dict[str, float] = {}
        for ccaa in sorted(ccaa_con_habitantes | ccaa_con_presupuesto):
            habitantes = habitantes_por_ccaa.get(ccaa, 0)
            if habitantes <= 0:
                tasas[ccaa] = 0.0
                continue
            presupuesto = presupuesto_por_ccaa.get(ccaa, 0.0)
            tasas[ccaa] = presupuesto / habitantes
        return tasas

    @property
    def proyectos(self) -> list[ProyectoConcedido]:
        return list(self._proyectos)

    def __len__(self) -> int:
        return len(self._proyectos)

    def __iter__(self) -> Iterator[ProyectoConcedido]:
        return iter(self._proyectos)


class Gestor_ProyectosContrato:
    def __init__(self) -> None:
        self._proyectos: list[ProyectoContrato] = []
        self._por_referencia: dict[str, ProyectoContrato] = {}

    def agregar(self, proyecto: ProyectoContrato) -> None:
        referencia = proyecto.referencia
        if referencia in self._por_referencia:
            raise ValueError(f"La referencia {referencia} ya existe en el gestor.")
        self._proyectos.append(proyecto)
        self._por_referencia[referencia] = proyecto

    def obtener(self, referencia: str) -> ProyectoContrato | None:
        return self._por_referencia.get(referencia)

    def conteo_por_ccaa(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.ccaa] = conteo.get(proyecto.ccaa, 0) + 1
        return conteo

    def conteo_por_entidad(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.entidad] = conteo.get(proyecto.entidad, 0) + 1
        return conteo

    def conteo_por_area(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            conteo[area] = conteo.get(area, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def conteo_por_macroarea(self) -> dict[str, int]:
        conteo: dict[str, int] = {codigo_macro: 0 for codigo_macro in MACROAREAS}
        for proyecto in self._proyectos:
            area = area_de_subarea(proyecto.area)
            macroarea = macroarea_de_area(area)
            conteo[macroarea] = conteo.get(macroarea, 0) + 1
        return dict(sorted(conteo.items(), key=lambda item: item[0]))

    def tasa_exito_por_ccaa(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_ccaa(self)

    def tasa_exito_por_area(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_area(self)

    def tasa_exito_por_macroarea(self, gestor_solicitados: Gestor_Proyectos) -> dict[str, float]:
        return gestor_solicitados.tasa_exito_por_macroarea(self)

    def top_n_entidades_por_tasa_exito(
        self, gestor_solicitados: Gestor_Proyectos, n: int
    ) -> list[tuple[str, float, int, int]]:
        return gestor_solicitados.top_n_entidades_por_tasa_exito(self, n)

    @property
    def proyectos(self) -> list[ProyectoContrato]:
        return list(self._proyectos)

    def __len__(self) -> int:
        return len(self._proyectos)

    def __iter__(self) -> Iterator[ProyectoContrato]:
        return iter(self._proyectos)
