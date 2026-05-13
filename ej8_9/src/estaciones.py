class Estaciones:
    def __init__(self):
        self.grafo_estaciones = {}

    def agregar_estacion_si_no_existe(self, estacion):
        if estacion not in self.grafo_estaciones:
            self.grafo_estaciones[estacion] = {}

    def agregar_linea_a_estacion(self, estacion, linea, posicion):
        self.agregar_estacion_si_no_existe(estacion)
        self.grafo_estaciones[estacion][linea] = posicion

    def obtener_estacion(self, nombre_estacion):
        clave_buscada = str(nombre_estacion).strip().upper()

        for estacion in self.grafo_estaciones:
            if estacion.clave() == clave_buscada:
                return estacion

        return None

    def asignar_coordenadas(self, nombre_estacion, latitud, longitud):
        estacion = self.obtener_estacion(nombre_estacion)
        if estacion is None:
            raise ValueError("No existe la estacion indicada.")

        estacion.latitud = latitud
        estacion.longitud = longitud

    def obtener_lineas_de_estacion(self, nombre_estacion):
        estacion = self.obtener_estacion(nombre_estacion)
        if estacion is None:
            return []

        lineas = []
        for linea in self.grafo_estaciones[estacion]:
            lineas.append(linea)

        return lineas

    def obtener_todas_las_lineas(self):
        lineas = []

        for estacion in self.grafo_estaciones:
            for linea in self.grafo_estaciones[estacion]:
                if linea not in lineas:
                    lineas.append(linea)

        return lineas

    def to_lineas(self):
        from lineas import Lineas

        datos_por_linea = {}

        for estacion in self.grafo_estaciones:
            lineas_estacion = self.grafo_estaciones[estacion]

            for linea in lineas_estacion:
                posicion = lineas_estacion[linea]

                if linea not in datos_por_linea:
                    datos_por_linea[linea] = []

                datos_por_linea[linea].append((posicion, estacion))

        lineas = Lineas()

        for linea in datos_por_linea:
            datos = datos_por_linea[linea]
            datos.sort(key=self._obtener_posicion)

            estaciones_ordenadas = []
            for dato in datos:
                estaciones_ordenadas.append(dato[1])

            lineas.agregar_linea(linea, estaciones_ordenadas)

        return lineas

    def estaciones_con_mas_lineas(self):
        resultado = []
        maximo = 0

        for estacion in self.grafo_estaciones:
            numero_lineas = len(self.grafo_estaciones[estacion])

            if numero_lineas > maximo:
                maximo = numero_lineas
                resultado = []
                resultado.append((estacion, numero_lineas))
            elif numero_lineas == maximo:
                resultado.append((estacion, numero_lineas))

        return resultado

    def lineas_con_mas_paradas(self):
        lineas = self.to_lineas()
        return lineas.lineas_con_mas_paradas()

    def estan_en_misma_linea(self, nombre_estacion_1, nombre_estacion_2):
        estacion_1 = self.obtener_estacion(nombre_estacion_1)
        estacion_2 = self.obtener_estacion(nombre_estacion_2)

        if estacion_1 is None or estacion_2 is None:
            return []

        lineas_comunes = []
        lineas_1 = self.grafo_estaciones[estacion_1]
        lineas_2 = self.grafo_estaciones[estacion_2]

        for linea in lineas_1:
            if linea in lineas_2:
                lineas_comunes.append(linea)

        return lineas_comunes

    def conectadas_con_un_transbordo(self, nombre_estacion_1, nombre_estacion_2):
        estacion_1 = self.obtener_estacion(nombre_estacion_1)
        estacion_2 = self.obtener_estacion(nombre_estacion_2)

        if estacion_1 is None or estacion_2 is None:
            return []

        rutas = []
        lineas_1 = self.grafo_estaciones[estacion_1]
        lineas_2 = self.grafo_estaciones[estacion_2]

        for linea_1 in lineas_1:
            for linea_2 in lineas_2:
                if linea_1 != linea_2:
                    for posible_transbordo in self.grafo_estaciones:
                        if posible_transbordo != estacion_1 and posible_transbordo != estacion_2:
                            lineas_transbordo = self.grafo_estaciones[posible_transbordo]

                            if linea_1 in lineas_transbordo and linea_2 in lineas_transbordo:
                                rutas.append((linea_1, posible_transbordo, linea_2))

        return rutas

    def eliminar_linea(self, nombre_linea):
        linea_eliminada = self._buscar_linea(nombre_linea)
        if linea_eliminada is None:
            raise ValueError("No existe la linea indicada.")

        nuevo_grafo = Estaciones()

        for estacion in self.grafo_estaciones:
            nuevo_grafo.agregar_estacion_si_no_existe(estacion)
            lineas_estacion = self.grafo_estaciones[estacion]

            for linea in lineas_estacion:
                if linea != linea_eliminada:
                    posicion = lineas_estacion[linea]
                    nuevo_grafo.agregar_linea_a_estacion(estacion, linea, posicion)

        return nuevo_grafo

    def es_conexo(self):
        componentes = self.componentes_conexas()
        return len(componentes) <= 1

    def componentes_conexas(self):
        adyacencias = self._crear_diccionario_adyacencias()
        visitadas = {}
        componentes = []

        for estacion in adyacencias:
            if estacion not in visitadas:
                componente = self._recorrer_desde(estacion, adyacencias, visitadas)
                componentes.append(componente)

        return componentes

    def trayecto_minimo(self, nombre_origen, nombre_destino):
        origen = self.obtener_estacion(nombre_origen)
        destino = self.obtener_estacion(nombre_destino)

        if origen is None or destino is None:
            return []

        if origen == destino:
            return [origen]

        adyacencias = self._crear_diccionario_adyacencias()
        visitadas = {}
        anteriores = {}
        cola = []
        posicion_cola = 0

        visitadas[origen] = True
        cola.append(origen)

        while posicion_cola < len(cola):
            actual = cola[posicion_cola]
            posicion_cola = posicion_cola + 1

            for siguiente in adyacencias[actual]:
                if siguiente not in visitadas:
                    visitadas[siguiente] = True
                    anteriores[siguiente] = actual

                    if siguiente == destino:
                        return self._reconstruir_trayecto(origen, destino, anteriores)

                    cola.append(siguiente)

        return []

    def distancia(self, nombre_estacion_1, nombre_estacion_2):
        estacion_1 = self.obtener_estacion(nombre_estacion_1)
        estacion_2 = self.obtener_estacion(nombre_estacion_2)

        if estacion_1 is None or estacion_2 is None:
            raise ValueError("No existe alguna de las estaciones indicadas.")

        return estacion_1.distancia_km(estacion_2)

    def longitud_total_linea(self, nombre_linea):
        lineas = self.to_lineas()
        return lineas.longitud_total_linea(nombre_linea)

    def linea_mas_larga(self):
        lineas = self.to_lineas()
        return lineas.linea_mas_larga()

    def lineas_criticas(self):
        resultado = []
        lineas = self.obtener_todas_las_lineas()
        total_estaciones = len(self.grafo_estaciones)

        for linea in lineas:
            estaciones_sin_linea = self.eliminar_linea(linea.nombre)
            componentes = estaciones_sin_linea.componentes_conexas()
            mayor_componente = self._tamano_mayor_componente(componentes)
            estaciones_desconectadas = total_estaciones - mayor_componente
            paradas_linea = self._contar_paradas_de_linea(linea)
            proporcion = 0

            if paradas_linea > 0:
                proporcion = estaciones_desconectadas / paradas_linea

            resultado.append((linea, estaciones_desconectadas, proporcion))

        resultado.sort(key=self._clave_linea_critica)
        return resultado

    def __eq__(self, otras_estaciones):
        if not isinstance(otras_estaciones, Estaciones):
            return False

        if len(self.grafo_estaciones) != len(otras_estaciones.grafo_estaciones):
            return False

        for estacion in self.grafo_estaciones:
            otra_estacion = otras_estaciones.obtener_estacion(estacion.nombre)
            if otra_estacion is None:
                return False

            lineas = self.grafo_estaciones[estacion]
            otras_lineas = otras_estaciones.grafo_estaciones[otra_estacion]

            if len(lineas) != len(otras_lineas):
                return False

            for linea in lineas:
                encontrada = False

                for otra_linea in otras_lineas:
                    if linea == otra_linea:
                        encontrada = True
                        if linea.escircular != otra_linea.escircular:
                            return False
                        if lineas[linea] != otras_lineas[otra_linea]:
                            return False

                if not encontrada:
                    return False

        return True

    def _obtener_posicion(self, dato):
        return dato[0]

    def _buscar_linea(self, nombre_linea):
        clave_buscada = str(nombre_linea).strip().upper()

        for estacion in self.grafo_estaciones:
            for linea in self.grafo_estaciones[estacion]:
                if linea.clave() == clave_buscada:
                    return linea

        return None

    def _crear_diccionario_adyacencias(self):
        adyacencias = {}

        for estacion in self.grafo_estaciones:
            adyacencias[estacion] = []

        lineas = self.to_lineas()

        for linea in lineas.grafo_lineas:
            estaciones = lineas.grafo_lineas[linea]

            for posicion in range(0, len(estaciones) - 1):
                estacion_1 = estaciones[posicion]
                estacion_2 = estaciones[posicion + 1]
                self._agregar_vecinos(adyacencias, estacion_1, estacion_2)

            if linea.escircular and len(estaciones) > 1:
                primera = estaciones[0]
                ultima = estaciones[len(estaciones) - 1]
                self._agregar_vecinos(adyacencias, primera, ultima)

        return adyacencias

    def _agregar_vecinos(self, adyacencias, estacion_1, estacion_2):
        if estacion_2 not in adyacencias[estacion_1]:
            adyacencias[estacion_1].append(estacion_2)

        if estacion_1 not in adyacencias[estacion_2]:
            adyacencias[estacion_2].append(estacion_1)

    def _recorrer_desde(self, origen, adyacencias, visitadas):
        cola = []
        componente = []
        posicion_cola = 0

        cola.append(origen)
        visitadas[origen] = True

        while posicion_cola < len(cola):
            actual = cola[posicion_cola]
            posicion_cola = posicion_cola + 1
            componente.append(actual)

            for siguiente in adyacencias[actual]:
                if siguiente not in visitadas:
                    visitadas[siguiente] = True
                    cola.append(siguiente)

        return componente

    def _reconstruir_trayecto(self, origen, destino, anteriores):
        camino = []
        actual = destino

        while actual != origen:
            camino.append(actual)
            actual = anteriores[actual]

        camino.append(origen)
        camino.reverse()
        return camino

    def _tamano_mayor_componente(self, componentes):
        mayor = 0

        for componente in componentes:
            if len(componente) > mayor:
                mayor = len(componente)

        return mayor

    def _contar_paradas_de_linea(self, linea_buscada):
        contador = 0

        for estacion in self.grafo_estaciones:
            if linea_buscada in self.grafo_estaciones[estacion]:
                contador = contador + 1

        return contador

    def _clave_linea_critica(self, dato):
        linea = dato[0]
        estaciones_desconectadas = dato[1]
        proporcion = dato[2]
        return (-estaciones_desconectadas, -proporcion, linea.nombre)
