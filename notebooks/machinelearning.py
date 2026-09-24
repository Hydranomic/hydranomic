import json

with open("hydranomic/workflows/conta.json", "r", encoding="utf-8") as info_contas:
    dados = json.load(info_contas)

print(dados)