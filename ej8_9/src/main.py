import os

from factoria_metro import FactoriaMetro


def main():
    ruta_excel = buscar_excel()
    factoria = FactoriaMetro()
    lineas = factoria.leer_lineas_desde_excel(ruta_excel)
    estaciones = lineas.to_estaciones()

    print("Datos cargados correctamente.")
    print("Lineas:", lineas.numero_de_lineas())
    print("Estaciones distintas:", lineas.numero_de_estaciones_distintas())
    print()

    comprobar_conversiones(lineas, estaciones)
    mostrar_lineas_con_mas_paradas(lineas)
    mostrar_estaciones_con_mas_lineas(estaciones)
    mostrar_misma_linea(estaciones, "Sol", "Gran Vía")
    mostrar_un_transbordo(estaciones, "Pinar de Chamartín", "Aeropuerto T4")
    mostrar_trayecto_minimo(estaciones, "Pinar de Chamartín", "Aeropuerto T4")
    mostrar_conectividad(estaciones)
    mostrar_lineas_criticas(estaciones)
    mostrar_distancias(estaciones)


def buscar_excel():
    carpeta_src = os.path.dirname(__file__)
    carpeta_proyecto = os.path.dirname(carpeta_src)
    carpeta_data = os.path.join(carpeta_proyecto, "data")

    for nombre_archivo in os.listdir(carpeta_data):
        if nombre_archivo.lower().endswith(".xlsx"):
            return os.path.join(carpeta_data, nombre_archivo)

    raise ValueError("No se ha encontrado ningun archivo Excel en la carpeta data.")


def comprobar_conversiones(lineas, estaciones):
    estaciones_reconstruidas = lineas.to_estaciones()
    lineas_reconstruidas = estaciones.to_lineas()

    print("Conversion Lineas -> Estaciones correcta:", estaciones == estaciones_reconstruidas)
    print("Conversion Estaciones -> Lineas correcta:", lineas == lineas_reconstruidas)
    print()


def mostrar_lineas_con_mas_paradas(lineas):
    print("Lineas con mas paradas:")
    resultados = lineas.lineas_con_mas_paradas()

    for resultado in resultados:
        linea = resultado[0]
        numero_paradas = resultado[1]
        print("-", linea.nombre, "con", numero_paradas, "paradas")

    print()


def mostrar_estaciones_con_mas_lineas(estaciones):
    print("Estaciones con mas lineas:")
    resultados = estaciones.estaciones_con_mas_lineas()

    for resultado in resultados:
        estacion = resultado[0]
        numero_lineas = resultado[1]
        print("-", estacion.nombre, "con", numero_lineas, "lineas")

    print()


def mostrar_misma_linea(estaciones, estacion_1, estacion_2):
    lineas_comunes = estaciones.estan_en_misma_linea(estacion_1, estacion_2)
    print("Lineas comunes entre", estacion_1, "y", estacion_2 + ":")

    if len(lineas_comunes) == 0:
        print("- No estan en la misma linea")
    else:
        for linea in lineas_comunes:
            print("-", linea.nombre)

    print()


def mostrar_un_transbordo(estaciones, estacion_1, estacion_2):
    rutas = estaciones.conectadas_con_un_transbordo(estacion_1, estacion_2)
    print("Rutas con un transbordo entre", estacion_1, "y", estacion_2 + ":")

    if len(rutas) == 0:
        print("- No se ha encontrado una ruta con un unico transbordo")
    else:
        limite = 5
        contador = 0

        for ruta in rutas:
            if contador < limite:
                linea_1 = ruta[0]
                transbordo = ruta[1]
                linea_2 = ruta[2]
                print("-", linea_1.nombre, "->", transbordo.nombre, "->", linea_2.nombre)

            contador = contador + 1

        if len(rutas) > limite:
            print("-", "Hay", len(rutas) - limite, "rutas mas")

    print()


def mostrar_trayecto_minimo(estaciones, origen, destino):
    trayecto = estaciones.trayecto_minimo(origen, destino)
    print("Trayecto minimo entre", origen, "y", destino + ":")

    if len(trayecto) == 0:
        print("- No hay trayecto")
    else:
        nombres = []
        for estacion in trayecto:
            nombres.append(estacion.nombre)
        print(" -> ".join(nombres))
        print("Numero de estaciones del trayecto:", len(trayecto))

    print()


def mostrar_conectividad(estaciones):
    print("El grafo completo es conexo:", estaciones.es_conexo())

    estaciones_sin_linea_1 = estaciones.eliminar_linea("Linea 1")
    print("El grafo sin Linea 1 es conexo:", estaciones_sin_linea_1.es_conexo())
    print()


def mostrar_lineas_criticas(estaciones):
    print("Lineas criticas:")
    resultados = estaciones.lineas_criticas()
    limite = 5
    contador = 0

    for resultado in resultados:
        if contador < limite:
            linea = resultado[0]
            estaciones_desconectadas = resultado[1]
            proporcion = resultado[2]
            print("-", linea.nombre, "deja", estaciones_desconectadas, "estaciones fuera del mayor grupo",
                  "(proporcion:", round(proporcion, 2), ")")

        contador = contador + 1

    print()


def mostrar_distancias(estaciones):
    print("Distancias geograficas:")

    try:
        distancia = estaciones.distancia("Sol", "Gran Vía")
        print("- Sol - Gran Vía:", round(distancia, 3), "km")
    except ValueError as error:
        print("-", error)
        print("- El Excel no incluye latitud y longitud, por eso esta consulta queda preparada pero no se puede ejecutar con estos datos.")


if __name__ == "__main__":
    main()
