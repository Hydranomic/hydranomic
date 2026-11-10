from datetime import datetime
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_contexto, carregar_json, salvar_json
from machinelearning import executar_pipeline_ml
from data_chart import processar_dados_grafico
from metas import avaliar_progresso_meta

def calcular_vazao_telemetria(contexto: Dict[str, Any], salvar: bool = True) -> Tuple[float, Dict[str, Any]]:
    """
    Calcula a vazão instantânea em m³/h com base na diferença de pulsos e tempo.
    Atualiza consumo_mes.json com a última leitura e a vazão calculada.
    """
    try:
        consumo_mes = carregar_json("consumo_mes.json")
    except Exception:
        hoje = datetime.now()
        consumo_mes = {
            "mes_referencia": f"{hoje.year}-{hoje.month:02d}",
            "unidade_consumidora": 14079,
            "consumo_acumulado_mes_m3": 0.0,
            "dias": []
        }

    agora = datetime.now()
    time_str = contexto.get("time") or contexto.get("timestamp")
    timestamp_atual = agora
    if time_str and isinstance(time_str, str):
        try:
            timestamp_atual = datetime.fromisoformat(time_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            timestamp_atual = agora

    pulsos_brutos = None
    if isinstance(contexto.get("data"), dict):
        pulsos_brutos = contexto["data"].get("Pulsos") or contexto["data"].get("pulsos")
    if pulsos_brutos is None:
        pulsos_brutos = contexto.get("Pulsos") or contexto.get("pulsos")

    try:
        pulsos_atuais = float(pulsos_brutos) if pulsos_brutos is not None else None
    except (ValueError, TypeError):
        pulsos_atuais = None

    ultima_leitura = consumo_mes.get("ultima_leitura", {}) if isinstance(consumo_mes, dict) else {}
    pulsos_anteriores = ultima_leitura.get("pulsos")
    time_anterior_str = ultima_leitura.get("timestamp")

    timestamp_anterior = None
    if time_anterior_str and isinstance(time_anterior_str, str):
        try:
            timestamp_anterior = datetime.fromisoformat(time_anterior_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            timestamp_anterior = None

    vazao_m3h = 0.0
    if timestamp_anterior is not None:
        delta_segundos = (timestamp_atual - timestamp_anterior).total_seconds()
        if pulsos_atuais is not None and pulsos_anteriores is not None and pulsos_atuais > pulsos_anteriores:
            delta_volume_m3 = (pulsos_atuais - pulsos_anteriores) * 0.001
        else:
            delta_volume_m3 = 0.1

        if 3 <= delta_segundos <= 7200:
            vazao_m3h = round((delta_volume_m3 * 3600.0) / delta_segundos, 2)
        else:
            vazao_m3h = 0.0
    else:
        vazao_m3h = float(consumo_mes.get("vazao_atual_m3h", 0.0) or 0.0)

    nova_leitura = {
        "pulsos": pulsos_atuais if pulsos_atuais is not None else pulsos_anteriores,
        "timestamp": timestamp_atual.isoformat(),
        "vazao_calculada_m3h": vazao_m3h
    }

    consumo_mes["vazao_atual_m3h"] = vazao_m3h
    consumo_mes["ultima_leitura"] = nova_leitura

    if salvar:
        salvar_json("consumo_mes.json", consumo_mes)

    return vazao_m3h, consumo_mes

def executar(estado: Any = None) -> Dict[str, Any]:
    contexto = carregar_contexto()
    vazao_m3h, consumo_mes = calcular_vazao_telemetria(contexto, salvar=True)

    if estado is None:
        estado = contexto.get("estado", contexto.get("acao", "tudo"))
    resultados = {
        "estado_executado": estado,
        "vazao_atual_m3h": vazao_m3h,
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
                "vazao_atual_m3h": vazao_m3h,
                "consumo_mes_acumulado_m3": consumo_mes.get("consumo_acumulado_mes_m3", consumo_mais_recente),
                "previsao_proximo_mes_m3": res_ml.get("previsao_m3"),
                "fatura_estimada_reais": res_ml.get("valor_estimado_conta"),
                "data_treinamento_ml": res_ml.get("data_treinamento"),
                "ano_grafico": res_grafico.get("ano_referencia"),
                "meta_status": res_meta.get("situacao") if res_meta else "sem_meta_ativa",
                "alertas_ativos": res_meta.get("alertas_ativos", []) if res_meta else [],
                "notificacoes": res_meta.get("notificacoes", {"notificacao_prazos": True, "alerta_status": True}) if res_meta else {"notificacao_prazos": True, "alerta_status": True}
            }
            salvar_json("sumario_execucao.json", sumario_execucao)
    return resultados

if __name__ == "__main__":
    executar()
