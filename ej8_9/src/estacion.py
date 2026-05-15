import math


class Estacion:
    def __init__(self, nombre, latitud=None, longitud=None):
        self.nombre = str(nombre).strip()
        self.latitud = latitud
        self.longitud = longitud

    def clave(self):
        return self.nombre.strip().upper()

    def tiene_coordenadas(self):
        return self.latitud is not None and self.longitud is not None

    def distancia_km(self, otra_estacion):
        if not self.tiene_coordenadas() or not otra_estacion.tiene_coordenadas():
            mensaje = "No se puede calcular la distancia porque faltan coordenadas."
            raise ValueError(mensaje)

        radio_tierra = 6371.0

        latitud_1 = math.radians(float(self.latitud))
        longitud_1 = math.radians(float(self.longitud))
        latitud_2 = math.radians(float(otra_estacion.latitud))
        longitud_2 = math.radians(float(otra_estacion.longitud))

        diferencia_latitud = latitud_2 - latitud_1
        diferencia_longitud = longitud_2 - longitud_1

        parte_1 = math.sin(diferencia_latitud / 2) ** 2
        parte_2 = math.cos(latitud_1) * math.cos(latitud_2)
        parte_3 = math.sin(diferencia_longitud / 2) ** 2
        valor = parte_1 + parte_2 * parte_3

        angulo = 2 * math.atan2(math.sqrt(valor), math.sqrt(1 - valor))
        return radio_tierra * angulo

    def __eq__(self, otra_estacion):
        if not isinstance(otra_estacion, Estacion):
            return False

        return self.clave() == otra_estacion.clave()

    def __hash__(self):
        return hash(self.clave())

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return self.nombre
