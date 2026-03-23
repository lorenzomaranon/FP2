from __future__ import annotations

from pathlib import Path

try:
    from .factoria import FactoriaProyectos
except ImportError:
    from factoria import FactoriaProyectos


def _tasa_exito_por_ccaa(
    total_por_ccaa: dict[str, int], concedidos_por_ccaa: dict[str, int]
) -> dict[str, float]:
    tasas: dict[str, float] = {}
    for ccaa, total in total_por_ccaa.items():
        if total <= 0:
            tasas[ccaa] = 0.0
            continue
        concedidos = concedidos_por_ccaa.get(ccaa, 0)
        tasas[ccaa] = (concedidos / total) * 100.0
    return dict(sorted(tasas.items(), key=lambda item: item[0]))


def _presupuesto_por_ccaa(concedidos) -> dict[str, float]:
    resumen: dict[str, float] = {}
    for proyecto in concedidos:
        resumen[proyecto.ccaa] = resumen.get(proyecto.ccaa, 0.0) + proyecto.presupuesto
    return dict(sorted(resumen.items(), key=lambda item: item[0]))


def main() -> None:
    carpeta_datos = Path(__file__).resolve().parent.parent / "data"
    gestor_todos, gestor_concedidos, gestor_contratos = FactoriaProyectos.desde_carpeta_datos(
        carpeta_datos
    )

    print("Conteo de registros")
    print(f"Total: {len(gestor_todos)} (esperado: 7092)")
    print(f"Concedidos: {len(gestor_concedidos)} (esperado: 3252)")
    print(f"Contratos: {len(gestor_contratos)} (esperado: 1149)")
    print()

    tasas = _tasa_exito_por_ccaa(
        total_por_ccaa=gestor_todos.conteo_por_ccaa(),
        concedidos_por_ccaa=gestor_concedidos.conteo_por_ccaa(),
    )
    print("Tasa de exito por CCAA (%)")
    for ccaa, tasa in tasas.items():
        print(f"{ccaa}: {tasa:.2f}%")
    print()

    print("Analisis economico (presupuesto total por CCAA)")
    for ccaa, presupuesto in _presupuesto_por_ccaa(gestor_concedidos).items():
        print(f"{ccaa}: {presupuesto:,.2f}")


if __name__ == "__main__":
    main()
