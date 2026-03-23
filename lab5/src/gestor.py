from __future__ import annotations

from typing import Generic, Iterator, TypeVar

try:
    from .proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
except ImportError:
    from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato


TProyecto = TypeVar("TProyecto", bound=Proyecto)


class _GestorBase(Generic[TProyecto]):
    def __init__(self) -> None:
        self._proyectos: list[TProyecto] = []
        self._por_referencia: dict[str, TProyecto] = {}

    def agregar(self, proyecto: TProyecto) -> None:
        referencia = proyecto.referencia
        if referencia in self._por_referencia:
            raise ValueError(f"La referencia {referencia} ya existe en el gestor.")
        self._proyectos.append(proyecto)
        self._por_referencia[referencia] = proyecto

    def obtener(self, referencia: str) -> TProyecto | None:
        return self._por_referencia.get(referencia)

    def conteo_por_ccaa(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for proyecto in self._proyectos:
            conteo[proyecto.ccaa] = conteo.get(proyecto.ccaa, 0) + 1
        return conteo

    @property
    def proyectos(self) -> list[TProyecto]:
        return list(self._proyectos)

    def __len__(self) -> int:
        return len(self._proyectos)

    def __iter__(self) -> Iterator[TProyecto]:
        return iter(self._proyectos)


class Gestor_Proyectos(_GestorBase[Proyecto]):
    pass


class Gestor_ProyectosConcedidos(_GestorBase[ProyectoConcedido]):
    pass


class Gestor_ProyectosContrato(_GestorBase[ProyectoContrato]):
    pass
