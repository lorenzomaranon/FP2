from typing import NamedTuple
from collections import Counter

class Actor(NamedTuple):
    nombre : str
    añoNcto: int

class Pelicula(NamedTuple):
    titulo: str
    año: int

class FPimdb():
    def __init__(self):
        self.datos: dict[Pelicula, list[Actor]] = {}
    
    def ejercicio_1(self): 
        datos = self.datos
        
        res = {}
        for pelicula, actores in datos.items():
            for actor in actores:
                if actor not in res:
                    res[actor]= []
                res[actor].append(pelicula)            
        
        for peliculas in res.values():
            peliculas.sort(key=lambda pelicula: pelicula.año)
        
        return res
    
    def ejercicio_2(self):
        datos = self.datos
        res = {}
        for pelicula, actores in datos.items():
            for actor in actores:
                if actor not in res:
                    res[actor] = []
                res[actor].append(pelicula)

        for actor, peliculas in res.items():
            años_trabajados = {pelicula.año for pelicula in peliculas}
            primer_año_trabajado = min(años_trabajados)
            ultimo_año_trabajado = max(años_trabajados)

            años_no_trabajados = []

            for año in range(primer_año_trabajado + 1, ultimo_año_trabajado):
                if año not in años_trabajados:
                    años_no_trabajados.append(año)
            
            res[actor] = años_no_trabajados
    
        
        return res

    def ejercicio_3(self,n):
        datos = self.datos
        contador = Counter()
        for actores in datos.values():
            for actor in actores:
                contador[actor] += 1
        return contador.most_common(n)

    def ejercicio_4(self):
        datos = self.datos
        res= {}

        for pelicula, actores in datos.items():
            edades = [pelicula.año - actor.añoNcto for actor in actores]
            res[pelicula] = sum(edades)/len(edades)

        return res

    def ejercicio_5(self):
        datos = self.datos
        actor_mayor = None
        edad_mayor = -1

        for pelicula, actores in datos.items():
            for actor in actores:
                edad = pelicula.año - actor.añoNcto
                if edad > edad_mayor:
                    edad_mayor = edad
                    actor_mayor = actor.nombre
            
            
        
        return actor_mayor


class Temporada(NamedTuple):
    nombre: str


class Equipo(NamedTuple):
    nombre: str


class Usuario(NamedTuple):
    nombre: str


class Cancion(NamedTuple):
    titulo: str
    genero: str
    duracion: float


