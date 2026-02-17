import Departamento

class Universidad:
    """Clase contenedora principal."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.departamentos = []

    def agregar_departamento(self, depto: Departamento):
        self.departamentos.append(depto)