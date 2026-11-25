"""Executa benchmarks reproduzíveis dos algoritmos de ordenação do projeto."""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import random
from statistics import fmean, stdev
import time

from crime import carregar_crimes
from insertion import insertion_sort
from merge import merge_sort
from quick import quick_sort
from selection import selection_sort

CABECALHO_METRICAS = [
    "algoritmo",
    "cenario",
    "tamanho",
    "repeticoes",
    "tempo_medio_segundos",
    "tempo_desvio_padrao_segundos",
    "comparacoes",
    "movimentacoes",
    "status",
    "observacao",
]


@dataclass(frozen=True)
class Algoritmo:
    nome: str
    funcao: object
    quadratico: bool = False


def parse_tamanhos(valor):
    """Converte "10000,100000,1000000" em uma lista ordenada de tamanhos."""
    try:
        tamanhos = sorted(
            {int(item.strip()) for item in valor.split(",") if item.strip()}
        )
    except ValueError as erro:
        raise argparse.ArgumentTypeError(
            "--tamanhos deve conter inteiros separados por vírgula."
        ) from erro

    if not tamanhos or any(tamanho <= 0 for tamanho in tamanhos):
        raise argparse.ArgumentTypeError(
            "--tamanhos deve conter pelo menos um inteiro positivo."
        )
    return tamanhos


def esta_ordenada(dados):
    """Verifica a saída sem usar uma ordenação da biblioteca."""
    return all(
        dados[indice] <= dados[indice + 1]
        for indice in range(len(dados) - 1)
    )


def algoritmos_disponiveis():
    return [
        Algoritmo("Merge Sort", merge_sort),
        Algoritmo("Quick Sort", quick_sort),
        Algoritmo("Insertion Sort", insertion_sort, quadratico=True),
        Algoritmo("Selection Sort", selection_sort, quadratico=True),
    ]


def preparar_cenarios(crimes, tamanho, semente):
    """Cria as três entradas equivalentes para um dado tamanho.

    A amostra é feita uma única vez com semente fixa. A ordem crescente é
    preparada pelo Merge Sort implementado no projeto e fica fora da medição.
    """
    gerador = random.Random(semente)
    aleatorio = gerador.sample(crimes, tamanho)
    ordenado = aleatorio.copy()
    merge_sort(ordenado)
    return [
        ("Aleatório", aleatorio),
        ("Ordenado", ordenado),
        ("Reverso", list(reversed(ordenado))),
    ]


def executar_benchmark(algoritmo, cenario, dados, repeticoes):
    """Mede somente a ordenação e devolve uma linha no formato do CSV."""
    tempos = []
    comparacoes = movimentacoes = None

    for repeticao in range(repeticoes):
        copia = dados.copy()
        inicio = time.perf_counter()
        metricas = algoritmo.funcao(copia)
        tempos.append(time.perf_counter() - inicio)

        if not esta_ordenada(copia):
            raise AssertionError(
                f"{algoritmo.nome} não ordenou a entrada "
                f"do cenário {cenario} na repetição {repeticao + 1}."
            )

        valores = (metricas.comparacoes, metricas.movimentacoes)
        if comparacoes is None:
            comparacoes, movimentacoes = valores
        elif valores != (comparacoes, movimentacoes):
            raise AssertionError(
                f"As métricas de {algoritmo.nome} variaram entre repetições; "
                "isso não é esperado para a mesma entrada."
            )

    media = fmean(tempos)
    desvio = stdev(tempos) if len(tempos) > 1 else 0.0
    print(
        f"[{algoritmo.nome} | {cenario} | n={len(dados):,}] "
        f"{media:.6f}s ± {desvio:.6f}s "
        f"({repeticoes} repetições) | Comp: {comparacoes} | Mov: {movimentacoes}"
    )
    return [
        algoritmo.nome,
        cenario,
        len(dados),
        repeticoes,
        media,
        desvio,
        comparacoes,
        movimentacoes,
        "medido",
        "",
    ]


