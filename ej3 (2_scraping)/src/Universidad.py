from Departamento import Departamento

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

        return {coef: round(sum(cargas) / len(cargas),2) for coef, cargas in cargas_por_experimentalidad.items()}

    def coeficientesMayorMenorCarga(self):
        if not self.departamentos:
            return None, None

        coef_mayor_media, mayor_media = max(self.mediaCargaRealConExperimentalidad().items(), key=lambda item: item[1])
        
        coef_menor_media, menor_media = min(self.mediaCargaRealConExperimentalidad().items(), key=lambda item: item[1])

        return coef_mayor_media, coef_menor_media
    
    def getAnalisisPorSedeEficiente(self):
        resultado = {}

        for depto in self.departamentos:
            sede = depto.sede if depto.sede else "Sede no definida"
            carga_actual = depto.getCargaReal()
            
            if sede not in resultado:
                # Inicializamos la sede con el primer depto que encontramos
                # Estructura: [nombre_max, carga_max, nombre_min, carga_min]
                resultado[sede] = [depto.nombre, carga_actual, depto.nombre, carga_actual]
            else:
                # Actualizamos el máximo si procede
                if carga_actual > resultado[sede][1]:
                    resultado[sede][0] = depto.nombre
                    resultado[sede][1] = carga_actual
                
                # Actualizamos el mínimo si procede
                if carga_actual < resultado[sede][3]:
                    resultado[sede][2] = depto.nombre
                    resultado[sede][3] = carga_actual

        # Convertimos las listas internas a tuplas para cumplir con tu requisito
        return {sede: tuple(info) for sede, info in resultado.items()}
    