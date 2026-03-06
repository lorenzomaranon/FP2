import csv
import re
import tempfile
from pathlib import Path

from dataset import DataSet
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


def probar_clasificador(nombre: str, dataset) -> None:
    if len(dataset.registros) < 6:
        print(f"\n[{nombre}] no hay suficientes registros para clasificar.")
        return

    entrenamiento = dataset.crear_subconjunto(dataset.registros[1:])
    consulta = dataset.registros[0]

    modelo = Clasificador_kNN(k=5, distancia="manhattan")
    modelo.entrenar(entrenamiento)
    prediccion = modelo.predecir(consulta)

    print(f"\n[Clasificador kNN - {nombre}]")
    print(f"  objetivo real: {consulta.objetivo}")
    print(f"  prediccion: {prediccion}")


def probar_regresor(nombre: str, dataset) -> None:
    if len(dataset.registros) < 6:
        print(f"\n[{nombre}] no hay suficientes registros para regresion.")
        return

    entrenamiento = dataset.crear_subconjunto(dataset.registros[1:])
    consulta = dataset.registros[0]
    pesos = [1.0] * len(consulta.datos)

    modelo = Regresor_kNN(k=5, distancia="ponderada", pesos=pesos)
    modelo.entrenar(entrenamiento)
    prediccion = modelo.predecir(consulta)

    print(f"\n[Regresor kNN - {nombre}]")
    print(f"  objetivo real: {consulta.objetivo:.4f}")
    print(f"  prediccion: {prediccion:.4f}")


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

    probar_clasificador("Diabetes", dataset_diabetes)
    probar_clasificador("Wine", dataset_wine)
    if dataset_iris is not None:
        probar_clasificador("Iris", dataset_iris)

    probar_regresor("BostonHousing", dataset_boston)


if __name__ == "__main__":
    main()
