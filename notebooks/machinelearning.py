import json # Biblioteca utilizada para leitura de arquivos JSON.
import pandas as pd # Transforma o JSON bruto em tabelas organizadas.
from sklearn.ensemble import RandomForestRegressor # Modelo de ML Regressivo, utilizado para as previsões.

with open("hydranomic/workflows/conta.json", "r", encoding="utf-8") as info_contas:
    dados = json.load(info_contas) # Função utilizada para leitura do arquivo JSON e armazenamento na váriavel.

# Converte o JSON bruto no DataFrame do Pandas.
dataframe = pd.DataFrame(dados)

# Ordenar cronologicamente e formatar de acordo com a DATA e UNIDADE_CONSUMIDORA.
dataframe = dataframe.sort_values(by=["unidade_consumidora", "id"]).reset_index(drop=True)

# De acordo com as limitações matemáticas do modelo, é necessário extrair as datas para evitar o ValueError.
# Fluxo - Separa o Mês, procura na parte ID, procura o espaço -, pega o item do vetor 1, tranforma o str em INT.
dataframe["mes"] = dataframe["id"].str.split("-").str[1].astype(int)

print(dataframe)