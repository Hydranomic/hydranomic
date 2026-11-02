"""
Orquestrador de execução para a plataforma WEGnology / Jupyter.
Permite despachar fluxos analíticos individuais (ML, Gráficos, Metas)
ou executar o pipeline consolidado para alimentação de Dashboards.

Lê parâmetros injetados pelo WEGnology via context.json ou variáveis de ambiente.
"""

from datetime import datetime
import sys
from pathlib import Path
from typing import Any, Dict

# Garante que o diretório atual esteja no path para importar os módulos
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_contexto, salvar_json
from machinelearning import executar_pipeline_ml
from data_chart import processar_dados_grafico
from metas import carregar_config, avaliar_progresso_meta


def executar_controlador(estado: Any = None) -> Dict[str, Any]:
    """
    Executa a ação correspondente ao estado informado ou obtido do contexto WEGnology.

    Estados suportados:
        1 ou "ml": Executa o modelo de previsão de Machine Learning (previsao_ml.json).
        2 ou "grafico": Processa a série anual de consumo para gráficos (grafico_anual.json).
        3 ou "metas": Avalia a situação da meta de consumo (progresso_meta.json).
        0 ou "tudo" ou None: Executa todo o pipeline consolidado de analytics do Hydranomic.
    """
    contexto = carregar_contexto() if "carregar_contexto" in globals() else {}

    # Captura telemetria dos pulsos sem erro de int.get()
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

    consumo_telemetria = 0.0
    if pulsos_brutos is not None:
        try:
            consumo_telemetria = round(float(pulsos_brutos) / 1000.0, 2)
        except (ValueError, TypeError):
            consumo_telemetria = 0.0
    else:
        consumo_telemetria = float(contexto.get("consumo_dia") or contexto.get("consumo_mes") or 0.0)

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
            resultado_meta = avaliar_progresso_meta(consumo_atual_m3=consumo_telemetria, salvar=True)
            resultados["detalhes"]["metas"] = resultado_meta
            print(f"Avaliação de meta concluída: {resultado_meta}")

        case _:
            print("[WEGnology App] Executando Pipeline Completo (ML + Gráfico + Metas)...")
            
            # 1. Gráfico anual
            res_grafico = processar_dados_grafico()
            resultados["detalhes"]["grafico"] = res_grafico
            
            # 2. Machine Learning
            resultado_ml = executar_pipeline_ml()
            resultados["detalhes"]["ml"] = resultado_ml
            
            # 3. Avalia a meta com o valor real
            resultado_meta = avaliar_progresso_meta(consumo_atual_m3=consumo_telemetria, salvar=True)
            resultados["detalhes"]["metas"] = resultado_meta

            # Gera o sumário com o valor real
            sumario = {
                "status": "sucesso",
                "mes_atual": datetime.now().strftime("%Y-%m"),
                "consumo_mes_acumulado_m3": consumo_telemetria,
                "previsao_proximo_mes_m3": resultado_ml.get("previsao_m3") if "resultado_ml" in locals() else 0.0,
                "fatura_estimada_reais": resultado_ml.get("valor_estimado_conta") if "resultado_ml" in locals() else 0.0,
                "data_treinamento_ml": datetime.now().isoformat(),
                "ano_grafico": datetime.now().year,
                "meta_status": resultado_meta.get("situacao") if ("resultado_meta" in locals() and resultado_meta) else "NORMAL"
            }
            salvar_json("sumario_execucao.json", sumario)
            print("[WEGnology App] Pipeline completo finalizado com sucesso!")

    return resultados


executar = executar_controlador


if __name__ == "__main__":
    executar_controlador()
