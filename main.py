from algebra.CorpoFinito import CorpoFinito
from algebra.EspacoVetorial import EspacoVetorial
from algebra.Vetor import Vetor
from codigo.CodigoLinear import CodigoLinear
from grafo.Grafo import Grafo
from visualizacao.Visualizador import Visualizador


# ============================================================
# 1. Corpo finito GF(2)
# ============================================================

F2 = CorpoFinito(2)

print("Corpo finito:")
print("GF(2)")
print("Elementos:", F2.elementos)


# ============================================================
# 2. Espaço vetorial GF(2)^4
# ============================================================

V = EspacoVetorial(F2, 6)

print("\nEspaço vetorial:")
print("GF(2)^4")
print("Dimensão:", V.dimensao)
print("Quantidade de vetores:", len(V.elementos()))


# ============================================================
# 3. Geradores do código linear
# ============================================================

g1 = Vetor((1, 0, 1, 0, 1, 0), F2)
g2 = Vetor((0, 1, 0, 1, 0, 1), F2)


# ============================================================
# 4. Código linear
# ============================================================

C = CodigoLinear(V, [g1, g2])

print("\nCódigo linear:")

for palavra in C.elementos():
    print(palavra)

print("\nDimensão:", C.dimensao())
print("Quantidade de palavras:", len(C.elementos()))


# ============================================================
# 5. Grafo
# ============================================================

G = Grafo(V.elementos())
G.construir_por_distancia_hamming(1)

print("\nGrafo:")
print("Quantidade de vértices:", G.quantidade_vertices())
print("Quantidade de arestas:", G.quantidade_arestas())


# ============================================================
# 6. Distâncias ao código
# ============================================================

rotulos = G.rotular_por_distancia(C)

classes = {}

for vertice, distancia in rotulos.items():
    if distancia not in classes:
        classes[distancia] = 0

    classes[distancia] += 1

print("\nClasses de distância:")

for distancia in sorted(classes):
    print(
        f"Distância {distancia}: "
        f"{classes[distancia]} vértices"
    )


# ============================================================
# 7. Visualização
# ============================================================

visualizador = Visualizador(G)
visualizador.visualizar_por_distancia(C)