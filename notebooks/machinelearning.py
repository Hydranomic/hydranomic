import json # Biblioteca utilizada para leitura de arquivos JSON.
import pandas as pd # Transforma o JSON bruto em tabelas organizadas.
from sklearn.ensemble import RandomForestRegressor # Modelo de ML Regressivo, utilizado para as previsões.

# É definido a tarifa atual do M3 da água.
tarifa_atual = 59.6

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


# Define as variáveis de ENTRADA (X) E SAÍDA (Y).
entrada = ["mes", "tempo_iniciofinal", "memoria_consumo"]
saida = "consumo_m3"

x = dataframe_treino["entrada"]
y = dataframe_treino["saida"]


# Treina o modelo regressivo de FLOREST.
modelo = RandomForestRegressor(n_estimators=250, random_state=45)
modelo.fit( x, y )

# Recuperação de Dados para aprimorar a próxima detecção de ciclo.
ultima_linha = dataframe.iloc[-1]

ultimo_ano = ultima_linha["ano"]
ultimo_mes = ultima_linha["mes"]
ultimo_consumo = ultima_linha["consumo_m3"]
ultimo_passo = ultima_linha["tempo_iniciofinal"]

# Definição da lógica de transição entre anos, a partir dos meses.

if ultimo_mes == 12:    
    proximo_mes = 1
    proximo_ano = ultimo_ano + 1

else:
    proximo_mes = ultimo_mes + 1
    proximo_ano = ultimo_ano

proximo_passo = ultimo_passo + 1

# O modelo recebe os dados já pré organizados para realizar o treinamento do modelo.
previsao_m3 = modelo.predict([[proximo_mes, proximo_passo, ultimo_consumo]])[0]

# Conta básica para calcular o provável valor mensal da tarifa
valor_conta = previsao_m3 * tarifa_atual

# Teste para exibição do resultado final no terminal
print(f"Previsão para o período: {proximo_ano}-{proximo_mes:02d}")
print(f"Unidade Consumidora: {ultima_linha['unidade_consumidora']}")
print(f"Consumo previsto: {previsao_m3:.2f} m³")
print(f"Tarifa aplicada: R$ {tarifa_atual:.2f} / m³")
print(f"Valor total estimado: R$ {valor_conta:,.2f}")








