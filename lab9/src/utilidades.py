from __future__ import annotations

import math


def media(valores: list[float]) -> float:
    if not valores:
        raise ValueError("La lista de valores no puede estar vacia.")
    return sum(valores) / float(len(valores))


def desviacion_tipica(valores: list[float]) -> float:
    promedio = media(valores)
    varianza = 0.0

    for valor in valores:
        diferencia = valor - promedio
        varianza += diferencia * diferencia

    varianza /= float(len(valores))
    return math.sqrt(varianza)


def mae(reales: list[float], predicciones: list[float]) -> float:
    if len(reales) != len(predicciones):
        raise ValueError("Las listas reales y predicciones deben tener la misma longitud.")
    if not reales:
        raise ValueError("Se requiere al menos un valor para calcular MAE.")

    error_total = 0.0
    for real, prediccion in zip(reales, predicciones):
        error_total += abs(float(real) - float(prediccion))

    return error_total / float(len(reales))


def correlacion_pearson_absoluta(columna: list[float], objetivos: list[float]) -> float:
    if len(columna) != len(objetivos):
        raise ValueError("La columna y los objetivos deben tener la misma longitud.")
    if not columna:
        return 0.0

    media_x = media(columna)
    media_y = media(objetivos)
    numerador = 0.0
    suma_x = 0.0
    suma_y = 0.0

    for valor_x, valor_y in zip(columna, objetivos):
        delta_x = valor_x - media_x
        delta_y = valor_y - media_y
        numerador += delta_x * delta_y
        suma_x += delta_x * delta_x
        suma_y += delta_y * delta_y

    if suma_x == 0.0 or suma_y == 0.0:
        return 0.0

    return abs(numerador / math.sqrt(suma_x * suma_y))


def acotar(valor: float, minimo: float, maximo: float) -> float:
    if valor < minimo:
        return minimo
    if valor > maximo:
        return maximo
    return valor

