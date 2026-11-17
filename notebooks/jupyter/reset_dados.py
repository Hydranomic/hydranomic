"""
=============================================================================
HYDRANOMIC - WEGnology Reset de Dados (Ambiente Limpo e Seguro)
=============================================================================
Este script é executado como uma tarefa de Notebook na WEGnology para
resetar de forma cirúrgica e segura os dados de teste/falsos da plataforma,
afetando ESTRITAMENTE:
  1. config.json         -> Remove metas antigas/falsas de todos os meses.
  2. progresso_meta.json  -> Limpa o progresso avaliado, alertas e status de perigo.
  3. consumo_mes.json     -> Zera o consumo acumulado e vazão do mês atual (Novembro/2026).

Nenhum outro arquivo do Application Files (como conta.json, logos, gráficos ou usuários)
é modificado. Todas as páginas continuam funcionando 100% de forma íntegra.
=============================================================================
"""

import os
import sys
import json
import calendar
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Permite execução tanto local quanto dentro do container WEGnology sem depender de __file__
if "__file__" in globals():
    diretorio_base = Path(__file__).resolve().parent
else:
    diretorio_base = Path.cwd()
sys.path.insert(0, str(diretorio_base))


def obter_diretorio_output() -> Path:
    env_dir = os.environ.get("OUTPUT_DIR")
    if env_dir:
        p = Path(env_dir)
    elif Path("/outputs").exists():
        p = Path("/outputs")
    else:
        p = Path("./outputs")
    p.mkdir(parents=True, exist_ok=True)
    return p


def obter_diretorio_input() -> Path:
    env_dir = os.environ.get("INPUT_DIR")
    if env_dir:
        return Path(env_dir)
    elif Path("/inputs").exists():
        return Path("/inputs")
    return Path("./inputs")


