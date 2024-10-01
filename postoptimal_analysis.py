from parameters import Parameters
from main import main
import pandas as pd
import numpy as np
import os

# DICCIONARIO DE PARAMETROS PARA CADA INDICADOR


def parametros_asistencia(numero_personas):
    return Parameters(n_personas=numero_personas)


def parametros_dias_consecutivos(dias):
    return Parameters(max_dias=dias)


def parametros_costo_oportunidad_vendedor(cupos_vendedor):
    return Parameters(cupos_vendedor=cupos_vendedor)


def parametros_aporte_vendedor(aporte_vendedor):
    return Parameters(aporte_vendedor=aporte_vendedor)


def parametros_costo_entradas(ponderador_entradas):
    return Parameters(ponderador_entradas=ponderador_entradas)


def parametros_maximo_sectores(_):
    return Parameters()


PARAMETROS_INDICADOR = {
    "Asistencia": parametros_asistencia,
    "DiasConsecutivos": parametros_dias_consecutivos,
    "CostoOportunidadVendedor": parametros_costo_oportunidad_vendedor,
    "GananciaPorVendedor": parametros_aporte_vendedor,
    "CostoEntradas": parametros_costo_entradas,
    "MaximoSectores": parametros_maximo_sectores
}

# FUNCION DE ANALISIS POST OPTIMAL


def analisis_posoptimal(indicador, min_, max_, incremento):
    """
    Recibe valor minimo, maximo e incremento para un indicador.
    Indicador puede ser:
    a) Asistencia (Int): Numero de personas que llegan al evento
    b) DiasConsecutivos (Int): Maxima cantidad de dias consecutivos que un
       sector puede ser usado
    c) CostoOportunidadVendedor (Int): Cuanta asistencia se pierde por cada
       vendedor dentro de un sector
    d) GananciaPorVendedor (Int): Cantidad de dinero que aporta tener un
       vendedor en un sector
    e) CostoEntradas (Float): Ponderador que multiplica al precio de entrada
       de cada sector
    f) MaximoSectores (Int): Numero de sectores habilitados. Tiene que ser
       menor o igual a 7
    """

    # variacion numero personas
    RANGO_INDICADOR = [*np.arange(min_, max_ + incremento, incremento)]

    efecto_indicador = pd.DataFrame(
        columns=[
            f"{indicador}",
            "ValorOptimo",
            "TiempoEjecucion",
            "SectoresHabilitadosDia0",
            "SectoresHabilitadosDia1",
            "SectoresHabilitadosDia2",
            "SectoresHabilitadosDia3"
        ]
    )
    counter = 0
    for valor in RANGO_INDICADOR:

        # parametros indicador
        p = PARAMETROS_INDICADOR[indicador](valor)

        if indicador == "MaximoSectores":
            # analisis de maximo de sectores tiene parametro adicional en main
            output_modelo = main(
                P=p, model_gap=5, max_sectores=valor, show_results=False
            )

        else:
            output_modelo = main(
                P=p, model_gap=5, show_results=False
            )

        # valor optimo
        optimo = int(output_modelo.m.objVal)

        # tiempo ejecucion
        tiempo = output_modelo.t

        # sectores habilitados por dia
        sectores_por_dia = []
        for DIA in p.DIAS:
            numero_sectores = sum(
                output_modelo.y[SECTOR, DIA].X for SECTOR in p.SECTORES
            )
            sectores_por_dia.append(numero_sectores)

        values_to_add = {
            f"{indicador}": valor,
            "ValorOptimo": optimo,
            "TiempoEjecucion": tiempo,
            "SectoresHabilitadosDia0": sectores_por_dia[0],
            "SectoresHabilitadosDia1": sectores_por_dia[1],
            "SectoresHabilitadosDia2": sectores_por_dia[2],
            "SectoresHabilitadosDia3": sectores_por_dia[3]
            }
        row_to_add = pd.Series(values_to_add, name=counter)

        efecto_indicador = efecto_indicador.append(row_to_add)
        counter += 1

    print(f"\nRESUMEN EFECTO {indicador}".upper())
    print(efecto_indicador)

    # Guardar datos
    root = './postoptimal_analysis_data'

    if not os.path.exists(root):
        os.mkdir(root)

    efecto_indicador.to_csv(f"{root}/{indicador}.csv")


if __name__ == "__main__":

    analisis_posoptimal("MaximoSectores", 3, 7, 1)
    analisis_posoptimal("Asistencia", 2_000, 12_000, 2_000)
    analisis_posoptimal("DiasConsecutivos", 1, 4, 1)
    analisis_posoptimal("CostoOportunidadVendedor", 3, 5, 1)
    analisis_posoptimal("GananciaPorVendedor", 80_000, 140_000, 20_000)
    analisis_posoptimal("CostoEntradas", 0.5, 2.0, 0.5)
