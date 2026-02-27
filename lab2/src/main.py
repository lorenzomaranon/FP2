import csv
import tempfile
from pathlib import Path

from Registro import Registro, RegistroClasificacion, RegistroRegresion
from dataset import DataSetClasificacion, DataSetRegresion
from factoria import FactoriaCSV, FactoriaXLS
from modelos import Clasificador_kNN, Regresor_kNN


def titulo(texto: str) -> None:
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def probar_registro() -> None:
    titulo("1) Pruebas de la clase Registro")

    r1 = Registro([1.0, 2.0, 3.0, 4.0])
    r2 = Registro([2.0, 2.5, 2.0, 8.0])
    pesos = [1.0, 0.5, 2.0, 1.0]

    print("r1:", r1)
    print("r2:", r2)
    print("Distancia euclidea:", round(r1.distancia_euclidea(r2), 4))
    print("Distancia manhattan:", round(r1.distancia_manhattan(r2), 4))
    print("Distancia ponderada:", round(r1.distancia_ponderada(r2, pesos), 4))

    r1_norm = r1.normalizar([0.0, 0.0, 0.0, 0.0], [10.0, 10.0, 10.0, 10.0])
    print("r1 normalizado:", r1_norm)

    base = [
        Registro([1.0, 2.0, 3.0, 4.0]),
        Registro([2.0, 2.5, 2.0, 8.0]),
        Registro([1.2, 1.9, 2.8, 4.1]),
        Registro([9.0, 9.0, 9.0, 9.0]),
    ]
    print("Indices de 2 vecinos mas cercanos a r1:", r1.k_vecinos(base, k=2, tipo="euclidea"))


def construir_dataset_manual() -> tuple[DataSetClasificacion, DataSetRegresion]:
    titulo("2) Pruebas de DataSet y Registros especializados")

    ds_clas = DataSetClasificacion()
    ds_clas.set_cabeceras(["x1", "x2", "etiqueta"])
    ds_clas.agregar_registro(RegistroClasificacion([1.0, 1.0], "A"))
    ds_clas.agregar_registro(RegistroClasificacion([1.8, 1.2], "A"))
    ds_clas.agregar_registro(RegistroClasificacion([8.5, 8.9], "B"))
    ds_clas.agregar_registro(RegistroClasificacion([9.1, 8.2], "B"))

    mins_c, maxs_c = ds_clas.calcular_min_max()
    print("Clasificacion - nombres atributos:", ds_clas.nombres_atributos)
    print("Clasificacion - minimos:", mins_c)
    print("Clasificacion - maximos:", maxs_c)

    sub_clas = ds_clas.crear_subconjunto(ds_clas.registros[:2])
    print("Subconjunto clasificacion (2 primeros):", len(sub_clas.registros), "registros")

    ds_reg = DataSetRegresion()
    ds_reg.set_cabeceras(["x1", "x2", "precio"])
    ds_reg.agregar_registro(RegistroRegresion([1.0, 1.0], 10.0))
    ds_reg.agregar_registro(RegistroRegresion([2.0, 1.0], 14.0))
    ds_reg.agregar_registro(RegistroRegresion([8.0, 9.0], 50.0))
    ds_reg.agregar_registro(RegistroRegresion([9.0, 8.0], 53.0))

    mins_r, maxs_r = ds_reg.calcular_min_max()
    print("Regresion - nombres atributos:", ds_reg.nombres_atributos)
    print("Regresion - minimos:", mins_r)
    print("Regresion - maximos:", maxs_r)

    sub_reg = ds_reg.crear_subconjunto(ds_reg.registros[1:3])
    print("Subconjunto regresion (indices 1 y 2):", len(sub_reg.registros), "registros")

    return ds_clas, ds_reg


def probar_modelos(ds_clas: DataSetClasificacion, ds_reg: DataSetRegresion) -> None:
    titulo("3) Pruebas de modelos")

    clasificador = Clasificador_kNN(k=3, distancia="euclidea")
    clasificador.entrenar(ds_clas)
    consulta_c = RegistroClasificacion([1.4, 1.1], "?")
    pred_c = clasificador.predecir(consulta_c)
    print("Prediccion clasificacion para", consulta_c.datos, "->", pred_c)

    regresor = Regresor_kNN(k=2, distancia="manhattan")
    regresor.entrenar(ds_reg)
    consulta_r = RegistroRegresion([8.7, 8.1], 0.0)
    pred_r = regresor.predecir(consulta_r)
    print("Prediccion regresion para", consulta_r.datos, "->", round(pred_r, 4))


def escribir_csv(path_csv: Path, cabecera: list[str], filas: list[list[object]]) -> None:
    with open(path_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cabecera)
        writer.writerows(filas)


def probar_factorias_csv() -> None:
    titulo("4) Pruebas de FactoriaCSV")

    with tempfile.TemporaryDirectory() as tmp:
        ruta_tmp = Path(tmp)

        archivo_clas = ruta_tmp / "clasificacion.csv"
        escribir_csv(
            archivo_clas,
            ["x1", "x2", "etiqueta"],
            [
                [1.0, 1.0, "A"],
                [2.0, 1.5, "A"],
                [8.0, 9.0, "B"],
            ],
        )

        ds_clas = FactoriaCSV.crear_dataset_clasificacion(str(archivo_clas))
        print("CSV clasificacion -> registros:", len(ds_clas.registros), "cabeceras:", ds_clas.nombres_atributos)

        archivo_reg = ruta_tmp / "regresion.csv"
        escribir_csv(
            archivo_reg,
            ["objetivo", "x1", "x2"],
            [
                [10.0, 1.0, 1.0],
                [12.0, 1.5, 1.2],
                [40.0, 7.5, 8.0],
            ],
        )

        ds_reg = FactoriaCSV.crear_dataset_regresion(str(archivo_reg), indice_objetivo=0)
        print("CSV regresion -> registros:", len(ds_reg.registros), "cabeceras:", ds_reg.nombres_atributos)


def probar_factorias_xls() -> None:
    titulo("5) Pruebas de FactoriaXLS (opcional)")

    try:
        import pandas as pd
    except ImportError:
        print("Saltado: pandas no esta instalado.")
        return

    with tempfile.TemporaryDirectory() as tmp:
        ruta_tmp = Path(tmp)

        archivo_xls = ruta_tmp / "clasificacion.xlsx"
        df = pd.DataFrame(
            {
                "x1": [1.0, 2.0, 8.0],
                "x2": [1.1, 1.3, 9.2],
                "etiqueta": ["A", "A", "B"],
            }
        )

        try:
            df.to_excel(archivo_xls, index=False)
            ds = FactoriaXLS.crear_dataset_clasificacion(str(archivo_xls))
            print("XLS clasificacion -> registros:", len(ds.registros), "cabeceras:", ds.nombres_atributos)
        except Exception as exc:
            print("Saltado: no se pudo probar Excel en este entorno ->", exc)


def main() -> None:
    print("INICIO DE PRUEBAS LABORATORIO 2")

    probar_registro()
    ds_clas, ds_reg = construir_dataset_manual()
    probar_modelos(ds_clas, ds_reg)
    probar_factorias_csv()
    probar_factorias_xls()

    print("\nFIN DE PRUEBAS")


if __name__ == "__main__":
    main()
