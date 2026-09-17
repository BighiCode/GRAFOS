from algebra.CorpoFinito import CorpoFinito
from algebra.EspacoVetorial import EspacoVetorial
from algebra.Vetor import Vetor
from codigo.CodigoLinear import CodigoLinear
from grafo.Grafo import Grafo
from visualizacao.Visualizador import Visualizador


# ============================================================
# 1. Corpo finito 
# ============================================================

F2 = CorpoFinito(2)

print("Corpo finito:")
print("GF(3)")
print("Elementos:", F2.elementos)


# ============================================================
# 2. Espaço vetorial 
# ============================================================

V = EspacoVetorial(F2, 8)

print("\nEspaço vetorial:")
print("GF(2)^8")
print("Dimensão:", V.dimensao)
print("Quantidade de vetores:", len(V.elementos()))


# ============================================================
# 3. Geradores do código linear
# ============================================================

g1 = Vetor((1, 0, 1, 0, 1, 0, 1, 0), F2)
g2 = Vetor((0, 1, 0, 1, 0, 1, 0, 1), F2)


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
# 5. Teste da distância de um vetor ao código
# ============================================================

v = Vetor((1, 1, 1, 1, 1, 1, 1, 1), F2)

print("\nVetor:", v)
print("Distância ao código:", C.distancia_ao_codigo(v))
print("Distância <= 1:", C.esta_a_distancia(v, 1))


# ============================================================
# 6. Construção do grafo
# ============================================================

G = Grafo(V.elementos())

G.construir_por_distancia_hamming(1)

print("\nGrafo:")
print("Quantidade de vértices:", G.quantidade_vertices())
print("Quantidade de arestas:", G.quantidade_arestas())


# ============================================================
# 7. Classes de distância ao código
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
# 8. Visualização
# ============================================================

d = C.distancia_minima()
k = C.capacidade_correcao()


print("\nParâmetros do código:")
print("Distância mínima:", d)
print("Capacidade de correção:", k)

visualizador = Visualizador(G)

visualizador.visualizar_por_distancia(
    C,
    k=k,
    arquivo="grafo.html"
)