
import pdfplumber


my_pdf = pdfplumber.open("C:/Users/loren/Desktop/FP2/ej2/data/departamentos.pdf")
#im = my_pdf.pages[0].to_image()
#im.debug_tablefinder().show()

table = my_pdf.pages[0].extract_table()

print(f' primera lectura: {table[:3]}')

for fila in table:
    # Limpiamos los datos de la fila
    fila_unico_string = [celda.replace('\n', ' ').strip() if celda else "" for celda in fila] # Esto devuelve algo así -> ["DEPARTAMENTO DE AGRONOMÍA 229,47 36,00 3,00 37,50 1,50"] como un único string.
    for linea in fila_unico_string:
        fila_limpia = linea.rsplit(maxsplit=5) # -> Esto ya devuelve una lista limpia con los 6 campos separados correctamente.

    
    if not fila_limpia[0] or "Departamento" in fila_limpia[0]:
        continue
                    
    # Eliminamos celdas vacías intermedias que genera el PDF [cite: 5, 11]
    datos = [c for c in fila_limpia if c != ""]               

    print(datos)