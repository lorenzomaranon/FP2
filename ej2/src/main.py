
from FactoriaUniversidad import FactoriaUniversidad


if __name__ == "__main__":
    factoria = FactoriaUniversidad("ej2/data/departamentos.pdf")
    mi_u = factoria.crear_objeto_universidad()

    print(f"Universidad: {mi_u.nombre}")
    print(f"\nTotal departamentos cargados: {len(mi_u.departamentos)}")
    # Ejemplo: Acceder al primer departamento (Administración de Empresas y Marketing) [cite: 5]
    print(f"\nPrimer depto: {mi_u.departamentos[0].nombre} - ETC: {mi_u.departamentos[0].numero_etc}")

    # Ejemplo: Obtener los 3 departamentos con mayor carga real
    print("\n3 departamentos con mayor carga real:")
    for depto in mi_u.getMayorCarga(3):
        print(f"{depto.nombre} - Carga Real: {depto.getCargaReal()}")

    # Ejemplo: Obtener los 3 departamentos con menor carga real
    print("\n3 departamentos con menor carga real:")
    for depto in mi_u.getMenorCarga(3):
        print(f"{depto.nombre} - Carga Real: {depto.getCargaReal()}")
    
    #Ejemplo: Número total de departamentos con experimentalidad
    print(f"\nNúmero total de departamentos: {mi_u.numeroDepartamentos()}")
    print(f"\nNúmero de departamentos por coeficiente de experimentalidad: {mi_u.numeroDepartamentosConExperimentalidad()}")

    #Ejemplo: Media de carga real por coeficiente de experimentalidad
    print(f"\nMedia de carga real por coeficiente de experimentalidad: {mi_u.mediaCargaRealConExperimentalidad()}")

    #Ejemplo: Coeficientes de experimentalidad del departamento con mayor y menor carga real
    mayor_coef, menor_coef = mi_u.coeficientesMayorMenorCarga()
    print(f"\nCoeficiente de experimentalidad con mayor media de carga real: {mayor_coef} - Media Carga Real: {mi_u.mediaCargaRealConExperimentalidad()[mayor_coef]}")
    print(f"Coeficiente de experimentalidad con menor media de carga real: {menor_coef} - Media Carga Real: {mi_u.mediaCargaRealConExperimentalidad()[menor_coef]}")