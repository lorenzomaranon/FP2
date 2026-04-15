from openpyxl import Workbook

from nombre import Nombre


class Nomenclator:
    def __init__(self):
        self.nombres = []
        self._indice_nombres = {}
        self.decadas = []

    def registrar_decada(self, decada):
        if decada not in self.decadas:
            self.decadas.append(decada)

    def obtener_o_crear_nombre(self, texto, genero):
        clave = genero + "|" + texto.upper()
        if clave not in self._indice_nombres:
            nombre = Nombre(texto, genero)
            self._indice_nombres[clave] = nombre
            self.nombres.append(nombre)
        return self._indice_nombres[clave]

    def filtrar_por_genero(self, genero):
        if genero is None:
            return self.nombres

        resultado = []
        for nombre in self.nombres:
            if nombre.genero == genero:
                resultado.append(nombre)
        return resultado

    def escribir_excel(self, ruta_salida):
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Nomenclator"

        cabecera = ["NOMBRE", "GENERO", "FRECUENCIA ACUMULADA"]
        for decada in self.decadas:
            cabecera.append(decada + " FRECUENCIA")
            cabecera.append(decada + " POR MIL")
        hoja.append(cabecera)

        nombres_ordenados = sorted(
            self.nombres,
            key=lambda nombre: (nombre.genero, nombre.texto)
        )

        for nombre in nombres_ordenados:
            fila = [nombre.texto, nombre.genero, nombre.frecuencia_acumulada]
            for decada in self.decadas:
                registro = nombre.obtener_registro(decada)
                if registro is None:
                    fila.append("")
                    fila.append("")
                else:
                    fila.append(registro.frecuencia)
                    fila.append(registro.tanto_por_mil)
            hoja.append(fila)

        libro.save(ruta_salida)

    def nombre_con_mayor_frecuencia(self, genero=None):
        nombres_filtrados = self.filtrar_por_genero(genero)
        if len(nombres_filtrados) == 0:
            return None

        mejor_nombre = nombres_filtrados[0]
        for nombre in nombres_filtrados[1:]:
            if nombre.frecuencia_acumulada > mejor_nombre.frecuencia_acumulada:
                mejor_nombre = nombre
        return mejor_nombre

    def nombres_mas_usados(self, cantidad, genero=None):
        nombres_filtrados = self.filtrar_por_genero(genero)
        nombres_ordenados = sorted(
            nombres_filtrados,
            key=lambda nombre: (-nombre.frecuencia_acumulada, nombre.texto)
        )
        return nombres_ordenados[:cantidad]

    def frecuencia_por_inicial(self, genero=None):
        acumulados = {}
        nombres_filtrados = self.filtrar_por_genero(genero)

        for nombre in nombres_filtrados:
            inicial = nombre.obtener_inicial()
            if inicial not in acumulados:
                acumulados[inicial] = {}
                for decada in self.decadas:
                    acumulados[inicial][decada] = 0

            for registro in nombre.registros:
                acumulados[inicial][registro.decada] += registro.frecuencia

        resultado = {}
        for inicial in sorted(acumulados.keys()):
            lista_decadas = []
            for decada in self.decadas:
                lista_decadas.append((decada, acumulados[inicial][decada]))
            resultado[inicial] = lista_decadas

        return resultado

    def letra_mas_frecuente_por_decada(self, genero=None):
        datos_por_inicial = self.frecuencia_por_inicial(genero)
        resultado = {}

        for indice_decada in range(len(self.decadas)):
            decada = self.decadas[indice_decada]
            letra_mayor = ""
            frecuencia_mayor = 0
            total_decada = 0

            for inicial in datos_por_inicial:
                frecuencia = datos_por_inicial[inicial][indice_decada][1]
                total_decada += frecuencia
                if frecuencia > frecuencia_mayor:
                    frecuencia_mayor = frecuencia
                    letra_mayor = inicial

            porcentaje = 0
            if total_decada > 0:
                porcentaje = (frecuencia_mayor * 100) / total_decada

            resultado[decada] = (letra_mayor, porcentaje)

        return resultado

    def conteo_simples_y_compuestos(self, genero=None):
        resultado = {}
        for decada in self.decadas:
            resultado[decada] = [0, 0]

        nombres_filtrados = self.filtrar_por_genero(genero)
        for nombre in nombres_filtrados:
            indice = 1 if nombre.es_compuesto() else 0
            for registro in nombre.registros:
                resultado[registro.decada][indice] += registro.frecuencia

        resultado_final = {}
        for decada in self.decadas:
            resultado_final[decada] = (resultado[decada][0], resultado[decada][1])
        return resultado_final

    def porcentaje_simples_y_compuestos(self, genero=None):
        conteos = self.conteo_simples_y_compuestos(genero)
        resultado = []

        for decada in self.decadas:
            simples = conteos[decada][0]
            compuestos = conteos[decada][1]
            total = simples + compuestos

            porcentaje_simples = 0
            porcentaje_compuestos = 0
            if total > 0:
                porcentaje_simples = (simples * 100) / total
                porcentaje_compuestos = (compuestos * 100) / total

            resultado.append((decada, porcentaje_simples, porcentaje_compuestos))

        return resultado

    def longitud_media_por_decada(self, genero=None):
        suma_longitudes = {}
        suma_frecuencias = {}
        for decada in self.decadas:
            suma_longitudes[decada] = 0
            suma_frecuencias[decada] = 0

        nombres_filtrados = self.filtrar_por_genero(genero)
        for nombre in nombres_filtrados:
            longitud = nombre.obtener_longitud_sin_espacios()
            for registro in nombre.registros:
                suma_longitudes[registro.decada] += longitud * registro.frecuencia
                suma_frecuencias[registro.decada] += registro.frecuencia

        resultado = []
        for decada in self.decadas:
            media = 0
            if suma_frecuencias[decada] > 0:
                media = suma_longitudes[decada] / suma_frecuencias[decada]
            resultado.append((decada, media))

        return resultado

    def nombres_al_menos_n_decadas(self, cantidad_decadas, genero=None):
        resultado = []
        nombres_filtrados = self.filtrar_por_genero(genero)

        for nombre in nombres_filtrados:
            if len(nombre.registros) >= cantidad_decadas:
                resultado.append(nombre)

        resultado.sort(key=lambda nombre: (-len(nombre.registros), nombre.texto))
        return resultado

    def nombres_de_moda_inicial(self, cantidad_decadas, genero=None):
        resultado = []
        nombres_filtrados = self.filtrar_por_genero(genero)

        for nombre in nombres_filtrados:
            posiciones = self._obtener_posiciones_presentes(nombre)
            if len(posiciones) == 0:
                continue

            ultima_posicion = posiciones[-1]
            son_consecutivas_desde_el_inicio = posiciones == list(range(ultima_posicion + 1))

            if son_consecutivas_desde_el_inicio and len(posiciones) <= cantidad_decadas:
                resultado.append(nombre)

        resultado.sort(key=lambda nombre: (len(nombre.registros), nombre.texto))
        return resultado

    def nombres_de_moda_reciente(self, cantidad_decadas, genero=None):
        resultado = []
        nombres_filtrados = self.filtrar_por_genero(genero)
        ultima_decada = len(self.decadas) - 1

        for nombre in nombres_filtrados:
            posiciones = self._obtener_posiciones_presentes(nombre)
            if len(posiciones) == 0:
                continue

            primera_posicion = posiciones[0]
            son_consecutivas_hasta_el_final = posiciones == list(range(primera_posicion, ultima_decada + 1))

            if son_consecutivas_hasta_el_final and len(posiciones) <= cantidad_decadas:
                resultado.append(nombre)

        resultado.sort(key=lambda nombre: (len(nombre.registros), nombre.texto))
        return resultado

    def nombres_resurgidos(self, n, m, genero=None):
        resultado = []
        nombres_filtrados = self.filtrar_por_genero(genero)

        for nombre in nombres_filtrados:
            presencia = self._obtener_presencia_por_decada(nombre)
            if self._cumple_patron_resurgimiento(presencia, n, m):
                resultado.append(nombre)

        resultado.sort(key=lambda nombre: nombre.texto)
        return resultado

    def series_tanto_por_mil(self, lista_nombres):
        nombres_buscados = []
        for texto in lista_nombres:
            nombres_encontrados = self._buscar_por_texto(texto)
            for nombre in nombres_encontrados:
                nombres_buscados.append(nombre)

        resultado = {}
        for nombre in nombres_buscados:
            etiqueta = nombre.texto + " (" + nombre.genero + ")"
            serie = []
            for decada in self.decadas:
                registro = nombre.obtener_registro(decada)
                if registro is None:
                    serie.append((decada, 0))
                else:
                    serie.append((decada, registro.tanto_por_mil))
            resultado[etiqueta] = serie

        return resultado

    def mayores_incrementos_de_tanto_por_mil(self, cantidad):
        incrementos = []

        for nombre in self.nombres:
            serie = []
            for decada in self.decadas:
                registro = nombre.obtener_registro(decada)
                if registro is None:
                    serie.append(0)
                else:
                    serie.append(registro.tanto_por_mil)

            for indice in range(len(serie) - 1):
                incremento = serie[indice + 1] - serie[indice]
                if incremento > 0:
                    incrementos.append(
                        (
                            nombre.texto,
                            nombre.genero,
                            self.decadas[indice],
                            self.decadas[indice + 1],
                            incremento
                        )
                    )

        incrementos.sort(key=lambda dato: (-dato[4], dato[0], dato[1]))
        return incrementos[:cantidad]

    def suma_top_n_por_mil_por_decada(self, cantidad, genero=None):
        nombres_filtrados = self.filtrar_por_genero(genero)
        valores_por_decada = {}

        for decada in self.decadas:
            valores_por_decada[decada] = []

        for nombre in nombres_filtrados:
            for registro in nombre.registros:
                valores_por_decada[registro.decada].append(registro.tanto_por_mil)

        resultado = {}
        for decada in self.decadas:
            valores = sorted(valores_por_decada[decada], reverse=True)
            resultado[decada] = sum(valores[:cantidad])

        return resultado

    def _obtener_posiciones_presentes(self, nombre):
        posiciones = []
        for indice in range(len(self.decadas)):
            decada = self.decadas[indice]
            if nombre.obtener_registro(decada) is not None:
                posiciones.append(indice)
        return posiciones

    def _obtener_presencia_por_decada(self, nombre):
        presencia = []
        for decada in self.decadas:
            presencia.append(nombre.obtener_registro(decada) is not None)
        return presencia

    def _cumple_patron_resurgimiento(self, presencia, n, m):
        total = len(presencia)
        for inicio in range(total):
            fin_bloque_presente = inicio + n
            fin_bloque_ausente = fin_bloque_presente + m

            if fin_bloque_ausente >= total:
                continue

            if inicio > 0 and presencia[inicio - 1]:
                continue

            primer_bloque_valido = True
            for indice in range(inicio, fin_bloque_presente):
                if not presencia[indice]:
                    primer_bloque_valido = False
                    break

            if not primer_bloque_valido:
                continue

            bloque_ausente_valido = True
            for indice in range(fin_bloque_presente, fin_bloque_ausente):
                if presencia[indice]:
                    bloque_ausente_valido = False
                    break

            if not bloque_ausente_valido:
                continue

            if fin_bloque_ausente < total and presencia[fin_bloque_ausente]:
                return True

        return False

    def _buscar_por_texto(self, texto):
        texto_buscado = texto.strip().upper()
        encontrados = []
        for nombre in self.nombres:
            if nombre.texto.upper() == texto_buscado:
                encontrados.append(nombre)
        return encontrados
