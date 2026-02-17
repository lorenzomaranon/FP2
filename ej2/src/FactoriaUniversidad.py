import pdfplumber
from Departamento import Departamento
from Universidad import Universidad




class FactoriaUniversidad:
    def __init__(self, ruta_pdf):
        self.ruta_pdf = ruta_pdf

    def crear_objeto_universidad(self):
        # Según el documento, el nombre principal es Universidad de Sevilla, y como es el único caso que vamos a utilizar lo hardcodeamos.
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
                    fila_unico_string = [celda.replace('\n', ' ').strip() if celda else "" for celda in fila] # Esto devuelve algo así -> ["DEPARTAMENTO DE AGRONOMÍA 229,47 36,00 3,00 37,50 1,50"] como un único string.

                    for linea in fila_unico_string:
                        fila_limpia = linea.rsplit(maxsplit=5) # -> Esto ya devuelve una lista limpia con los 6 campos separados correctamente.
                    
                    # Filtramos filas vacías o que son encabezados [cite: 5, 11, 18, 24]
                    if not fila[0] or "Departamento" in fila_limpia[0]:
                        continue
                    
                    # Eliminamos celdas vacías intermedias que genera el PDF [cite: 5, 11]
                    datos = [c for c in fila_limpia if c != ""]

                    # Si la fila tiene las 6 columnas esperadas [cite: 5, 18, 29]
                    if len(datos) == 6:
                        depto_obj = Departamento(
                            nombre=datos[0],
                            etc=float(datos[1].replace('.','').replace(',', '.')), # Para convertir el número con formato europeo a float.
                            tc=float(datos[2].replace('.','').replace(',', '.')),
                            tp=float(datos[3].replace('.','').replace(',', '.')),
                            total=float(datos[4].replace('.','').replace(',', '.')),
                            exp=float(datos[5].replace('.','').replace(',', '.'))
                        )
                        universidad.agregar_departamento(depto_obj)
        
        return universidad

