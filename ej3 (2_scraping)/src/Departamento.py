class Departamento:
    """Clase que representa un departamento individual."""
    def __init__(self, nombre, etc, tc, tp, total, exp, sede=None):
        self.nombre = nombre
        self.numero_etc = etc
        self.profesores_tc = tc
        self.profesores_tp = tp
        self.total_profesores = total
        self.coef_experimentalidad = exp
        self.sede = sede

    def __repr__(self):
        return f"Departamento('{self.nombre}')"
    
    def getCargaReal(self):
        
        return (self.numero_etc * self.coef_experimentalidad)/self.total_profesores
    
    