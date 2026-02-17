from Departamento import Departamento
from Universidad import Universidad
from FactoriaUniversidad import FactoriaUniversidad



factoria = FactoriaUniversidad("ej2/data/departamentos.pdf")
mi_u = factoria.crear_objeto_universidad()

print(f"Universidad: {mi_u.nombre}")
print(f"Total departamentos cargados: {len(mi_u.departamentos)}")
# Ejemplo: Acceder al primer departamento (Administración de Empresas y Marketing) [cite: 5]
print(f"Primer depto: {mi_u.departamentos[0].nombre} - ETC: {mi_u.departamentos[0].numero_etc}")
