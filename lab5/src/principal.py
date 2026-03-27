from __future__ import annotations

from pathlib import Path

try:
    from .areas import AREAS_TEMATICAS, MACROAREAS
    from .factoria import FactoriaProyectos
except ImportError:
    from areas import AREAS_TEMATICAS, MACROAREAS
    from factoria import FactoriaProyectos


def _mostrar_conteo_registros(gestor_todos, gestor_concedidos, gestor_contratos) -> None:
    print("Conteo de registros")
    print(f"Total: {len(gestor_todos)} (esperado: 7092)")
    print(f"Concedidos: {len(gestor_concedidos)} (esperado: 3252)")
    print(f"Contratos: {len(gestor_contratos)} (esperado: 1149)")
    print()


def _mostrar_tasa_exito_por_ccaa(gestor_todos, gestor_concedidos, gestor_contratos) -> None:
    tasas_concedidos = gestor_concedidos.tasa_exito_por_ccaa(gestor_todos)
    tasas_contratado = gestor_contratos.tasa_exito_por_ccaa(gestor_todos)

    print("Tasa de exito por CCAA (%)")
    for ccaa in tasas_concedidos:
        tasa_concedidos = tasas_concedidos[ccaa]
        tasa_contratado = tasas_contratado.get(ccaa, 0.0)
        print(f"{ccaa}: concedidos={tasa_concedidos:.2f}% | con contratado={tasa_contratado:.2f}%")
    print()


def _mostrar_analisis_economico(gestor_concedidos) -> None:
    print("Analisis economico (presupuesto total por CCAA)")
    for ccaa, presupuesto in gestor_concedidos.presupuesto_total_por_ccaa().items():
        print(f"{ccaa}: {presupuesto:,.2f}")


def _mostrar_financiacion_por_habitante(gestor_concedidos, habitantes_por_ccaa) -> None:
    print()
    print("Tasa de financiacion por habitante (EUR/habitante)")
    tasas = gestor_concedidos.financiacion_por_habitante(habitantes_por_ccaa)
    for ccaa, tasa in tasas.items():
        print(f"{ccaa}: {tasa:.2f}")


def _mostrar_top_entidades_tasa_exito(
    gestor_todos, gestor_concedidos, gestor_contratos, n: int
) -> None:
    print()
    print(f"Top {n} entidades por tasa de exito (concedidos / solicitados)")
    top_concedidos = gestor_concedidos.top_n_entidades_por_tasa_exito(gestor_todos, n)
    for posicion, (entidad, tasa, exitos, total) in enumerate(top_concedidos, start=1):
        print(f"{posicion}. {entidad}: {tasa:.2f}% ({exitos}/{total})")

    print()
    print(f"Top {n} entidades por tasa de exito (con contratado / solicitados)")
    top_contratados = gestor_contratos.top_n_entidades_por_tasa_exito(gestor_todos, n)
    for posicion, (entidad, tasa, exitos, total) in enumerate(top_contratados, start=1):
        print(f"{posicion}. {entidad}: {tasa:.2f}% ({exitos}/{total})")


def _mostrar_tasa_exito_por_area_y_macroarea(
    gestor_todos, gestor_concedidos, gestor_contratos
) -> None:
    print()
    print("Tasa de exito por area (%)")
    tasas_area_concedidos = gestor_concedidos.tasa_exito_por_area(gestor_todos)
    tasas_area_contratados = gestor_contratos.tasa_exito_por_area(gestor_todos)

    for codigo_area in tasas_area_concedidos:
        nombre_area = AREAS_TEMATICAS[codigo_area]["nombre"]
        tasa_concedidos = tasas_area_concedidos[codigo_area]
        tasa_contratados = tasas_area_contratados.get(codigo_area, 0.0)
        print(
            f"{codigo_area} ({nombre_area}): "
            f"concedidos={tasa_concedidos:.2f}% | con contratado={tasa_contratados:.2f}%"
        )

    print()
    print("Tasa de exito por macroarea (%)")
    tasas_macro_concedidos = gestor_concedidos.tasa_exito_por_macroarea(gestor_todos)
    tasas_macro_contratados = gestor_contratos.tasa_exito_por_macroarea(gestor_todos)

    for codigo_macro in tasas_macro_concedidos:
        nombre_macro = MACROAREAS[codigo_macro]
        tasa_concedidos = tasas_macro_concedidos[codigo_macro]
        tasa_contratados = tasas_macro_contratados.get(codigo_macro, 0.0)
        print(
            f"{codigo_macro} ({nombre_macro}): "
            f"concedidos={tasa_concedidos:.2f}% | con contratado={tasa_contratados:.2f}%"
        )


def main() -> None:
    carpeta_datos = Path(__file__).resolve().parent.parent / "data"
    gestor_todos, gestor_concedidos, gestor_contratos = FactoriaProyectos.desde_carpeta_datos(
        carpeta_datos
    )
    habitantes_por_ccaa = FactoriaProyectos.cargar_habitantes_ccaa(
        carpeta_datos / "Habitantes CCAA.xlsx"
    )
    _mostrar_conteo_registros(gestor_todos, gestor_concedidos, gestor_contratos)
    _mostrar_tasa_exito_por_ccaa(gestor_todos, gestor_concedidos, gestor_contratos)
    _mostrar_analisis_economico(gestor_concedidos)
    _mostrar_financiacion_por_habitante(gestor_concedidos, habitantes_por_ccaa)
    _mostrar_top_entidades_tasa_exito(gestor_todos, gestor_concedidos, gestor_contratos, n=10)
    _mostrar_tasa_exito_por_area_y_macroarea(gestor_todos, gestor_concedidos, gestor_contratos)


if __name__ == "__main__":
    main()
