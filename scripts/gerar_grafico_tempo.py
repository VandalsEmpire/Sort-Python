"""Gera uma figura de tempo legível para o artigo."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


RAIZ = Path(__file__).resolve().parents[1]
CORES = {
    "Merge Sort": "#1f77b4",
    "Quick Sort": "#d62728",
    "Insertion Sort": "#2ca02c",
    "Selection Sort": "#9467bd",
}
CENARIOS = ("Aleatório", "Ordenado", "Reverso")


def carregar():
    with (RAIZ / "data" / "metricas.csv").open(encoding="utf-8", newline="") as arquivo:
        return [
            linha
            for linha in csv.DictReader(arquivo)
            if linha["status"] == "medido"
        ]


def main():
    dados = carregar()
    grupos = defaultdict(list)
    for linha in dados:
        grupos[linha["cenario"]].append(linha)

    figura, eixos = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for eixo, cenario in zip(eixos, CENARIOS):
        por_algoritmo = defaultdict(list)
        for linha in grupos[cenario]:
            por_algoritmo[linha["algoritmo"]].append(linha)

        for algoritmo, linhas in por_algoritmo.items():
            linhas.sort(key=lambda linha: int(linha["tamanho"]))
            tamanhos = [int(linha["tamanho"]) for linha in linhas]
            tempos = [float(linha["tempo_medio_segundos"]) for linha in linhas]
            desvios = [
                float(linha["tempo_desvio_padrao_segundos"]) for linha in linhas
            ]
            eixo.errorbar(
                tamanhos,
                tempos,
                yerr=desvios,
                label=algoritmo,
                color=CORES[algoritmo],
                marker="o",
                linewidth=1.8,
                capsize=2,
            )

        eixo.set_xscale("log")
        eixo.set_yscale("log")
        eixo.set_xticks([10_000, 100_000, 1_000_000])
        eixo.set_xticklabels(["10 mil", "100 mil", "1 mi"])
        eixo.set_title(cenario)
        eixo.grid(True, which="both", linestyle=":", alpha=0.45)
        eixo.set_xlabel("Registros")

    eixos[0].set_ylabel("Tempo médio (s, escala logarítmica)")
    identificadores, rotulos = eixos[0].get_legend_handles_labels()
    figura.legend(
        identificadores,
        rotulos,
        loc="upper center",
        ncol=4,
        bbox_to_anchor=(0.5, 1.08),
    )
    figura.tight_layout()
    figura.savefig(RAIZ / "artigo" / "tempo_por_cenario.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
