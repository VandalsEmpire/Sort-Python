from dataclasses import dataclass 
@dataclass 
class Metricas: 
    comparacoes: int = 0 
    movimentacoes: int = 0 

def merge_sort(arr):
    metricas = Metricas()
    if len(arr) <= 1:
        return metricas
    temp = arr.copy()  # Copia segura sem invocar a função list()
    _merge_sort_rec(arr, temp, 0, len(arr), metricas)
    return metricas

def _merge_sort_rec(arr, temp, inicio, fim, metricas):
    if fim - inicio <= 1:
        return
    meio = inicio + (fim - inicio) // 2
    _merge_sort_rec(arr, temp, inicio, meio, metricas)
    _merge_sort_rec(arr, temp, meio, fim, metricas)
    _intercalar(arr, temp, inicio, meio, fim, metricas)

def _intercalar(arr, temp, inicio, meio, fim, metricas):
    i, j, k = inicio, meio, inicio
    while i < meio and j < fim:
        metricas.comparacoes += 1
        if arr[i] <= arr[j]:
            temp[k] = arr[i]
            i += 1
        else:
            temp[k] = arr[j]
            j += 1
        metricas.movimentacoes += 1
        k += 1
    while i < meio:
        temp[k] = arr[i]
        i += 1
        k += 1
        metricas.movimentacoes += 1
    while j < fim:
        temp[k] = arr[j]
        j += 1
        k += 1
        metricas.movimentacoes += 1
    for idx in range(inicio, fim):
        arr[idx] = temp[idx]
        metricas.movimentacoes += 1