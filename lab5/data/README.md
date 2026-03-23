# Especificaciones de Implementación: Laboratorio 5 AEI

Este documento describe los requisitos técnicos para el sistema de gestión de proyectos de la Agencia Estatal de Investigación. **IMPORTANTE: No utilizar la librería Pandas.** El objetivo es reforzar el uso de Programación Orientada a Objetos (POO) y estructuras de datos nativas (listas, diccionarios y tuplas).

## 1. Modelo de Objetos (`proyectos.py`)

Implementar la siguiente jerarquía de clases:

### Clase `Proyecto`
* **Atributos**: `referencia`, `area`, `entidad`, `ccaa`.
* **Estado**: Atributo `concedido` inicializado siempre en `False`.

### Clase `ProyectoConcedido` (Hereda de `Proyecto`)
* **Atributos**:
    * `concedido`: `True`.
    * `costes_directos`, `costes_indirectos`, `anticipo`, `subvencion`.
    * `anualidades`: Lista con los importes de 2025, 2026, 2027 y 2028.
* **Propiedades**:
    * `presupuesto`: Suma de `costes_directos` + `costes_indirectos`.
    * `contratado_predoc`: Booleano basado en si el campo `Nº Contrat. PREDOC.` es > 0.
* **Validación**: Verificar que `costes_directos + costes_indirectos == anticipo + subvencion`.

### Clase `ProyectoContrato` (Hereda de `ProyectoConcedido`)
* **Atributos**:
    * `contratado_predoc`: Siempre `True`.
    * `titulo`: Título completo del proyecto.

---

## 2. Origen de Datos (Mapeo de CSV)

Para la carga de datos en `factoria.py`, utiliza los siguientes encabezados detectados en los archivos:

1. **Anexo I (Proyectos Concedidos)**: 
   - Columnas: `REFERENCIA`, `AREA`, `ENTIDAD SOLICITANTE`, `CCAA Entidad Solicitante`, `Nº Contrat. PREDOC.`.
2. **Anexo II (Presupuestos)**: 
   - Columnas: `REFERENCIA`, `CD_COSTES_DIRECTOS`, `CI_COSTES_INDIRECTOS`, `ANTICIPO_REEMBOLSABLE`, `SUBVENCION`, `SUBVENCION_2025_TOTAL`, `SUBVENCION_2026`, `SUBVENCION_2027`, `SUBVENCION_2028`.
3. **Anexo III (Denegados)**: 
   - Columnas: `REFERENCIA`, `AREA`, `ENTIDAD SOLICITANTE`, `CCAA Entidad Solicitante`.
4. **Anexo IV (Contratos Predoctorales)**: 
   - Columnas: `REFERENCIA`, `TITULO DEL PROYECTO`.

---

## 3. Lógica de Negocio y Contenedores

### `gestor.py`
Crear tres clases contenedoras (`Gestor_Proyectos`, `Gestor_ProyectosConcedidos`, `Gestor_ProyectosContrato`). Cada una debe gestionar una lista de sus respectivos objetos. Se recomienda el uso de un **diccionario interno** cuya clave sea la `referencia` para agilizar la unión de datos entre el Anexo I y el Anexo II.

### `factoria.py`
Debe leer los CSV usando el módulo `csv` de Python.
* **Pasos sugeridos**:
    1. Leer Anexo III e instanciar objetos `Proyecto` (Denegados).
    2. Leer Anexo I y Anexo II simultáneamente (usando la Referencia como clave) para instanciar objetos `ProyectoConcedido`.
    3. Si un proyecto del Anexo I aparece en el Anexo IV, instanciarlo como `ProyectoContrato`.

---

## 4. Requerimientos de Salida (`principal.py`)

El programa debe imprimir por consola:
1. Conteo de registros (Esperados: Total 7092, Concedidos 3252, Contratos 1149).
2. **Tasa de éxito por CCAA**: (Proyectos Concedidos en CCAA / Total Proyectos Solicitados en CCAA) * 100.
3. **Análisis Económico**: Suma total de `presupuesto` por cada Comunidad Autónoma.

---
**Nota para el desarrollador**: El código debe ser modular, evitar variables globales y estar debidamente comentado para facilitar su comprensión educativa.