import Departamento

class Universidad:
    """Clase contenedora principal."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.departamentos = []

    def agregar_departamento(self, depto: Departamento):
        self.departamentos.append(depto)
    
    def getMayorCarga(self, n: int):
        return sorted(self.departamentos, key=lambda d: d.getCargaReal(), reverse= True)[:n]
    
    def getMenorCarga(self, n: int):
        return sorted(self.departamentos, key=lambda d: d.getCargaReal(), reverse= False)[:n]
    
    def numeroDepartamentos(self):
        return len(self.departamentos)
    
    def numeroDepartamentosConExperimentalidad(self):
        return dict([(d.coef_experimentalidad, len(list(filter(lambda x: x.coef_experimentalidad == d.coef_experimentalidad, self.departamentos)))) for d in self.departamentos])
    
    def mediaCargaRealConExperimentalidad(self):
        cargas_por_experimentalidad = {}

        for depto in self.departamentos:
            coef = depto.coef_experimentalidad
            carga = depto.getCargaReal()

            if coef not in cargas_por_experimentalidad:
                cargas_por_experimentalidad[coef] = []

            cargas_por_experimentalidad[coef].append(carga)

        return {coef: sum(cargas) / len(cargas) for coef, cargas in cargas_por_experimentalidad.items()}

    def coeficientesMayorMenorCarga(self):
        if not self.departamentos:
            return None, None

        mayor_carga_depto = max(self.departamentos, key=lambda d: d.getCargaReal())
        menor_carga_depto = min(self.departamentos, key=lambda d: d.getCargaReal())

        return mayor_carga_depto.coef_experimentalidad, menor_carga_depto.coef_experimentalidad
    