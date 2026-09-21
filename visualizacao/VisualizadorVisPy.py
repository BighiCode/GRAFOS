from vispy import app, scene
from vispy.scene import visuals
import numpy as np
import math


class VisualizadorVisPy:

    def __init__(self, grafo):

        self.grafo = grafo

        # ========================================================
        # VISPY
        # ========================================================

        self.canvas = None
        self.view = None

        self.vertices_visual = None
        self.arestas_visual = None
        self.textos_visual = []

        # ========================================================
        # DADOS DO GRAFO
        # ========================================================

        self.vertices = []
        self.posicoes = {}
        self.velocidades = {}

        self.palavras_codigo = []
        self.classes = {}

        # ========================================================
        # FÍSICA
        # ========================================================

        self.timer = None

        self.fisica_ativa = True
        self.estabilizada = False

        self.iteracoes = 0
        self.max_iteracoes = 2000

        self.gravitational_constant = -150
        self.central_gravity = 0.01
        self.spring_length = 100
        self.spring_constant = 0.04
        self.damping = 0.80

        self.min_velocity = 0.75
        self.avoid_overlap = 1.0

        # ========================================================
        # ARRASTAR VÉRTICES
        # ========================================================

        self.vertice_arrastado = None
        self.mouse_arrastando = False

        # ========================================================
        # CONFIGURAÇÃO VISUAL
        # ========================================================

        self.raio_codigo = 1000

        self.tamanho_codigo = 22
        self.tamanho_normal = 8

    # ============================================================
    # CORES
    # ============================================================

    def _cores_codigo(self):

        return [
            (1.00, 0.00, 0.00, 1.0),   # #FF0000
            (0.00, 0.00, 1.00, 1.0),   # #0000FF
            (0.00, 0.667, 0.00, 1.0),  # #00AA00
            (1.00, 0.502, 0.00, 1.0),  # #FF8000
            (0.502, 0.00, 1.00, 1.0),  # #8000FF
            (0.00, 0.667, 0.667, 1.0), # #00AAAA
            (1.00, 0.00, 0.667, 1.0),  # #FF00AA
            (0.627, 0.376, 0.00, 1.0), # #A06000
            (0.00, 0.502, 0.502, 1.0), # #008080
            (0.502, 0.00, 0.502, 1.0)  # #800080
        ]

    # ============================================================
    # POSIÇÕES INICIAIS
    # ============================================================

    def _posicoes_codigo(self):

        posicoes = {}

        quantidade = len(self.palavras_codigo)

        if quantidade == 0:
            return posicoes

        if quantidade == 1:

            posicoes[
                self.palavras_codigo[0]
            ] = np.array(
                [0.0, 0.0],
                dtype=np.float32
            )

            return posicoes

        for i, palavra in enumerate(
            self.palavras_codigo
        ):

            angulo = (
                2 * math.pi * i / quantidade
            )

            x = (
                self.raio_codigo
                * math.cos(angulo)
            )

            y = (
                self.raio_codigo
                * math.sin(angulo)
            )

            posicoes[palavra] = np.array(
                [x, y],
                dtype=np.float32
            )

        return posicoes

    def _posicoes_outros_vertices(
        self,
        posicoes
    ):

        outros = [
            v
            for v in self.vertices
            if v not in posicoes
        ]

        quantidade = len(outros)

        if quantidade == 0:
            return

        # Distribuição inicial em uma região central.
        # A física depois reorganiza os vértices.

        raio = 300

        for i, vertice in enumerate(outros):

            angulo = (
                2 * math.pi * i / quantidade
            )

            x = (
                raio
                * math.cos(angulo)
            )

            y = (
                raio
                * math.sin(angulo)
            )

            posicoes[vertice] = np.array(
                [x, y],
                dtype=np.float32
            )

    def _inicializar_posicoes(self):

        self.posicoes = self._posicoes_codigo()

        self._posicoes_outros_vertices(
            self.posicoes
        )

        self.velocidades = {
            vertice: np.zeros(
                2,
                dtype=np.float32
            )
            for vertice in self.vertices
        }

    # ============================================================
    # CLASSES DE DISTÂNCIA
    # ============================================================

    def _calcular_classes(
        self,
        k
    ):

        self.classes = {}

        for vertice in self.vertices:

            proximas = []

            for i, palavra in enumerate(
                self.palavras_codigo
            ):

                distancia = (
                    vertice.distancia_hamming(
                        palavra
                    )
                )

                if distancia <= k:
                    proximas.append(i)

            self.classes[vertice] = proximas

    # ============================================================
    # COR DOS VÉRTICES
    # ============================================================

    def _cor_do_vertice(
        self,
        vertice
    ):

        cores = self._cores_codigo()

        if vertice in self.palavras_codigo:

            indice = (
                self.palavras_codigo.index(
                    vertice
                )
            )

            return cores[
                indice % len(cores)
            ]

        proximas = self.classes.get(
            vertice,
            []
        )

        if proximas:

            indice = proximas[0]

            return cores[
                indice % len(cores)
            ]

        # Mesmo cinza do Visualizador HTML atual.
        return (
            0.8,
            0.8,
            0.8,
            1.0
        )

    # ============================================================
    # VERIFICA SE UMA ARESTA PERTENCE A UMA BOLA
    # ============================================================

    def _cor_da_aresta(
        self,
        u,
        v,
        k
    ):

        cores = self._cores_codigo()

        for i, palavra in enumerate(
            self.palavras_codigo
        ):

            distancia_u = (
                u.distancia_hamming(
                    palavra
                )
            )

            distancia_v = (
                v.distancia_hamming(
                    palavra
                )
            )

            if (
                distancia_u <= k
                and distancia_v <= k
            ):

                return cores[
                    i % len(cores)
                ]

        return (
            0.667,
            0.667,
            0.667,
            1.0
        )

    # ============================================================
    # FÍSICA - REPULSÃO
    # ============================================================

    def _aplicar_repulsao(self):

        vertices = self.vertices

        for i in range(len(vertices)):

            u = vertices[i]

            for j in range(i + 1, len(vertices)):

                v = vertices[j]

                delta = (
                    self.posicoes[u]
                    - self.posicoes[v]
                )

                distancia = np.linalg.norm(
                    delta
                )

                if distancia < 0.01:

                    delta = np.random.uniform(
                        -1,
                        1,
                        2
                    ).astype(
                        np.float32
                    )

                    distancia = np.linalg.norm(
                        delta
                    )

                direcao = (
                    delta / distancia
                )

                # ForceAtlas2 utiliza uma força
                # aproximadamente proporcional a 1/d.

                forca = (
                    abs(self.gravitational_constant)
                    / distancia
                )

                # Evita que os vértices fiquem
                # excessivamente próximos.

                if distancia < 40:

                    forca += (
                        self.avoid_overlap
                        * (40 - distancia)
                    )

                self.velocidades[u] += (
                    direcao * forca
                )

                self.velocidades[v] -= (
                    direcao * forca
                )

    # ============================================================
    # FÍSICA - ARESTAS
    # ============================================================

    def _aplicar_molas(self):

        arestas_processadas = set()

        for u in self.vertices:

            for v in self.grafo.vizinhos(u):

                identificador = frozenset(
                    (u, v)
                )

                if identificador in arestas_processadas:
                    continue

                arestas_processadas.add(
                    identificador
                )

                delta = (
                    self.posicoes[v]
                    - self.posicoes[u]
                )

                distancia = np.linalg.norm(
                    delta
                )

                if distancia < 0.01:
                    continue

                direcao = (
                    delta / distancia
                )

                diferenca = (
                    distancia
                    - self.spring_length
                )

                forca = (
                    self.spring_constant
                    * diferenca
                )

                self.velocidades[u] += (
                    direcao * forca
                )

                self.velocidades[v] -= (
                    direcao * forca
                )

    # ============================================================
    # FÍSICA - GRAVIDADE CENTRAL
    # ============================================================

    def _aplicar_gravidade(self):

        for vertice in self.vertices:

            # Codewords ficam fixados.
            if vertice in self.palavras_codigo:
                continue

            posicao = self.posicoes[vertice]

            self.velocidades[vertice] -= (
                posicao
                * self.central_gravity
            )

    # ============================================================
    # ATUALIZAÇÃO DA FÍSICA
    # ============================================================

    def _atualizar_fisica(
        self,
        event=None
    ):

        if not self.fisica_ativa:
            return

        if self.estabilizada:
            return

        if self.iteracoes >= self.max_iteracoes:

            self.estabilizada = True

            return

        # --------------------------------------------------------
        # Zera forças
        # --------------------------------------------------------

        for vertice in self.vertices:

            self.velocidades[vertice][:] = 0

        # --------------------------------------------------------
        # Aplica forças
        # --------------------------------------------------------

        self._aplicar_repulsao()

        self._aplicar_molas()

        self._aplicar_gravidade()

        # --------------------------------------------------------
        # Atualiza posições
        # --------------------------------------------------------

        velocidade_maxima = 0.0

        for vertice in self.vertices:

            if vertice in self.palavras_codigo:
                continue

            velocidade = (
                self.velocidades[vertice]
                * self.damping
            )

            self.posicoes[vertice] += (
                velocidade * 0.02
            )

            modulo = np.linalg.norm(
                velocidade
            )

            velocidade_maxima = max(
                velocidade_maxima,
                modulo
            )

        self.iteracoes += 1

        # --------------------------------------------------------
        # Verifica estabilização
        # --------------------------------------------------------

        if velocidade_maxima < self.min_velocity:

            if self.iteracoes > 100:

                self.estabilizada = True

        self._atualizar_visual()

    # ============================================================
    # ATUALIZA VÉRTICES E ARESTAS NA TELA
    # ============================================================

    def _atualizar_visual(self):

        if self.vertices_visual is None:
            return

        posicoes = np.array(
            [
                self.posicoes[vertice]
                for vertice in self.vertices
            ],
            dtype=np.float32
        )

        self.vertices_visual.set_data(
            posicoes
        )

        # --------------------------------------------------------
        # Atualiza posições dos textos
        # --------------------------------------------------------

        for texto, vertice in self.textos_visual:

            texto.pos = (
                self.posicoes[vertice]
                + np.array([0, 20])
            )

        # --------------------------------------------------------
        # Atualiza arestas
        # --------------------------------------------------------

        if self.arestas_visual is not None:

            linhas = []

            for u in self.vertices:

                for v in self.grafo.vizinhos(u):

                    identificador = frozenset(
                        (u, v)
                    )

                    # A identificação é controlada
                    # pelo método auxiliar.

                    if hasattr(
                        self,
                        "_arestas_processadas_visual"
                    ):

                        if identificador in self._arestas_processadas_visual:
                            continue

                    else:

                        self._arestas_processadas_visual = set()

                    self._arestas_processadas_visual.add(
                        identificador
                    )

                    linhas.append(
                        self.posicoes[u]
                    )

                    linhas.append(
                        self.posicoes[v]
                    )

            self._arestas_processadas_visual = set()

            if linhas:

                self.arestas_visual.set_data(
                    np.array(
                        linhas,
                        dtype=np.float32
                    )
                )

        self.canvas.update()

    # ============================================================
    # DESENHA ARESTAS
    # ============================================================

    def _criar_arestas(
        self,
        k
    ):

        # --------------------------------------------------------
        # Arestas normais
        # --------------------------------------------------------

        linhas_normais = []

        # --------------------------------------------------------
        # Arestas coloridas por código
        # --------------------------------------------------------

        linhas_coloridas = [
            []
            for _ in self.palavras_codigo
        ]

        processadas = set()

        for u in self.vertices:

            for v in self.grafo.vizinhos(u):

                identificador = frozenset(
                    (u, v)
                )

                if identificador in processadas:
                    continue

                processadas.add(
                    identificador
                )

                cor = self._cor_da_aresta(
                    u,
                    v,
                    k
                )

                # ------------------------------------------------
                # Verifica se é uma aresta de alguma bola.
                # ------------------------------------------------

                indice_cor = None

                for i, palavra in enumerate(
                    self.palavras_codigo
                ):

                    distancia_u = (
                        u.distancia_hamming(
                            palavra
                        )
                    )

                    distancia_v = (
                        v.distancia_hamming(
                            palavra
                        )
                    )

                    if (
                        distancia_u <= k
                        and distancia_v <= k
                    ):

                        indice_cor = i
                        break

                if indice_cor is None:

                    linhas_normais.append(
                        self.posicoes[u]
                    )

                    linhas_normais.append(
                        self.posicoes[v]
                    )

                else:

                    linhas_coloridas[
                        indice_cor
                    ].append(
                        self.posicoes[u]
                    )

                    linhas_coloridas[
                        indice_cor
                    ].append(
                        self.posicoes[v]
                    )

        # --------------------------------------------------------
        # Arestas normais
        # --------------------------------------------------------

        if linhas_normais:

            self.arestas_visual = visuals.Line(
                pos=np.array(
                    linhas_normais,
                    dtype=np.float32
                ),
                color=(
                    0.667,
                    0.667,
                    0.667,
                    1.0
                ),
                width=1
            )

            self.view.add(
                self.arestas_visual
            )

        # --------------------------------------------------------
        # Arestas coloridas
        # --------------------------------------------------------

        cores = self._cores_codigo()

        for i, linhas in enumerate(
            linhas_coloridas
        ):

            if not linhas:
                continue

            visual = visuals.Line(
                pos=np.array(
                    linhas,
                    dtype=np.float32
                ),
                color=cores[
                    i % len(cores)
                ],
                width=3
            )

            self.view.add(
                visual
            )

    # ============================================================
    # DESENHA VÉRTICES
    # ============================================================

    def _criar_vertices(self):

        posicoes = np.array(
            [
                self.posicoes[v]
                for v in self.vertices
            ],
            dtype=np.float32
        )

        cores = np.array(
            [
                self._cor_do_vertice(v)
                for v in self.vertices
            ],
            dtype=np.float32
        )

        tamanhos = np.array(
            [
                self.tamanho_codigo
                if v in self.palavras_codigo
                else self.tamanho_normal
                for v in self.vertices
            ],
            dtype=np.float32
        )

        self.vertices_visual = visuals.Markers()

        self.vertices_visual.set_data(
            posicoes,
            face_color=cores,
            edge_color=(
                0.15,
                0.15,
                0.15,
                1.0
            ),
            edge_width=1,
            size=tamanhos
        )

        self.view.add(
            self.vertices_visual
        )

    # ============================================================
    # RÓTULOS DOS VÉRTICES
    # ============================================================

    def _criar_rotulos(self):

        for vertice in self.vertices:

            texto = visuals.Text(
                str(vertice),
                color="black",
                font_size=10,
                anchor_x="center",
                anchor_y="bottom"
            )

            texto.pos = (
                self.posicoes[vertice]
                + np.array([0, 20])
            )

            self.view.add(
                texto
            )

            self.textos_visual.append(
                (texto, vertice)
            )

    # ============================================================
    # CONVERSÃO DO MOUSE PARA COORDENADAS DO GRAFO
    # ============================================================

    def _posicao_mouse(self, pos):

        try:

            transformacao = (
                self.view.scene_transform
            )

            resultado = transformacao.imap(
                pos
            )

            return np.array(
                resultado[:2],
                dtype=float
            )

        except Exception:

            try:

                transformacao = (
                    self.view.scene.transform
                )

                resultado = transformacao.imap(
                    pos
                )

                return np.array(
                    resultado[:2],
                    dtype=float
                )

            except Exception:

                return np.array(
                    pos[:2],
                    dtype=float
                )

    # ============================================================
    # ENCONTRA VÉRTICE PRÓXIMO DO MOUSE
    # ============================================================

    def _encontrar_vertice(
        self,
        pos_mouse
    ):

        vertice_encontrado = None

        menor_distancia = float("inf")

        # Tolerância de seleção.
        tolerancia = 30

        for vertice in self.vertices:

            distancia = np.linalg.norm(
                self.posicoes[vertice]
                - pos_mouse
            )

            if (
                distancia < tolerancia
                and distancia < menor_distancia
            ):

                menor_distancia = distancia

                vertice_encontrado = vertice

        return vertice_encontrado

    # ============================================================
    # MOUSE PRESSIONADO
    # ============================================================

    def _mouse_press(self, event):

        if event.button != 1:
            return

        pos = self._posicao_mouse(
            event.pos
        )

        vertice = self._encontrar_vertice(
            pos
        )

        if vertice is None:
            return

        # Codewords permanecem fixados,
        # como no visualizador HTML.

        if vertice in self.palavras_codigo:
            return

        self.vertice_arrastado = vertice
        self.mouse_arrastando = True

        self.fisica_ativa = False

    # ============================================================
    # MOUSE MOVENDO
    # ============================================================

    def _mouse_move(self, event):

        if not self.mouse_arrastando:
            return

        if self.vertice_arrastado is None:
            return

        pos = self._posicao_mouse(
            event.pos
        )

        self.posicoes[
            self.vertice_arrastado
        ] = pos.astype(
            np.float32
        )

        self._atualizar_visual()

    # ============================================================
    # MOUSE SOLTO
    # ============================================================

    def _mouse_release(self, event):

        if event.button != 1:
            return

        self.vertice_arrastado = None
        self.mouse_arrastando = False

    # ============================================================
    # TECLADO
    # ============================================================

    def _teclado(self, event):

        # Espaço ativa/desativa física.

        if event.key == "Space":

            self.fisica_ativa = (
                not self.fisica_ativa
            )

            if self.fisica_ativa:
                self.estabilizada = False

        # R reinicia a física.

        elif event.key == "R":

            self._inicializar_posicoes()

            self.estabilizada = False
            self.iteracoes = 0

            self._atualizar_visual()

    # ============================================================
    # VISUALIZAÇÃO
    # ============================================================

    def visualizar(
        self,
        codigo=None,
        k=1,
        titulo="Grafo"
    ):

        # --------------------------------------------------------
        # Dados
        # --------------------------------------------------------

        self.vertices = list(
            self.grafo.vertices
        )

        self.palavras_codigo = []

        if codigo is not None:

            self.palavras_codigo = list(
                codigo.elementos()
            )

        # --------------------------------------------------------
        # Classes de Hamming
        # --------------------------------------------------------

        self._calcular_classes(k)

        # --------------------------------------------------------
        # Posições
        # --------------------------------------------------------

        self._inicializar_posicoes()

        # --------------------------------------------------------
        # Canvas
        # --------------------------------------------------------

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            show=True,
            bgcolor="#ffffff",
            size=(1400, 900)
        )

        self.canvas.title = titulo

        self.view = (
            self.canvas.central_widget.add_view()
        )

        # --------------------------------------------------------
        # Câmera 2D
        # --------------------------------------------------------

        self.view.camera = "panzoom"

        # --------------------------------------------------------
        # Arestas
        # --------------------------------------------------------

        self._criar_arestas(k)

        # --------------------------------------------------------
        # Vértices
        # --------------------------------------------------------

        self._criar_vertices()

        # --------------------------------------------------------
        # Rótulos
        # --------------------------------------------------------

        self._criar_rotulos()

        # --------------------------------------------------------
        # Eventos
        # --------------------------------------------------------

        self.canvas.events.mouse_press.connect(
            self._mouse_press
        )

        self.canvas.events.mouse_move.connect(
            self._mouse_move
        )

        self.canvas.events.mouse_release.connect(
            self._mouse_release
        )

        self.canvas.events.key_press.connect(
            self._teclado
        )

        # --------------------------------------------------------
        # Câmera inicial
        # --------------------------------------------------------

        self.view.camera.set_range(
            margin=0.2
        )

        # --------------------------------------------------------
        # Física
        # --------------------------------------------------------

        self.timer = app.Timer(
            interval=1 / 60,
            connect=self._atualizar_fisica,
            start=True
        )

        # --------------------------------------------------------
        # Executa
        # --------------------------------------------------------

        app.run()

    # ============================================================
    # VISUALIZAÇÃO POR DISTÂNCIA
    # ============================================================

    def visualizar_por_distancia(
        self,
        codigo,
        k=1,
        titulo="Grafo de Hamming"
    ):

        self.visualizar(
            codigo=codigo,
            k=k,
            titulo=titulo
        )