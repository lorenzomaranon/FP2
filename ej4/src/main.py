from __future__ import annotations

from pathlib import Path

from boletin4_poo import AnalizadorBoletin4


def main() -> None:
    ruta_excel = Path(__file__).resolve().parents[1] / "Plantillas1D-2017-18.xls"
    analizador = AnalizadorBoletin4.desde_excel(ruta_excel)

    e1 = analizador.ejercicio_1()
    print(f"Ejercicio 1: {e1.jugador} ({e1.equipo} - {e1.temporada}) | Partidos: {e1.partidos} | Goles: {e1.goles}")

    e2 = analizador.ejercicio_2()
    print(f"Ejercicio 2: {e2.jugador}: {int(e2.valor)} goles")

    e3 = analizador.ejercicio_3()
    print(f"Ejercicio 3: {e3.jugador} - Equipos: {', '.join(e3.equipos)}")

    e4 = analizador.ejercicio_4()
    print(f"Ejercicio 4: {e4.jugador} - Equipo: {e4.equipo}, Partidos: {e4.valor}")

    e5 = analizador.ejercicio_5()
    print(f"Ejercicio 5: {e5.jugador} con {int(e5.valor)} minutos")

    print("Ejercicio 6:")
    for item in analizador.ejercicio_6():
        print(f"- {item.jugador} - Equipos: {', '.join(item.equipos)}")

    print("Ejercicio 7:")
    for item in analizador.ejercicio_7():
        print(f"- {item.jugador} - Equipo: {item.equipo}, Temporadas seguidas: {item.valor}")

    print("Ejercicio 8:")
    for item in analizador.ejercicio_8():
        print(f"- {item.jugador_1} & {item.jugador_2} - Equipo: {item.equipo}, Minutos juntos: {item.minutos_juntos}")

    print("Ejercicio 9:")
    for item in analizador.ejercicio_9():
        print(f"- {item.jugador}: {int(item.valor)} partidos enteros jugados")

    print("Ejercicio 10:")
    for item in analizador.ejercicio_10():
        print(f"- {item.equipo} ({item.temporada}): {item.valor} tarjetas conjuntas")

    print("Ejercicio 11:")
    for item in analizador.ejercicio_11():
        print(f"- {item.jugador}: {item.goles} goles. Marca un gol cada {round(item.minutos_por_gol)} minutos")

    print("Ejercicio 12:")
    for item in analizador.ejercicio_12():
        print(f"- {item.jugador}: {item.anios_activo} anos en activo (De {item.inicio} a {item.fin})")

    print("Ejercicio 13:")
    for item in analizador.ejercicio_13():
        print(f"- {item.jugador}: {int(item.valor)} partidos disputados de forma impoluta")

    print("Ejercicio 14:")
    for item in analizador.ejercicio_14():
        print(f"- {item.jugador}: Cambiado en {int(item.valor)} ocasiones")

    print("Ejercicio 15:")
    for item in analizador.ejercicio_15():
        print(f"- {item.jugador}: {item.goles} goles. Todos anotados en la {item.temporada}")

    print("Ejercicio 16:")
    for item in analizador.ejercicio_16():
        print(f"- {item.jugador}: {item.goles} goles. Marca un gol cada {item.minutos_por_gol:.1f} minutos")

    print("Ejercicio 17:")
    for item in analizador.ejercicio_17():
        print(f"- {item.jugador}: {int(item.valor)} partidos enteros sin celebrar un gol")

    print("Ejercicio 18:")
    for item in analizador.ejercicio_18():
        decadas = ", ".join(str(decada) for decada in item.decadas)
        print(f"- {item.jugador}: Goles en {len(item.decadas)} decadas distintas ({decadas})")

    print("Ejercicio 19:")
    for item in analizador.ejercicio_19():
        print(
            f"- Temporada {item.temporada}: Descendieron {item.num_equipos} equipos: "
            f"{', '.join(item.equipos)}"
        )

    print("Ejercicio 20:")
    for item in analizador.ejercicio_20():
        print(f"- {item.equipo}: {item.valor} descensos")

    print("Ejercicio 21:")
    for item in analizador.ejercicio_21():
        print(
            f"- Temporada {item.temporada}: Ascendieron {item.num_equipos} equipos: "
            f"{', '.join(item.equipos)}"
        )

    print("Ejercicio 22:")
    for item in analizador.ejercicio_22():
        print(f"- {item.equipo}: {item.valor} ascensos")

    print("Ejercicio 23:")
    for item in analizador.ejercicio_23():
        print(f"- {item.equipo}: {item.valor} temporadas")

    print("Ejercicio 24:")
    for item in analizador.ejercicio_24():
        print(f"- {item.equipo}: {item.valor} temporadas")

    print("Ejercicio 25:")
    for item in analizador.ejercicio_25():
        print(f"- {item.equipo}: {item.valor} goles")

    print("Ejercicio 26:")
    for item in analizador.ejercicio_26():
        print(f"- {item.equipo}: {item.valor} goles")

    print("Ejercicio 27:")
    for item in analizador.ejercicio_27():
        print(
            f"- Temporada {item.temporada}: {item.goles} goles en {item.partidos} partidos. "
            f"Media: {item.media_goles:.2f} goles/partido"
        )

    print("Ejercicio 28:")
    for item in analizador.ejercicio_28():
        print(f"- Temporada {item.temporada}: Maximo goleador fue {', '.join(item.equipos)}")

    print("Ejercicio 29:")
    for item in analizador.ejercicio_29():
        print(f"- {item.equipo}: Racha de {item.valor} temporadas consecutivas siendo el maximo goleador")

    print("Ejercicio 30:")
    item = analizador.ejercicio_30()
    print(
        f"- {item.equipo_1} vs {item.equipo_2}: {item.num_jugadores} jugadores. "
        f"Ejemplos: {', '.join(item.ejemplos)}"
    )

    print("Ejercicio 31:")
    for item in analizador.ejercicio_31():
        print(
            f"- {item.jugador}: Promedio de {item.promedio_minutos:.1f} minutos por temporada "
            f"(Total: {item.minutos_totales} minutos en {item.temporadas} temporadas)"
        )

    print("Ejercicio 32:")
    for item in analizador.ejercicio_32():
        print(f"- {item.jugador} - Equipo: {item.equipo}, Anos fuera: {item.anios_fuera}")

    print("Ejercicio 33:")
    for item in analizador.ejercicio_33():
        print(f"- {item.jugador}: Racha de {int(item.valor)} temporadas consecutivas")


if __name__ == "__main__":
    main()
