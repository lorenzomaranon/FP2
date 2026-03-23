from __future__ import annotations

from dataclasses import dataclass, field
from math import isclose


@dataclass
class Proyecto:
    referencia: str
    area: str
    entidad: str
    ccaa: str
    concedido: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.referencia = self.referencia.strip()
        self.area = self.area.strip()
        self.entidad = self.entidad.strip()
        self.ccaa = self.ccaa.strip()


@dataclass
class ProyectoConcedido(Proyecto):
    costes_directos: float
    costes_indirectos: float
    anticipo: float
    subvencion: float
    anualidades: list[float]
    num_contratos_predoc: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.concedido = True
        if len(self.anualidades) != 4:
            raise ValueError("La lista de anualidades debe contener 4 importes (2025-2028).")
        equilibrio_presupuestario = self.costes_directos + self.costes_indirectos
        equilibrio_financiacion = self.anticipo + self.subvencion
        if not isclose(equilibrio_presupuestario, equilibrio_financiacion, abs_tol=0.05):
            raise ValueError(
                "Inconsistencia economica: "
                f"costes ({equilibrio_presupuestario:.2f}) != "
                f"anticipo+subvencion ({equilibrio_financiacion:.2f}) "
                f"en {self.referencia}"
            )

    @property
    def presupuesto(self) -> float:
        return self.costes_directos + self.costes_indirectos

    @property
    def contratado_predoc(self) -> bool:
        return self.num_contratos_predoc > 0


@dataclass
class ProyectoContrato(ProyectoConcedido):
    titulo: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.titulo = self.titulo.strip()
        if self.num_contratos_predoc <= 0:
            self.num_contratos_predoc = 1

    @property
    def contratado_predoc(self) -> bool:
        return True
