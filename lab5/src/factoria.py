from __future__ import annotations

import csv
import io
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from .gestor import (
        Gestor_Proyectos,
        Gestor_ProyectosConcedidos,
        Gestor_ProyectosContrato,
    )
    from .proyectos import Proyecto, ProyectoConcedido, ProyectoContrato
except ImportError:
    from gestor import Gestor_Proyectos, Gestor_ProyectosConcedidos, Gestor_ProyectosContrato
    from proyectos import Proyecto, ProyectoConcedido, ProyectoContrato


NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
RID_ATTR = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _tag(nombre: str) -> str:
    return f"{{{NS_MAIN}}}{nombre}"


def _normalizar_nombre_columna(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", str(nombre).strip())
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.replace("º", "O").replace("ª", "A")
    texto = re.sub(r"[^A-Z0-9]+", "_", texto.upper()).strip("_")
    if texto in {"N_CONTRAT_PREDOC", "NO_CONTRAT_PREDOC", "NUM_CONTRATOS_PREDOC"}:
        return "NUM_CONTRATOS_PREDOC"
    return texto


def _limpiar_valor(valor: object) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def _parse_numero(valor: str) -> float:
    texto = _limpiar_valor(valor)
    if not texto:
        return 0.0

    texto = texto.replace(" ", "").replace("\xa0", "").replace("EUR", "").replace("€", "")
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

    return float(texto)


def _parse_entero(valor: str) -> int:
    return int(round(_parse_numero(valor)))


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
    ruta_shared = "xl/sharedStrings.xml"
    if ruta_shared not in zf.namelist():
        return []
    raiz = ET.fromstring(zf.read(ruta_shared))
    valores: list[str] = []
    for item in raiz.findall(_tag("si")):
        valores.append(_texto_celda_si(item))
    return valores


def _obtener_ruta_primera_hoja(zf: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = workbook.find(_tag("sheets"))
    if sheets is None:
        raise ValueError("El fichero XLSX no contiene hojas.")
    primera_hoja = sheets.find(_tag("sheet"))
    if primera_hoja is None:
        raise ValueError("El fichero XLSX no contiene una hoja valida.")

    rid = primera_hoja.attrib.get(RID_ATTR)
    if rid is None:
        raise ValueError("No se pudo localizar la relacion de la primera hoja.")

    relaciones = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    for relacion in relaciones.findall(f"{{{NS_REL}}}Relationship"):
        if relacion.attrib.get("Id") == rid:
            destino = relacion.attrib.get("Target", "")
            if not destino:
                break
            if not destino.startswith("/"):
                destino = f"xl/{destino}"
            return destino.replace("\\", "/")
    raise ValueError("No se pudo localizar el XML de la primera hoja del XLSX.")


def _indice_columna_desde_referencia(ref_celda: str) -> int:
    letras = []
    for caracter in ref_celda:
        if caracter.isalpha():
            letras.append(caracter.upper())
        else:
            break
    indice = 0
    for letra in letras:
        indice = (indice * 26) + (ord(letra) - ord("A") + 1)
    return max(indice - 1, 0)


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


def _leer_xlsx_como_filas(ruta_xlsx: Path) -> list[list[str]]:
    with zipfile.ZipFile(ruta_xlsx) as zf:
        shared_strings = _leer_shared_strings(zf)
        ruta_hoja = _obtener_ruta_primera_hoja(zf)
        raiz_hoja = ET.fromstring(zf.read(ruta_hoja))
        datos_hoja = raiz_hoja.find(_tag("sheetData"))
        if datos_hoja is None:
            return []

        filas: list[list[str]] = []
        for fila_xml in datos_hoja.findall(_tag("row")):
            celdas = fila_xml.findall(_tag("c"))
            if not celdas:
                continue

            valores_por_indice: dict[int, str] = {}
            for celda in celdas:
                referencia = celda.attrib.get("r", "")
                indice_col = _indice_columna_desde_referencia(referencia)
                valores_por_indice[indice_col] = _valor_celda_xlsx(celda, shared_strings)

            max_indice = max(valores_por_indice)
            fila = [""] * (max_indice + 1)
            for indice, valor in valores_por_indice.items():
                fila[indice] = _limpiar_valor(valor)

            filas.append(fila)
        return filas


def _leer_tabla(ruta: Path) -> list[dict[str, str]]:
    extension = ruta.suffix.lower()
    if extension == ".csv":
        with ruta.open("r", encoding="utf-8-sig", newline="") as descriptor:
            reader = csv.DictReader(descriptor)
            return _normalizar_filas(reader)
    if extension == ".xlsx":
        filas = _leer_xlsx_como_filas(ruta)
        if not filas:
            return []
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(filas)
        buffer.seek(0)
        reader = csv.DictReader(buffer)
        return _normalizar_filas(reader)
    raise ValueError(f"Formato no soportado para {ruta}. Usa .csv o .xlsx")


def _normalizar_filas(reader: csv.DictReader) -> list[dict[str, str]]:
    filas: list[dict[str, str]] = []
    for fila in reader:
        fila_normalizada: dict[str, str] = {}
        for columna, valor in fila.items():
            if columna is None:
                continue
            clave = _normalizar_nombre_columna(columna)
            fila_normalizada[clave] = _limpiar_valor(valor)
        if any(valor != "" for valor in fila_normalizada.values()):
            filas.append(fila_normalizada)
    return filas


def _obligatorio(fila: dict[str, str], campo: str, contexto: str) -> str:
    valor = _limpiar_valor(fila.get(campo, ""))
    if valor == "":
        raise ValueError(f"Falta el campo obligatorio {campo} en {contexto}")
    return valor


class FactoriaProyectos:
    @classmethod
    def desde_carpeta_datos(
        cls, carpeta_datos: str | Path
    ) -> tuple[Gestor_Proyectos, Gestor_ProyectosConcedidos, Gestor_ProyectosContrato]:
        base = Path(carpeta_datos)
        return cls.desde_anexos(
            anexo_i=base / "Anexo I.xlsx",
            anexo_ii=base / "Anexo II.xlsx",
            anexo_iii=base / "Anexo III.xlsx",
            anexo_iv=base / "Anexo IV.xlsx",
        )

    @classmethod
    def desde_anexos(
        cls,
        anexo_i: str | Path,
        anexo_ii: str | Path,
        anexo_iii: str | Path,
        anexo_iv: str | Path,
    ) -> tuple[Gestor_Proyectos, Gestor_ProyectosConcedidos, Gestor_ProyectosContrato]:
        ruta_i = Path(anexo_i)
        ruta_ii = Path(anexo_ii)
        ruta_iii = Path(anexo_iii)
        ruta_iv = Path(anexo_iv)

        for ruta in (ruta_i, ruta_ii, ruta_iii, ruta_iv):
            if not ruta.exists():
                raise FileNotFoundError(f"No existe el fichero: {ruta}")

        gestor_todos = Gestor_Proyectos()
        gestor_concedidos = Gestor_ProyectosConcedidos()
        gestor_contratos = Gestor_ProyectosContrato()

        filas_denegados = _leer_tabla(ruta_iii)
        for indice, fila in enumerate(filas_denegados, start=2):
            proyecto = Proyecto(
                referencia=_obligatorio(fila, "REFERENCIA", f"{ruta_iii.name}:{indice}"),
                area=_obligatorio(fila, "AREA", f"{ruta_iii.name}:{indice}"),
                entidad=_obligatorio(fila, "ENTIDAD_SOLICITANTE", f"{ruta_iii.name}:{indice}"),
                ccaa=_obligatorio(fila, "CCAA_ENTIDAD_SOLICITANTE", f"{ruta_iii.name}:{indice}"),
            )
            gestor_todos.agregar(proyecto)

        filas_contrato = _leer_tabla(ruta_iv)
        titulos_por_referencia: dict[str, str] = {}
        for fila in filas_contrato:
            referencia = _limpiar_valor(fila.get("REFERENCIA", ""))
            if referencia:
                titulos_por_referencia[referencia] = _limpiar_valor(
                    fila.get("TITULO_DEL_PROYECTO", "")
                )

        filas_anexo_i = _leer_tabla(ruta_i)
        datos_base_por_referencia: dict[str, dict[str, str]] = {}
        for fila in filas_anexo_i:
            referencia = _limpiar_valor(fila.get("REFERENCIA", ""))
            if referencia:
                datos_base_por_referencia[referencia] = fila

        filas_anexo_ii = _leer_tabla(ruta_ii)
        datos_economicos_por_referencia: dict[str, dict[str, str]] = {}
        for fila in filas_anexo_ii:
            referencia = _limpiar_valor(fila.get("REFERENCIA", ""))
            if referencia:
                datos_economicos_por_referencia[referencia] = fila

        for referencia, base in datos_base_por_referencia.items():
            economia = datos_economicos_por_referencia.get(referencia)
            if economia is None:
                raise ValueError(f"No hay datos economicos en Anexo II para {referencia}")

            contexto = f"{referencia} ({ruta_i.name}+{ruta_ii.name})"
            area = _obligatorio(base, "AREA", contexto)
            entidad = _obligatorio(base, "ENTIDAD_SOLICITANTE", contexto)
            ccaa = _obligatorio(base, "CCAA_ENTIDAD_SOLICITANTE", contexto)
            num_contratos_predoc = _parse_entero(base.get("NUM_CONTRATOS_PREDOC", "0"))

            costes_directos = _parse_numero(economia.get("CD_COSTES_DIRECTOS", "0"))
            costes_indirectos = _parse_numero(economia.get("CI_COSTES_INDIRECTOS", "0"))
            anticipo = _parse_numero(economia.get("ANTICIPO_REEMBOLSABLE", "0"))
            subvencion = _parse_numero(economia.get("SUBVENCION", "0"))
            anualidades = [
                _parse_numero(economia.get("SUBVENCION_2025_TOTAL", "0")),
                _parse_numero(economia.get("SUBVENCION_2026", "0")),
                _parse_numero(economia.get("SUBVENCION_2027", "0")),
                _parse_numero(economia.get("SUBVENCION_2028", "0")),
            ]

            titulo = titulos_por_referencia.get(referencia, "")
            if titulo:
                proyecto_concedido: ProyectoConcedido = ProyectoContrato(
                    referencia=referencia,
                    area=area,
                    entidad=entidad,
                    ccaa=ccaa,
                    costes_directos=costes_directos,
                    costes_indirectos=costes_indirectos,
                    anticipo=anticipo,
                    subvencion=subvencion,
                    anualidades=anualidades,
                    num_contratos_predoc=max(num_contratos_predoc, 1),
                    titulo=titulo,
                )
                gestor_contratos.agregar(proyecto_concedido)
            else:
                proyecto_concedido = ProyectoConcedido(
                    referencia=referencia,
                    area=area,
                    entidad=entidad,
                    ccaa=ccaa,
                    costes_directos=costes_directos,
                    costes_indirectos=costes_indirectos,
                    anticipo=anticipo,
                    subvencion=subvencion,
                    anualidades=anualidades,
                    num_contratos_predoc=num_contratos_predoc,
                )

            gestor_concedidos.agregar(proyecto_concedido)
            gestor_todos.agregar(proyecto_concedido)

        return gestor_todos, gestor_concedidos, gestor_contratos
