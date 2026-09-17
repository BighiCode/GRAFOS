from algebra.Vetor import Vetor


class CodigoLinear:
    def __init__(self, espaco, geradores):
        self.espaco = espaco
        self.geradores = tuple(geradores)

        for gerador in self.geradores:
            if not self.espaco.contem(gerador):
                raise ValueError(
                    "Todos os geradores devem pertencer ao espaço vetorial."
                )

        self._elementos = None

    def elementos(self):
        """
        Retorna todos os vetores do código linear.

        O código é o subespaço gerado pelos geradores:
            C = span{geradores}
        """

        if self._elementos is not None:
            return self._elementos

        elementos = {self.espaco.zero()}

        for gerador in self.geradores:
            novos_elementos = set()

            for vetor in elementos:
                for escalar in self.espaco.corpo.elementos:
                    novos_elementos.add(vetor + escalar * gerador)

            elementos = novos_elementos

        self._elementos = elementos

        return elementos

    def contem(self, vetor):
        """Verifica se um vetor pertence ao código."""

        return vetor in self.elementos()

    def distancia_ao_codigo(self, vetor):
        """
        Calcula a distância de Hamming de um vetor ao código:

            d(v,C) = min{d_H(v,c) : c ∈ C}.
        """

        if not self.espaco.contem(vetor):
            raise ValueError(
                "O vetor deve pertencer ao espaço vetorial."
            )

        return min(
            vetor.distancia_hamming(codigo)
            for codigo in self.elementos()
        )

    def esta_a_distancia(self, vetor, k):
        """
        Verifica se o vetor está a distância de Hamming
        menor ou igual a k do código.
        """

        return self.distancia_ao_codigo(vetor) <= k

    def dimensao(self):
        """
        Retorna a dimensão do código.

        Para um código linear sobre GF(q):

            |C| = q^k

        onde k é a dimensão do código.
        """

        quantidade = len(self.elementos())
        q = len(self.espaco.corpo.elementos)

        dimensao = 0

        while quantidade > 1:
            quantidade //= q
            dimensao += 1

        return dimensao

    def __len__(self):
        return len(self.elementos())

    def __repr__(self):
        return (
            f"CodigoLinear("
            f"dimensao={self.dimensao()}, "
            f"comprimento={self.espaco.dimensao})"
        )