def resultado_nao_executado(algoritmo, cenario, tamanho, repeticoes, motivo):
    print(
        f"[{algoritmo.nome} | {cenario} | n={tamanho:,}] "
        f"NÃO EXECUTADO: {motivo}"
    )
    return [
        algoritmo.nome,
        cenario,
        tamanho,
        repeticoes,
        "",
        "",
        "",
        "",
        "nao_executado",
        motivo,
    ]


def executar_tamanho(
    crimes, tamanho, semente, repeticoes, algoritmos, max_n_quadratico
):
    cenarios = preparar_cenarios(crimes, tamanho, semente)
    resultados = []
    print(f"\n=== TAMANHO n={tamanho:,} | semente={semente} ===")

    for cenario, dados in cenarios:
        print(f"\n--- CENÁRIO: {cenario.upper()} ---")
        for algoritmo in algoritmos:
            if algoritmo.quadratico and tamanho > max_n_quadratico:
                motivo = (
                    f"n > limite quadrático configurado ({max_n_quadratico:,}); "
                    "execução omitida por inviabilidade."
                )
                resultados.append(
                    resultado_nao_executado(
                        algoritmo, cenario, tamanho, repeticoes, motivo
                    )
                )
                continue
            resultados.append(
                executar_benchmark(algoritmo, cenario, dados, repeticoes)
            )
    return resultados


def salvar_metricas(linhas, caminho_saida):
    caminho = Path(caminho_saida)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(CABECALHO_METRICAS)
        escritor.writerows(linhas)
    print(f"\nMétricas salvas em: {caminho}")


def main():
    parser = argparse.ArgumentParser(
        description="Compara algoritmos de ordenação com entradas reproduzíveis."
    )
    parser.add_argument("--csv", default="data/crime_data.csv",
                        help="CSV de entrada.")
    parser.add_argument("--saida", default="data/metricas.csv",
                        help="CSV de métricas gerado.")
    parser.add_argument(
        "--tamanhos",
        type=parse_tamanhos,
        default=None,
        help="Tamanhos separados por vírgula; ex.: 10000,100000,1000000.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Compatibilidade: executa um único tamanho. Use --tamanhos para o relatório.",
    )
    parser.add_argument("--repeticoes", type=int, default=5,
                        help="Medições por algoritmo e cenário (padrão: 5).")
    parser.add_argument("--semente", type=int, default=42,
                        help="Semente da amostra aleatória (padrão: 42).")
    parser.add_argument(
        "--max-n-quadratico",
        type=int,
        default=10_000,
        help=(
            "Maior tamanho executado para Insertion e Selection "
            "(padrão: 10000). Os maiores são registrados como não executados."
        ),
    )
    args = parser.parse_args()

    if args.tamanhos is not None and args.limite is not None:
        parser.error("Use --tamanhos ou --limite, não os dois.")
    if args.limite is not None and args.limite <= 0:
        parser.error("--limite deve ser um inteiro positivo.")
    if args.repeticoes <= 0:
        parser.error("--repeticoes deve ser um inteiro positivo.")
    if args.max_n_quadratico < 0:
        parser.error("--max-n-quadratico deve ser maior ou igual a zero.")

    tamanhos = args.tamanhos or [args.limite or 1000]
    print(f"Carregando dataset de crimes: {args.csv}...")
    try:
        crimes = carregar_crimes(args.csv)
        print(f"Registros carregados: {len(crimes):,}")
        maior_tamanho = max(tamanhos)
        if maior_tamanho > len(crimes):
            raise ValueError(
                f"O CSV tem {len(crimes):,} registros, mas o benchmark pediu "
                f"{maior_tamanho:,}."
            )

        algoritmos = algoritmos_disponiveis()
        resultados = []
        for tamanho in tamanhos:
            resultados.extend(
                executar_tamanho(
                    crimes,
                    tamanho,
                    args.semente,
                    args.repeticoes,
                    algoritmos,
                    args.max_n_quadratico,
                )
            )
        salvar_metricas(resultados, args.saida)
    except (OSError, ValueError, AssertionError) as erro:
        print(f"Erro durante a execução: {erro}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
