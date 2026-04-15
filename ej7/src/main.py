from pathlib import Path

from factoria_nomenclator import FactoriaNomenclator
from graficador_nombres import GraficadorNombres


def imprimir_nombre(titulo, nombre):
    print(titulo)
    if nombre is None:
        print("No hay datos")
    else:
        print(nombre.texto, "-", nombre.genero, "-", nombre.frecuencia_acumulada)
    print()


def imprimir_lista_nombres(titulo, nombres):
    print(titulo)
    for nombre in nombres:
        print(nombre.texto, "-", nombre.genero, "-", nombre.frecuencia_acumulada)
    print()


def imprimir_diccionario_iniciales(titulo, diccionario):
    print(titulo)
    for clave in sorted(diccionario.keys()):
        print(clave, "->", diccionario[clave])
    print()


def imprimir_diccionario_simple(titulo, diccionario):
    print(titulo)
    for clave in diccionario:
        print(clave, "->", diccionario[clave])
    print()


def imprimir_lista_tuplas(titulo, lista):
    print(titulo)
    for elemento in lista:
        print(elemento)
    print()


def main():
    carpeta_base = Path(__file__).resolve().parents[1]
    ruta_excel = carpeta_base / "data" / "frecuencia_nombres.xlsx"
    carpeta_salida = carpeta_base / "data" / "salida"
    carpeta_salida.mkdir(exist_ok=True)

    nomenclator = FactoriaNomenclator.desde_excel(ruta_excel)

    ruta_excel_salida = carpeta_salida / "nomenclator.xlsx"
    nomenclator.escribir_excel(ruta_excel_salida)

    imprimir_nombre(
        "Nombre con mayor frecuencia acumulada:",
        nomenclator.nombre_con_mayor_frecuencia()
    )
    imprimir_nombre(
        "Nombre masculino con mayor frecuencia acumulada:",
        nomenclator.nombre_con_mayor_frecuencia("H")
    )
    imprimir_nombre(
        "Nombre femenino con mayor frecuencia acumulada:",
        nomenclator.nombre_con_mayor_frecuencia("M")
    )

    imprimir_lista_nombres(
        "5 nombres mas usados del historico:",
        nomenclator.nombres_mas_usados(5)
    )
    imprimir_lista_nombres(
        "5 nombres masculinos mas usados del historico:",
        nomenclator.nombres_mas_usados(5, "H")
    )
    imprimir_lista_nombres(
        "5 nombres femeninos mas usados del historico:",
        nomenclator.nombres_mas_usados(5, "M")
    )

    imprimir_diccionario_iniciales(
        "Frecuencia absoluta por inicial:",
        nomenclator.frecuencia_por_inicial()
    )
    imprimir_diccionario_simple(
        "Letra mas frecuente por decada:",
        nomenclator.letra_mas_frecuente_por_decada()
    )
    imprimir_diccionario_simple(
        "Conteo de nombres simples y compuestos:",
        nomenclator.conteo_simples_y_compuestos()
    )
    imprimir_lista_tuplas(
        "Porcentaje de nombres simples y compuestos:",
        nomenclator.porcentaje_simples_y_compuestos()
    )
    imprimir_lista_tuplas(
        "Longitud media de los nombres por decada:",
        nomenclator.longitud_media_por_decada()
    )
    imprimir_lista_nombres(
        "Nombres que han estado al menos 8 decadas:",
        nomenclator.nombres_al_menos_n_decadas(8)
    )
    imprimir_lista_nombres(
        "Nombres de moda en las primeras 3 decadas o menos:",
        nomenclator.nombres_de_moda_inicial(3)
    )
    imprimir_lista_nombres(
        "Nombres de moda solo en las ultimas 3 decadas:",
        nomenclator.nombres_de_moda_reciente(3)
    )
    imprimir_lista_nombres(
        "Nombres que estuvieron 2 decadas, desaparecieron 2 y resurgieron:",
        nomenclator.nombres_resurgidos(2, 2)
    )
    imprimir_lista_tuplas(
        "Mayores incrementos de tanto por mil:",
        nomenclator.mayores_incrementos_de_tanto_por_mil(10)
    )
    imprimir_diccionario_simple(
        "Suma del tanto por mil de los 10 nombres mas frecuentes por decada:",
        nomenclator.suma_top_n_por_mil_por_decada(10)
    )

    try:
        GraficadorNombres.graficar_tendencias(
            nomenclator,
            ["JOSE", "ANTONIO", "MARIA", "CARMEN", "LUCIA", "HUGO"],
            carpeta_salida / "tendencia_nombres.png"
        )
        GraficadorNombres.graficar_diversificacion(
            nomenclator,
            10,
            None,
            carpeta_salida / "diversificacion.png"
        )
        print("Graficos generados en:", carpeta_salida)
    except ImportError:
        print("No se han generado los graficos porque matplotlib no esta instalado.")

    print("Excel generado en:", ruta_excel_salida)


if __name__ == "__main__":
    main()
