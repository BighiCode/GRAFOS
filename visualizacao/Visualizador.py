from pyvis.network import Network


class Visualizador:
    def __init__(self, grafo):
        self.grafo = grafo

    def visualizar_por_distancia(
        self,
        codigo,
        k=1,
        arquivo="grafo.html"
    ):
        rede = Network(
            height="800px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000"
        )

        # Paleta de cores para as palavras do código
        cores = [
            "#FF0000",  # vermelho
            "#0000FF",  # azul
            "#00AA00",  # verde
            "#FF8000",  # laranja
            "#8000FF",  # roxo
            "#00AAAA",  # ciano
            "#FF00AA",  # rosa
            "#A06000",  # marrom
            "#008080",  # verde-azulado
            "#800080"   # púrpura
        ]

        palavras_codigo = list(codigo.elementos())

        # Calcula a distância de cada vértice ao código
        distancias = self.grafo.rotular_por_distancia(codigo)

        # Para cada vértice, determina a qual palavra do código
        # ele pertence dentro do raio k.
        classes = {}

        for vertice in self.grafo.vertices:
            palavras_proximas = []

            for i, palavra in enumerate(palavras_codigo):
                distancia = vertice.distancia_hamming(palavra)

                if distancia <= k:
                    palavras_proximas.append(i)

            classes[vertice] = palavras_proximas

        # Adiciona os vértices
        for vertice in self.grafo.vertices:

            proximas = classes[vertice]

            if proximas:
                # O vértice está dentro de uma bola de Hamming.
                indice = proximas[0]
                cor = cores[indice % len(cores)]

            else:
                # Vértices fora de todos os raios.
                cor = "#FFFF00"

            distancia = distancias[vertice]

            rede.add_node(
                str(vertice),
                label=str(vertice),
                title=(
                    f"Vértice: {vertice}<br>"
                    f"Distância ao código: {distancia}"
                ),
                color=cor,
                size=20 if vertice in palavras_codigo else 15
            )

        # Adiciona as arestas
        arestas_adicionadas = set()

        for u in self.grafo.vertices:
            for v in self.grafo.vizinhos(u):

                aresta = frozenset((str(u), str(v)))

                if aresta in arestas_adicionadas:
                    continue

                # Verifica se a aresta liga uma palavra do código
                # a uma palavra dentro do raio k.
                cor_aresta = "#999999"
                largura = 1

                for i, palavra in enumerate(palavras_codigo):

                    u_eh_codigo = u == palavra
                    v_eh_codigo = v == palavra

                    if u_eh_codigo:
                        distancia = v.distancia_hamming(palavra)

                        if 0 < distancia <= k:
                            cor_aresta = cores[i % len(cores)]
                            largura = 4
                            break

                    if v_eh_codigo:
                        distancia = u.distancia_hamming(palavra)

                        if 0 < distancia <= k:
                            cor_aresta = cores[i % len(cores)]
                            largura = 4
                            break

                rede.add_edge(
                    str(u),
                    str(v),
                    color=cor_aresta,
                    width=largura
                )

                arestas_adicionadas.add(aresta)

        rede.set_options("""
        {
            "physics": {
                "enabled": true
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": true,
                "dragNodes": true,
                "zoomView": true,
                "dragView": true
            }
        }
        """
        )

        rede.write_html(arquivo)

        print(f"Grafo gerado em: {arquivo}")