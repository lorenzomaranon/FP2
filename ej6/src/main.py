from __future__ import annotations

from pathlib import Path
import unicodedata

try:
    from .factoria import FactoriaEleccion
    from .servicios import ResolutorBoletin6
except ImportError:
    from factoria import FactoriaEleccion
    from servicios import ResolutorBoletin6


def _print_top_porcentajes(titulo: str, datos: list[tuple[str, float]]) -> None:
    print(titulo)
    for nombre, valor in datos:
        print(f"- {nombre}: {valor:.2f}%")
    print()


def _slug(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in normalizado if not unicodedata.combining(c))
    limpio = "".join(c.lower() if c.isalnum() else "_" for c in sin_tildes)
    while "__" in limpio:
        limpio = limpio.replace("__", "_")
    return limpio.strip("_")


def _generar_graficos(resolutor: ResolutorBoletin6, eleccion, carpeta_salida: Path) -> None:
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    nombres_ccaa = sorted(eleccion.comunidades.keys())
    nombre_ccaa = "Comunidad de Madrid" if "Comunidad de Madrid" in eleccion.comunidades else nombres_ccaa[0]
    nombre_circ = (
        "Madrid"
        if eleccion.obtener_circunscripcion("Madrid")
        else next(c.nombre_provincia for c in eleccion.iter_circunscripciones())
    )

    specs = [
        ("votos", "nacional", None, "barras"),
        ("votos", "nacional", None, "sectores"),
        ("votos", "ccaa", nombre_ccaa, "barras"),
        ("votos", "ccaa", nombre_ccaa, "sectores"),
        ("votos", "circunscripcion", nombre_circ, "barras"),
        ("votos", "circunscripcion", nombre_circ, "sectores"),
        ("escanos", "nacional", None, "barras"),
        ("escanos", "nacional", None, "sectores"),
        ("escanos", "ccaa", nombre_ccaa, "barras"),
        ("escanos", "ccaa", nombre_ccaa, "sectores"),
        ("escanos", "circunscripcion", nombre_circ, "barras"),
        ("escanos", "circunscripcion", nombre_circ, "sectores"),
    ]

    visualizador = resolutor.visualizador
    for tipo_dato, nivel, ambito, tipo_grafico in specs:
        ambito_slug = _slug(ambito) if ambito else "total"
        nombre = f"{tipo_dato}_{nivel}_{ambito_slug}_{tipo_grafico}.png"
        ruta = carpeta_salida / nombre

        if tipo_dato == "votos":
            visualizador.graficar_votos(
                eleccion=eleccion,
                nivel=nivel,
                ambito=ambito,
                tipo=tipo_grafico,
                top_n=15,
                mostrar=False,
                guardar_en=str(ruta),
            )
        else:
            visualizador.graficar_escanos(
                eleccion=eleccion,
                nivel=nivel,
                ambito=ambito,
                usar_oficiales=True,
                tipo=tipo_grafico,
                top_n=15,
                mostrar=False,
                guardar_en=str(ruta),
            )

    print(f"Graficos guardados en: {carpeta_salida}")
    print(f"- CCAA usada para nivel autonomico: {nombre_ccaa}")
    print(f"- Circunscripcion usada para nivel provincial: {nombre_circ}")
    print()


