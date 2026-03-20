import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from dataset import DataSetClasificacion, DataSetRegresion
from factoria import FactoriaXLS
from Registro import RegistroClasificacion


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
EPSILON = 1e-12
K_VALUES = list(range(1, 52))


@dataclass(frozen=True)
class ResultadoBusqueda:
    dataset: str
    tarea: str
    preprocesado: str
    pesos: str
    k: int
    score: float


def cargar_wdbc(ruta_data: Path) -> DataSetClasificacion:
    dataset = DataSetClasificacion()
    dataset.nombres_atributos = [f"feature_{i}" for i in range(1, 31)]

    with ruta_data.open(mode="r", encoding="utf-8", newline="") as archivo:
        lector = csv.reader(archivo)
        for fila in lector:
            if not fila:
                continue

            diagnostico = fila[1].strip()
            atributos = [float(valor) for valor in fila[2:]]
            dataset.agregar_registro(RegistroClasificacion(atributos, diagnostico))

    return dataset


def extraer_matrices_clasificacion(dataset: DataSetClasificacion) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray([registro.datos for registro in dataset.registros], dtype=float)
    y = np.asarray([registro.objetivo for registro in dataset.registros], dtype=object)
    return x, y


def extraer_matrices_regresion(dataset: DataSetRegresion) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray([registro.datos for registro in dataset.registros], dtype=float)
    y = np.asarray([float(registro.objetivo) for registro in dataset.registros], dtype=float)
    return x, y


