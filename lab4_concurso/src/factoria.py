import csv

from dataset import DataSetClasificacion, DataSetRegresion
from Registro import RegistroClasificacion, RegistroRegresion


def _resolver_indice(indice_objetivo: int, total_columnas: int) -> int:
    indice = indice_objetivo if indice_objetivo >= 0 else total_columnas + indice_objetivo
    if indice < 0 or indice >= total_columnas:
        raise IndexError("El indice_objetivo esta fuera del rango de columnas.")
    return indice


def _separar_atributos_objetivo(fila: list[object], indice_objetivo: int) -> tuple[list[object], object]:
    atributos = [valor for i, valor in enumerate(fila) if i != indice_objetivo]
    objetivo = fila[indice_objetivo]
    return atributos, objetivo


def _setear_cabeceras(
    dataset: DataSetClasificacion | DataSetRegresion,
    cabeceras: list[str],
    indice_objetivo: int,
) -> None:
    cabeceras_reordenadas = [str(valor) for i, valor in enumerate(cabeceras) if i != indice_objetivo]
    cabeceras_reordenadas.append(str(cabeceras[indice_objetivo]))
    dataset.set_cabeceras(cabeceras_reordenadas)


class FactoriaCSV:
    @staticmethod
    def crear_dataset_clasificacion(
        ruta_archivo: str,
        indice_objetivo: int = -1,
    ) -> DataSetClasificacion:
        with open(ruta_archivo, mode="r", newline="", encoding="utf-8-sig") as archivo_csv:
            lector = csv.reader(archivo_csv)
            cabeceras = next(lector, None)
            if cabeceras is None:
                raise ValueError("El archivo CSV esta vacio.")

            indice = _resolver_indice(indice_objetivo, len(cabeceras))
            dataset = DataSetClasificacion()
            _setear_cabeceras(dataset, cabeceras, indice)

            for numero_fila, fila in enumerate(lector, start=2):
                if not fila:
                    continue
                if len(fila) != len(cabeceras):
                    raise ValueError(
                        f"Fila {numero_fila} invalida: se esperaban {len(cabeceras)} columnas y hay {len(fila)}."
                    )

                atributos_crudos, objetivo_crudo = _separar_atributos_objetivo(fila, indice)
                atributos = [float(valor) for valor in atributos_crudos]
                objetivo = str(objetivo_crudo).strip()
                dataset.agregar_registro(RegistroClasificacion(atributos, objetivo))

        return dataset

    @staticmethod
    def crear_dataset_regresion(
        ruta_archivo: str,
        indice_objetivo: int = -1,
    ) -> DataSetRegresion:
        with open(ruta_archivo, mode="r", newline="", encoding="utf-8-sig") as archivo_csv:
            lector = csv.reader(archivo_csv)
            cabeceras = next(lector, None)
            if cabeceras is None:
                raise ValueError("El archivo CSV esta vacio.")

            indice = _resolver_indice(indice_objetivo, len(cabeceras))
            dataset = DataSetRegresion()
            _setear_cabeceras(dataset, cabeceras, indice)

            for numero_fila, fila in enumerate(lector, start=2):
                if not fila:
                    continue
                if len(fila) != len(cabeceras):
                    raise ValueError(
                        f"Fila {numero_fila} invalida: se esperaban {len(cabeceras)} columnas y hay {len(fila)}."
                    )

                atributos_crudos, objetivo_crudo = _separar_atributos_objetivo(fila, indice)
                atributos = [float(valor) for valor in atributos_crudos]
                objetivo = float(objetivo_crudo)
                dataset.agregar_registro(RegistroRegresion(atributos, objetivo))

        return dataset


class FactoriaXLS:
    @staticmethod
    def crear_dataset_clasificacion(
        ruta_archivo: str,
        indice_objetivo: int = -1,
    ) -> DataSetClasificacion:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "FactoriaXLS requiere pandas instalado para leer archivos Excel."
            ) from exc

        try:
            tabla = pd.read_excel(ruta_archivo)
        except ImportError as exc:
            raise ImportError(
                "No hay motor de Excel disponible. Instala openpyxl para ficheros .xlsx."
            ) from exc

        if len(tabla.columns) == 0:
            raise ValueError("El archivo Excel no contiene columnas.")

        cabeceras = [str(valor) for valor in tabla.columns.tolist()]
        indice = _resolver_indice(indice_objetivo, len(cabeceras))
        dataset = DataSetClasificacion()
        _setear_cabeceras(dataset, cabeceras, indice)

        for fila in tabla.itertuples(index=False, name=None):
            fila_lista = list(fila)
            atributos_crudos, objetivo_crudo = _separar_atributos_objetivo(fila_lista, indice)
            atributos = [float(valor) for valor in atributos_crudos]
            objetivo = "" if pd.isna(objetivo_crudo) else str(objetivo_crudo).strip()
            dataset.agregar_registro(RegistroClasificacion(atributos, objetivo))

        return dataset

    @staticmethod
    def crear_dataset_regresion(
        ruta_archivo: str,
        indice_objetivo: int = -1,
    ) -> DataSetRegresion:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "FactoriaXLS requiere pandas instalado para leer archivos Excel."
            ) from exc

        try:
            tabla = pd.read_excel(ruta_archivo)
        except ImportError as exc:
            raise ImportError(
                "No hay motor de Excel disponible. Instala openpyxl para ficheros .xlsx."
            ) from exc

        if len(tabla.columns) == 0:
            raise ValueError("El archivo Excel no contiene columnas.")

        cabeceras = [str(valor) for valor in tabla.columns.tolist()]
        indice = _resolver_indice(indice_objetivo, len(cabeceras))
        dataset = DataSetRegresion()
        _setear_cabeceras(dataset, cabeceras, indice)

        for fila in tabla.itertuples(index=False, name=None):
            fila_lista = list(fila)
            atributos_crudos, objetivo_crudo = _separar_atributos_objetivo(fila_lista, indice)
            atributos = [float(valor) for valor in atributos_crudos]
            objetivo = float(objetivo_crudo)
            dataset.agregar_registro(RegistroRegresion(atributos, objetivo))

        return dataset
