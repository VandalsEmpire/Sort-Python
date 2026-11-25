from metricas import Metricas

def quick_sort(arr):
    metricas = Metricas()

    if len(arr) <= 1:
        return metricas

    def escolher_pivo(inicio, fim):
        meio = inicio + (fim - inicio) // 2

        a = arr[inicio]
        b = arr[meio]
        c = arr[fim]

        # acha a mediana entre primeiro meio e último
        metricas.comparacoes += 1
        if a < b:
            metricas.comparacoes += 1
            if b < c:
                return b
            
            metricas.comparacoes += 1
            return c if a < c else a
        
        metricas.comparacoes += 1
        if a < c:
            return a
        
        metricas.comparacoes += 1
        return c if b < c else b

    def trocar(i, j):
        if i != j:
            arr[i], arr[j] = arr[j], arr[i]
            metricas.movimentacoes += 2

    # cada elemento representa um intervalo a ordenar
    pilha = [(0, len(arr) - 1)]

    while pilha:
        inicio, fim = pilha.pop()

        if inicio >= fim:
            continue

        pivo = escolher_pivo(inicio, fim)
        # separa em três regiões menores que o pivô; iguais ao pivô e maiores que o pivô
        menor = inicio
        atual = inicio
        maior = fim

        while atual <= maior:
            metricas.comparacoes += 1

            if arr[atual] < pivo:
                trocar(menor, atual)
                menor += 1
                atual += 1

            else:
                metricas.comparacoes += 1

                if arr[atual] > pivo:
                    trocar(atual, maior)
                    maior -= 1
                else:
                    atual += 1

        # adiciona só os intervalos que precisam ser ordenados
        if inicio < menor - 1:
            pilha.append((inicio, menor - 1))

        if maior + 1 < fim:
            pilha.append((maior + 1, fim))

    return metricas
