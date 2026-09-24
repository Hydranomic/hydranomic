import json # Biblioteca utilizada para leitura de arquivos JSON.
import pandas as pd # Transforma o JSON bruto em tabelas organizadas.
from sklearn.ensemble import RandomForestRegressor # Modelo de ML Regressivo, utilizado para as previsões.

with open("hydranomic/workflows/conta.json", "r", encoding="utf-8") as info_contas:
    dados = json.load(info_contas) # Função utilizada para leitura do arquivo JSON e armazenamento na váriavel.

