import argparse
import csv
import itertools
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crime import Crime
from insertion import insertion_sort
import main
from merge import merge_sort
from metricas import Metricas
from quick import quick_sort
from selection import selection_sort


ALGORITMOS = (merge_sort, quick_sort, insertion_sort, selection_sort)


class OrdenacaoTests(unittest.TestCase):
    def test_listas_pequenas_com_repetidos_e_negativos(self):
        for tamanho in range(6):
            for valores in itertools.product((-1, 0, 1), repeat=tamanho):
                for ordenar in ALGORITMOS:
                    with self.subTest(algoritmo=ordenar.__name__, valores=valores):
                        dados = list(valores)
                        metricas = ordenar(dados)
                        self.assertEqual(dados, sorted(valores))
                        self.assertIsInstance(metricas, Metricas)

    def test_registros_crime_e_preservacao_dos_objetos(self):
        crimes = [
            Crime(chave, "", "", "", 0, str(indice))
            for indice, chave in enumerate([3, 1, 3, 0, 1])
        ]
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                dados = crimes.copy()
                ordenar(dados)
                self.assertEqual([crime.dr_no for crime in dados], [0, 1, 1, 3, 3])
                self.assertCountEqual(
                    [id(crime) for crime in dados],
                    [id(crime) for crime in crimes],
                )

    def test_insertion_preserva_ordem_de_chaves_iguais(self):
        dados = [
            Crime(chave, "", "", "", 0, str(indice))
            for indice, chave in enumerate([2, 1, 2, 1])
        ]
        esperado = sorted(dados)
        insertion_sort(dados)
        self.assertEqual(
            [id(crime) for crime in dados],
            [id(crime) for crime in esperado],
        )

    def test_contadores_conhecidos(self):
        casos = [
            ([], (0, 0), (0, 0)),
            ([7], (0, 0), (0, 0)),
            ([1, 2, 3], (2, 2), (3, 0)),
            ([3, 2, 1], (3, 5), (3, 2)),
            ([3, 1, 2], (3, 4), (3, 4)),
            ([2, 2, 2], (2, 2), (3, 0)),
        ]
        for dados, insertion_esperado, selection_esperado in casos:
            for ordenar, esperado in [
                (insertion_sort, insertion_esperado),
                (selection_sort, selection_esperado),
            ]:
                with self.subTest(algoritmo=ordenar.__name__, dados=dados):
                    metricas = ordenar(dados.copy())
                    self.assertEqual(
                        (metricas.comparacoes, metricas.movimentacoes), esperado
                    )

    def test_quick_sort_usa_pivo_medio_e_nao_recursao(self):
        dados = list(range(2_000, 0, -1))
        metricas = quick_sort(dados)
        self.assertEqual(dados, list(range(1, 2_001)))
        self.assertGreater(metricas.comparacoes, 0)
        self.assertGreater(metricas.movimentacoes, 0)

    def test_metricas_nao_acumulam_entre_chamadas(self):
        for ordenar in ALGORITMOS:
            primeira = ordenar([3, 2, 1])
            segunda = ordenar([])
            self.assertIsNot(primeira, segunda)
            self.assertEqual(segunda, Metricas())


class BenchmarkTests(unittest.TestCase):
    def test_parse_tamanhos(self):
        self.assertEqual(main.parse_tamanhos("100000,10000,10000"),
                         [10000, 100000])
        with self.assertRaises(argparse.ArgumentTypeError):
            main.parse_tamanhos("0,100")

    def test_cenarios_sao_deterministicos_e_nao_alteram_entrada(self):
        crimes = [Crime(indice, "", "", "", 0, "") for indice in range(7)]
        primeira = main.preparar_cenarios(crimes, 5, 42)
        segunda = main.preparar_cenarios(crimes, 5, 42)

        self.assertEqual([crime.dr_no for crime in crimes], list(range(7)))
        self.assertEqual(
            [[crime.dr_no for crime in dados] for _, dados in primeira],
            [[crime.dr_no for crime in dados] for _, dados in segunda],
        )
        self.assertTrue(main.esta_ordenada(primeira[1][1]))
        self.assertTrue(main.esta_ordenada(list(reversed(primeira[2][1]))))

    def test_benchmark_valida_e_registra_media(self):
        algoritmo = main.Algoritmo("Insertion Sort", insertion_sort, True)
        linha = main.executar_benchmark(
            algoritmo, "Reverso", [4, 3, 2, 1], repeticoes=3
        )
        self.assertEqual(linha[:4], ["Insertion Sort", "Reverso", 4, 3])
        self.assertEqual(linha[6:9], [6, 9, "medido"])
        self.assertGreaterEqual(linha[4], 0)
        self.assertGreaterEqual(linha[5], 0)

    def test_quadratico_acima_do_limite_e_registrado_como_nao_executado(self):
        crimes = [Crime(indice, "", "", "", 0, "") for indice in range(4)]
        algoritmo = main.Algoritmo("Selection Sort", selection_sort, True)
        linhas = main.executar_tamanho(
            crimes, 4, 42, 1, [algoritmo], max_n_quadratico=3
        )
        self.assertEqual(len(linhas), 3)
        self.assertTrue(all(linha[8] == "nao_executado" for linha in linhas))

    def test_cli_le_csv_e_escreve_metricas_estruturadas(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "crimes.csv"
            with entrada.open("w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(["DR_NO"])
                escritor.writerows((indice,) for indice in range(1003, 0, -1))

            saida = Path(pasta) / "metricas.csv"
            resultado = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(ROOT / "src/main.py"),
                    "--csv",
                    str(entrada),
                    "--tamanhos",
                    "3,5",
                    "--repeticoes",
                    "1",
                    "--saida",
                    str(saida),
                ],
                cwd=pasta,
                capture_output=True,
                text=True,
                check=True,
                timeout=20,
            )
            self.assertIn("Métricas salvas", resultado.stdout)
            with saida.open(newline="", encoding="utf-8") as arquivo:
                linhas = list(csv.DictReader(arquivo))
            self.assertEqual(len(linhas), 24)
            self.assertEqual({int(linha["tamanho"]) for linha in linhas}, {3, 5})
            self.assertEqual({linha["status"] for linha in linhas}, {"medido"})
            self.assertEqual({linha["repeticoes"] for linha in linhas}, {"1"})
            for linha in linhas:
                self.assertGreaterEqual(float(linha["tempo_medio_segundos"]), 0)

    def test_cli_rejeita_opcoes_invalidas(self):
        resultado = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "src/main.py"),
                "--limite",
                "-1",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("--limite deve ser um inteiro positivo", resultado.stderr)


if __name__ == "__main__":
    unittest.main()
