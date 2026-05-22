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