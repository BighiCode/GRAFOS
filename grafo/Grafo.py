class Grafo:
    def __init__(self, vertices=None):
        self.vertices = set(vertices) if vertices is not None else set()
        self.arestas = {}

        for vertice in self.vertices:
            self.arestas[vertice] = set()

    def adicionar_vertice(self, vertice):
        if vertice not in self.vertices:
            self.vertices.add(vertice)
            self.arestas[vertice] = set()

    def adicionar_aresta(self, u, v):
        if u not in self.vertices:
            self.adicionar_vertice(u)

        if v not in self.vertices:
            self.adicionar_vertice(v)

        if u == v:
            return

        self.arestas[u].add(v)
        self.arestas[v].add(u)

    def tem_aresta(self, u, v):
        return v in self.arestas.get(u, set())

    def vizinhos(self, vertice):
        return self.arestas.get(vertice, set())

    def grau(self, vertice):
        return len(self.vizinhos(vertice))

    def quantidade_vertices(self):
        return len(self.vertices)

    def quantidade_arestas(self):
        return sum(
            len(vizinhos)
            for vizinhos in self.arestas.values()
        ) // 2

    def construir_por_distancia_hamming(self, distancia=1):
        vertices = list(self.vertices)

        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                u = vertices[i]
                v = vertices[j]

                if u.distancia_hamming(v) == distancia:
                    self.adicionar_aresta(u, v)

    def __repr__(self):
        return (
            f"Grafo("
            f"vertices={self.quantidade_vertices()}, "
            f"arestas={self.quantidade_arestas()})"
        )

    def distancias_ao_codigo(self, codigo):
        distancias = {}

        for vertice in self.vertices:
            distancias[vertice] = codigo.distancia_ao_codigo(vertice)

        return distancias

    def classes_de_distancia(self, codigo):
        distancias = self.distancias_ao_codigo(codigo)

        classes = {}

        for vertice, distancia in distancias.items():
            if distancia not in classes:
                classes[distancia] = set()

            classes[distancia].add(vertice)

        return classes

    def rotular_por_distancia(self, codigo):
        rotulos = {}

        for vertice in self.vertices:
            rotulos[vertice] = codigo.distancia_ao_codigo(vertice)

        return rotulos

    def classe_de_rotulo(self, rotulos, rotulo):
        return {
            vertice
            for vertice in self.vertices
            if rotulos[vertice] == rotulo
        }

    def rotulos(self, codigo):
        return set(
            codigo.distancia_ao_codigo(vertice)
            for vertice in self.vertices
        )