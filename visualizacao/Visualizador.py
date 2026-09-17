
from pyvis.network import Network
import math


class Visualizador:

    def __init__(self, grafo):
        self.grafo = grafo

    def _posicoes_codigo(self, palavras_codigo):
        """
        Coloca as palavras do código em posições afastadas,
        distribuídas em uma circunferência.
        """

        posicoes = {}

        quantidade = len(palavras_codigo)

        if quantidade == 1:
            posicoes[palavras_codigo[0]] = (0, 0)
            return posicoes

        raio = 1000

        for i, palavra in enumerate(palavras_codigo):

            angulo = (
                2 * math.pi * i / quantidade
            )

            x = raio * math.cos(angulo)
            y = raio * math.sin(angulo)

            posicoes[palavra] = (x, y)

        return posicoes

    def visualizar_por_distancia(
        self,
        codigo,
        k=1,
        arquivo="grafo.html"
    ):

        rede = Network(
            height="900px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#000000"
        )

        # ==================================================
        # CORES
        # ==================================================

        cores = [
            "#FF0000",
            "#0000FF",
            "#00AA00",
            "#FF8000",
            "#8000FF",
            "#00AAAA",
            "#FF00AA",
            "#A06000",
            "#008080",
            "#800080"
        ]

        palavras_codigo = list(codigo.elementos())

        # ==================================================
        # POSIÇÕES DAS PALAVRAS DO CÓDIGO
        # ==================================================

        posicoes_codigo = self._posicoes_codigo(
            palavras_codigo
        )

        # ==================================================
        # DISTÂNCIAS AO CÓDIGO
        # ==================================================

        distancias = self.grafo.rotular_por_distancia(
            codigo
        )

        # ==================================================
        # DETERMINA A BOLA DE CADA VÉRTICE
        # ==================================================

        classes = {}

        for vertice in self.grafo.vertices:

            palavras_proximas = []

            for i, palavra in enumerate(
                palavras_codigo
            ):

                distancia = (
                    vertice.distancia_hamming(palavra)
                )

                if distancia <= k:
                    palavras_proximas.append(i)

            classes[vertice] = palavras_proximas

        # ==================================================
        # VÉRTICES
        # ==================================================

        for vertice in self.grafo.vertices:

            proximas = classes[vertice]

            if proximas:

                indice = proximas[0]

                cor = cores[
                    indice % len(cores)
                ]

            else:

                cor = "#CCCCCC"

            distancia = distancias[vertice]

            if vertice in palavras_codigo:

                tamanho = 22
                borda = 4

                x, y = posicoes_codigo[vertice]

                fixed = True

            else:

                tamanho = 8
                borda = 1

                fixed = False

            atributos = {
                "label": str(vertice),
                "title": (
                    f"Vértice: {vertice}<br>"
                    f"Distância ao código: {distancia}"
                ),
                "color": cor,
                "size": tamanho,
                "borderWidth": borda,
                "fixed": fixed
            }

            if fixed:
                atributos["x"] = x
                atributos["y"] = y

            rede.add_node(
                str(vertice),
                **atributos
            )

        # ==================================================
        # ARESTAS
        # ==================================================

        arestas_adicionadas = set()

        for u in self.grafo.vertices:

            for v in self.grafo.vizinhos(u):

                identificador = frozenset(
                    (str(u), str(v))
                )

                if identificador in arestas_adicionadas:
                    continue

                cor_aresta = "#AAAAAA"
                largura = 1

                for i, palavra in enumerate(
                    palavras_codigo
                ):

                    distancia_u = (
                        u.distancia_hamming(palavra)
                    )

                    distancia_v = (
                        v.distancia_hamming(palavra)
                    )

                    if (
                        distancia_u <= k
                        and
                        distancia_v <= k
                    ):

                        cor_aresta = cores[
                            i % len(cores)
                        ]

                        largura = 3

                        break

                rede.add_edge(
                    str(u),
                    str(v),
                    color=cor_aresta,
                    width=largura
                )

                arestas_adicionadas.add(
                    identificador
                )

        # ==================================================
        # FÍSICA
        # ==================================================

        rede.set_options(
            """
            {
                "physics": {
                    "enabled": true,

                    "solver": "forceAtlas2Based",

                    "forceAtlas2Based": {
                        "gravitationalConstant": -150,
                        "centralGravity": 0.01,
                        "springLength": 100,
                        "springConstant": 0.04,
                        "damping": 0.8,
                        "avoidOverlap": 1
                    },

                    "minVelocity": 0.75,

                    "stabilization": {
                        "enabled": true,
                        "iterations": 2000,
                        "updateInterval": 100
                    }
                },

                "interaction": {
                    "hover": true,
                    "navigationButtons": true,
                    "keyboard": true,
                    "dragNodes": true,
                    "zoomView": true,
                    "dragView": true,
                    "selectConnectedEdges": false
                },

                "nodes": {
                    "font": {
                        "size": 14
                    }
                },

                "edges": {
                    "smooth": false
                }
            }
            """
        )

        # ==================================================
        # GERA O HTML
        # ==================================================

        rede.write_html(arquivo)

        # ==================================================
        # PAINEL DE INFORMAÇÕES
        # ==================================================

        corpo = codigo.espaco.corpo
        dimensao = codigo.espaco.dimensao
        geradores = codigo.geradores

        geradores_html = "<br>".join(
            str(gerador)
            for gerador in geradores
        )

        painel = f"""
        <div style="
            position: fixed;
            top: 15px;
            left: 15px;
            z-index: 9999;

            background: white;

            border: 1px solid #888;
            border-radius: 8px;

            padding: 12px;

            font-family: Arial, sans-serif;
            font-size: 14px;

            box-shadow:
                0 2px 8px
                rgba(0,0,0,0.25);

            min-width: 220px;
        ">

            <b>Código Linear</b>

            <hr>

            Corpo: {corpo}<br>

            Dimensão: {dimensao}<br>

            k: {k}<br>

            <br>

            <b>Vetores geradores:</b><br>

            {geradores_html}

        </div>
        """

        # ==================================================
        # INSERE O PAINEL NO HTML
        # ==================================================

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            html = f.read()

        html = html.replace(
            "</body>",
            painel + "</body>"
        )

        with open(
            arquivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        print(
            f"Grafo gerado em: {arquivo}"
        )
