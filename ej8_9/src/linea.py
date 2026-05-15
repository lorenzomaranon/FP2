class Linea:
    def __init__(self, nombre, escircular=False):
        self.nombre = str(nombre).strip()
        self.escircular = escircular

    def clave(self):
        return self.nombre.strip().upper()

    def __eq__(self, otra_linea):
        if not isinstance(otra_linea, Linea):
            return False

        return self.clave() == otra_linea.clave()

    def __hash__(self):
        return hash(self.clave())

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return self.nombre
