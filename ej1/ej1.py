from datetime import date, datetime
import csv

class Asignatura:
    def __init__(self, nombre: str, creditos: float, curso: int, cuatrimestre: int):
        self.nombre = nombre
        self.creditos = creditos
        self.curso = curso if 1 <= curso <= 4 else 1
        self.cuatrimestre = cuatrimestre if cuatrimestre in [1, 2] else 1

    def set_curso(self, nuevo_curso: int):
        if 1 <= nuevo_curso <= 4:
            self.curso = nuevo_curso

    def set_cuatrimestre(self, nuevo_cuatri: int):
        if nuevo_cuatri in [1, 2]:
            self.cuatrimestre = nuevo_cuatri

class Persona:
    def __init__(self, apellidos: str, nombre: str, dni: str, fechaNac: date):
        self.apellidos = apellidos
        self.nombre = nombre
        self.dni = dni
        self.fechaNac = fechaNac

    def getEdad(self) -> int:
        hoy = date.today()
        edad = hoy.year - self.fechaNac.year - ((hoy.month, hoy.day) < (self.fechaNac.month, self.fechaNac.day))
        return edad

class Alumno(Persona):
    def __init__(self, apellidos: str, nombre: str, dni: str, fechaNac: date, grupo: int):
        super().__init__(apellidos, nombre, dni, fechaNac)
        self.asignaturas = []  # Lista de tuplas (Asignatura, nota)
        self.grupo = grupo

    def set_grupo(self, nuevo_grupo: int):
        self.grupo = nuevo_grupo

    def getNumeroCreditosSuperados(self) -> float:
        return sum(asig.creditos for asig, nota in self.asignaturas if nota >= 5.0)

    def getNotaMedia(self) -> float:
        if not self.asignaturas:
            return 0.0
        total_notas = sum(nota for _, nota in self.asignaturas)
        return total_notas / len(self.asignaturas)

class Profesor(Persona):
    def __init__(self, apellidos: str, nombre: str, dni: str, fechaNac: date, nombreAsignatura: str):
        super().__init__(apellidos, nombre, dni, fechaNac)
        self.nombreAsignatura = nombreAsignatura
        self.alumnos = []

    def set_nota_alumno(self, dni: str, nueva_nota: float):
        for alumno in self.alumnos:
            if alumno.dni == dni:
                # Buscamos la asignatura que imparte este profesor en la lista del alumno
                for i, (asig, nota) in enumerate(alumno.asignaturas):
                    if asig.nombre == self.nombreAsignatura:
                        alumno.asignaturas[i] = (asig, nueva_nota)
                        print(f"Nota actualizada para {alumno.nombre} en {self.nombreAsignatura}.")
                        return
        print("Alumno o asignatura no encontrados.")


# Asumimos que las clases Asignatura, Persona, Alumno y Profesor están definidas arriba

def cargar_datos():
    # 1. Cargar Asignaturas en un diccionario para acceso rápido
    diccionario_asignaturas = {}
    with open('asignaturas.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            asig = Asignatura(
                fila['nombre'], 
                float(fila['creditos']), 
                int(fila['curso']), 
                int(fila['cuatrimestre'])
            )
            diccionario_asignaturas[fila['nombre']] = asig

    # 2. Cargar Alumnos en un diccionario (clave: DNI)
    diccionario_alumnos = {}
    with open('alumnos.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            # Convertir string "YYYY-MM-DD" a objeto date
            fecha = datetime.strptime(fila['fechaNac'], '%Y-%m-%d').date()
            alum = Alumno(
                fila['apellidos'], 
                fila['nombre'], 
                fila['dni'], 
                fecha, 
                int(fila['grupo'])
            )
            diccionario_alumnos[fila['dni']] = alum

    # 3. Cargar Notas y asociarlas a los alumnos
    with open('notas.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            dni = fila['dni_alumno']
            nom_asig = fila['nombre_asignatura']
            nota = float(fila['nota'])
            
            if dni in diccionario_alumnos and nom_asig in diccionario_asignaturas:
                asignatura_obj = diccionario_asignaturas[nom_asig]
                diccionario_alumnos[dni].asignaturas.append((asignatura_obj, nota))

    return diccionario_alumnos

# --- PROGRAMA PRINCIPAL ---
if __name__ == "__main__":
    # Cargamos los datos de los ficheros
    todos_los_alumnos = cargar_datos()

    # Creamos un Profesor (por ejemplo, de Inteligencia Artificial)
    profe_ia = Profesor("Giammarini", "Luis", "99999999Z", datetime(1975, 5, 10).date(), "Inteligencia Artificial")

    # Asignamos todos los alumnos cargados a la lista del profesor
    profe_ia.alumnos = list(todos_los_alumnos.values())

    # Mostrar listado solicitado
    print(f"{'ALUMNO':<30} | {'NOTA MEDIA':<12} | {'CRÉDITOS AP.'}")
    print("-" * 60)

    for alumno in profe_ia.alumnos:
        nombre_completo = f"{alumno.apellidos}, {alumno.nombre}"
        nota_media = alumno.getNotaMedia()
        creditos = alumno.getNumeroCreditosSuperados()
        
        print(f"{nombre_completo:<30} | {nota_media:<12.2f} | {creditos:<12.1f}")