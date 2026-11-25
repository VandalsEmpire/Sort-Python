import argparse
import csv
import os
import random
import time

from crime import carregar_crimes
from insertion import insertion_sort
from merge import merge_sort
from selection import selection_sort
from quick import quick_sort


def salvar_metricas(lista_resultados, caminho_out="data/metricas.csv"):
    os.makedirs(os.path.dirname(caminho_out) or ".", exist_ok=True)
    with open(caminho_out, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "algoritmo", "cenario", "tamanho", "tempo_segundos",
            "comparacoes", "movimentacoes",
        ])
        writer.writerows(lista_resultados)
    print(f"\nMétricas salvas com sucesso em: {caminho_out}")


def executar_benchmark(nome_algoritmo, cenario, funcao_sort, dados):
    copia_dados = dados.copy()
    inicio = time.perf_counter()
    metricas = funcao_sort(copia_dados)
    fim = time.perf_counter()
    duracao = fim - inicio
    # Verifica se a lista realmente ficou ordenada.
    
    if any(
    copia_dados[i] > copia_dados[i + 1]
    for i in range(len(copia_dados) - 1)
    ):
        raise ValueError(f"Erro: {nome_algoritmo} gerou uma lista desordenada")

    print(
        f"[{nome_algoritmo} | {cenario}] Tempo: {duracao:.4f}s | "
        f"Comp: {metricas.comparacoes} | Mov: {metricas.movimentacoes}"
    )
    return [
        nome_algoritmo, cenario, len(dados), duracao,
        metricas.comparacoes, metricas.movimentacoes,
    ]


def main():
    parser = argparse.ArgumentParser(description="Compara algoritmos de ordenação.")
    parser.add_argument("--csv", default="data/crime_data.csv", help="Dataset de entrada.")
    parser.add_argument("--saida", default="data/metricas.csv", help="CSV de métricas.")
    parser.add_argument(
        "--limite", type=int, default=1000,
        help="Máximo de registros por teste (padrão: 1000; 0 usa todos).",
    )
    args = parser.parse_args()
    if args.limite < 0:
        parser.error("--limite deve ser maior ou igual a zero.")

    print(f"Carregando dataset de crimes: {args.csv}...")
    try:
        crimes = carregar_crimes(args.csv)
        print(f"Total de registros de crimes carregados: {len(crimes)}")

        # A mesma amostra e a mesma ordem são usadas por todos os algoritmos.
        tamanho = min(args.limite, len(crimes)) if args.limite else len(crimes)
        amostra = random.Random(42).sample(crimes, tamanho)
        print(f"Registros por teste: {len(amostra)} (semente aleatória: 42)")
        crimes_ordenados = sorted(amostra)
        cenarios = [
            ("Aleatório", amostra),
            ("Ordenado", crimes_ordenados),
            ("Reverso", crimes_ordenados[::-1]),
        ]
        algoritmos = [
            ("Merge Sort", merge_sort),
            ("Insertion Sort", insertion_sort),
            ("Selection Sort", selection_sort),
            ("Quick Sort", quick_sort),
        ]

        resultados = []
        for cenario, dados in cenarios:
            print(f"\n=== TESTE: DADOS {cenario.upper()} ===")
            for nome, funcao_sort in algoritmos:
                resultados.append(executar_benchmark(nome, cenario, funcao_sort, dados))
        salvar_metricas(resultados, args.saida)
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
