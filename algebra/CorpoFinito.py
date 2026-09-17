from itertools import product


class CorpoFinito:
    """
    Representa um corpo finito GF(q), onde q = p^m.

    O usuário fornece apenas q:

        CorpoFinito(2)  -> GF(2)
        CorpoFinito(4)  -> GF(4)
        CorpoFinito(8)  -> GF(8)
        CorpoFinito(9)  -> GF(9)

    Para m > 1, um polinômio irredutível é encontrado
    automaticamente.

    Polinômios são representados por tuplas de coeficientes
    em ordem crescente:

        (a0, a1, ..., an)

    representa

        a0 + a1*x + ... + an*x^n
    """

    def __init__(self, q):

        if not isinstance(q, int) or q < 2:
            raise ValueError(
                "A ordem do corpo deve ser um inteiro >= 2."
            )

        p, m = self._decompor_ordem(q)

        self.p = p
        self.m = m
        self.q = q

        # ----------------------------------------------------
        # GF(p)
        # ----------------------------------------------------

        if m == 1:

            self.polinomio_irredutivel = None
            self.elementos = tuple(range(p))

            self.zero = 0
            self.um = 1

        # ----------------------------------------------------
        # GF(p^m)
        # ----------------------------------------------------

        else:

            self.polinomio_irredutivel = (
                self._encontrar_polinomio_irredutivel(p, m)
            )

            # Todos os polinômios de grau < m.
            self.elementos = tuple(
                product(range(p), repeat=m)
            )

            self.zero = (0,) * m
            self.um = (1,) + (0,) * (m - 1)

    # ========================================================
    # CONSTRUÇÃO DO CORPO
    # ========================================================

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

    @classmethod
    def _decompor_ordem(cls, q):

        """
        Encontra p e m tais que

            q = p^m

        com p primo.
        """

        # Caso q seja primo
        if cls._eh_primo(q):
            return q, 1

        # Procura um primo p e um expoente m
        # tais que p^m = q.
        p = 2

        while p <= q:

            if cls._eh_primo(p):

                potencia = p
                m = 1

                while potencia < q:
                    potencia *= p
                    m += 1

                if potencia == q:
                    return p, m

            p += 1

        raise ValueError(
            f"{q} não é uma potência de primo."
        )

    # ========================================================
    # POLINÔMIOS
    # ========================================================

    @staticmethod
    def _normalizar_polinomio(polinomio, p):

        polinomio = [
            coef % p
            for coef in polinomio
        ]

        while len(polinomio) > 1 and polinomio[-1] == 0:
            polinomio.pop()

        return polinomio

    @staticmethod
    def _grau_polinomio(polinomio):

        polinomio = list(polinomio)

        while len(polinomio) > 1 and polinomio[-1] == 0:
            polinomio.pop()

        return len(polinomio) - 1

    @classmethod
    def _dividir_polinomios(cls, a, b, p):

        a = cls._normalizar_polinomio(a, p)
        b = cls._normalizar_polinomio(b, p)

        if b == [0]:
            raise ZeroDivisionError(
                "Divisão por polinômio nulo."
            )

        quociente = [0] * max(
            1,
            len(a) - len(b) + 1
        )

        resto = a[:]

        inv_lider = pow(
            b[-1],
            p - 2,
            p
        )

        while resto != [0] and len(resto) >= len(b):

            diferenca = len(resto) - len(b)

            fator = (
                resto[-1] * inv_lider
            ) % p

            quociente[diferenca] = fator

            for i in range(len(b)):

                indice = diferenca + i

                resto[indice] -= (
                    fator * b[i]
                )

                resto[indice] %= p

            resto = cls._normalizar_polinomio(
                resto,
                p
            )

        return (
            cls._normalizar_polinomio(quociente, p),
            resto
        )

    @classmethod
    def _resto_polinomios(cls, a, b, p):

        return cls._dividir_polinomios(
            a,
            b,
            p
        )[1]

    @classmethod
    def _mdc_polinomios(cls, a, b, p):

        a = cls._normalizar_polinomio(a, p)
        b = cls._normalizar_polinomio(b, p)

        while b != [0]:

            resto = cls._resto_polinomios(
                a,
                b,
                p
            )

            a = b
            b = resto

        # Normaliza o polinômio para que o
        # coeficiente líder seja 1.
        if a == [0]:
            return [0]

        inv_lider = pow(
            a[-1],
            p - 2,
            p
        )

        return [
            (coef * inv_lider) % p
            for coef in a
        ]

    @classmethod
    def _multiplicar_polinomios(cls, a, b, p):

        resultado = [0] * (
            len(a) + len(b) - 1
        )

        for i, coef_a in enumerate(a):

            for j, coef_b in enumerate(b):

                resultado[i + j] += (
                    coef_a * coef_b
                )

                resultado[i + j] %= p

        return cls._normalizar_polinomio(
            resultado,
            p
        )

    @classmethod
    def _potencia_polinomio_modulo(
        cls,
        base,
        expoente,
        modulo,
        p
    ):

        resultado = [1]

        base = cls._resto_polinomios(
            base,
            modulo,
            p
        )

        while expoente > 0:

            if expoente % 2 == 1:

                produto = cls._multiplicar_polinomios(
                    resultado,
                    base,
                    p
                )

                resultado = cls._resto_polinomios(
                    produto,
                    modulo,
                    p
                )

            produto = cls._multiplicar_polinomios(
                base,
                base,
                p
            )

            base = cls._resto_polinomios(
                produto,
                modulo,
                p
            )

            expoente //= 2

        return resultado

    # ========================================================
    # IRREDUTIBILIDADE
    # ========================================================

    @classmethod
    def _eh_irredutivel(cls, polinomio, p):

        """
        Testa se um polinômio é irredutível sobre GF(p).

        Usa o critério de Rabin.
        """

        grau = cls._grau_polinomio(polinomio)

        if grau <= 0:
            return False

        # x
        x = [0, 1]

        # Para cada divisor primo r de grau:
        #
        # gcd(f, x^(p^(grau/r)) - x) = 1
        #
        for r in cls._divisores_primos(grau):

            expoente = p ** (grau // r)

            potencia = cls._potencia_polinomio_modulo(
                x,
                expoente,
                polinomio,
                p
            )

            diferenca = potencia[:]

            if len(diferenca) < 2:
                diferenca += [0] * (
                    2 - len(diferenca)
                )

            diferenca[1] -= 1
            diferenca = cls._normalizar_polinomio(
                diferenca,
                p
            )

            mdc = cls._mdc_polinomios(
                polinomio,
                diferenca,
                p
            )

            if cls._grau_polinomio(mdc) != 0:
                return False

        # Condição final:
        #
        # x^(p^grau) = x (mod f)
        #
        potencia = cls._potencia_polinomio_modulo(
            x,
            p ** grau,
            polinomio,
            p
        )

        diferenca = potencia[:]

        if len(diferenca) < 2:
            diferenca += [0] * (
                2 - len(diferenca)
            )

        diferenca[1] -= 1

        diferenca = cls._normalizar_polinomio(
            diferenca,
            p
        )

        return diferenca == [0]

    @staticmethod
    def _divisores_primos(n):

        divisores = set()
        divisor = 2

        while divisor * divisor <= n:

            if n % divisor == 0:

                divisores.add(divisor)

                while n % divisor == 0:
                    n //= divisor

            divisor += 1

        if n > 1:
            divisores.add(n)

        return divisores

    @classmethod
    def _encontrar_polinomio_irredutivel(
        cls,
        p,
        m
    ):

        # O polinômio será mónico:
        #
        # a0 + a1*x + ... + a_(m-1)*x^(m-1) + x^m
        #
        for coeficientes in product(
            range(p),
            repeat=m
        ):

            polinomio = (
                tuple(coeficientes)
                + (1,)
            )

            if cls._eh_irredutivel(
                polinomio,
                p
            ):
                return polinomio

        raise ValueError(
            f"Não foi encontrado polinômio "
            f"irredutível de grau {m} sobre GF({p})."
        )

    # ========================================================
    # OPERAÇÕES DO CORPO
    # ========================================================

    def contem(self, elemento):

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

        produto = [0] * (
            2 * self.m - 1
        )

        for i, coef_a in enumerate(a):

            for j, coef_b in enumerate(b):

                produto[i + j] += (
                    coef_a * coef_b
                )

                produto[i + j] %= self.p

        produto = self._reduzir_polinomio(
            produto
        )

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

            base = self.multiplicar(
                base,
                base
            )

            n //= 2

        return resultado

    def inverso(self, a):

        self._verificar_elementos(a)

        if a == self.zero:

            raise ZeroDivisionError(
                "O elemento zero não possui inverso."
            )

        return self.potencia(
            a,
            self.q - 2
        )

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
                    f"{elemento} não pertence "
                    f"a GF({self.q})."
                )

    # ========================================================
    # REPRESENTAÇÃO
    # ========================================================

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