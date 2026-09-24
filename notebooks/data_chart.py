# É utilizado para recuperar o ano atual proveniente do servidor.
from datetime import datetime
import json

# Guarda o ano atual, para garantir a seleção necessária dos dados.
verificar_data = datetime.now()
ano_atual = verificar_data.year

# Define os arquivos de entrada / saída.
arquivo_entrada = "hydranomic/workflows/conta_povoada.json"
arquivo_saida = "hydranomic/workflows/grafico_anual.json"

# Abre e Armazena os dados dos JSON's.
with open(arquivo_entrada, "r", encoding="utf-8") as dados:
    data = json.load(dados)

with open(arquivo_saida, "r", encoding="utf-8") as dados:
    data_novo = json.load(dados)