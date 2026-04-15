class GraficadorNombres:
    @classmethod
    def graficar_tendencias(cls, nomenclator, lista_nombres, ruta_salida):
        import matplotlib.pyplot as plt

        series = nomenclator.series_tanto_por_mil(lista_nombres)
        if len(series) == 0:
            return

        plt.figure(figsize=(12, 6))

        for etiqueta in series:
            datos = series[etiqueta]
            decadas = []
            valores = []
            for decada, valor in datos:
                decadas.append(decada)
                valores.append(valor)
            plt.plot(decadas, valores, marker="o", label=etiqueta)

        plt.title("Tendencia del tanto por mil")
        plt.xlabel("Decada")
        plt.ylabel("Tanto por mil")
        plt.xticks(rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(ruta_salida)
        plt.close()

    @classmethod
    def graficar_diversificacion(cls, nomenclator, cantidad, genero, ruta_salida):
        import matplotlib.pyplot as plt

        datos = nomenclator.suma_top_n_por_mil_por_decada(cantidad, genero)
        decadas = list(datos.keys())
        valores = list(datos.values())

        plt.figure(figsize=(12, 6))
        plt.plot(decadas, valores, marker="o")
        plt.title("Suma del tanto por mil de los nombres mas frecuentes")
        plt.xlabel("Decada")
        plt.ylabel("Suma del tanto por mil")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(ruta_salida)
        plt.close()
