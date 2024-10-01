from time import time
from Print import LockPrint, gprint
from gurobipy import Model, GRB, quicksum
from parameters import Parameters
from collections import namedtuple


def main(P, model_gap=0.1, max_sectores=7, show_results=True):

    _print = LockPrint()
    _print.lock()

    # P = Parameters()

    # Ajustamos numero de sectores segun maximo de sectores
    P.SECTORES = P.SECTORES[0:max_sectores]

    T1 = time()

    m = Model('Grupo 64')

    # VARIABLES

    # Se acepta entrada de una persona en un sector
    x = m.addVars(P.PERSONAS, P.SECTORES, P.DIAS, vtype=GRB.BINARY, name='x')

    # Se habilita el uso de un sector
    y = m.addVars(P.SECTORES, P.DIAS, vtype=GRB.BINARY, name='y')

    # Cantidad de vendedores en un sector
    w = m.addVars(P.SECTORES, P.DIAS, vtype=GRB.INTEGER, lb=0, name='w')

    # Cantidad de personal de seguridad en un sector
    u = m.addVars(P.SECTORES, P.DIAS, vtype=GRB.INTEGER, lb=0, name='u')

    m.update()

    # RESTRICCIONES

    for SECTOR in P.SECTORES:
        for DIA in P.DIAS:
            m.addConstr(
                quicksum(
                    x[PERSONA, SECTOR, DIA] for PERSONA in P.PERSONAS
                ) + (P.CUPOS_VENDEDOR * w[SECTOR, DIA]) + u[SECTOR, DIA]
                <= P.AFOROS[SECTOR],
                name=f'R1_{{{SECTOR=},{DIA=}}}'
            )  # Los aforos por sector no pueden ser superados

            m.addConstr(
                quicksum(
                    x[PERSONA, SECTOR, DIA] for PERSONA in P.PERSONAS
                ) <= P.M * y[SECTOR, DIA],
                name=f'R2_{{{SECTOR=},{DIA=}}}'
            )  # Si un sector no se habilita, no se aceptan asistentes

            m.addConstr(
                w[SECTOR, DIA] <= P.M * y[SECTOR, DIA],
                name=f'R3_{{{SECTOR=},{DIA=}}}'
            )  # Si un sector no se habilita, no se aceptan vendedores

    for SECTOR in P.SECTORES:
        for DIA in P.DIAS[: -P.MAX_DIAS]:
            m.addConstr(
                quicksum(
                    y[SECTOR, DIA + i] for i in range(P.MAX_DIAS + 1)
                ) <= P.MAX_DIAS,
                name=f'R4_{{{SECTOR=},{DIA=}}}'
            )  # No superar los dias consecutivos

    for PERSONA in P.PERSONAS:
        for SECTOR in P.SECTORES:
            for DIA in P.DIAS:
                m.addConstr(
                    x[PERSONA, SECTOR, DIA] <= P.PASE[PERSONA],
                    name=f'R5_{{{PERSONA=},{SECTOR=},{DIA=}}}'
                )  # Solo se aceptan personas con pase de movilidad

    for PERSONA in P.PERSONAS:
        m.addConstr(
            quicksum(
                quicksum(
                    x[PERSONA, SECTOR, DIA] for SECTOR in P.SECTORES
                ) for DIA in P.DIAS
            ) <= 1,
            name=f'R6_{{{PERSONA=}}}'
        )  # Las personas solo son aceptadas en 1 sector como maximo en 1 dia

    for SECTOR in P.SECTORES:
        for DIA in P.DIAS:
            m.addConstr(
                w[SECTOR, DIA] >= P.RAZON_MAX[SECTOR] * quicksum(
                    x[PERSONA, SECTOR, DIA] for PERSONA in P.PERSONAS
                ),
                name=f'R7_{{{SECTOR=},{DIA=}}}'
            )
            # La razon entre personas y vendedores debe superar un cierto R

    for PERSONA in P.PERSONAS:
        for SECTOR in P.SECTORES:
            for DIA in P.DIAS:
                m.addConstr(
                    x[PERSONA, SECTOR, DIA]
                    <= P.DISPOSICION[PERSONA, SECTOR, DIA],
                    name=f'R8_{{{PERSONA=},{SECTOR=},{DIA=}}}'
                )  # Las personas son aceptadas en lugares de su preferencia

    for SECTOR in P.SECTORES:
        for DIA in P.DIAS:
            m.addConstr(
                quicksum(
                    x[PERSONA, SECTOR, DIA] for PERSONA in P.PERSONAS
                ) <= P.PROP_SEGURIDAD * u[SECTOR, DIA],
                name=f'R9_{{{SECTOR=},{DIA=}}}'
            )  # Cada cierta cantidad de asistentes, debe haber 1 guardia

        m.addConstr(
            u[SECTOR, DIA] <= P.M * y[SECTOR, DIA],
            name=f'R10_{{{SECTOR=},{DIA=}}}'
        )  # Si un sector no se habilita, no hay guardias

    # FUNCION OBJETIVO

    ENTRADAS = quicksum(
        quicksum(
            quicksum(
                P.ENTRADA[SECTOR][DIA] * x[PERSONA, SECTOR, DIA]
                for PERSONA in P.PERSONAS
            )
            for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Ganancia relacionada a la venta de entradas

    VENDEDORES = quicksum(
        quicksum(
            P.VENDEDOR[SECTOR][DIA] * w[SECTOR, DIA]
            for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Ganancia relacionada a la comision de los vendedores

    COSTO_SECTORES = quicksum(
        quicksum(
            P.COSTO_SECTOR[SECTOR] * y[SECTOR, DIA]
            for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Costos por habilitar los distintos sectores

    COSTO_SEGURIDAD = quicksum(
        quicksum(
            P.SEGURIDAD[SECTOR] * u[SECTOR, DIA]
            for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Costos por contratar personal de seguridad

    COSTO_VENTILACION = quicksum(
        quicksum(
            (1 - P.TERRAZA[SECTOR]) * quicksum(
                P.COSTO_VENTILACION[SECTOR] * x[PERSONA, SECTOR, DIA]
                for PERSONA in P.PERSONAS
            ) for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Costos relacionados a ventilacion de espacios cerrados

    COSTO_SANITIZACION = quicksum(
        quicksum(
            P.SANITIZAR[SECTOR] * (1 - y[SECTOR, DIA])
            for SECTOR in P.SECTORES
        )
        for DIA in P.DIAS
    )  # Costos relacionados a ventilacion de espacios cerrados

    COSTO_ARTISTA = P.K  # * len(P.DIAS)

    OBJETIVO = (
        - COSTO_ARTISTA
        + ENTRADAS
        + VENDEDORES
        - COSTO_SECTORES
        - COSTO_SEGURIDAD
        - COSTO_VENTILACION
        - COSTO_SANITIZACION
    )

    m.setObjective(OBJETIVO, GRB.MAXIMIZE)

    m.Params.MIPGap = model_gap / 100

    m.optimize()

    T2 = time()

    _print.unlock()

    size = 50
    gap = ' ' * 10

    if show_results:

        print()
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + f'    OPTIMO: $ {int(m.objVal):_}'.center(size) + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')

        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + f'EXEC TIME: {(T2 - T1):2.2f} s'.center(size) + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')

        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + 'RESUMEN DE VARIABLES'.center(size) + ' ')
        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')
        for DIA in P.DIAS:
            gprint(' ' + f'  DIA N°{DIA}'.ljust(size) + ' ')
            for SECTOR in P.SECTORES:
                nombre = P.NOMBRE_SECTORES[SECTOR]
                gprint(' ' + f'SECTOR N°{SECTOR}: {nombre}'.center(size) + ' ')
                habilitado = 'SI' if int(y[SECTOR, DIA].X) == 1 else 'NO'
                gprint(
                    ' ' + f'{gap}HABILITADO: {habilitado}'.ljust(size) + ' '
                )
                if habilitado == 'SI':
                    personas = int(
                        sum(x[p, SECTOR, DIA].X for p in P.PERSONAS)
                    )
                    gprint(
                        ' ' + f'{gap}ASISTENTES: {personas}'.ljust(size) + ' '
                    )
                    vend = int(w[SECTOR, DIA].X)
                    gprint(
                        ' ' + f'{gap}VENDEDORES: {vend}'.ljust(size) + ' '
                    )
                    seguridad = int(u[SECTOR, DIA].X)
                    gprint(
                        ' ' + f'{gap}SEGURIDAD : {seguridad}'.ljust(size) + ' '
                    )

                gprint(' ' + ' ' * size + ' ')
                gprint(' ' + ' ' * size + ' ')

        gprint(' ' + ' ' * size + ' ')
        gprint(' ' + ' ' * size + ' ')

        print('\n')
        constr = {}
        for i in range(1, 11):
            constr[f'R{i}'] = []

        for r in m.getConstrs():
            name = r.ConstrName.split('_')[0]
            constr[name].append(r)

        print('   Restriccion  |  Activas  |  Totales')
        print()
        for i in range(1, 11):
            R = f'R{i}'
            activas = sum(map(lambda x: 1 if x.slack == 0.0 else 0, constr[R]))
            totales = len(constr[R])
            print(f'   {R:11.11s}  |  {str(activas):7.7}  |  {totales}')

    OutputModelo = namedtuple('OutputModelo', ['m', 'x', 'y', 'w', 'u', 't'])

    output_modelo = OutputModelo(
        m,
        x,
        y,
        w,
        u,
        T2-T1
    )

    return output_modelo


if __name__ == '__main__':
    P = Parameters()
    main(P=P)