class Futbol:
    def __init__(self, datos: dict[Temporada, dict[Equipo, int]] | None = None):
        self.datos: dict[Temporada, dict[Equipo, int]] = datos or {}

    def ejercicio_1(self) -> dict[Equipo, dict[Temporada, int]]:
        '''-> Dict[Equipo, Dict[Temporada, Goles]]'''
        datos = self.datos
        res = {}

        for temporada, equipos in datos.items():
            for equipo, goles in equipos.items():
                if equipo not in res:
                    res[equipo] = {}
                res[equipo][temporada] = goles
            
        return res
            

    def ejercicio_2(self) -> dict[Equipo, int]:
        datos = self.datos
        res = {}
        for equipos in datos.values():
            for equipo, goles in equipos.items():
                if equipo not in res:
                    res[equipo] = 0
                res[equipo] += goles
        return res
    

    def ejercicio_3(self) -> Temporada | None:
        """Devuelve la temporada con mas goles."""
        datos = self.datos
        res = Counter()
        
        if not datos:
            return None
        for temporada, equipos in datos.items():
            for goles in equipos.values():    
                if temporada not in res:
                    res[temporada] = 0
                res[temporada] += goles
        
        return res.most_common(1)[0][0]

    def ejercicio_4(self) -> dict[Temporada, list[tuple[Equipo, int]]]:
        """Devuelve equipos y goles por temporada, ordenados por goles."""
        datos = self.datos
        res = {}

        for temporada, equipos in datos.items():
            for equipo, goles in equipos.items():
                if temporada not in res:
                    res[temporada] = []
                res[temporada].append((equipo,goles))
        
        for resultados in res.values():
            resultados.sort(key = lambda x: x[1], reverse= True)
        
        return res

    def ejercicio_5(self, n: int) -> list[tuple[Equipo, Temporada]]:
        """Devuelve equipos que marcaron mas de n goles en una temporada."""
        datos = self.datos
        res = []
        for temporada, equipos in datos.items():
            for equipo, goles in equipos.items():
                if goles > n:
                    res.append((equipo,temporada))
        return res

    def ejercicio_6(self) -> dict[Equipo, int]:
        """Devuelve el numero de temporadas disputadas por equipo."""
        datos = self.datos
        res= Counter()
        for equipos in datos.values():
            for equipo in equipos.keys():
                res[equipo] +=1
        
        return dict(res)

    def ejercicio_7(self) -> dict[Equipo, float]:
        """Devuelve la media de goles de cada equipo."""
        datos = self.datos
        res= Counter()
        
        temporadas = 0

        for equipos in datos.values():
            temporadas +=1
            for equipo, goles in equipos.items():
                res[equipo] += goles
        
        for equipo, goles in res.items():
            res[equipo]= goles/temporadas
        
        return dict(res)

    def ejercicio_8(self) -> dict[Temporada, dict[Equipo, float]]:
        """Devuelve el porcentaje de goles de cada equipo por temporada."""
        datos = self.datos
        res = {}

        for temporada, equipos in datos.items():
            res[temporada] = {}
            goles_t = sum(equipos.values)
            
            for equipo, goles in res[temporada].items():
                res[temporada][equipo] = goles/goles_t *100
        
        return res
                
    def ejercicio_9(self) -> dict[Temporada, Equipo]:
        """Devuelve el equipo con mas goles en cada temporada."""
        datos = self.datos
        res = {}

        for temporada, equipos in datos.items():
            equipo_max = None
            goles_max_t = 0 
            for equipo, goles in equipos.items():
                if goles > goles_max_t:
                    equipo_max = equipo
                    goles_max_t = goles
            res[temporada] = equipo_max
        return res

                

    def ejercicio_10(self) -> dict[Equipo, list[Temporada]]:
        """Devuelve las temporadas en las que descendio cada equipo."""
        datos = self.datos
        res= {}
        lista_equipos_previa = []
        temporada_previa = 0
        
        for temporada, equipos in datos.items():
            for equipo in lista_equipos_previa:
                if equipo not in equipos:
                    if equipo not in res:
                        res[equipo] = []
                    res[equipo].append(temporada_previa)
            temporada_previa = temporada
            lista_equipos_previa = list(equipos.keys())
        return res


class FPtify:
    def __init__(self, datos: dict[Usuario, list[Cancion]] | None = None):
        self.datos: dict[Usuario, list[Cancion]] = datos or {}

    def ejercicio_1(self) -> dict[Usuario, float]:
        """Devuelve los minutos totales escuchados por cada usuario."""
        raise NotImplementedError("Implementa el ejercicio 1 de FPtify")

    def ejercicio_2(self, titulo: str) -> list[Usuario]:
        """Devuelve los usuarios que escucharon una cancion, sin duplicados."""
        raise NotImplementedError("Implementa el ejercicio 2 de FPtify")

    def ejercicio_3(self) -> dict[str, float]:
        """Devuelve los minutos escuchados acumulados por genero."""
        raise NotImplementedError("Implementa el ejercicio 3 de FPtify")

    def ejercicio_4(self) -> dict[Usuario, str]:
        """Devuelve el genero mas escuchado por cada usuario."""
        raise NotImplementedError("Implementa el ejercicio 4 de FPtify")

    def ejercicio_5(self, n: int) -> list[tuple[Usuario, float]]:
        """Devuelve los n usuarios con mas minutos consumidos."""
        raise NotImplementedError("Implementa el ejercicio 5 de FPtify")

    def ejercicio_6(self) -> dict[Usuario, list[str]]:
        """Devuelve los generos distintos escuchados por cada usuario."""
        raise NotImplementedError("Implementa el ejercicio 6 de FPtify")

    def ejercicio_7(self) -> dict[str, Usuario]:
        """Devuelve el usuario que mas tiempo consumio de cada genero."""
        raise NotImplementedError("Implementa el ejercicio 7 de FPtify")

    def ejercicio_8(self, n: int) -> dict[Usuario, list[tuple[Cancion, int]]]:
        """Devuelve las n canciones mas escuchadas por cada usuario."""
        raise NotImplementedError("Implementa el ejercicio 8 de FPtify")

    def ejercicio_9(self, n: int) -> list[tuple[Cancion, int]]:
        """Devuelve las n canciones mas escuchadas de la plataforma."""
        raise NotImplementedError("Implementa el ejercicio 9 de FPtify")

    def ejercicio_10(self, usuario: Usuario) -> Usuario | None:
        """Devuelve el usuario con gusto musical mas parecido."""
        raise NotImplementedError("Implementa el ejercicio 10 de FPtify")
