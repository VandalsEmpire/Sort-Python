"""Quick Sort iterativo com mediana de três e partição em três vias."""

from metricas import Metricas


def _escolher_pivo(lista, inicio, fim, metricas):
    """Devolve a mediana entre o primeiro, o meio e o último elemento."""
    meio = inicio + (fim - inicio) // 2
    primeiro, central, ultimo = lista[inicio], lista[meio], lista[fim]

    metricas.comparacoes += 1
    if primeiro < central:
        metricas.comparacoes += 1
        if central < ultimo:
            return central
        metricas.comparacoes += 1
        return ultimo if primeiro < ultimo else primeiro

    metricas.comparacoes += 1
    if primeiro < ultimo:
        return primeiro
    metricas.comparacoes += 1
    return ultimo if central < ultimo else central


def _trocar(lista, primeiro, segundo, metricas):
    if primeiro != segundo:
        lista[primeiro], lista[segundo] = lista[segundo], lista[primeiro]
        metricas.movimentacoes += 2


def _particionar_tres_vias(lista, inicio, fim, pivo, metricas):
    """Particiona em ``< pivo``, ``== pivo`` e ``> pivo``.

    Devolve os limites inclusivos da região que contém elementos iguais ao pivô.
    Assim, valores repetidos não voltam à pilha de ordenação.
    """
    menor, atual, maior = inicio, inicio, fim
    while atual <= maior:
        metricas.comparacoes += 1
        if lista[atual] < pivo:
            _trocar(lista, menor, atual, metricas)
            menor += 1
            atual += 1
        else:
            metricas.comparacoes += 1
            if lista[atual] > pivo:
                _trocar(lista, atual, maior, metricas)
                maior -= 1
            else:
                atual += 1
    return menor, maior


def quick_sort(lista):
    """Ordena ``lista`` no próprio lugar e devolve as métricas da execução.

    A partição em três vias trata repetidos eficientemente. Em cada etapa, o
    menor subvetor é processado de imediato e o maior fica na pilha explícita,
    limitando o espaço auxiliar da pilha a O(log n).
    """
    metricas = Metricas()
    if len(lista) < 2:
        return metricas

    pilha = [(0, len(lista) - 1)]
    while pilha:
        inicio, fim = pilha.pop()
        while inicio < fim:
            pivo = _escolher_pivo(lista, inicio, fim, metricas)
            primeiro_igual, ultimo_igual = _particionar_tres_vias(
                lista, inicio, fim, pivo, metricas
            )

            tamanho_esquerda = primeiro_igual - inicio
            tamanho_direita = fim - ultimo_igual
            if tamanho_esquerda < tamanho_direita:
                if ultimo_igual + 1 < fim:
                    pilha.append((ultimo_igual + 1, fim))
                fim = primeiro_igual - 1
            else:
                if inicio < primeiro_igual - 1:
                    pilha.append((inicio, primeiro_igual - 1))
                inicio = ultimo_igual + 1

    return metricas
