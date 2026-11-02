"""
Módulo para geração e formatação de dados de consumo anual de água para gráficos.
Adaptado para a metodologia WEGnology / Jupyter Notebook.

Pode ser executado diretamente em uma célula do Jupyter Notebook,
por um script de automação, ou em lote dentro de um container WEGnology.
"""

from datetime import datetime
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Garante que o diretório atual esteja no path para importar wegnology_adapter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto


NOME_ARQUIVO_ENTRADA = "conta_povoada.json"
NOME_ARQUIVO_SAIDA = "grafico_anual.json"


def processar_dados_grafico(
    dados: Optional[List[Dict[str, Any]]] = None,
    ano_referencia: Optional[int] = None,
    salvar: bool = True,
    nome_arquivo_saida: str = NOME_ARQUIVO_SAIDA,
) -> Dict[str, Any]:
    """
    Processa os registros de consumo mensal de água e formata o resultado
    no schema esperado pelo front-end / WEGnology Experience Dashboard.
    Captura telemetria de pulsos em tempo de execução para atualizar o mês vigente.
    """
    # 1. Carregar contexto WEGnology se disponível
    contexto = carregar_contexto()

    # 2. Carregar dados de entrada se não fornecidos
    if dados is None:
        try:
            dados = carregar_json(NOME_ARQUIVO_ENTRADA)
        except FileNotFoundError:
            # Fallback para conta.json se conta_povoada.json não existir
            dados = carregar_json("conta.json", padrao=[])

    if not dados:
        dados = []

    # 3. Extração segura dos pulsos sem erro de int.get()
    pulsos_brutos = None
    if isinstance(contexto, dict):
        if "Pulsos" in contexto:
            pulsos_brutos = contexto["Pulsos"]
        elif "pulsos" in contexto:
            pulsos_brutos = contexto["pulsos"]
        elif isinstance(contexto.get("data"), dict):
            p_data = contexto["data"].get("Pulsos") or contexto["data"].get("pulsos")
            if isinstance(p_data, dict):
                pulsos_brutos = p_data.get("value")
            else:
                pulsos_brutos = p_data

        if isinstance(pulsos_brutos, dict):
            pulsos_brutos = pulsos_brutos.get("value")

    consumo_telemetria = None
    if pulsos_brutos is not None:
        try:
            consumo_telemetria = round(float(pulsos_brutos) / 1000.0, 2)
        except (ValueError, TypeError):
            consumo_telemetria = None
    elif isinstance(contexto, dict):
        consumo_direto = contexto.get("consumo_dia") or contexto.get("novo_consumo_dia") or contexto.get("consumo_hoje")
        if consumo_direto is not None:
            try:
                consumo_telemetria = round(float(consumo_direto), 2)
            except (ValueError, TypeError):
                consumo_telemetria = None

    hoje = datetime.now()
    mes_atual_id = f"{hoje.year}-{hoje.month:02d}"

    # 4. Atualiza ou insere o consumo do mês atual
    if consumo_telemetria is not None:
        encontrado = False
        for reg in dados:
            if str(reg.get("id")) == mes_atual_id:
                reg["consumo_m3"] = consumo_telemetria
                encontrado = True
                break
        if not encontrado:
            dados.append({
                "id": mes_atual_id,
                "consumo_m3": consumo_telemetria,
                "unidade_consumidora": 14079
            })

    # 5. Determinar o ano de referência
    if ano_referencia is None:
        if isinstance(contexto, dict) and "ano_referencia" in contexto and contexto["ano_referencia"] is not None:
            ano_referencia = int(contexto["ano_referencia"])
        elif dados:
            anos_encontrados = []
            for r in dados:
                partes = str(r.get("id", "")).split("-")
                if len(partes) == 2 and partes[0].isdigit():
                    anos_encontrados.append(int(partes[0]))
            ano_referencia = max(anos_encontrados) if anos_encontrados else hoje.year
        else:
            ano_referencia = hoje.year

    # 6. Processar consumo mensal
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

    meses_tags = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]

    resultado = {
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

    # 7. Salvar resultado no OUTPUT_DIR do WEGnology
    if salvar:
        salvar_json(nome_arquivo_saida, resultado)

    return resultado


# Aliás para compatibilidade reversa com o nome da função antiga
gerar_dados_grafico = processar_dados_grafico
modulo_grafico_anual = processar_dados_grafico


if __name__ == "__main__":
    print("--- Executando geração de dados para gráfico anual ---")
    dados_grafico = processar_dados_grafico()
    print(f"Ano de Referência: {dados_grafico['ano_referencia']}")
    print(f"Mês Atual Identificado: {dados_grafico['mes_atual']}")
    meses_com_consumo = [m for m in dados_grafico["meses"] if m["consumo_m3"] is not None]
    print(f"Total de meses com dados registrados: {len(meses_com_consumo)}")