def main() -> None:
    ruta_excel = Path(__file__).resolve().parents[1] / "data" / "PROV_02_202307_1.xlsx"
    eleccion = FactoriaEleccion.desde_excel(ruta_excel, validar=True)

    resolutor = ResolutorBoletin6()
    incongruencias_escanos = resolutor.comprobar_resultados_escanos(eleccion)

    total_circ = sum(1 for _ in eleccion.iter_circunscripciones())
    print(f"Eleccion cargada ({eleccion.anio})")
    print(f"- Circunscripciones: {total_circ}")
    print(f"- Comunidades: {len(eleccion.comunidades)}")
    print(f"- Partidos con votos > 0 en alguna circunscripcion: {len(eleccion.partidos)}")
    print()

    if incongruencias_escanos:
        print(f"Hay {len(incongruencias_escanos)} diferencias entre D'Hondt y el Excel:")
        for linea in incongruencias_escanos[:10]:
            print(f"- {linea}")
        if len(incongruencias_escanos) > 10:
            print(f"- ... ({len(incongruencias_escanos) - 10} diferencias adicionales)")
    else:
        print("Los escanos calculados con D'Hondt coinciden con los oficiales del Excel.")
    print()

    top_nulos_blanco = resolutor.mayor_porcentaje_nulos_blanco(eleccion, top_n=5)
    _print_top_porcentajes("Top 5 CCAA por porcentaje de votos nulos+blanco:", top_nulos_blanco["ccaa_nulos_blanco"])
    _print_top_porcentajes(
        "Top 5 circunscripciones por porcentaje de votos nulos+blanco:",
        top_nulos_blanco["circunscripciones_nulos_blanco"],
    )

    top_cera = resolutor.mayor_participacion_cera(eleccion, top_n=5)
    _print_top_porcentajes("Top 5 CCAA por participacion CERA:", top_cera["ccaa"])

    partidos_en_una = resolutor.partidos_exactamente_n_circunscripciones(eleccion, n=1)
    print(f"Partidos que se presentaron exactamente en 1 circunscripcion: {len(partidos_en_una)}")
    print(", ".join(partidos_en_una[:12]) + ("..." if len(partidos_en_una) > 12 else ""))
    print()

    top_ratio_cera = resolutor.ccaa_mayor_ratio_cera_poblacion(eleccion, top_n=5)
    _print_top_porcentajes("Top 5 CCAA por ratio votantes CERA / poblacion:", top_ratio_cera)

    ultimos = resolutor.ultimo_escano_y_casi_ganador(eleccion)
    print("Ultimo escano y partido mas cercano (primeras 5 circunscripciones):")
    for item in ultimos[:5]:
        print(
            f"- {item.circunscripcion}: ultimo={item.partido_ultimo_escano}, "
            f"casi={item.partido_casi_gana}, faltaron={item.votos_que_faltaron}"
        )
    print()

    baratos = resolutor.escanos_mas_baratos(eleccion, top_n=5)["nacional"]
    caros = resolutor.escanos_mas_caros(eleccion, top_n=5)["nacional"]
    print("Escanos mas baratos (nacional):")
    for item in baratos:
        print(f"- {item.partido}: {item.votos_por_escano:.2f} votos/escano")
    print()
    print("Escanos mas caros (nacional):")
    for item in caros:
        print(f"- {item.partido}: {item.votos_por_escano:.2f} votos/escano")
    print()

    menos_votos_diputado = resolutor.circunscripciones_menos_votos_por_diputado(eleccion, top_n=5)
    print("Circunscripciones con menos votos por diputado:")
    for provincia, ratio in menos_votos_diputado:
        print(f"- {provincia}: {ratio:.2f}")
    print()

    mas_votado_sin_escano = resolutor.partido_mas_votado_sin_escano(eleccion)
    if mas_votado_sin_escano is not None:
        provincia, partido, votos = mas_votado_sin_escano
        print("Partido mas votado sin escano:")
        print(f"- {partido} en {provincia}: {votos} votos")
    print()

    parejas = resolutor.n_parejas_menos_votos_positivos(eleccion, n=10)
    print("10 parejas (partido-circunscripcion) con menos votos (>0):")
    for partido, provincia, votos in parejas:
        print(f"- {partido} - {provincia}: {votos}")
    print()

    coaliciones = resolutor.pactometro(eleccion, n=176)
    print(f"Combinaciones de pactometro con al menos 176 diputados: {len(coaliciones)}")
    for coalicion in coaliciones[:10]:
        print(f"- {coalicion.partidos} => {coalicion.diputados}")

    try:
        carpeta_graficos = Path(__file__).resolve().parents[1] / "data" / "graficos"
        _generar_graficos(resolutor, eleccion, carpeta_graficos)
    except ImportError:
        print("No se generaron graficos porque matplotlib no esta instalado.")
        print("Instala con: pip install matplotlib")


if __name__ == "__main__":
    main()
