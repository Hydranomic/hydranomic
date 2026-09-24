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

# Armazena o consumo de cada mês
consumo_mensal = {}

# Lógica que garante que os dados armazenados serão do ano atual.
for registro in data:
    registro_id = registro.get("id", "")
    separar_partes = registro.split("-")

    if len(separar_partes) == 2:

        try:
            ano_registro = int(separar_partes[0])
            mes_registro = int(separar_partes[1])

            if ano_registro == ano_atual and 1 <= mes_registro <= 12:

                consumo_mensal[mes_registro] = registro.get("consumo_m3")

        except ValueError:
            continue


