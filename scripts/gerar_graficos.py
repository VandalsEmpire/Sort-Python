"""Gera gráficos a partir do CSV de métricas produzido por src/main.py."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


COLUNAS_NECESSARIAS = {
    "algoritmo",
    "cenario",
    "tamanho",
    "tempo_medio_segundos",
    "tempo_desvio_padrao_segundos",
    "comparacoes",
    "movimentacoes",
    "status",
}


def ler_metricas(caminho):
    dados = pd.read_csv(caminho)
    faltantes = COLUNAS_NECESSARIAS - set(dados.columns)
    if faltantes:
        raise ValueError(
            "CSV incompatível com o benchmark atual. Colunas ausentes: "
            + ", ".join(sorted(faltantes))
        )
    dados = dados[dados["status"] == "medido"].copy()
    if dados.empty:
        raise ValueError("Não há medições concluídas no CSV.")
    return dados


def grafico_linhas(dados, coluna, titulo, eixo_y, saida, erro=None):
    plt.figure(figsize=(10, 6))
    for (algoritmo, cenario), grupo in dados.groupby(["algoritmo", "cenario"]):
        grupo = grupo.sort_values("tamanho")
        argumentos = {
            "x": grupo["tamanho"],
            "y": grupo[coluna],
            "marker": "o",
            "linewidth": 1.8,
            "label": f"{algoritmo} — {cenario}",
        }
        if erro is not None:
            argumentos["yerr"] = grupo[erro]
            argumentos["capsize"] = 3
        plt.errorbar(**argumentos)

    tamanhos = sorted(dados["tamanho"].unique())
    plt.xscale("log")
    plt.xticks(tamanhos, [f"{tamanho:,}" for tamanho in tamanhos])
    plt.title(titulo)
    plt.xlabel("Tamanho da entrada (registros)")
    plt.ylabel(eixo_y)
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(saida, dpi=300)
    plt.close()


def main():
    raiz = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metricas", default=raiz / "data" / "metricas.csv",
                        type=Path, help="CSV produzido pelo benchmark.")
    parser.add_argument("--saida", default=raiz / "graficos", type=Path,
                        help="Pasta dos PNGs.")
    args = parser.parse_args()

    try:
        dados = ler_metricas(args.metricas)
    except (OSError, ValueError, pd.errors.ParserError) as erro:
        print(f"Erro: {erro}")
        return 1

    args.saida.mkdir(parents=True, exist_ok=True)
    grafico_linhas(
        dados,
        "tempo_medio_segundos",
        "Tempo médio de execução por tamanho e cenário",
        "Tempo médio (segundos)",
        args.saida / "desempenho_tempo.png",
        erro="tempo_desvio_padrao_segundos",
    )
    grafico_linhas(
        dados,
        "comparacoes",
        "Comparações por tamanho e cenário",
        "Comparações entre chaves",
        args.saida / "desempenho_comparacoes.png",
    )
    grafico_linhas(
        dados,
        "movimentacoes",
        "Movimentações por tamanho e cenário",
        "Escritas em listas",
        args.saida / "desempenho_movimentacoes.png",
    )
    print(f"Gráficos gerados em: {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
