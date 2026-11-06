import time 
import csv 
import os 
from crime import carregar_crimes 
from merge import merge_sort 

def salvar_metricas(lista_resultados, caminho_out="data/metricas.csv"):
     os.makedirs(os.path.dirname(caminho_out), exist_ok=True) 
     with open(caminho_out, mode="w", newline="", encoding="utf-8") as f: 
        writer = csv.writer(f) 
        writer.writerow(["algoritmo", "cenario", "tamanho", "tempo_segundos", "comparacoes", "movimentacoes"]) 
        for r in lista_resultados: 
            writer.writerow(r) 
        print(f"\nMétricas salvas com sucesso em: {caminho_out}") 
        
def executar_benchmark(nome_algoritmo, cenario, funcao_sort, dados): 
    copia_dados = dados.copy() 
    inicio = time.perf_counter()
    metricas = funcao_sort(copia_dados) 
    fim = time.perf_counter() 
    duracao = fim - inicio 
    print(f"[{nome_algoritmo} | {cenario}] Tempo: {duracao:.4f}s | Comp: {metricas.comparacoes} | Mov: {metricas.movimentacoes}") 
    return [nome_algoritmo, cenario, len(dados), duracao, metricas.comparacoes, metricas.movimentacoes] 

def main(): 
    caminho_csv = "data/crime_data.csv" 
    print(f"Carregando dataset de crimes: {caminho_csv}...") 
    
    try: 
        crimes = carregar_crimes(caminho_csv) 
        print(f"Total de registros de crimes carregados: {len(crimes)}") 
        resultados = [] 
        
        # 1. Dados Aleatórios 
        print("\n=== TESTE: DADOS ALEATÓRIOS ===") 
        resultados.append(executar_benchmark("Merge Sort", "Aleatório", merge_sort, crimes)) 
        
        # 2. Dados Ordenados 
        print("\n=== TESTE: DADOS ORDENADOS ===") 
        crimes_ordenados = sorted(crimes) 
        resultados.append(executar_benchmark("Merge Sort", "Ordenado", merge_sort, crimes_ordenados)) 
        
        # 3. Dados Reversos 
        print("\n=== TESTE: DADOS REVERSOS ===") 
        crimes_reversos = crimes_ordenados[::-1] 
        resultados.append(executar_benchmark("Merge Sort", "Reverso", merge_sort, crimes_reversos)) 
        salvar_metricas(resultados) 
    except Exception as e: 
        print(f"Erro durante a execução: {e}") 
if __name__ == "__main__": 
    main()