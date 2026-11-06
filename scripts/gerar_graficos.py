import pandas as pd 
import matplotlib.pyplot as plt 
import os 

def gerar_graficos(): 
    caminho_csv = "data/metricas.csv" 
    if not os.path.exists(caminho_csv): 
        print(f"Erro: Arquivo '{caminho_csv}' não encontrado. Execute o main.py primeiro.") 
        return 
    df = pd.read_csv(caminho_csv) 
    os.makedirs("graficos", exist_ok=True) 
    plt.style.use("ggplot") 

    # 1\. Gráfico de Tempo de Execução por Cenário 
    plt.figure(figsize=(10, 6)) 
    for cenario in df['cenario'].unique(): 
        sub_df = df[df['cenario'] == cenario] 
        plt.bar([f"{alg}\n({cenario})" for alg in sub_df['algoritmo']], sub_df['tempo_segundos']) 
    plt.title("Tempo de Execução dos Algoritmos (Dataset de Crimes)") 
    plt.ylabel("Tempo (segundos)") 
    plt.xlabel("Algoritmo / Cenário") 
    plt.xticks(rotation=30, ha="right") 
    plt.tight_layout() 
    plt.savefig("graficos/desempenho_tempo.png", dpi=300) 
    plt.close() 

    # 2\. Gráfico de Comparações 
    plt.figure(figsize=(10, 6)) 
    for cenario in df['cenario'].unique(): 
        sub_df = df[df['cenario'] == cenario] 
        plt.bar([f"{alg}\n({cenario})" for alg in sub_df['algoritmo']], sub_df['comparacoes']) 
    plt.title("Número de Comparações (Dataset de Crimes)") 
    plt.ylabel("Quantidade de Comparações") 
    plt.xlabel("Algoritmo / Cenário") 
    plt.xticks(rotation=30, ha="right") 
    plt.tight_layout() 
    plt.savefig("graficos/desempenho_comparacoes.png", dpi=300) 
    plt.close() 

    print("Gráficos gerados com sucesso na pasta 'graficos/'!") 

if __name__ == "__main__": 
    gerar_graficos()