class Lineas:
    def __init__(self):
        self.grafo_lineas = {}

    def agregar_linea(self, linea, estaciones):
        estaciones_ordenadas = []

        for estacion in estaciones:
            estaciones_ordenadas.append(estacion)

        self.grafo_lineas[linea] = estaciones_ordenadas

    def obtener_linea(self, nombre_linea):
        clave_buscada = str(nombre_linea).strip().upper()

        for linea in self.grafo_lineas:
            if linea.clave() == clave_buscada:
                return linea

        return None

    def obtener_estaciones_de_linea(self, nombre_linea):
        linea = self.obtener_linea(nombre_linea)
        if linea is None:
            return []

        return self.grafo_lineas[linea]

    def obtener_estacion(self, nombre_estacion):
        clave_buscada = str(nombre_estacion).strip().upper()

        for linea in self.grafo_lineas:
            estaciones = self.grafo_lineas[linea]
            for estacion in estaciones:
                if estacion.clave() == clave_buscada:
                    return estacion

        return None

    def numero_de_lineas(self):
        return len(self.grafo_lineas)

    def numero_de_estaciones_distintas(self):
        estaciones = self.obtener_todas_las_estaciones()
        return len(estaciones)

    def obtener_todas_las_estaciones(self):
        estaciones = []

        for linea in self.grafo_lineas:
            estaciones_linea = self.grafo_lineas[linea]
            for estacion in estaciones_linea:
                if estacion not in estaciones:
                    estaciones.append(estacion)

        return estaciones

    def to_estaciones(self):
        from estaciones import Estaciones

        estaciones = Estaciones()

        for linea in self.grafo_lineas:
            lista_estaciones = self.grafo_lineas[linea]
            posicion = 1

            for estacion in lista_estaciones:
                estaciones.agregar_estacion_si_no_existe(estacion)
                estaciones.agregar_linea_a_estacion(estacion, linea, posicion)
                posicion = posicion + 1

        return estaciones

    def es_linea_circular(self, nombre_linea):
        linea = self.obtener_linea(nombre_linea)
        if linea is None:
            return False

        return linea.escircular

    def lineas_con_mas_paradas(self):
        resultado = []
        maximo = 0

        for linea in self.grafo_lineas:
            numero_paradas = len(self.grafo_lineas[linea])

            if numero_paradas > maximo:
                maximo = numero_paradas
                resultado = []
                resultado.append((linea, numero_paradas))
            elif numero_paradas == maximo:
                resultado.append((linea, numero_paradas))

        return resultado

    def estan_en_misma_linea(self, nombre_estacion_1, nombre_estacion_2):
        clave_1 = str(nombre_estacion_1).strip().upper()
        clave_2 = str(nombre_estacion_2).strip().upper()
        lineas_comunes = []

        for linea in self.grafo_lineas:
            estaciones = self.grafo_lineas[linea]
            encontrada_1 = False
            encontrada_2 = False

            for estacion in estaciones:
                if estacion.clave() == clave_1:
                    encontrada_1 = True
                if estacion.clave() == clave_2:
                    encontrada_2 = True

            if encontrada_1 and encontrada_2:
                lineas_comunes.append(linea)

        return lineas_comunes

    def longitud_total_linea(self, nombre_linea):
        linea = self.obtener_linea(nombre_linea)
        if linea is None:
            raise ValueError("No existe la linea indicada.")

        estaciones = self.grafo_lineas[linea]
        total = 0

        for posicion in range(0, len(estaciones) - 1):
            estacion_1 = estaciones[posicion]
            estacion_2 = estaciones[posicion + 1]
            total = total + estacion_1.distancia_km(estacion_2)

        if linea.escircular and len(estaciones) > 1:
            primera = estaciones[0]
            ultima = estaciones[len(estaciones) - 1]
            total = total + ultima.distancia_km(primera)

        return total

    def linea_mas_larga(self):
        mejor_linea = None
        mejor_distancia = 0

        for linea in self.grafo_lineas:
            distancia = self.longitud_total_linea(linea.nombre)

            if mejor_linea is None or distancia > mejor_distancia:
                mejor_linea = linea
                mejor_distancia = distancia

        return mejor_linea, mejor_distancia

    def __eq__(self, otras_lineas):
        if not isinstance(otras_lineas, Lineas):
            return False

        if len(self.grafo_lineas) != len(otras_lineas.grafo_lineas):
            return False

        for linea in self.grafo_lineas:
            otra_linea = otras_lineas.obtener_linea(linea.nombre)
            if otra_linea is None:
                return False

            if linea.escircular != otra_linea.escircular:
                return False

            estaciones = self.grafo_lineas[linea]
            otras_estaciones = otras_lineas.grafo_lineas[otra_linea]

            if len(estaciones) != len(otras_estaciones):
                return False

            for posicion in range(0, len(estaciones)):
                if estaciones[posicion] != otras_estaciones[posicion]:
                    return False

        return True
