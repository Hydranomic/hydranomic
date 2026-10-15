"""
Orquestrador de execução para a plataforma WEGnology / Jupyter.
Permite despachar fluxos analíticos individuais (ML, Gráficos, Metas)
ou executar o pipeline consolidado para alimentação de Dashboards.

Lê parâmetros injetados pelo WEGnology via context.json ou variáveis de ambiente.
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Garante que o diretório atual esteja no path para importar os módulos
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_contexto, salvar_json
from machinelearning import executar_pipeline_ml
from data_chart import processar_dados_grafico
from metas import carregar_config, avaliar_progresso_meta


def executar(estado: Any = None) -> Dict[str, Any]:
    """
    Executa a ação correspondente ao estado informado ou obtido do contexto WEGnology.

    Estados suportados:
        1 ou "ml": Executa o modelo de previsão de Machine Learning (previsao_ml.json).
        2 ou "grafico": Processa a série anual de consumo para gráficos (grafico_anual.json).
        3 ou "metas": Avalia a situação da meta de consumo (progresso_meta.json).
        0 ou "tudo" ou None: Executa todo o pipeline consolidado de analytics do Hydranomic.
    """
    contexto = carregar_contexto()

    if estado is None:
        estado = contexto.get("estado", contexto.get("acao", "tudo"))

    resultados = {
        "estado_executado": estado,
        "detalhes": {}
    }

    match estado:
        case 1 | "1" | "ml":
            print("[WEGnology App] Executando Estado 1: Previsão Machine Learning...")
            resultado_ml = executar_pipeline_ml()
            resultados["detalhes"]["ml"] = resultado_ml
            print(f"Previsão gerada: {resultado_ml['previsao_m3']} m³ (R$ {resultado_ml['valor_estimado_conta']})")

        case 2 | "2" | "grafico":
            print("[WEGnology App] Executando Estado 2: Gráfico Anual...")
            resultado_grafico = processar_dados_grafico()
            resultados["detalhes"]["grafico"] = resultado_grafico
            print(f"Gráfico anual gerado para o ano {resultado_grafico['ano_referencia']}.")

        case 3 | "3" | "metas":
            print("[WEGnology App] Executando Estado 3: Avaliação de Metas...")
            # Pega o último consumo registrado no gráfico ou contexto para avaliar a meta
            consumo_atual = contexto.get("consumo_atual")
            if consumo_atual is None:
                grafico = processar_dados_grafico(salvar=False)
                meses_validos = [m["consumo_m3"] for m in grafico["meses"] if m["consumo_m3"] is not None]
                consumo_atual = meses_validos[-1] if meses_validos else 0.0

            resultado_meta = avaliar_progresso_meta(float(consumo_atual))
            resultados["detalhes"]["metas"] = resultado_meta
            print(f"Avaliação de meta concluída: {resultado_meta}")

        case _:
            print("[WEGnology App] Executando Pipeline Completo (ML + Gráfico + Metas)...")
            
            # 1. Gráfico anual
            res_grafico = processar_dados_grafico()
            resultados["detalhes"]["grafico"] = res_grafico
            
            # 2. Machine Learning
            res_ml = executar_pipeline_ml()
            resultados["detalhes"]["ml"] = res_ml
            
            # 3. Metas
            meses_validos = [m["consumo_m3"] for m in res_grafico["meses"] if m["consumo_m3"] is not None]
            consumo_mais_recente = meses_validos[-1] if meses_validos else 0.0
            res_meta = avaliar_progresso_meta(float(consumo_mais_recente))
            resultados["detalhes"]["metas"] = res_meta

            # Salva sumário geral da execução no OUTPUT_DIR
            sumario_execucao = {
                "status": "sucesso",
                "previsao_proximo_mes_m3": res_ml.get("previsao_m3"),
                "fatura_estimada_reais": res_ml.get("valor_estimado_conta"),
                "ano_grafico": res_grafico.get("ano_referencia"),
                "meta_status": res_meta.get("situacao") if res_meta else "sem_meta_ativa"
            }
            salvar_json("sumario_execucao.json", sumario_execucao)
            print("[WEGnology App] Pipeline completo finalizado com sucesso!")

    return resultados


if __name__ == "__main__":
    executar()
