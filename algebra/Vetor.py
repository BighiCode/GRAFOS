from itertools import product


class Vetor:
    def __init__(self, elementos, corpo):
        self.elementos = tuple(elementos)
        self.corpo = corpo

        if len(self.elementos) == 0:
            raise ValueError("Um vetor deve possuir pelo menos uma coordenada.")

        for elemento in self.elementos:
            if not corpo.contem(elemento):
                raise ValueError(
                    f"{elemento} não pertence ao corpo fornecido."
                )

    @property
    def dimensao(self):
        return len(self.elementos)

    def __add__(self, outro):
        self._verificar_compatibilidade(outro)

        elementos = [
            self.corpo.somar(a, b)
            for a, b in zip(self.elementos, outro.elementos)
        ]

        return Vetor(elementos, self.corpo)

    def __sub__(self, outro):
        self._verificar_compatibilidade(outro)

        elementos = [
            self.corpo.subtrair(a, b)
            for a, b in zip(self.elementos, outro.elementos)
        ]

        return Vetor(elementos, self.corpo)

    def __mul__(self, escalar):
        if not self.corpo.contem(escalar):
            raise ValueError(
                f"{escalar} não pertence ao corpo do vetor."
            )

        elementos = [
            self.corpo.multiplicar(escalar, elemento)
            for elemento in self.elementos
        ]

        return Vetor(elementos, self.corpo)

    def __rmul__(self, escalar):
        return self * escalar

    def distancia_hamming(self, outro):
        self._verificar_compatibilidade(outro)

        return sum(
            a != b
            for a, b in zip(self.elementos, outro.elementos)
        )

    def peso_hamming(self):
        return sum(
            elemento != self.corpo.zero
            for elemento in self.elementos
        )

    def _verificar_compatibilidade(self, outro):
        if not isinstance(outro, Vetor):
            raise TypeError("A operação exige outro Vetor.")

        if self.corpo != outro.corpo:
            raise ValueError("Os vetores pertencem a corpos diferentes.")

        if self.dimensao != outro.dimensao:
            raise ValueError("Os vetores possuem dimensões diferentes.")

    def __eq__(self, outro):
        if not isinstance(outro, Vetor):
            return False

        return (
            self.corpo == outro.corpo
            and self.elementos == outro.elementos
        )

    def __hash__(self):
        return hash((self.corpo, self.elementos))

    def __repr__(self):
        return str(self.elementos)