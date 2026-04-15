from registro_decada import RegistroDecada


class Nombre:
    def __init__(self, texto, genero):
        self.texto = texto
        self.genero = genero
        self.registros = []
        self.registros_por_decada = {}
        self.frecuencia_acumulada = 0

    def agregar_registro(self, decada, frecuencia, tanto_por_mil):
        registro = RegistroDecada(decada, frecuencia, tanto_por_mil)
        self.registros.append(registro)
        self.registros_por_decada[decada] = registro
        self.frecuencia_acumulada += frecuencia

    def obtener_registro(self, decada):
        return self.registros_por_decada.get(decada)

    def obtener_inicial(self):
        if self.texto == "":
            return ""
        return self.texto[0]

    def es_compuesto(self):
        partes = self.texto.split()
        return len(partes) > 1

    def obtener_longitud_sin_espacios(self):
        texto_sin_espacios = self.texto.replace(" ", "")
        return len(texto_sin_espacios)
