from datetime import datetime
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto

NOME_ARQUIVO_ENTRADA = "conta_povoada.json"
NOME_ARQUIVO_SAIDA = "grafico_anual.json"

def processar_dados_grafico(dados: Optional[List[Dict[str, Any]]] = None, ano_referencia: Optional[int] = None, salvar: bool = True, nome_arquivo_saida: str = NOME_ARQUIVO_SAIDA) -> Dict[str, Any]:
    contexto = carregar_contexto()
    if dados is None:
        try:
            dados = carregar_json(NOME_ARQUIVO_ENTRADA)
        except Exception:
            dados = carregar_json("conta.json", padrao=[])
    if ano_referencia is None:
        if "ano_referencia" in contexto:
            ano_referencia = int(contexto["ano_referencia"])
        elif dados:
            anos_encontrados = []
            for r in dados:
                partes = str(r.get("id", "")).split("-")
                if len(partes) == 2 and partes[0].isdigit():
                    anos_encontrados.append(int(partes[0]))
            ano_referencia = max(anos_encontrados) if anos_encontrados else datetime.now().year
        else:
            ano_referencia = datetime.now().year
    consumo_mensal: Dict[int, Optional[float]] = {}
    mes_atual: Optional[int] = None
    for registro in dados:
        registro_id = str(registro.get("id", ""))
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
    meses_tags = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    resultado = {
        "ano_referencia": ano_referencia,
        "mes_atual": mes_atual,
        "unidade_medida": "m³",
        "meses": [
            {
                "mes": mes,
                "rotulo": meses_tags[mes - 1],
                "consumo_m3": consumo_mensal.get(mes)
            }
            for mes in range(1, 13)
        ]
    }
    if salvar:
        salvar_json(nome_arquivo_saida, resultado)
    return resultado

gerar_dados_grafico = processar_dados_grafico

if __name__ == "__main__":
    processar_dados_grafico()
