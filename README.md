# Sort-Python

Experimento reproduzível para comparar quatro algoritmos de ordenação usando
registros do dataset público **Crime Data from 2020 to Present**, do Los Angeles
Police Department (LAPD). A chave de ordenação é o campo numérico `DR_NO`
(*Division of Records Number*).

Cada algoritmo ordena a lista recebida **no próprio lugar** e devolve um objeto
`Metricas` com as comparações e movimentações realizadas.

## Algoritmos

| Algoritmo | Melhor caso | Caso médio | Pior caso |
| --- | --- | --- | --- |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) |
| Quick Sort | O(n log n) | O(n log n) | O(n²) |
| Insertion Sort | O(n) | O(n²) | O(n²) |
| Selection Sort | O(n²) | O(n²) | O(n²) |

- **Merge Sort:** divide a entrada, ordena as partes e as intercala.
- **Quick Sort:** escolhe o pivô pela mediana de três (primeiro, meio e último),
  particiona em regiões menor/igual/maior e usa uma pilha explícita. O menor
  subproblema é processado primeiro, limitando a pilha auxiliar a O(log n).
- **Insertion Sort:** desloca os elementos maiores e insere a chave na posição
  correta; é estável.
- **Selection Sort:** seleciona o menor elemento restante e o troca para a
  posição atual; não é estável.

## Dataset

O repositório inclui `data/crime_data_reduzido.csv`, com 10 mil registros,
para testes rápidos. O CSV completo tem cerca de um milhão de linhas e não é
versionado.

Para baixar o arquivo completo da fonte oficial:

```bash
python3 scripts/baixar_dataset.py --saida data/crime_data.csv
```

Também é possível baixar manualmente o CSV no
[portal de dados de Los Angeles](https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD)
e salvá-lo como `data/crime_data.csv`.

## Dependências

O benchmark e os testes usam apenas a biblioteca padrão do Python. Para gerar
gráficos, instale:

```bash
python3 -m pip install --user pandas matplotlib
```

## Executar o benchmark

Teste rápido usando a amostra incluída:

```bash
python3 src/main.py \
  --csv data/crime_data_reduzido.csv \
  --tamanhos 1000,10000 \
  --repeticoes 5 \
  --max-n-quadratico 10000 \
  --saida data/metricas_teste.csv
```

Execução completa planejada para o relatório:

```bash
python3 src/main.py \
  --csv data/crime_data.csv \
  --tamanhos 10000,100000,1000000 \
  --repeticoes 5 \
  --max-n-quadratico 10000 \
  --saida data/metricas.csv
```

Para compatibilidade com o comando anterior, `--limite N` executa apenas um
tamanho. Para o relatório, prefira `--tamanhos`.

O programa:

- escolhe uma amostra reproduzível com semente 42;
- gera os cenários aleatório, ordenado e reverso a partir da mesma amostra;
- cronometra somente a ordenação, nunca a preparação do cenário;
- repete cada combinação e registra média e desvio-padrão;
- verifica se cada saída ficou ordenada;
- registra Insertion e Selection como `nao_executado` acima de
  `--max-n-quadratico`, em vez de transformar uma execução inviável em um
  resultado.

O CSV de saída inclui algoritmo, cenário, tamanho, repetições, média, desvio
padrão, comparações, movimentações e status.

## Gráficos

Depois de gerar o CSV de métricas:

```bash
python3 scripts/gerar_graficos.py
```

São criados em `graficos/` três arquivos PNG: tempo médio com barras de
desvio-padrão, comparações e movimentações. O script usa somente linhas com
status `medido`.

Para gerar a figura usada no artigo, em escala logarítmica e separada por
cenário, execute:

```bash
python3 scripts/gerar_grafico_tempo.py
```

## Artigo e apresentação

O artigo final está em `artigo/`. O repositório mantém tanto o PDF quanto as
fontes LaTeX e a figura usada no texto, para permitir conferência e recompilação.

Para recompilar o artigo:

```bash
cd artigo
pdflatex main.tex
pdflatex main.tex
```

O PDF final da apresentação deve ser salvo em `slides/apresentacao.pdf` antes
da entrega. Arquivos auxiliares gerados pelo LaTeX não são versionados.

## Convenção das métricas

- **Comparações:** apenas comparações entre chaves; testes de índice e de laço
  não entram na contagem.
- **Movimentações:** escritas em posições de listas. No Insertion, contam-se os
  deslocamentos e a escrita final; no Selection e no Quick, uma troca entre
  posições distintas vale duas escritas; no Merge, contam-se as escritas no
  buffer e a cópia de volta ao vetor.

## Testes

```bash
python3 -B -m unittest discover -s tests -v
```

Os testes cobrem ordenação de inteiros e registros, valores repetidos, métricas
conhecidas, estabilidade do Insertion, Quick iterativo, reprodutibilidade dos
cenários e o formato do CSV de resultados.

## Estrutura

```text
.
├── data/       amostra reduzida e saídas locais do benchmark
├── artigo/     fontes LaTeX, figura e PDF do artigo
├── slides/     PDF final da apresentação
├── scripts/    download e geração de gráficos
├── src/        implementações e programa de benchmark
└── tests/      testes automatizados
```

Os resultados devem sempre ser gerados novamente após alterações nos
algoritmos ou no ambiente de execução.
