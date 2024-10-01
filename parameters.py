from random import seed, choices, uniform


class Parameters:

    def __init__(
        self,
        n_personas=25000,
        n_sectores=7,
        n_dias=4,
        max_dias=2,
        cupos_vendedor=5,
        aporte_vendedor=100_000,
        ponderador_entradas=1.0
    ):
        seed('SAQUENME DE OPTI')
        # seed('https://www.youtube.com/watch?v=SkgTxQm9DWM&t=491s')

        self.PERSONAS = list(range(n_personas))  # I

        self.SECTORES = list(range(n_sectores))  # J

        self.DIAS = list(range(n_dias))          # T

        self.NOMBRE_SECTORES = {
            0: 'DIAMANTE',
            1: 'PLATINUM',
            2: 'PLATEA_ZAFIRO',
            3: 'PLATEA_ROYAL',
            4: 'GOLDEN',
            5: 'PLATEA_ALTA',
            6: 'TRIBUNA',
        }

        self.AFOROS = [
            126,  #
            356,
            583,  #
            358,  #
            264,
            790,
            96,
        ]  # A

        self.RAZON_MAX = [14/2_573] * n_sectores  # R
        self.RAZON_MIN = [7/2_573] * n_sectores  # R'

        self.ENTRADA = [
            112_700,
            102_350,
            90_850,
            82_800,
            77_050,
            46_000,
            33_350,
        ]  # g

        self.ENTRADA = [
            [
                int(x * uniform(0.95, 1.05) * ponderador_entradas)
                for dia in self.DIAS
            ]
            for x in self.ENTRADA
        ]

        self.VENDEDOR = [
            aporte_vendedor * ponderador_entradas
        ] * n_sectores  # v

        self.VENDEDOR = [
            [int(x * uniform(0.9, 1.1)) for dia in self.DIAS]
            for x in self.VENDEDOR
        ]

        self.CUPOS_VENDEDOR = cupos_vendedor  # V

        self.COSTO_SECTOR = [
            779_831,
            3_905_344,
            3_608_265,
            2_215_710,
            3_602_076,
            16_902_525,
            594_157,
        ]  # k

        self.SEGURIDAD = [50_000] * n_sectores  # l

        self.COSTO_VENTILACION = [944] * n_sectores  # c

        self.VACUNADOS = 0.9

        self.PASE = choices(
            [0, 1], weights=[1 - self.VACUNADOS, self.VACUNADOS], k=n_personas
        )  # m

        self.TERRAZA = [0] * n_sectores  # B

        self.DISPOSICION = {
            (PERSONA, SECTOR, DIA): choices([0, 1], weights=[0.3, 0.7], k=1)[0]
            for SECTOR in self.SECTORES
            for PERSONA in self.PERSONAS
            for DIA in self.DIAS
        }  # p

        self.PROP_SEGURIDAD = 52  # s

        self.MAX_DIAS = max_dias  # D

        self.SANITIZAR = [
            int(x * 0.1) for x in self.COSTO_SECTOR
        ]

        self.M = 10_000_000_000_000_000

        self.K = 81_140_000

        assert len(self.SECTORES) == len(self.NOMBRE_SECTORES)
        assert len(self.SECTORES) == len(self.AFOROS)
        assert len(self.SECTORES) == len(self.RAZON_MAX)
        assert len(self.SECTORES) == len(self.RAZON_MIN)
        assert len(self.SECTORES) == len(self.ENTRADA)
        assert len(self.SECTORES) == len(self.VENDEDOR)
        assert len(self.SECTORES) == len(self.COSTO_SECTOR)
        assert len(self.SECTORES) == len(self.SEGURIDAD)
        assert len(self.SECTORES) == len(self.COSTO_VENTILACION)
        assert len(self.SECTORES) == len(self.TERRAZA)
        assert len(self.SECTORES) == len(self.SANITIZAR)


if __name__ == '__main__':
    p = Parameters(n_personas=5)
    print(p.ENTRADA)