def crear_folds(n_muestras: int, n_folds: int = 5) -> list[np.ndarray]:
    indices = np.arange(n_muestras)
    fold_sizes = np.full(n_folds, n_muestras // n_folds, dtype=int)
    fold_sizes[: n_muestras % n_folds] += 1

    folds: list[np.ndarray] = []
    inicio = 0
    for tam in fold_sizes:
        fin = inicio + tam
        folds.append(indices[inicio:fin])
        inicio = fin

    return folds


def aplicar_preprocesado(
    x_train: np.ndarray,
    x_test: np.ndarray,
    nombre: str,
) -> tuple[np.ndarray, np.ndarray]:
    if nombre == "sin_preprocesado":
        return x_train.copy(), x_test.copy()

    if nombre == "normalizado":
        minimos = x_train.min(axis=0)
        maximos = x_train.max(axis=0)
        rangos = np.where((maximos - minimos) == 0.0, 1.0, maximos - minimos)
        return (x_train - minimos) / rangos, (x_test - minimos) / rangos

    if nombre == "estandarizado":
        medias = x_train.mean(axis=0)
        desvios = x_train.std(axis=0)
        desvios = np.where(desvios == 0.0, 1.0, desvios)
        return (x_train - medias) / desvios, (x_test - medias) / desvios

    raise ValueError(f"Preprocesado desconocido: {nombre}")


def pesos_clasificacion(x_train: np.ndarray, y_train: np.ndarray) -> dict[str, np.ndarray]:
    clases, y_cod = np.unique(y_train, return_inverse=True)
    varianzas = x_train.var(axis=0)
    rangos = x_train.max(axis=0) - x_train.min(axis=0)

    scores_f = np.zeros(x_train.shape[1], dtype=float)
    media_global = x_train.mean(axis=0)
    for indice_clase, _ in enumerate(clases):
        mascara = y_cod == indice_clase
        x_clase = x_train[mascara]
        if x_clase.size == 0:
            continue
        media_clase = x_clase.mean(axis=0)
        var_clase = x_clase.var(axis=0)
        scores_f += x_clase.shape[0] * (media_clase - media_global) ** 2 / (var_clase + EPSILON)

    return {
        "uniformes": np.ones(x_train.shape[1], dtype=float),
        "inversa_varianza": 1.0 / (varianzas + EPSILON),
        "inversa_rango": 1.0 / (rangos + EPSILON),
        "f_score": scores_f + EPSILON,
        "f_score_cuadrado": (scores_f + EPSILON) ** 2,
    }


def pesos_regresion(x_train: np.ndarray, y_train: np.ndarray) -> dict[str, np.ndarray]:
    varianzas = x_train.var(axis=0)
    rangos = x_train.max(axis=0) - x_train.min(axis=0)
    correlaciones = np.zeros(x_train.shape[1], dtype=float)

    y_centrado = y_train - y_train.mean()
    norma_y = np.sqrt(np.sum(y_centrado**2))
    for i in range(x_train.shape[1]):
        columna = x_train[:, i]
        columna_centrada = columna - columna.mean()
        norma_x = np.sqrt(np.sum(columna_centrada**2))
        if norma_x == 0.0 or norma_y == 0.0:
            correlaciones[i] = 0.0
        else:
            correlaciones[i] = abs(np.dot(columna_centrada, y_centrado) / (norma_x * norma_y))

    return {
        "uniformes": np.ones(x_train.shape[1], dtype=float),
        "inversa_varianza": 1.0 / (varianzas + EPSILON),
        "inversa_rango": 1.0 / (rangos + EPSILON),
        "correlacion": correlaciones + EPSILON,
        "correlacion_cuadrada": (correlaciones + EPSILON) ** 2,
    }


def matriz_distancias(
    x_train: np.ndarray,
    x_test: np.ndarray,
    pesos: np.ndarray,
) -> np.ndarray:
    raiz_pesos = np.sqrt(np.clip(pesos, a_min=0.0, a_max=None))
    train_ponderado = x_train * raiz_pesos
    test_ponderado = x_test * raiz_pesos

    norma_test = np.sum(test_ponderado**2, axis=1, keepdims=True)
    norma_train = np.sum(train_ponderado**2, axis=1)
    distancias = norma_test + norma_train - 2.0 * test_ponderado @ train_ponderado.T
    return np.maximum(distancias, 0.0)


def accuracy_para_k(
    vecinos_ordenados: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    k: int,
) -> float:
    aciertos = 0
    for i, indices in enumerate(vecinos_ordenados[:, :k]):
        etiquetas, conteos = np.unique(y_train[indices], return_counts=True)
        pred = etiquetas[np.argmax(conteos)]
        aciertos += int(pred == y_test[i])
    return aciertos / len(y_test)


def mse_para_k(
    vecinos_ordenados: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    k: int,
) -> float:
    vecinos = y_train[vecinos_ordenados[:, :k]]
    predicciones = vecinos.mean(axis=1)
    return float(np.mean((predicciones - y_test) ** 2))


def buscar_mejor_clasificacion(nombre: str, x: np.ndarray, y: np.ndarray) -> ResultadoBusqueda:
    folds = crear_folds(len(x), n_folds=5)
    mejor_resultado: ResultadoBusqueda | None = None

    for preprocesado in ("sin_preprocesado", "normalizado", "estandarizado"):
        for nombre_pesos in ("uniformes", "inversa_varianza", "inversa_rango", "f_score", "f_score_cuadrado"):
            scores_por_k: dict[int, list[float]] = {k: [] for k in K_VALUES}

            for fold_idx in range(5):
                test_idx = folds[fold_idx]
                train_idx = np.concatenate([folds[i] for i in range(5) if i != fold_idx])

                x_train, x_test = aplicar_preprocesado(x[train_idx], x[test_idx], preprocesado)
                y_train, y_test = y[train_idx], y[test_idx]

                pesos = pesos_clasificacion(x_train, y_train)[nombre_pesos]
                distancias = matriz_distancias(x_train, x_test, pesos)
                vecinos_ordenados = np.argsort(distancias, axis=1)[:, : max(K_VALUES)]

                for k in K_VALUES:
                    scores_por_k[k].append(accuracy_para_k(vecinos_ordenados, y_train, y_test, k))

            for k in K_VALUES:
                score = float(np.mean(scores_por_k[k]))
                candidato = ResultadoBusqueda(
                    dataset=nombre,
                    tarea="clasificacion",
                    preprocesado=preprocesado,
                    pesos=nombre_pesos,
                    k=k,
                    score=score,
                )
                if mejor_resultado is None or candidato.score > mejor_resultado.score:
                    mejor_resultado = candidato

    if mejor_resultado is None:
        raise RuntimeError("No se pudo calcular el mejor clasificador.")
    return mejor_resultado


def buscar_mejor_regresion(nombre: str, x: np.ndarray, y: np.ndarray) -> ResultadoBusqueda:
    folds = crear_folds(len(x), n_folds=5)
    mejor_resultado: ResultadoBusqueda | None = None

    for preprocesado in ("sin_preprocesado", "normalizado", "estandarizado"):
        for nombre_pesos in (
            "uniformes",
            "inversa_varianza",
            "inversa_rango",
            "correlacion",
            "correlacion_cuadrada",
        ):
            scores_por_k: dict[int, list[float]] = {k: [] for k in K_VALUES}

            for fold_idx in range(5):
                test_idx = folds[fold_idx]
                train_idx = np.concatenate([folds[i] for i in range(5) if i != fold_idx])

                x_train, x_test = aplicar_preprocesado(x[train_idx], x[test_idx], preprocesado)
                y_train, y_test = y[train_idx], y[test_idx]

                pesos = pesos_regresion(x_train, y_train)[nombre_pesos]
                distancias = matriz_distancias(x_train, x_test, pesos)
                vecinos_ordenados = np.argsort(distancias, axis=1)[:, : max(K_VALUES)]

                for k in K_VALUES:
                    scores_por_k[k].append(mse_para_k(vecinos_ordenados, y_train, y_test, k))

            for k in K_VALUES:
                score = float(np.mean(scores_por_k[k]))
                candidato = ResultadoBusqueda(
                    dataset=nombre,
                    tarea="regresion",
                    preprocesado=preprocesado,
                    pesos=nombre_pesos,
                    k=k,
                    score=score,
                )
                if mejor_resultado is None or candidato.score < mejor_resultado.score:
                    mejor_resultado = candidato

    if mejor_resultado is None:
        raise RuntimeError("No se pudo calcular el mejor regresor.")
    return mejor_resultado


def imprimir_resultado(resultado: ResultadoBusqueda) -> None:
    metrica = "accuracy" if resultado.tarea == "clasificacion" else "MSE"
    print(f"[{resultado.dataset}]")
    print(f"  tarea: {resultado.tarea}")
    print(f"  mejor k: {resultado.k}")
    print(f"  preprocesado: {resultado.preprocesado}")
    print(f"  pesos: {resultado.pesos}")
    print(f"  {metrica}: {resultado.score:.6f}")


def main() -> None:
    ruta_concrete = DATA_DIR / "concrete+compressive+strength" / "Concrete_Data.xls"
    ruta_wdbc = DATA_DIR / "breast+cancer+wisconsin+diagnostic" / "wdbc.data"

    dataset_concrete = FactoriaXLS.crear_dataset_regresion(str(ruta_concrete))
    dataset_wdbc = cargar_wdbc(ruta_wdbc)

    x_concrete, y_concrete = extraer_matrices_regresion(dataset_concrete)
    x_wdbc, y_wdbc = extraer_matrices_clasificacion(dataset_wdbc)

    print("Busqueda 5-fold CV sin shuffle")
    print(f"Concrete: {x_concrete.shape[0]} filas, {x_concrete.shape[1]} atributos")
    print(f"WDBC: {x_wdbc.shape[0]} filas, {x_wdbc.shape[1]} atributos")
    print()

    mejor_regresion = buscar_mejor_regresion("Concrete", x_concrete, y_concrete)
    mejor_clasificacion = buscar_mejor_clasificacion("WDBC", x_wdbc, y_wdbc)

    imprimir_resultado(mejor_regresion)
    print()
    imprimir_resultado(mejor_clasificacion)


if __name__ == "__main__":
    main()
