from __future__ import annotations

import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from .modelos import (
        Circunscripcion,
        EleccionGeneral,
        ResultadoPartidoCircunscripcion,
        ValidacionDatosError,
    )
except ImportError:
    from modelos import Circunscripcion, EleccionGeneral, ResultadoPartidoCircunscripcion, ValidacionDatosError


NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
RID_ATTR = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _tag(nombre: str) -> str:
    return f"{{{NS_MAIN}}}{nombre}"


def _limpiar_texto(valor: object) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def _normalizar_texto(valor: object) -> str:
    texto = unicodedata.normalize("NFKD", _limpiar_texto(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def _a_int(valor: object) -> int:
    texto = _limpiar_texto(valor)
    if texto == "":
        return 0

    texto = texto.replace(" ", "").replace("\xa0", "")
    ultima_coma = texto.rfind(",")
    ultimo_punto = texto.rfind(".")

    if ultima_coma != -1 and ultimo_punto != -1:
        if ultima_coma > ultimo_punto:
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif ultima_coma != -1:
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1:
        partes = texto.split(".")
        texto = "".join(partes[:-1]) + "." + partes[-1]

    return int(round(float(texto)))


def _indice_columna_desde_referencia(referencia: str) -> int:
    letras = []
    for caracter in referencia:
        if caracter.isalpha():
            letras.append(caracter.upper())
        else:
            break
    indice = 0
    for letra in letras:
        indice = (indice * 26) + (ord(letra) - ord("A") + 1)
    return indice


def _texto_celda_si(elemento_si: ET.Element) -> str:
    texto_directo = elemento_si.find(_tag("t"))
    if texto_directo is not None and texto_directo.text is not None:
        return texto_directo.text
    partes: list[str] = []
    for run in elemento_si.findall(_tag("r")):
        texto_run = run.find(_tag("t"))
        if texto_run is not None and texto_run.text is not None:
            partes.append(texto_run.text)
    return "".join(partes)


def _leer_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    ruta = "xl/sharedStrings.xml"
    if ruta not in zf.namelist():
        return []
    raiz = ET.fromstring(zf.read(ruta))
    return [_texto_celda_si(item) for item in raiz.findall(_tag("si"))]


def _obtener_ruta_primera_hoja(zf: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = workbook.find(_tag("sheets"))
    if sheets is None:
        raise ValueError("El XLSX no contiene hojas.")
    primera = sheets.find(_tag("sheet"))
    if primera is None:
        raise ValueError("El XLSX no contiene una hoja valida.")

    rid = primera.attrib.get(RID_ATTR)
    if not rid:
        raise ValueError("No se encontro el identificador de relacion de la hoja.")

    relaciones = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    for relacion in relaciones.findall(f"{{{NS_REL}}}Relationship"):
        if relacion.attrib.get("Id") != rid:
            continue
        destino = relacion.attrib.get("Target", "")
        if not destino:
            break
        if not destino.startswith("/"):
            destino = f"xl/{destino}"
        return destino.replace("\\", "/")
    raise ValueError("No se pudo localizar el XML de la hoja de datos.")


def _valor_celda_xlsx(celda: ET.Element, shared_strings: list[str]) -> str:
    tipo = celda.attrib.get("t")
    if tipo == "s":
        valor = celda.find(_tag("v"))
        if valor is None or valor.text is None:
            return ""
        try:
            return shared_strings[int(valor.text)]
        except (ValueError, IndexError):
            return valor.text
    if tipo == "inlineStr":
        inline = celda.find(_tag("is"))
        if inline is None:
            return ""
        return _texto_celda_si(inline)

    valor = celda.find(_tag("v"))
    if valor is None or valor.text is None:
        return ""
    return valor.text


def _leer_filas_xlsx(ruta_xlsx: Path) -> dict[int, dict[int, str]]:
    with zipfile.ZipFile(ruta_xlsx) as zf:
        shared_strings = _leer_shared_strings(zf)
        ruta_hoja = _obtener_ruta_primera_hoja(zf)
        raiz = ET.fromstring(zf.read(ruta_hoja))
        sheet_data = raiz.find(_tag("sheetData"))
        if sheet_data is None:
            return {}

        filas: dict[int, dict[int, str]] = {}
        for fila_xml in sheet_data.findall(_tag("row")):
            numero_fila = int(fila_xml.attrib.get("r", "0"))
            valores: dict[int, str] = {}
            for celda in fila_xml.findall(_tag("c")):
                referencia = celda.attrib.get("r", "")
                indice_columna = _indice_columna_desde_referencia(referencia)
                valores[indice_columna] = _limpiar_texto(_valor_celda_xlsx(celda, shared_strings))
            if valores:
                filas[numero_fila] = valores
        return filas


def _es_codigo_provincia(valor: str) -> bool:
    if valor == "":
        return False
    return re.fullmatch(r"\d+(\.0+)?", valor) is not None


def _extraer_anio(filas: dict[int, dict[int, str]], ruta_excel: Path) -> int:
    titulo = _limpiar_texto(filas.get(3, {}).get(1, ""))
    match = re.search(r"(20\d{2})", titulo)
    if match:
        return int(match.group(1))

    match = re.search(r"(20\d{2})", ruta_excel.stem)
    if match:
        return int(match.group(1))
    return 2023


class ValidadorCoherencia:
    @classmethod
    def validar(cls, eleccion: EleccionGeneral) -> None:
        errores: list[str] = []

        for circ in eleccion.iter_circunscripciones():
            contexto = f"{circ.nombre_provincia} ({circ.nombre_comunidad})"

            if circ.censo_total != circ.censo_sin_cera + circ.censo_cera:
                errores.append(
                    f"{contexto}: censo_total ({circ.censo_total}) != censo_sin_cera + censo_cera "
                    f"({circ.censo_sin_cera + circ.censo_cera})"
                )

            if circ.votantes_total != circ.votantes_cer + circ.votantes_cera:
                errores.append(
                    f"{contexto}: votantes_total ({circ.votantes_total}) != votantes_cer + votantes_cera "
                    f"({circ.votantes_cer + circ.votantes_cera})"
                )

            if circ.votos_validos != circ.votos_candidaturas + circ.votos_blanco:
                errores.append(
                    f"{contexto}: votos_validos ({circ.votos_validos}) != votos_candidaturas + votos_blanco "
                    f"({circ.votos_candidaturas + circ.votos_blanco})"
                )

            if circ.votantes_total != circ.votos_validos + circ.votos_nulos:
                errores.append(
                    f"{contexto}: votantes_total ({circ.votantes_total}) != votos_validos + votos_nulos "
                    f"({circ.votos_validos + circ.votos_nulos})"
                )

            if circ.total_votos_partidos != circ.votos_candidaturas:
                errores.append(
                    f"{contexto}: suma votos partidos ({circ.total_votos_partidos}) != votos_candidaturas "
                    f"({circ.votos_candidaturas})"
                )

            if circ.total_escanos_oficiales != circ.diputados:
                errores.append(
                    f"{contexto}: suma escaños oficiales ({circ.total_escanos_oficiales}) != diputados ({circ.diputados})"
                )

        if eleccion.totales_oficiales_nacionales:
            total_votantes = sum(c.votantes_total for c in eleccion.iter_circunscripciones())
            total_candidaturas = sum(c.votos_candidaturas for c in eleccion.iter_circunscripciones())
            total_blancos = sum(c.votos_blanco for c in eleccion.iter_circunscripciones())
            total_nulos = sum(c.votos_nulos for c in eleccion.iter_circunscripciones())
            total_validos = sum(c.votos_validos for c in eleccion.iter_circunscripciones())

            if eleccion.totales_oficiales_nacionales.get("total_votantes", -1) != total_votantes:
                errores.append(
                    f"Nacional: total_votantes oficial ({eleccion.totales_oficiales_nacionales.get('total_votantes')}) "
                    f"!= suma circunscripciones ({total_votantes})"
                )
            if eleccion.totales_oficiales_nacionales.get("votos_candidaturas", -1) != total_candidaturas:
                errores.append(
                    f"Nacional: votos_candidaturas oficial ({eleccion.totales_oficiales_nacionales.get('votos_candidaturas')}) "
                    f"!= suma circunscripciones ({total_candidaturas})"
                )
            if eleccion.totales_oficiales_nacionales.get("votos_blanco", -1) != total_blancos:
                errores.append(
                    f"Nacional: votos_blanco oficial ({eleccion.totales_oficiales_nacionales.get('votos_blanco')}) "
                    f"!= suma circunscripciones ({total_blancos})"
                )
            if eleccion.totales_oficiales_nacionales.get("votos_nulos", -1) != total_nulos:
                errores.append(
                    f"Nacional: votos_nulos oficial ({eleccion.totales_oficiales_nacionales.get('votos_nulos')}) "
                    f"!= suma circunscripciones ({total_nulos})"
                )
            if eleccion.totales_oficiales_nacionales.get("votos_validos", -1) != total_validos:
                errores.append(
                    f"Nacional: votos_validos oficial ({eleccion.totales_oficiales_nacionales.get('votos_validos')}) "
                    f"!= suma circunscripciones ({total_validos})"
                )

        if eleccion.totales_oficiales_nacionales_partidos:
            votos_modelo = eleccion.votos_nacionales_por_partido()
            escanos_modelo = eleccion.escanos_oficiales_por_partido()
            for clave, (votos_oficial, escanos_oficial) in eleccion.totales_oficiales_nacionales_partidos.items():
                if votos_modelo.get(clave, 0) != votos_oficial:
                    errores.append(
                        f"Nacional partido {clave}: votos oficiales ({votos_oficial}) != modelo ({votos_modelo.get(clave, 0)})"
                    )
                if escanos_modelo.get(clave, 0) != escanos_oficial:
                    errores.append(
                        f"Nacional partido {clave}: escaños oficiales ({escanos_oficial}) != modelo ({escanos_modelo.get(clave, 0)})"
                    )

        if errores:
            raise ValidacionDatosError(errores)


class FactoriaEleccion:
    @classmethod
    def desde_excel(cls, ruta_excel: str | Path, validar: bool = True) -> EleccionGeneral:
        ruta = Path(ruta_excel)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el fichero Excel: {ruta}")

        filas = _leer_filas_xlsx(ruta)
        if not filas:
            raise ValueError(f"No se pudieron leer filas del fichero: {ruta}")

        anio = _extraer_anio(filas, ruta)
        eleccion = EleccionGeneral(anio=anio)

        cabecera_larga = filas.get(4, {})
        cabecera_siglas = filas.get(5, {})
        cabecera_columnas = filas.get(6, {})
        max_columna = max(max(fila.keys()) for fila in filas.values())

        columnas_partidos: list[tuple[int, int, str, str]] = []
        for col_votos in range(16, max_columna + 1, 2):
            col_escanos = col_votos + 1
            etiqueta_votos = _normalizar_texto(cabecera_columnas.get(col_votos, ""))
            etiqueta_escanos = _normalizar_texto(cabecera_columnas.get(col_escanos, ""))
            if "votos" not in etiqueta_votos or "diputados" not in etiqueta_escanos:
                continue

            nombre_largo = _limpiar_texto(cabecera_larga.get(col_votos, ""))
            siglas = _limpiar_texto(cabecera_siglas.get(col_votos, ""))
            if siglas == "" and nombre_largo == "":
                continue
            if nombre_largo == "":
                nombre_largo = siglas
            if siglas == "":
                siglas = nombre_largo
            columnas_partidos.append((col_votos, col_escanos, nombre_largo, siglas))

        for numero_fila in sorted(filas):
            if numero_fila < 7:
                continue
            fila = filas[numero_fila]

            codigo_provincia = _limpiar_texto(fila.get(2, ""))
            nombre_provincia = _limpiar_texto(fila.get(3, ""))

            if _es_codigo_provincia(codigo_provincia) and nombre_provincia != "":
                circ = Circunscripcion(
                    nombre_comunidad=_limpiar_texto(fila.get(1, "")),
                    codigo_provincia=str(_a_int(codigo_provincia)),
                    nombre_provincia=nombre_provincia,
                    poblacion=_a_int(fila.get(4, "")),
                    numero_mesas=_a_int(fila.get(5, "")),
                    censo_sin_cera=_a_int(fila.get(6, "")),
                    censo_cera=_a_int(fila.get(7, "")),
                    censo_total=_a_int(fila.get(8, "")),
                    votantes_cer=_a_int(fila.get(9, "")),
                    votantes_cera=_a_int(fila.get(10, "")),
                    votantes_total=_a_int(fila.get(11, "")),
                    votos_validos=_a_int(fila.get(12, "")),
                    votos_candidaturas=_a_int(fila.get(13, "")),
                    votos_blanco=_a_int(fila.get(14, "")),
                    votos_nulos=_a_int(fila.get(15, "")),
                    diputados=0,
                )

                total_diputados_oficiales = 0
                for col_votos, col_escanos, nombre_largo, siglas in columnas_partidos:
                    votos = _a_int(fila.get(col_votos, ""))
                    escanos = _a_int(fila.get(col_escanos, ""))
                    total_diputados_oficiales += escanos
                    if votos <= 0:
                        continue
                    partido = eleccion.obtener_o_crear_partido(siglas=siglas, nombre=nombre_largo)
                    circ.agregar_resultado(
                        ResultadoPartidoCircunscripcion(
                            partido=partido,
                            votos=votos,
                            escanos_oficiales=escanos,
                        )
                    )

                circ.diputados = total_diputados_oficiales
                eleccion.agregar_circunscripcion(circ)
                continue

            if _normalizar_texto(nombre_provincia) == "espana":
                eleccion.totales_oficiales_nacionales = {
                    "poblacion": _a_int(fila.get(4, "")),
                    "votos_validos": _a_int(fila.get(12, "")),
                    "votos_candidaturas": _a_int(fila.get(13, "")),
                    "votos_blanco": _a_int(fila.get(14, "")),
                    "votos_nulos": _a_int(fila.get(15, "")),
                    "total_votantes": _a_int(fila.get(11, "")),
                }

                totales_partidos: dict[str, tuple[int, int]] = {}
                for col_votos, col_escanos, nombre_largo, siglas in columnas_partidos:
                    votos = _a_int(fila.get(col_votos, ""))
                    escanos = _a_int(fila.get(col_escanos, ""))
                    if votos <= 0 and escanos <= 0:
                        continue
                    clave = (siglas or nombre_largo).strip()
                    totales_partidos[clave] = (votos, escanos)
                eleccion.totales_oficiales_nacionales_partidos = totales_partidos

        if validar:
            ValidadorCoherencia.validar(eleccion)
        return eleccion
