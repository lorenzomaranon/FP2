from __future__ import annotations

from pathlib import Path

from boletin5_poo import FactoriaLiga


def main() -> None:
    ruta_excel = Path(__file__).resolve().parents[1] / "data" / "Plantillas1D-2017-18.xls"
    liga = FactoriaLiga.desde_excel(ruta_excel)

    print(f"Temporadas cargadas: {liga.num_temporadas}")
    print(f"Temporadas no jugadas: {liga.num_temporadas_no_jugadas}")

    e1 = liga.ejercicio_1()
    print(f"Ejercicio 1: {e1.jugador} ({e1.equipo} - {e1.temporada}) | Partidos: {e1.partidos} | Goles: {e1.goles}")

    e2 = liga.ejercicio_2()
    print(f"Ejercicio 2: {e2.jugador}: {int(e2.valor)} goles")

    e3 = liga.ejercicio_3()
    print(f"Ejercicio 3: {e3.jugador} - Equipos: {', '.join(e3.equipos)}")

    e4 = liga.ejercicio_4()
    print(f"Ejercicio 4: {e4.jugador} - Equipo: {e4.equipo}, Partidos: {e4.valor}")

    e5 = liga.ejercicio_5()
    print(f"Ejercicio 5: {e5.jugador} con {int(e5.valor)} minutos")

    print("Ejercicio 6:")
    for item in liga.ejercicio_6():
        print(f"- {item.jugador} - Equipos: {', '.join(item.equipos)}")

    print("Ejercicio 7:")
    for item in liga.ejercicio_7():
        print(f"- {item.jugador} - Equipo: {item.equipo}, Temporadas seguidas: {item.valor}")

    print("Ejercicio 8:")
    for item in liga.ejercicio_8():
        print(f"- {item.jugador_1} & {item.jugador_2} - Equipo: {item.equipo}, Minutos juntos: {item.minutos_juntos}")

    print("Ejercicio 9:")
    for item in liga.ejercicio_9():
        print(f"- {item.jugador}: {int(item.valor)} partidos enteros jugados")

    print("Ejercicio 10:")
    for item in liga.ejercicio_10():
        print(f"- {item.equipo} ({item.temporada}): {item.valor} tarjetas conjuntas")

    print("Ejercicio 11:")
    for item in liga.ejercicio_11():
        print(f"- {item.jugador}: {item.goles} goles. Marca un gol cada {round(item.minutos_por_gol)} minutos")

    print("Ejercicio 12:")
    for item in liga.ejercicio_12():
        print(f"- {item.jugador}: {item.anios_activo} anos en activo (De {item.inicio} a {item.fin})")

    print("Ejercicio 13:")
    for item in liga.ejercicio_13():
        print(f"- {item.jugador}: {int(item.valor)} partidos disputados de forma impoluta")

    print("Ejercicio 14:")
    for item in liga.ejercicio_14():
        print(f"- {item.jugador}: Cambiado en {int(item.valor)} ocasiones")

    print("Ejercicio 15:")
    for item in liga.ejercicio_15():
        print(f"- {item.jugador}: {item.goles} goles. Todos anotados en la {item.temporada}")

    print("Ejercicio 16:")
    for item in liga.ejercicio_16():
        print(f"- {item.jugador}: {item.goles} goles. Marca un gol cada {item.minutos_por_gol:.1f} minutos")


if __name__ == "__main__":
    main()
