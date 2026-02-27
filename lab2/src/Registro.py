import math


class Registro:
    def __init__(self, datos: list[float], objetivo: object = None) -> None:
        self.datos = [float(valor) for valor in datos]
        self.objetivo = objetivo

    def _validar_dimension(self, otro: "Registro") -> None:
        if len(self.datos) != len(otro.datos):
            raise ValueError("Los registros deben tener la misma dimension.")

    def distancia_euclidea(self, otro: "Registro") -> float:
        self._validar_dimension(otro)
        return math.sqrt(sum((p - q) ** 2 for p, q in zip(self.datos, otro.datos)))

    def distancia_manhattan(self, otro: "Registro") -> float:
        self._validar_dimension(otro)
        return sum(abs(p - q) for p, q in zip(self.datos, otro.datos))

    def distancia_ponderada(self, otro: "Registro", pesos: list[float]) -> float:
        self._validar_dimension(otro)
        if len(pesos) != len(self.datos):
            raise ValueError("La lista de pesos debe tener la misma dimension que los registros.")

        suma_ponderada = sum(
            float(w) * (p - q) ** 2 for w, p, q in zip(pesos, self.datos, otro.datos)
        )
        return math.sqrt(suma_ponderada)

    def calcula_distancia(
        self, otro: "Registro", tipo: str = "euclidea", pesos: list[float] | None = None
    ) -> float:
        tipo_normalizado = tipo.strip().lower().replace("í", "i")

        if tipo_normalizado == "euclidea":
            return self.distancia_euclidea(otro)
        if tipo_normalizado == "manhattan":
            return self.distancia_manhattan(otro)
        if tipo_normalizado == "ponderada":
            if pesos is None:
                raise ValueError("Se requieren pesos para calcular la distancia ponderada.")
            return self.distancia_ponderada(otro, pesos)
        return self.distancia_euclidea(otro)

    def normalizar(self, minimos: list[float], maximos: list[float]) -> "Registro":
        if len(minimos) != len(self.datos) or len(maximos) != len(self.datos):
            raise ValueError("Las listas de minimos y maximos deben tener la misma dimension.")

        nuevos_datos: list[float] = []
        for valor, minimo, maximo in zip(self.datos, minimos, maximos):
            rango = float(maximo) - float(minimo)
            if rango == 0.0:
                nuevos_datos.append(0.0)
            else:
                nuevos_datos.append((valor - float(minimo)) / rango)

        return self.__class__(nuevos_datos, self.objetivo)

    def k_vecinos(
        self,
        lista_registros: list["Registro"],
        k: int,
        tipo: str = "euclidea",
        pesos: list[float] | None = None,
    ) -> list[int]:
        if k <= 0:
            raise ValueError("El valor de k debe ser mayor que 0.")

        distancias: list[tuple[float, int]] = []
        for indice, registro in enumerate(lista_registros):
            distancia = self.calcula_distancia(registro, tipo=tipo, pesos=pesos)
            distancias.append((distancia, indice))

        distancias.sort(key=lambda item: item[0])
        vecinos = min(k, len(distancias))
        return [indice for _, indice in distancias[:vecinos]]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(datos={self.datos})"

    def __str__(self) -> str:
        return self.__repr__()


class RegistroClasificacion(Registro):
    def __init__(self, datos: list[float], objetivo: str) -> None:
        if not isinstance(objetivo, str):
            raise TypeError("El objetivo de RegistroClasificacion debe ser una cadena.")
        super().__init__(datos, objetivo=objetivo)

    def normalizar(self, minimos: list[float], maximos: list[float]) -> "RegistroClasificacion":
        return super().normalizar(minimos, maximos)

    def __repr__(self) -> str:
        texto_padre = super().__repr__()
        return texto_padre[:-1] + f", objetivo={self.objetivo!r})"


class RegistroRegresion(Registro):
    def __init__(self, datos: list[float], objetivo: float) -> None:
        if isinstance(objetivo, bool) or not isinstance(objetivo, (int, float)):
            raise TypeError("El objetivo de RegistroRegresion debe ser un valor real.")
        super().__init__(datos, objetivo=float(objetivo))

    def normalizar(self, minimos: list[float], maximos: list[float]) -> "RegistroRegresion":
        return super().normalizar(minimos, maximos)

    def __repr__(self) -> str:
        texto_padre = super().__repr__()
        return texto_padre[:-1] + f", objetivo={self.objetivo!r})"
