import csv

# 1. Datos de ASIGNATURAS
asignaturas_data = [
    ["Matemáticas I", 6.0, 1, 1],
    ["Física", 6.0, 1, 1],
    ["Programación I", 6.0, 1, 1],
    ["Lógica", 6.0, 1, 2],
    ["Programación II", 6.0, 1, 2],
    ["Estadística", 6.0, 2, 1],
    ["Estructura de Datos", 7.5, 2, 1],
    ["Bases de Datos", 6.0, 2, 2],
    ["Redes de Computadores", 6.0, 2, 2],
    ["Ingeniería del Software", 6.0, 3, 1],
    ["Inteligencia Artificial", 6.0, 3, 1],
    ["Sistemas Operativos", 7.5, 3, 2]
]

# 2. Datos de ALUMNOS
alumnos_data = [
    ["García López", "Ana", "10000001A", "2002-05-20", 101],
    ["Martínez Ruiz", "Luis", "10000002B", "2001-11-15", 101],
    ["Fernández Díaz", "Sofía", "10000003C", "2002-02-10", 102],
    ["Sánchez Romero", "Pedro", "10000004D", "2001-08-30", 102],
    ["Pérez Gómez", "Lucía", "10000005E", "2003-01-05", 101],
    ["González Torres", "Javier", "10000006F", "2000-12-12", 201],
    ["Rodríguez Vázquez", "Elena", "10000007G", "2000-07-22", 201],
    ["López Serrano", "Carlos", "10000008H", "1999-03-14", 202],
    ["Ramírez Castillo", "Marta", "10000009I", "2001-09-09", 102],
    ["Torres Gil", "Daniel", "10000010J", "2002-06-18", 101],
    ["Ruiz Herrera", "Laura", "10000011K", "2000-11-01", 202],
    ["Díaz Marín", "Jorge", "10000012L", "1998-05-25", 301],
    ["Muñoz Ibáñez", "Carmen", "10000013M", "1999-10-10", 201],
    ["Serrano Garrido", "Pablo", "10000014N", "2001-04-04", 102],
    ["Garrido Castro", "Raquel", "10000015O", "1998-01-20", 301],
    ["Castro Ortiz", "Alejandro", "10000016P", "2002-12-30", 101],
    ["Ortiz Rubio", "Beatriz", "10000017Q", "2000-08-15", 202],
    ["Rubio Molina", "Sergio", "10000018R", "1999-02-28", 301],
    ["Molina Gil", "Patricia", "10000019S", "2003-03-15", 101],
    ["Gil Vega", "Andrés", "10000020T", "2001-07-07", 102]
]

# 3. Datos de NOTAS
notas_data = [
    ["10000001A", "Matemáticas I", 8.5], ["10000001A", "Física", 6.0], ["10000001A", "Programación I", 9.0],
    ["10000002B", "Matemáticas I", 4.5], ["10000002B", "Física", 5.0], ["10000002B", "Programación I", 3.0],
    ["10000003C", "Lógica", 7.0], ["10000003C", "Programación II", 6.5],
    ["10000004D", "Física", 2.0], ["10000004D", "Matemáticas I", 5.0],
    ["10000005E", "Matemáticas I", 9.5], ["10000005E", "Física", 8.0], ["10000005E", "Programación I", 10.0], ["10000005E", "Lógica", 9.0],
    ["10000006F", "Estructura de Datos", 5.0], ["10000006F", "Bases de Datos", 6.0],
    ["10000007G", "Estructura de Datos", 3.5], ["10000007G", "Redes de Computadores", 4.0],
    ["10000008H", "Estadística", 7.5], ["10000008H", "Bases de Datos", 8.0],
    ["10000009I", "Matemáticas I", 5.0], ["10000009I", "Programación I", 5.5],
    ["10000010J", "Física", 4.9], ["10000010J", "Lógica", 6.0],
    ["10000011K", "Estructura de Datos", 9.0], ["10000011K", "Sistemas Operativos", 8.5],
    ["10000012L", "Ingeniería del Software", 6.0], ["10000012L", "Inteligencia Artificial", 7.5], ["10000012L", "Sistemas Operativos", 5.0],
    ["10000013M", "Redes de Computadores", 10.0], ["10000013M", "Estadística", 9.0],
    ["10000014N", "Matemáticas I", 3.0],
    ["10000015O", "Ingeniería del Software", 8.0], ["10000015O", "Inteligencia Artificial", 8.5],
    ["10000016P", "Programación I", 2.5], ["10000016P", "Física", 3.0],
    ["10000017Q", "Bases de Datos", 6.0], ["10000017Q", "Estadística", 5.5],
    ["10000018R", "Inteligencia Artificial", 9.5], ["10000018R", "Sistemas Operativos", 9.0], ["10000018R", "Ingeniería del Software", 8.0],
    ["10000019S", "Matemáticas I", 6.5],
    ["10000020T", "Física", 5.0], ["10000020T", "Programación I", 5.0]
]

def guardar_csv(nombre_archivo, cabecera, datos):
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(cabecera)
        writer.writerows(datos)
    print(f"Archivo {nombre_archivo} creado con éxito.")

# Ejecutar la creación
guardar_csv('asignaturas.csv', ['nombre', 'creditos', 'curso', 'cuatrimestre'], asignaturas_data)
guardar_csv('alumnos.csv', ['apellidos', 'nombre', 'dni', 'fechaNac', 'grupo'], alumnos_data)
guardar_csv('notas.csv', ['dni_alumno', 'nombre_asignatura', 'nota'], notas_data)