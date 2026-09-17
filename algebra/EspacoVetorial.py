from .Vetor import Vetor
from itertools import product

class EspacoVetorial:
    def __init__(self, corpo, dimensao):
        self.corpo = corpo
        self.dimensao = dimensao

    def vetor(self, elementos):
        return Vetor(elementos, self.corpo)

class EspacoVetorial:
    def __init__(self, corpo, dimensao):
        if dimensao <= 0:
            raise ValueError("A dimensão deve ser positiva.")

        self.corpo = corpo
        self.dimensao = dimensao

    def vetor(self, elementos):
        if len(elementos) != self.dimensao:
            raise ValueError(
                f"O vetor deve possuir {self.dimensao} coordenadas."
            )

        return Vetor(elementos, self.corpo)

    def zero(self):
        return Vetor(
            [self.corpo.zero] * self.dimensao,
            self.corpo
        )

    def elementos(self):
        elementos = product(
            self.corpo.elementos,
            repeat=self.dimensao
        )

        return [
            Vetor(coordenadas, self.corpo)
            for coordenadas in elementos
        ]

    def contem(self, vetor):
        return (
            isinstance(vetor, Vetor)
            and vetor.corpo == self.corpo
            and vetor.dimensao == self.dimensao
        )

    def __repr__(self):
        return f"{self.corpo}^{self.dimensao}"