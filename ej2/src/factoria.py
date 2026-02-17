import pdfplumber

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

class Universidad:
    """Clase contenedora principal."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.departamentos = []

    def agregar_departamento(self, depto: Departamento):
        self.departamentos.append(depto)

class FactoriaUniversidad:
    def __init__(self, ruta_pdf):
        self.ruta_pdf = ruta_pdf

    def crear_objeto_universidad(self):
        # Según el documento, el nombre principal es Universidad de Sevilla 
        universidad = Universidad("Universidad de Sevilla")
        #-----------------------------------------------------------------------------------------------
        #------------------------------- LECTURA Y PROCESAMIENTO DEL PDF -------------------------------
        #-----------------------------------------------------------------------------------------------

        with pdfplumber.open(self.ruta_pdf) as pdf:
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if not tabla:
                    continue

                for fila in tabla:
                    # Limpiamos los datos de la fila
                    fila_limpia = [celda.replace('\n', ' ').strip() if celda else "" for celda in fila]
                    
                    # Filtramos filas vacías o que son encabezados [cite: 5, 11, 18, 24]
                    if not fila_limpia[0] or "Departamento" in fila_limpia[0]:
                        continue
                    
                    # Eliminamos celdas vacías intermedias que genera el PDF [cite: 5, 11]
                    datos = [c for c in fila_limpia if c != ""]

                    # Si la fila tiene las 6 columnas esperadas [cite: 5, 18, 29]
                    if len(datos) == 6:
                        depto_obj = Departamento(
                            nombre=datos[0],
                            etc=datos[1],
                            tc=datos[2],
                            tp=datos[3],
                            total=datos[4],
                            exp=datos[5]
                        )
                        universidad.agregar_departamento(depto_obj)
        
        return universidad

# --- Ejecución ---
factoria = FactoriaUniversidad("departamentos.pdf")
mi_u = factoria.crear_objeto_universidad()

print(f"Universidad: {mi_u.nombre}")
print(f"Total departamentos cargados: {len(mi_u.departamentos)}")
# Ejemplo: Acceder al primer departamento (Administración de Empresas y Marketing) [cite: 5]
print(f"Primer depto: {mi_u.departamentos[0].nombre} - ETC: {mi_u.departamentos[0].numero_etc}")