from itertools import product


class CorpoFinito:
    """
    Representa um corpo finito GF(p^m).

    Para m = 1:
        GF(p)

    Para m > 1:
        GF(p)[x] / (f(x))

    onde f é um polinômio irredutível de grau m.

    Polinômios são representados por tuplas de coeficientes
    em ordem crescente:

        (a0, a1, ..., an)

    representa

        a0 + a1*x + ... + an*x^n
    """

    def __init__(self, p, m=1, polinomio_irredutivel=None):

        if not self._eh_primo(p):
            raise ValueError("p deve ser primo.")

        if m < 1:
            raise ValueError("A extensão deve ter grau >= 1.")

        self.p = p
        self.m = m
        self.q = p ** m

        # Caso base: GF(p)
        if m == 1:
            self.polinomio_irredutivel = None
            self.elementos = tuple(range(p))
            self.zero = 0
            self.um = 1

        # Caso de extensão: GF(p^m)
        else:
            if polinomio_irredutivel is None:
                raise ValueError(
                    "Para GF(p^m), forneça um polinômio irredutível."
                )

            polinomio = tuple(
                coef % p for coef in polinomio_irredutivel
            )

            if len(polinomio) != m + 1:
                raise ValueError(
                    f"O polinômio deve possuir grau {m}."
                )

            if polinomio[-1] == 0:
                raise ValueError(
                    "O coeficiente líder não pode ser zero."
                )

            self.polinomio_irredutivel = polinomio

            # Todos os polinômios de grau < m.
            self.elementos = tuple(
                product(range(p), repeat=m)
            )

            self.zero = (0,) * m
            self.um = (1,) + (0,) * (m - 1)

    @staticmethod
    def _eh_primo(n):
        if n < 2:
            return False

        if n == 2:
            return True

        if n % 2 == 0:
            return False

        divisor = 3

        while divisor * divisor <= n:
            if n % divisor == 0:
                return False

            divisor += 2

        return True

    def contem(self, elemento):
        """
        Verifica se elemento pertence ao corpo.
        """

        return elemento in self.elementos

    def somar(self, a, b):
        self._verificar_elementos(a, b)

        if self.m == 1:
            return (a + b) % self.p

        return tuple(
            (x + y) % self.p
            for x, y in zip(a, b)
        )

    def subtrair(self, a, b):
        self._verificar_elementos(a, b)

        if self.m == 1:
            return (a - b) % self.p

        return tuple(
            (x - y) % self.p
            for x, y in zip(a, b)
        )

    def oposto(self, a):
        self._verificar_elementos(a)

        if self.m == 1:
            return (-a) % self.p

        return tuple(
            (-x) % self.p
            for x in a
        )

    def multiplicar(self, a, b):
        self._verificar_elementos(a, b)

        if self.m == 1:
            return (a * b) % self.p

        produto = [0] * (2 * self.m - 1)

        # Multiplicação de polinômios
        for i, coef_a in enumerate(a):
            for j, coef_b in enumerate(b):
                produto[i + j] += coef_a * coef_b
                produto[i + j] %= self.p

        # Redução módulo f(x)
        produto = self._reduzir_polinomio(produto)

        return tuple(produto)

    def potencia(self, a, n):
        self._verificar_elementos(a)

        if n < 0:
            return self.potencia(
                self.inverso(a),
                -n
            )

        resultado = self.um
        base = a

        while n > 0:
            if n % 2 == 1:
                resultado = self.multiplicar(
                    resultado,
                    base
                )

            base = self.multiplicar(base, base)
            n //= 2

        return resultado

    def inverso(self, a):
        self._verificar_elementos(a)

        if a == self.zero:
            raise ZeroDivisionError(
                "O elemento zero não possui inverso."
            )

        # Todo elemento não nulo de GF(q) satisfaz:
        #
        # a^(q-1) = 1
        #
        # portanto:
        #
        # a^(-1) = a^(q-2)

        return self.potencia(a, self.q - 2)

    def dividir(self, a, b):
        self._verificar_elementos(a, b)

        return self.multiplicar(
            a,
            self.inverso(b)
        )

    def _reduzir_polinomio(self, polinomio):

        polinomio = [
            coef % self.p
            for coef in polinomio
        ]

        f = self.polinomio_irredutivel

        # O coeficiente líder de f
        # precisa ser invertível.
        inverso_lider = pow(
            f[-1],
            self.p - 2,
            self.p
        )

        while len(polinomio) > self.m:

            grau = len(polinomio) - 1

            coef = polinomio[-1]

            if coef != 0:

                fator = (
                    coef * inverso_lider
                ) % self.p

                diferenca = grau - self.m

                for i in range(self.m + 1):

                    indice = diferenca + i

                    polinomio[indice] -= (
                        fator * f[i]
                    )

                    polinomio[indice] %= self.p

            polinomio.pop()

        while len(polinomio) < self.m:
            polinomio.append(0)

        return polinomio

    def _verificar_elementos(self, *elementos):

        for elemento in elementos:
            if not self.contem(elemento):
                raise ValueError(
                    f"{elemento} não pertence a GF({self.q})."
                )

    def __eq__(self, outro):

        if not isinstance(outro, CorpoFinito):
            return False

        return (
            self.p == outro.p
            and self.m == outro.m
            and self.polinomio_irredutivel
            == outro.polinomio_irredutivel
        )

    def __hash__(self):
        return hash(
            (
                self.p,
                self.m,
                self.polinomio_irredutivel
            )
        )

    def __repr__(self):

        if self.m == 1:
            return f"GF({self.p})"

        return f"GF({self.p}^{self.m})"