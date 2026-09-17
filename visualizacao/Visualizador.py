import matplotlib.pyplot as plt
import networkx as nx


class Visualizador:
    def __init__(self, grafo):
        self.grafo = grafo

    def construir_grafo_networkx(self):
        G = nx.Graph()

        for vertice in self.grafo.vertices:
            G.add_node(vertice)

        for vertice in self.grafo.vertices:
            for vizinho in self.grafo.vizinhos(vertice):
                G.add_edge(vertice, vizinho)

        return G

    def visualizar(self, rotulos=None):
        G = self.construir_grafo_networkx()

        posicoes = nx.spring_layout(G, seed=42)

        if rotulos is None:
            rotulos = {
                vertice: ""
                for vertice in self.grafo.vertices
            }

        nx.draw(
            G,
            posicoes,
            with_labels=True,
            labels={
                vertice: str(vertice)
                for vertice in self.grafo.vertices
            },
            node_size=30,
            font_size=4
        )

        nx.draw_networkx_labels(
            G,
            posicoes,
            labels=rotulos,
            font_size=12,
            verticalalignment="bottom"
        )

        plt.title("Grafo")
        plt.show()

    def visualizar_por_distancia(self, codigo):
        G = self.construir_grafo_networkx()

        posicoes = nx.spring_layout(G, seed=42)

        distancias = self.grafo.rotular_por_distancia(codigo)

        nx.draw(
            G,
            posicoes,
            with_labels=True,
            labels={
                vertice: str(vertice)
                for vertice in self.grafo.vertices
            },
            node_size=1800,
            font_size=9,
            node_color=[
                distancias[vertice]
                for vertice in G.nodes
            ],
            cmap="viridis"
        )

        plt.title("Grafo por distância ao código")
        plt.show()