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

# Permite execução tanto local quanto dentro do container WEGnology
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from wegnology_adapter import (
        obter_diretorio_input,
        obter_diretorio_output,
        carregar_json,
        salvar_json,
    )
except ImportError:
    def obter_diretorio_output() -> Path:
        p = Path(os.environ.get("OUTPUT_DIR", "./outputs"))
        p.mkdir(parents=True, exist_ok=True)
        return p

    def obter_diretorio_input() -> Path:
        p = Path(os.environ.get("INPUT_DIR", "./inputs"))
        return p

    def carregar_json(nome: str, padrao: Any = None) -> Any:
        for d in [obter_diretorio_input(), Path.cwd()]:
            c = d / nome
            if c.exists() and c.stat().st_size > 0:
                with open(c, "r", encoding="utf-8") as f:
                    return json.load(f)
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

    # -------------------------------------------------------------------------
    # 2. CONFIG.JSON LIMPO
    # -------------------------------------------------------------------------
    config_limpo = {
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
        "tarifa_m3": 59.6,
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
    # Grava exclusivamente os 3 arquivos de saída
    # -------------------------------------------------------------------------
    p_cfg = salvar_json("config.json", config_limpo)
    p_prog = salvar_json("progresso_meta.json", progresso_limpo)
    p_cons = salvar_json("consumo_mes.json", consumo_limpo)

    resumo = {
        "status": "sucesso",
        "timestamp": hoje.isoformat(),
        "arquivos_resetados": [
            str(p_cfg.name),
            str(p_prog.name),
            str(p_cons.name)
        ],
        "mes_referencia": mes_atual
    }

    print("=" * 65)
    print("        HYDRANOMIC - RESET DE DADOS CONCLUÍDO COM SUCESSO       ")
    print("=" * 65)
    print(f"✓ Mês de referência ativo: {mes_atual}")
    print("✓ config.json: Metas zeradas em todos os meses (preferências salvas).")
    print("✓ progresso_meta.json: Situação 'NORMAL', alertas limpos, 0% atingido.")
    print("✓ consumo_mes.json: Consumo acumulado zerado (0.0 m³), vazão zerada.")
    print("✓ Nenhum outro arquivo foi alterado.")
    print("=" * 65)

    return resumo


if __name__ == "__main__":
    executar_reset()
