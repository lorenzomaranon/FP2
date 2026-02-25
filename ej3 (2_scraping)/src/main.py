
from FactoriaUniversidad import FactoriaUniversidad


if __name__ == "__main__":
    from FactoriaUniversidad import FactoriaUniversidad

if __name__ == "__main__":
    # Inicialización de la factoría
    ruta_pdf = "ej3 (2_scraping)/data/departamentos.pdf"
    factoria = FactoriaUniversidad(ruta_pdf)

    print(f"--- Procesando Universidad y Scraping de Sedes ---")
    
    # Creamos el objeto Universidad (incluyendo el scraping de sedes)
    mi_u = factoria.crear_objeto_universidad(buscar_sede=True)

    print(f"Universidad: {mi_u.nombre}")
    print(f"Departamentos cargados: {mi_u.numeroDepartamentos()}")

    # 1. Prueba de la función de análisis por Sede
    print("\n--- ANÁLISIS DE CARGA POR SEDE ---")
    analisis_sedes = mi_u.getAnalisisPorSedeEficiente()

    for sede, datos in analisis_sedes.items():
        # datos es la tupla: (nombre_max, carga_max, nombre_min, carga_min)
        print(f"\nSede: {sede}")
        print(f"  Mayor carga: {datos[0]} ({datos[1]})")
        print(f"  Menor carga: {datos[2]} ({datos[3]})")

    # 2. Resumen de estadísticas globales (métodos previos)
    print("\n--- ESTADÍSTICAS GLOBALES ---")
    
    # Media de carga por experimentalidad
    medias = mi_u.mediaCargaRealConExperimentalidad()
    print(f"Medias de carga por experimentalidad: {medias}")

    # Coeficientes extremos
    mayor_coef, menor_coef = mi_u.coeficientesMayorMenorCarga()
    print(f"Coeficiente con mayor media: {mayor_coef}")
    print(f"Coeficiente con menor media: {menor_coef}")

    # --- MEDIA DE CARGA DOCENTE POR SEDE (Pasada única) ---
    medias_sede = mi_u.getMediaPonderadaSede() 
    for sede, media in medias_sede.items():
        print(f"Sede: {sede} -> Media de Carga: {media}")