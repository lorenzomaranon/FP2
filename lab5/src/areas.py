from __future__ import annotations


MACROAREAS = {
    "CMIFQ": "Ciencias Matematicas, Fisicas, Quimicas e Ingenierias",
    "CSH": "Ciencias Sociales y Humanidades",
    "CV": "Ciencias de la Vida",
}


AREAS_TEMATICAS = {
    "CSO": {
        "nombre": "Ciencias Sociales",
        "macroarea": "CSH",
        "subareas": {
            "COM": "Comunicacion",
            "CPO": "Ciencia politica",
            "FEM": "Estudios feministas, de las mujeres y de genero",
            "GEO": "Geografia",
            "SOC": "Sociologia y antropologia social",
        },
    },
    "DER": {
        "nombre": "Derecho",
        "macroarea": "CSH",
        "subareas": {
            "DER": "Derecho",
        },
    },
    "ECO": {
        "nombre": "Economia",
        "macroarea": "CSH",
        "subareas": {
            "EMA": "Economia, metodos y aplicaciones",
            "EYF": "Empresas y finanzas",
        },
    },
    "MLP": {
        "nombre": "Mente, lenguaje y pensamiento",
        "macroarea": "CSH",
        "subareas": {
            "FIL": "Filosofia",
            "LYL": "Linguistica y lenguas",
        },
    },
    "FLA": {
        "nombre": "Cultura: filologia, literatura y arte",
        "macroarea": "CSH",
        "subareas": {
            "ART": "Arte, bellas artes y museistica",
            "LFL": "Literatura, filologia y estudios culturales",
        },
    },
    "PHA": {
        "nombre": "Estudios del pasado: historia y arqueologia",
        "macroarea": "CSH",
        "subareas": {
            "ARQ": "Arqueologia",
            "HIS": "Historia",
        },
    },
    "EDU": {
        "nombre": "Ciencias de la educacion",
        "macroarea": "CSH",
        "subareas": {
            "EDU": "Ciencias de la educacion",
        },
    },
    "PSI": {
        "nombre": "Psicologia",
        "macroarea": "CSH",
        "subareas": {
            "PSI": "Psicologia",
        },
    },
    "MTM": {
        "nombre": "Ciencias matematicas",
        "macroarea": "CMIFQ",
        "subareas": {
            "MTM": "Ciencias matematicas",
        },
    },
    "FIS": {
        "nombre": "Ciencias fisicas",
        "macroarea": "CMIFQ",
        "subareas": {
            "AYA": "Astronomia y astrofisica",
            "ESP": "Investigacion espacial",
            "FPN": "Fisica de particulas y nuclear",
            "FAB": "Fisica aplicada y biofisica",
            "FCM": "Fisica cuantica y de la materia",
        },
    },
    "PIN": {
        "nombre": "Produccion industrial, ingenieria civil e ingenierias para la sociedad",
        "macroarea": "CMIFQ",
        "subareas": {
            "ICA": "Ingenieria civil y arquitectura",
            "IBI": "Ingenieria biomedica",
            "IEA": "Ingenieria electrica, electronica y automatica",
            "INA": "Ingenieria mecanica, naval y aeronautica",
        },
    },
    "TIC": {
        "nombre": "Tecnologias de la informacion y de las comunicaciones",
        "macroarea": "CMIFQ",
        "subareas": {
            "INF": "Ciencias de la computacion y tecnologia informatica",
            "MNF": "Microelectronica, nanotecnologia y fotonica",
            "TCO": "Tecnologias de las comunicaciones",
        },
    },
    "EYT": {
        "nombre": "Energia y transporte",
        "macroarea": "CMIFQ",
        "subareas": {
            "ENE": "Energia",
            "TRA": "Transporte",
        },
    },
    "CTQ": {
        "nombre": "Ciencias y tecnologias quimicas",
        "macroarea": "CMIFQ",
        "subareas": {
            "IQM": "Ingenieria quimica",
            "QMC": "Quimica",
        },
    },
    "MAT": {
        "nombre": "Ciencias y tecnologias de materiales",
        "macroarea": "CMIFQ",
        "subareas": {
            "MBM": "Materiales para biomedicina",
            "MEN": "Materiales para la energia y el medio ambiente",
            "MES": "Materiales estructurales",
            "MFU": "Materiales con funcionalidad electrica, magnetica, optica o termica",
        },
    },
    "CTM": {
        "nombre": "Ciencias y tecnologias medioambientales",
        "macroarea": "CV",
        "subareas": {
            "BDV": "Biodiversidad",
            "CTA": "Ciencias de la tierra y del agua",
            "CYA": "Clima y atmosfera",
            "MAR": "Ciencias y tecnologias marinas",
            "POL": "Investigacion polar",
            "TMA": "Tecnologias medioambientales",
        },
    },
    "CAA": {
        "nombre": "Ciencias agrarias y agroalimentarias",
        "macroarea": "CV",
        "subareas": {
            "ALI": "Ciencia y tecnologia de alimentos",
            "AYF": "Agricultura y forestal",
            "GYA": "Ganaderia y acuicultura",
        },
    },
    "BIO": {
        "nombre": "Biociencias y biotecnologia",
        "macroarea": "CV",
        "subareas": {
            "BIF": "Biologia integrativa y fisiologia",
            "BMC": "Biologia molecular y celular",
            "BTC": "Biotecnologia",
        },
    },
    "BME": {
        "nombre": "Biomedicina",
        "macroarea": "CV",
        "subareas": {
            "CAN": "Cancer",
            "ESN": "Enfermedades del sistema nervioso",
            "DPT": "Herramientas diagnosticas, pronosticas y terapeuticas",
            "FOS": "Fisiopatologia de organos y sistemas",
            "IIT": "Inmunidad, infeccion e inmunoterapia",
        },
    },
}


SUBAREA_A_AREA = {
    codigo_subarea: codigo_area
    for codigo_area, datos_area in AREAS_TEMATICAS.items()
    for codigo_subarea in datos_area["subareas"]
}


AREA_A_MACROAREA = {
    codigo_area: datos_area["macroarea"] for codigo_area, datos_area in AREAS_TEMATICAS.items()
}


def area_de_subarea(codigo_subarea: str) -> str:
    codigo = codigo_subarea.strip().upper()
    area = SUBAREA_A_AREA.get(codigo)
    if area is None:
        raise ValueError(f"Subarea no reconocida: {codigo_subarea}")
    return area


def macroarea_de_area(codigo_area: str) -> str:
    codigo = codigo_area.strip().upper()
    macroarea = AREA_A_MACROAREA.get(codigo)
    if macroarea is None:
        raise ValueError(f"Area no reconocida: {codigo_area}")
    return macroarea