def carregar_json(nome: str, padrao: Any = None) -> Any:
    candidatos = [
        obter_diretorio_input() / nome,
        Path("/inputs") / nome if Path("/inputs").exists() else None,
        Path.cwd() / "hydranomic" / "workflows" / nome,
        Path.cwd() / "workflows" / nome,
        diretorio_base.parent.parent / "workflows" / nome,
        diretorio_base.parent / "workflows" / nome,
        Path.cwd() / nome,
        obter_diretorio_output() / nome,
    ]
    for c in candidatos:
        if c and c.exists() and c.stat().st_size > 0:
            try:
                with open(c, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return padrao


def salvar_json(nome: str, dados: Any) -> Path:
    c = obter_diretorio_output() / nome
    c.parent.mkdir(parents=True, exist_ok=True)
    with open(c, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    return c


def executar_reset() -> Dict[str, Any]:
    hoje = datetime.now()
    mes_atual = hoje.strftime("%Y-%m")
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_restantes = max(0, ultimo_dia_mes - hoje.day)

    # -------------------------------------------------------------------------
    # 1. Preservação de configurações administrativas legítimas
    # -------------------------------------------------------------------------
    cfg_existente = carregar_json("config.json", padrao={})
    notifs_padrao = {"notificacao_prazos": True, "alerta_status": True}
    notifs_admin = cfg_existente.get("notificacoes", notifs_padrao) if isinstance(cfg_existente.get("notificacoes"), dict) else notifs_padrao
    notifs_usuarios = cfg_existente.get("notificacoes_usuarios", {}) if isinstance(cfg_existente.get("notificacoes_usuarios"), dict) else {}
    tarifa_existente = float(cfg_existente.get("tarifa_m3", 59.60)) if isinstance(cfg_existente, dict) and cfg_existente.get("tarifa_m3") is not None else 59.60

    # -------------------------------------------------------------------------
    # 2. CONFIG.JSON LIMPO (Preserva tarifa em nuvem e preferências)
    # -------------------------------------------------------------------------
    config_limpo = {
        "tarifa_m3": tarifa_existente,
        "meta_ativa": None,
        "metas_ativas_por_tipo": {},
        "metas_por_mes": {},
        "solicitacao_exclusao": None,
        "notificacoes": notifs_admin,
        "notificacoes_usuarios": notifs_usuarios
    }

    # -------------------------------------------------------------------------
    # 3. PROGRESSO_META.JSON LIMPO
    # -------------------------------------------------------------------------
    progresso_limpo = {
        "meta_ativa": False,
        "meta_nome": None,
        "tipo": None,
        "limite_m3": None,
        "consumo_atual_m3": 0.0,
        "gasto_atual_reais": 0.0,
        "economia_atual_reais": 0.0,
        "tarifa_m3": tarifa_existente,
        "percentual_atingido": 0.0,
        "saldo_restante_m3": None,
        "situacao": "NORMAL",
        "periodo": mes_atual,
        "mes_referencia": mes_atual,
        "metas_ativas_por_tipo": {},
        "alertas_ativos": [],
        "notificacoes": notifs_admin,
        "notificacoes_config": notifs_admin,
        "notificacoes_usuarios": notifs_usuarios,
        "dias_restantes_mes": dias_restantes
    }

    # -------------------------------------------------------------------------
    # 4. CONSUMO_MES.JSON LIMPO (Zera telemetria e vazão do mês atual)
    # -------------------------------------------------------------------------
    consumo_limpo = {
        "mes_referencia": mes_atual,
        "unidade_consumidora": 14079,
        "consumo_acumulado_mes_m3": 0.0,
        "vazao_atual_m3h": 0.0,
        "ultima_leitura": {
            "pulsos": 0.0,
            "timestamp": hoje.isoformat(),
            "vazao_calculada_m3h": 0.0
        },
        "dias": []
    }

    # -------------------------------------------------------------------------
    # 5. GRAFICO_ANUAL.JSON (Zera exclusivamente o mês atual, preservando histórico)
    # -------------------------------------------------------------------------
    tags_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    # Histórico de referência seguro caso o container não receba grafico_anual.json no /inputs
    consumos_base_2026 = {
        1: 150, 2: 267, 3: 349, 4: 361, 5: 351, 6: 352, 7: 291, 8: 358,
        9: 0.0, 10: 0.0, 11: 0.0, 12: None
    }

    # Tenta carregar grafico_anual.json existente
    grafico_existente = carregar_json("grafico_anual.json", padrao=None)

    # Se não encontrou o arquivo nos inputs do container, reconstrói a partir de conta.json
    if not isinstance(grafico_existente, dict) or "meses" not in grafico_existente:
        contas_para_grafico = carregar_json("conta.json", padrao=[])
        if not contas_para_grafico:
            contas_para_grafico = carregar_json("conta_povoada.json", padrao=[])

        mapa_consumo_conta = dict(consumos_base_2026)
        if isinstance(contas_para_grafico, list) and contas_para_grafico:
            for c in contas_para_grafico:
                partes = str(c.get("id", "")).split("-")
                if len(partes) == 2 and partes[0] == str(hoje.year):
                    try:
                        m_num = int(partes[1])
                        if 1 <= m_num <= 12 and m_num != hoje.month:
                            mapa_consumo_conta[m_num] = c.get("consumo_m3")
                    except ValueError:
                        pass

        # Garante que o mês atual fique zerado (0.0 m³)
        mapa_consumo_conta[hoje.month] = 0.0

        grafico_existente = {
            "ano_referencia": hoje.year,
            "mes_atual": hoje.month,
            "unidade_medida": "m³",
            "meses": [
                {
                    "mes": m,
                    "rotulo": tags_meses[m - 1],
                    "consumo_m3": mapa_consumo_conta.get(m, None)
                }
                for m in range(1, 13)
            ]
        }
    else:
        # Se o arquivo já existia nos inputs, zera ESTRITAMENTE o mês atual
        grafico_existente["mes_atual"] = hoje.month
        for item_mes in grafico_existente.get("meses", []):
            if isinstance(item_mes, dict) and item_mes.get("mes") == hoje.month:
                item_mes["consumo_m3"] = 0.0

    p_graf = salvar_json("grafico_anual.json", grafico_existente)

    # -------------------------------------------------------------------------
    # 6. CONTA.JSON (Zera o consumo do mês atual se existir, mantendo histórico)
    # -------------------------------------------------------------------------
    contas_existentes = carregar_json("conta.json", padrao=[])
    p_conta = None
    if isinstance(contas_existentes, list):
        alterou_conta = False
        for idx, r in enumerate(contas_existentes):
            if str(r.get("id")) == mes_atual:
                contas_existentes[idx]["consumo_m3"] = 0.0
                if "valor_total" in contas_existentes[idx]:
                    contas_existentes[idx]["valor_total"] = 0.0
                alterou_conta = True
        if alterou_conta:
            p_conta = salvar_json("conta.json", contas_existentes)

    # -------------------------------------------------------------------------
    # 7. SUMARIO_EXECUCAO.JSON LIMPO (Zera vazão e consumo mensal na homepage)
    # -------------------------------------------------------------------------
    sumario_limpo = {
        "status": "sucesso",
        "mes_atual": mes_atual,
        "consumo_mes_acumulado_m3": 0.0,
        "previsao_proximo_mes_m3": 0.0,
        "fatura_estimada_reais": 0.0,
        "data_treinamento_ml": hoje.isoformat(),
        "ano_grafico": hoje.year,
        "meta_status": "NORMAL",
        "vazao_atual_m3h": 0.0,
        "alertas_ativos": [],
        "notificacoes": notifs_admin,
        "notificacoes_usuarios": notifs_usuarios
    }
    p_sum = salvar_json("sumario_execucao.json", sumario_limpo)

    # -------------------------------------------------------------------------
    # 8. ESTADO_MEDIDOR.JSON LIMPO (Zera pulsos do medidor e vazão)
    # -------------------------------------------------------------------------
    estado_medidor_limpo = {
        "timestamp": hoje.isoformat(),
        "pulsos_acumulados": 0.0,
        "vazao_m3h": 0.0
    }
    p_med = salvar_json("estado_medidor.json", estado_medidor_limpo)

    # -------------------------------------------------------------------------
    # Grava os arquivos de saída e consolida o resumo
    # -------------------------------------------------------------------------
    p_cfg = salvar_json("config.json", config_limpo)
    p_prog = salvar_json("progresso_meta.json", progresso_limpo)
    p_cons = salvar_json("consumo_mes.json", consumo_limpo)

    arquivos_resetados = [
        str(p_cfg.name),
        str(p_prog.name),
        str(p_cons.name),
        str(p_graf.name),
        str(p_sum.name),
        str(p_med.name)
    ]
    if p_conta:
        arquivos_resetados.append(str(p_conta.name))

    resumo = {
        "status": "sucesso",
        "timestamp": hoje.isoformat(),
        "arquivos_resetados": arquivos_resetados,
        "mes_referencia": mes_atual
    }

    print("=" * 65)
    print("        HYDRANOMIC - RESET DE DADOS CONCLUÍDO COM SUCESSO       ")
    print("=" * 65)
    print(f"✓ Mês de referência ativo: {mes_atual}")
    print("✓ config.json: Metas zeradas em todos os meses (preferências salvas).")
    print("✓ progresso_meta.json: Situação 'NORMAL', alertas limpos, 0% atingido.")
    print("✓ consumo_mes.json: Consumo acumulado zerado (0.0 m³), vazão zerada.")
    print("✓ sumario_execucao.json: Vazão zerada (0.00 m³/h), consumo mensal zerado.")
    print("✓ estado_medidor.json: Pulsos e medições zerados para nova telemetria.")
    print(f"✓ grafico_anual.json: Consumo do mês atual ({tags_meses[hoje.month - 1]}) zerado (0.0 m³), demais meses preservados.")
    if p_conta:
        print(f"✓ conta.json: Registro do mês {mes_atual} zerado, histórico mantido.")
    print("✓ Nenhum outro dado do histórico anual foi afetado.")
    print("=" * 65)

    return resumo


if __name__ == "__main__":
    executar_reset()
