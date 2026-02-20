import math

class Registro:
    def __init__(self, atributos):
        # El constructor acepta un vector (List) de números flotantes [cite: 43]
        self.atributos = [float(x) for x in atributos]

    def distancia_euclidea(self, otro):
        # Calcula la distancia Euclídea entre dos Registros [cite: 44]
        return math.sqrt(sum((p - q) ** 2 for p, q in zip(self.atributos, otro.atributos)))

    def distancia_manhattan(self, otro):
        # Calcula la distancia Manhattan entre dos Registros [cite: 45]
        return sum(abs(p - q) for p, q in zip(self.atributos, otro.atributos))

    def distancia_ponderada(self, otro, pesos):
        # Aplica la fórmula: Wi * (Pi - qi)² [cite: 47, 48]
        
        suma_ponderada = sum(w * (p - q) ** 2 for w, p, q in zip(pesos, self.atributos, otro.atributos))
        return math.sqrt(suma_ponderada)

    def calcula_distancia(self, otro, tipo="euclídea", pesos=None):
        # Selector de distancia según la cadena recibida [cite: 49]
        if tipo == "euclídea":
            return self.distancia_euclidea(otro)
        elif tipo == "manhattan":
            return self.distancia_manhattan(otro)
        elif tipo == "ponderada":
            if pesos is None:
                raise ValueError("Se requieren pesos para la distancia ponderada") 
            return self.distancia_ponderada(otro, pesos)
        else:
            return self.distancia_euclidea(otro) # Por defecto euclídea [cite: 49]

    def normalizar(self, minimos, maximos):
        # Escala los valores usando (x - min) / (max - min) [cite: 51, 52]
        atributos_normalizados = []
        for x, mi, ma in zip(self.atributos, minimos, maximos):
            x_prime = (x - mi) / (ma - mi) 
            atributos_normalizados.append(x_prime)
        
        # Devuelve un NUEVO objeto Registro con los valores normalizados [cite: 54]
        return Registro(atributos_normalizados)

    def k_vecinos(self, lista_registros, k, tipo="euclídea", pesos=None):
        # 1. Calcular distancias entre el objeto actual y todos los de la lista [cite: 63, 64]
        distancias = []
        for i, reg_lista in enumerate(lista_registros):
            dist = self.calcula_distancia(reg_lista, tipo, pesos)
            distancias.append((dist, i)) # Guardamos (distancia, índice original)
        
        # 2. Ordenar por distancia (de menor a mayor)
        distancias.sort(key=lambda x: x[0])
        
        # 3. Devolver los índices de los k puntos más cercanos 
        indices_cercanos = [idx for dist, idx in distancias[:k]]
        return indices_cercanos

    def __str__(self):
        # Auxiliar para visualizar el objeto en el test
        return f"Registro({[round(a, 3) for a in self.atributos]})"