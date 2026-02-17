class Departamento:
    """Clase que representa un departamento individual."""
    def __init__(self, nombre, etc, tc, tp, total, exp):
        self.nombre = nombre
        self.numero_etc = etc
        self.profesores_tc = tc
        self.profesores_tp = tp
        self.total_profesores = total
        self.coef_experimentalidad = exp

    def __repr__(self):
        return f"Departamento('{self.nombre}')"