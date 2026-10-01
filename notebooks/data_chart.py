############################################

# CÓDIGO FINALIZADO 1.0 - 01/10/2026 #
# FALTANDO INTEGRAÇÃO WEGNOLOGY E FRONT-END #

############################################

from datetime import datetime
import json

arquivo_entrada = "hydranomic/workflows/conta_povoada.json"
arquivo_saida = "hydranomic/workflows/grafico_anual.json"

def gerar_dados_grafico(data, ano_referencia=None):
    
    if ano_referencia is None:
        ano_referencia = datetime.now().year

    consumo_mensal = {}
    mes_atual = None

    for registro in data:
        registro_id = registro.get("id", "")
        separar_partes = registro_id.split("-")

        if len(separar_partes) != 2:
            continue

        try:
            ano_registro = int(separar_partes[0])
            mes_registro = int(separar_partes[1])
        except ValueError:
            continue

        if ano_registro == ano_referencia and 1 <= mes_registro <= 12:
            consumo_mensal[mes_registro] = registro.get("consumo_m3")
            mes_atual = mes_registro

    meses_tags = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]

    return {
        "ano_referencia": ano_referencia,
        "mes_atual": mes_atual,
        "unidade_medida": "m³",
        "meses": [
            {
                "mes": mes,
                "rotulo": meses_tags[mes - 1],
                "consumo_m3": consumo_mensal.get(mes),
            }
            for mes in range(1, 13)
        ],
    }
