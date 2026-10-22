import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_contexto, salvar_json
from machinelearning import executar_pipeline_ml
from data_chart import processar_dados_grafico
from metas import avaliar_progresso_meta

def executar(estado: Any = None) -> Dict[str, Any]:
    contexto = carregar_contexto()
    if estado is None:
        estado = contexto.get("estado", contexto.get("acao", "tudo"))
    resultados = {
        "estado_executado": estado,
        "detalhes": {}
    }
    match str(estado).lower().strip():
        case "1" | "ml":
            resultado_ml = executar_pipeline_ml()
            resultados["detalhes"]["ml"] = resultado_ml
        case "2" | "grafico":
            resultado_grafico = processar_dados_grafico()
            resultados["detalhes"]["grafico"] = resultado_grafico
        case "3" | "metas":
            consumo_atual = contexto.get("consumo_atual")
            if consumo_atual is None:
                grafico = processar_dados_grafico(salvar=False)
                meses_validos = [m["consumo_m3"] for m in grafico["meses"] if m["consumo_m3"] is not None]
                consumo_atual = meses_validos[-1] if meses_validos else 0.0
            resultado_meta = avaliar_progresso_meta(float(consumo_atual))
            resultados["detalhes"]["metas"] = resultado_meta
        case _:
            res_grafico = processar_dados_grafico()
            resultados["detalhes"]["grafico"] = res_grafico
            res_ml = executar_pipeline_ml()
            resultados["detalhes"]["ml"] = res_ml
            meses_validos = [m["consumo_m3"] for m in res_grafico["meses"] if m["consumo_m3"] is not None]
            consumo_mais_recente = meses_validos[-1] if meses_validos else 0.0
            res_meta = avaliar_progresso_meta(float(consumo_mais_recente))
            resultados["detalhes"]["metas"] = res_meta
            sumario_execucao = {
                "status": "sucesso",
                "previsao_proximo_mes_m3": res_ml.get("previsao_m3"),
                "fatura_estimada_reais": res_ml.get("valor_estimado_conta"),
                "data_treinamento_ml": res_ml.get("data_treinamento"),
                "ano_grafico": res_grafico.get("ano_referencia"),
                "meta_status": res_meta.get("situacao") if res_meta else "sem_meta_ativa"
            }
            salvar_json("sumario_execucao.json", sumario_execucao)
    return resultados

if __name__ == "__main__":
    executar()
