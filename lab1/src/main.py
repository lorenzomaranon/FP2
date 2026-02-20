import random
from Registro import Registro

if __name__ == "__main__":
    # 1. Crear aleatoriamente unos 10 objetos de tipo Registro de dimensión 4 
    registros = []
    for _ in range(10):
        # Valores aleatorios entre 0 y 10 para simular datos históricos [cite: 21, 65]
        valores = [random.uniform(0, 10) for _ in range(4)]
        registros.append(Registro(valores))
    
    # 2. Seleccionar el primer registro para probar los métodos contra él
    sujeto = registros[0]
    objetivo = registros[1]
    
    print("--- PRUEBA DE REGISTROS ---")
    print(f"Sujeto de prueba: {sujeto}")
    print(f"Registro objetivo: {objetivo}")
    print("-" * 30)

    # 3. Probar los tres tipos de distancias [cite: 44, 45, 46]
    print("MÉTRICAS DE DISTANCIA:")
    
    # Euclídea [cite: 44]
    dist_euc = sujeto.distancia_euclidea(objetivo)
    print(f"1. Euclídea: {dist_euc:.4f}")
    
    # Manhattan [cite: 45]
    dist_man = sujeto.distancia_manhattan(objetivo)
    print(f"2. Manhattan: {dist_man:.4f}")
    
    # Ponderada [cite: 46]
    # Definimos pesos para las 4 dimensiones (ejemplo: [1, 2, 0.5, 1]) [cite: 47]
    pesos_test = [1.0, 2.0, 0.5, 1.0]
    dist_pon = sujeto.distancia_ponderada(objetivo, pesos_test)
    print(f"3. Ponderada (pesos {pesos_test}): {dist_pon:.4f}")
    print("-" * 30)

    # 4. Probar la función selectora 'calcula_distancia' 
    print("SELECTOR DE DISTANCIA (calcula_distancia):")
    # Probamos el valor por defecto (euclídea) 
    print(f"Resultado por defecto: {sujeto.calcula_distancia(objetivo):.4f}")
    # Probamos pasando el nombre explícito 
    print(f"Resultado 'manhattan': {sujeto.calcula_distancia(objetivo, 'manhattan'):.4f}")
    print("-" * 30)

    # 5. Probar normalización [cite: 51]
    # Usamos mínimos y máximos teóricos para los valores aleatorios (0 a 10) [cite: 51, 62]
    minimos = [0.0, 0.0, 0.0, 0.0]
    maximos = [10.0, 10.0, 10.0, 10.0]
    sujeto_normalizado = sujeto.normalizar(minimos, maximos)
    print("NORMALIZACIÓN:")
    print(f"Original:    {sujeto}")
    print(f"Normalizado: {sujeto_normalizado}") # Debe estar entre 0 y 1 
    print("-" * 30)

    # 6. Probar k-vecinos [cite: 63]
    k = 3
    print(f"ALGORITMO K-VECINOS (k={k}):")
    # Buscamos los 3 más cercanos en la lista de los 10 registros creados 
    indices = sujeto.k_vecinos(registros, k, tipo="euclídea")
    print(f"Los índices de los {k} registros más cercanos son: {indices}")

###################################################################################
###################################################################################
###################################################################################
'''


import csv

def cargar_desde_csv(ruta_archivo):
    """
    Función para leer un archivo CSV y convertir cada fila en un objeto Registro.
    Se asume que el CSV contiene solo valores numéricos (atributos).
    """
    lista_de_registros = []
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as fichero:
            # DictReader o reader dependiendo de si el CSV tiene cabecera
            lector = csv.reader(fichero)
            
            # Si el archivo tiene una línea de títulos (ej: "glucosa, edad, peso"), 
            # descomenta la siguiente línea para saltarla:
            # next(lector) 
            
            for fila in lector:
                # Convertimos cada elemento de la fila a float y creamos el objeto
                # [cite: 37, 43]
                nuevo_registro = Registro([float(valor) for valor in fila])
                lista_de_registros.append(nuevo_registro)
                
        return lista_de_registros
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo}")
        return []

'''
# --- Ejemplo de uso (comentado para que no interfiera con tu test actual) ---
# if __name__ == "__main__":
#     mis_datos = cargar_desde_csv("./lab1/data/pacientes.csv")
#     if mis_datos:
#         print(f"Se han cargado {len(mis_datos)} registros correctamente.")
#         # Ahora podrías normalizarlos o buscar k-vecinos [cite: 63, 64]