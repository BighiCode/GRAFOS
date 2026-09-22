from algebra.CorpoFinito import CorpoFinito
from algebra.EspacoVetorial import EspacoVetorial
from algebra.Vetor import Vetor
from codigo.CodigoLinear import CodigoLinear
from grafo.Grafo import Grafo
from visualizacao.Visualizador import Visualizador
from visualizacao.VisualizadorVisPy import VisualizadorVisPy

# ============================================================
# CONFIGURAÇÃO
# ============================================================

CORPO = 2
DIMENSAO = 7
GERADORES = [
    (1, 0, 1, 0,1,0,1), (0, 1, 0, 1,0,1,0), (0,0,1,1,1,0,0),(1,1,0,0,0,1,1),(1,1,0,1,1,1,0)

]


# ============================================================
# CORPO FINITO
# ============================================================

F = CorpoFinito(CORPO)

print("========================================")
print("CORPO FINITO")
print("========================================")

print("Corpo:", F)
print("Elementos:", F.elementos)


# ============================================================
# ESPAÇO VETORIAL
# ============================================================

V = EspacoVetorial(F, DIMENSAO)

print("\n========================================")
print("ESPAÇO VETORIAL")
print("========================================")

print("Espaço:", f"GF({CORPO})^{DIMENSAO}")
print("Dimensão:", V.dimensao)
print("Quantidade de vetores:", len(V.elementos()))


# ============================================================
# CONVERSÃO DOS GERADORES PARA Vetor
# ============================================================

geradores = []

for componentes in GERADORES:

    if len(componentes) != DIMENSAO:
        raise ValueError(
            f"O vetor {componentes} possui "
            f"{len(componentes)} componentes, mas "
            f"a dimensão é {DIMENSAO}."
        )

    geradores.append(
        Vetor(componentes, F)
    )


# ============================================================
# CÓDIGO LINEAR
# ============================================================

C = CodigoLinear(V, geradores)

print("\n========================================")
print("CÓDIGO LINEAR")
print("========================================")

print("Geradores:")

for gerador in geradores:
    print(" ", gerador)

print("\nPalavras do código:")

for palavra in C.elementos():
    print(" ", palavra)


# ============================================================
# PARÂMETROS DO CÓDIGO
# ============================================================

d = C.distancia_minima()
k = C.capacidade_correcao()

print("\n========================================")
print("PARÂMETROS")
print("========================================")

print("Dimensão do código:", C.dimensao())
print("Quantidade de palavras:", len(C.elementos()))
print("Comprimento:", DIMENSAO)
print("Distância mínima:", d)
print("Capacidade de correção:", k)


# ============================================================
# NOME DO ARQUIVO HTML
# ============================================================

geradores_nome = "__".join(
    "".join(str(x) for x in gerador)
    for gerador in GERADORES
)

ARQUIVO = (
    f"GF{CORPO}_n{DIMENSAO}_"
    f"k{k}_"
    f"G{geradores_nome}.html"
)


# ============================================================
# GRAFO DE HAMMING
# ============================================================

G = Grafo(V.elementos())

G.construir_por_distancia_hamming(1)

print("\n========================================")
print("GRAFO")
print("========================================")

print("Quantidade de vértices:", G.quantidade_vertices())
print("Quantidade de arestas:", G.quantidade_arestas())


# ============================================================
# VISUALIZAÇÃO
# ============================================================

visualizador = Visualizador(G)

visualizador.visualizar_por_distancia(
    C,
    k=k,
    arquivo=ARQUIVO
)

print("\nVisualização criada em:", ARQUIVO)

"""
visualizadorVisPy = VisualizadorVisPy(G)

visualizadorVisPy.visualizar_por_distancia(
    C,
    k=k,
    titulo=f"GF({CORPO})^{DIMENSAO}"
)
"""