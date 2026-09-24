import json # Biblioteca utilizada para leitura de arquivos JSON.
import pandas as pd # Transforma o JSON bruto em tabelas organizadas.
from sklearn.ensemble import RandomForestRegressor # Modelo de ML Regressivo, utilizado para as previsões.

with open("hydranomic/workflows/conta_povoada.json", "r", encoding="utf-8") as info_contas:
    dados = json.load(info_contas) # Função utilizada para leitura do arquivo JSON e armazenamento na váriavel.

# Converte o JSON bruto no DataFrame do Pandas.
dataframe = pd.DataFrame(dados)

# Ordenar cronologicamente e formatar de acordo com a DATA e UNIDADE_CONSUMIDORA.
dataframe = dataframe.sort_values(by=["unidade_consumidora", "id"]).reset_index(drop=True)

# De acordo com as limitações matemáticas do modelo, é necessário extrair as datas para evitar o ValueError.
# Fluxo - Separa o Mês, procura na parte ID, procura o espaço -, pega o item do vetor 1, tranforma o str em INT.
dataframe["mes"] = dataframe["id"].str.split("-").str[1].astype(int)
dataframe["ano"] = dataframe["id"].str.split("-").str[0].astype(int)
# A extração do ano segue a mesma lógica, apenas mudando o vetor.

# Salva o ano mais antigo da base de dados.
ano_inicial = dataframe["ano"].min()
mes_inicial = dataframe.loc[dataframe["ano"] == ano_inicial, "mes"].min()
# Salva o mes mais antigo, dentro do range do ano mais antigo.

# Calcula quantos meses se passaram desde o período inicial.
# É necessário para configuração da lógica do modelo.
dataframe["tempo_iniciofinal"] = (dataframe["ano"] - ano_inicial) * 12 + (dataframe["mes"] - mes_inicial)

# Guarda em memória consumo do mês anterior agrupado por unidade consumidora.
# Serve para o modelo ter base de comparação.
dataframe["memoria_consumo"] = dataframe.groupby("unidade_consumidora")["consumo_m3"].shift(1)

# Serve para remove as linhas inicias que não tem conteúdo, evitando erros que possam interromper o serviço.
dataframe_treino = dataframe.dropna(subset=["memoria_consumo"]).copy()



# Define as variáveis de ENTRADA (X) E SAÍDA (Y)
entrada = ["mes", "tempo_iniciofinal", "memoria_consumo"]
saida = "consumo_m3"

x = dataframe_treino["entrada"]
y = dataframe_treino["saida"]








