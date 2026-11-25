"""Baixa o CSV histórico de crimes de Los Angeles usado no experimento."""

import argparse
from pathlib import Path
import shutil
import sys
from urllib.request import Request, urlopen


URL_PADRAO = (
    "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
)


def baixar(url, destino, sobrescrever=False):
    destino = Path(destino)
    if destino.exists() and not sobrescrever:
        raise FileExistsError(
            f"{destino} já existe. Use --sobrescrever para substituí-lo."
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(destino.suffix + ".part")
    temporario.unlink(missing_ok=True)
    requisicao = Request(url, headers={"User-Agent": "Sort-Python/1.0"})
    try:
        with urlopen(requisicao, timeout=120) as resposta, temporario.open("wb") as arquivo:
            shutil.copyfileobj(resposta, arquivo)
        temporario.replace(destino)
    except BaseException:
        temporario.unlink(missing_ok=True)
        raise
    return destino.stat().st_size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", default="data/crime_data.csv",
                        help="Caminho do CSV baixado.")
    parser.add_argument("--url", default=URL_PADRAO,
                        help="URL CSV do portal de dados.")
    parser.add_argument("--sobrescrever", action="store_true",
                        help="Permite substituir a saída existente.")
    args = parser.parse_args()

    try:
        tamanho = baixar(args.url, args.saida, args.sobrescrever)
    except (OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    print(f"Dataset salvo em {args.saida} ({tamanho / 1024**2:.2f} MiB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
