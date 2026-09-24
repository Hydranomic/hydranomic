import json # Biblioteca utilizada para leitura de arquivos JSON.

with open("hydranomic/workflows/conta.json", "r", encoding="utf-8") as info_contas:
    dados = json.load(info_contas) # Função utilizada para leitura do arquivo JSON e armazenamento na váriavel.

