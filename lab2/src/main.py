import csv
import re
import tempfile
from collections import Counter
from pathlib import Path
from random import Random

from dataset import DataSet, DataSetClasificacion, DataSetRegresion
from factoria import FactoriaCSV, FactoriaXLS
from modelos import Clasificador_kNN, Regresor_kNN


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"


def imprimir_resumen(nombre: str, dataset: DataSet) -> None:
    total = len(dataset.registros)
    total_atributos = len(dataset.nombres_atributos)
    print(f"[{nombre}] registros={total}, atributos={total_atributos}")
    if total:
        print(f"  primer registro: {dataset.registros[0]}")


def imprimir_contexto_registro(dataset: DataSet, limite: int = 4) -> None:
    if not dataset.registros:
        return

    consulta = dataset.registros[0]
    pares = list(zip(dataset.nombres_atributos, consulta.datos))
    muestra = pares[:limite]

    print("  Contexto del caso de prueba (primer registro):")
    for nombre, valor in muestra:
        print(f"    {nombre} = {valor}")

    if len(pares) > limite:
        restantes = len(pares) - limite
        print(f"    ... ({restantes} atributos mas)")


def evaluar_clasificador_holdout(
    dataset: DataSetClasificacion, k: int, distancia: str
) -> tuple[float, int]:
    if len(dataset.registros) < 10:
        return 0.0, 0

    registros = dataset.registros.copy()
    Random(42).shuffle(registros)
    tam_test = max(1, len(registros) // 5)
    test = registros[:tam_test]
    entrenamiento = dataset.crear_subconjunto(registros[tam_test:])

    modelo = Clasificador_kNN(k=k, distancia=distancia)
    modelo.entrenar(entrenamiento)

    aciertos = 0
    for registro in test:
        if modelo.predecir(registro) == registro.objetivo:
            aciertos += 1

    return aciertos / len(test), len(test)


def evaluar_regresor_holdout(
    dataset: DataSetRegresion, k: int, distancia: str, pesos: list[float]
) -> tuple[float, int]:
    if len(dataset.registros) < 10:
        return 0.0, 0

    registros = dataset.registros.copy()
    Random(42).shuffle(registros)
    tam_test = max(1, len(registros) // 5)
    test = registros[:tam_test]
    entrenamiento = dataset.crear_subconjunto(registros[tam_test:])

    modelo = Regresor_kNN(k=k, distancia=distancia, pesos=pesos)
    modelo.entrenar(entrenamiento)

    error_total = 0.0
    for registro in test:
        pred = modelo.predecir(registro)
        error_total += abs(pred - float(registro.objetivo))

    return error_total / len(test), len(test)


def extraer_cabeceras_wine(ruta_wine_names: Path) -> list[str]:
    lineas = ruta_wine_names.read_text(encoding="utf-8", errors="ignore").splitlines()
    capturando = False
    atributos: list[str] = []

    for linea in lineas:
        if "The attributes are" in linea:
            capturando = True
            continue

        if not capturando:
            continue

        texto = linea.strip()
        coincidencia = re.match(r"^(\d+)\)\s*(.+)$", texto)
        if coincidencia is None:
            continue

        indice = int(coincidencia.group(1))
        if not (1 <= indice <= 13):
            continue

        nombre = " ".join(coincidencia.group(2).split())
        atributos.append(nombre)
        if len(atributos) == 13:
            break

    if len(atributos) != 13:
        raise ValueError("No fue posible extraer las 13 cabeceras de wine.names.")

    return ["Class"] + atributos


def crear_csv_temporal_wine(ruta_wine_data: Path, ruta_wine_names: Path) -> Path:
    cabeceras = extraer_cabeceras_wine(ruta_wine_names)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        suffix=".csv",
        delete=False,
    ) as temporal:
        escritor = csv.writer(temporal)
        escritor.writerow(cabeceras)

        with ruta_wine_data.open(mode="r", encoding="utf-8", newline="") as archivo_data:
            lector = csv.reader(archivo_data)
            for fila in lector:
                if not fila:
                    continue
                escritor.writerow([valor.strip() for valor in fila])

    return Path(temporal.name)


def probar_registro(dataset: DataSet) -> None:
    if len(dataset.registros) < 2:
        print("No hay suficientes registros para probar distancias.")
        return

    r0 = dataset.registros[0]
    r1 = dataset.registros[1]
    pesos = [1.0] * len(r0.datos)

    print("\n[Pruebas Registro]")
    print(f"  distancia euclidea: {r0.distancia_euclidea(r1):.4f}")
    print(f"  distancia manhattan: {r0.distancia_manhattan(r1):.4f}")
    print(f"  distancia ponderada: {r0.distancia_ponderada(r1, pesos):.4f}")

    minimos, maximos = dataset.calcular_min_max()
    r0_normalizado = r0.normalizar(minimos, maximos)
    print(f"  registro normalizado: {r0_normalizado}")

    vecinos = r0.k_vecinos(dataset.registros[1:21], k=5, tipo="euclidea")
    print(f"  indices de 5 vecinos (sobre muestra de 20): {vecinos}")


def probar_dataset(dataset: DataSet) -> None:
    print("\n[Pruebas DataSet]")
    minimos, maximos = dataset.calcular_min_max()
    if minimos and maximos:
        print(f"  minimos (primeros 5): {minimos[:5]}")
        print(f"  maximos (primeros 5): {maximos[:5]}")

    subconjunto = dataset.crear_subconjunto(dataset.registros[:50])
    print(f"  subconjunto creado con {len(subconjunto.registros)} registros")


def probar_clasificador(
    nombre: str,
    dataset: DataSetClasificacion,
    objetivo: str,
    mapa_etiquetas: dict[str, str] | None = None,
) -> None:
    if len(dataset.registros) < 6:
        print(f"\n[{nombre}] no hay suficientes registros para clasificar.")
        return

    k = 5
    distancia = "manhattan"
    entrenamiento = dataset.crear_subconjunto(dataset.registros[1:])
    consulta = dataset.registros[0]

    modelo = Clasificador_kNN(k=k, distancia=distancia)
    modelo.entrenar(entrenamiento)
    prediccion = modelo.predecir(consulta)

    indices_vecinos = consulta.k_vecinos(entrenamiento.registros, k=k, tipo=distancia)
    etiquetas_vecinas = [entrenamiento.registros[i].objetivo for i in indices_vecinos]
    votos = Counter(etiquetas_vecinas)
    acierto = prediccion == consulta.objetivo

    def texto_etiqueta(etiqueta: str) -> str:
        if mapa_etiquetas and etiqueta in mapa_etiquetas:
            return f"{etiqueta} ({mapa_etiquetas[etiqueta]})"
        return str(etiqueta)

    accuracy, total_test = evaluar_clasificador_holdout(dataset, k=k, distancia=distancia)

    print(f"\n[Clasificador kNN - {nombre}]")
    print(f"  Se esta prediciendo: {objetivo}")
    imprimir_contexto_registro(dataset, limite=4)
    print(f"  Configuracion: k={k}, distancia={distancia}")
    print(f"  Votos de los vecinos: {dict(votos)}")
    print(f"  Objetivo real: {texto_etiqueta(str(consulta.objetivo))}")
    print(f"  Prediccion: {texto_etiqueta(str(prediccion))}")
    print(f"  Resultado del caso: {'ACIERTO' if acierto else 'FALLO'}")
    if total_test:
        print(f"  Accuracy hold-out (20%, {total_test} casos): {accuracy:.2%}")


def probar_regresor(
    nombre: str,
    dataset: DataSetRegresion,
    objetivo: str,
    unidad: str = "",
) -> None:
    if len(dataset.registros) < 6:
        print(f"\n[{nombre}] no hay suficientes registros para regresion.")
        return

    k = 5
    distancia = "ponderada"
    entrenamiento = dataset.crear_subconjunto(dataset.registros[1:])
    consulta = dataset.registros[0]
    pesos = [1.0] * len(consulta.datos)

    modelo = Regresor_kNN(k=k, distancia=distancia, pesos=pesos)
    modelo.entrenar(entrenamiento)
    prediccion = modelo.predecir(consulta)

    indices_vecinos = consulta.k_vecinos(entrenamiento.registros, k=k, tipo=distancia, pesos=pesos)
    valores_vecinos = [float(entrenamiento.registros[i].objetivo) for i in indices_vecinos]
    valor_real = float(consulta.objetivo)
    error_abs = abs(prediccion - valor_real)
    mae, total_test = evaluar_regresor_holdout(dataset, k=k, distancia=distancia, pesos=pesos)

    sufijo_unidad = f" {unidad}" if unidad else ""

    print(f"\n[Regresor kNN - {nombre}]")
    print(f"  Se esta prediciendo: {objetivo}")
    imprimir_contexto_registro(dataset, limite=4)
    print(f"  Configuracion: k={k}, distancia={distancia}")
    print(f"  Objetivos de vecinos usados: {[round(v, 4) for v in valores_vecinos]}")
    print(f"  Valor real: {valor_real:.4f}{sufijo_unidad}")
    print(f"  Prediccion: {prediccion:.4f}{sufijo_unidad}")
    print(f"  Error absoluto: {error_abs:.4f}{sufijo_unidad}")
    if total_test:
        print(f"  MAE hold-out (20%, {total_test} casos): {mae:.4f}{sufijo_unidad}")


def main() -> None:
    ruta_boston = DATA_DIR / "BostonHousing.csv"
    ruta_diabetes = DATA_DIR / "diabetes.csv"
    ruta_iris = DATA_DIR / "iris.xlsx"
    ruta_wine_index = DATA_DIR / "wine" / "Index"
    ruta_wine_data = DATA_DIR / "wine" / "wine.data"
    ruta_wine_names = DATA_DIR / "wine" / "wine.names"

    print("=== Carga de datasets ===")
    dataset_diabetes = FactoriaCSV.crear_dataset_clasificacion(str(ruta_diabetes))
    dataset_boston = FactoriaCSV.crear_dataset_regresion(str(ruta_boston), indice_objetivo=-2)
    imprimir_resumen("Diabetes (clasificacion)", dataset_diabetes)
    imprimir_resumen("Boston (regresion, objetivo MEDV)", dataset_boston)

    print("\n=== Archivos wine ===")
    print(ruta_wine_index.read_text(encoding="utf-8", errors="ignore").strip())
    ruta_wine_csv = crear_csv_temporal_wine(ruta_wine_data, ruta_wine_names)
    try:
        dataset_wine = FactoriaCSV.crear_dataset_clasificacion(str(ruta_wine_csv), indice_objetivo=0)
    finally:
        ruta_wine_csv.unlink(missing_ok=True)
    imprimir_resumen("Wine (clasificacion)", dataset_wine)

    print("\n=== Archivo iris.xlsx ===")
    dataset_iris = None
    try:
        dataset_iris = FactoriaXLS.crear_dataset_clasificacion(str(ruta_iris))
        imprimir_resumen("Iris (clasificacion)", dataset_iris)
    except ImportError as error:
        print(f"No se pudo leer iris.xlsx: {error}")

    probar_registro(dataset_diabetes)
    probar_dataset(dataset_diabetes)

    probar_clasificador(
        "Diabetes",
        dataset_diabetes,
        objetivo="Outcome (1 = diabetes, 0 = no diabetes)",
        mapa_etiquetas={"0": "No diabetes", "1": "Diabetes"},
    )
    probar_clasificador(
        "Wine",
        dataset_wine,
        objetivo="Clase de vino (1, 2 o 3)",
    )
    if dataset_iris is not None:
        probar_clasificador(
            "Iris",
            dataset_iris,
            objetivo="Especie de flor (setosa, versicolor o virginica)",
        )

    probar_regresor(
        "BostonHousing",
        dataset_boston,
        objetivo="MEDV: valor mediano de vivienda",
        unidad="(miles de USD)",
    )


if __name__ == "__main__":
    main()
