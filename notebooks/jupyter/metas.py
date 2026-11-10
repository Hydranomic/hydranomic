import sys
import calendar
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto

NOME_ARQUIVO_CONFIG = "config.json"
NOME_ARQUIVO_PROGRESSO = "progresso_meta.json"

def obter_config_padrao() -> Dict[str, Any]:
    return {
        "meta_ativa": None,
        "metas_por_mes": {},
        "solicitacao_exclusao": None,
        "notificacoes": {
            "notificacao_prazos": True,
            "alerta_status": True
        }
    }

def carregar_config(nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Dict[str, Any]:
    try:
        config = carregar_json(nome_arquivo, padrao=obter_config_padrao())
    except Exception:
        config = obter_config_padrao()
    if not isinstance(config, dict):
        config = obter_config_padrao()
    config.setdefault("meta_ativa", None)
    config.setdefault("metas_por_mes", {})
    config.setdefault("solicitacao_exclusao", None)
    if "notificacoes" not in config or not isinstance(config["notificacoes"], dict):
        config["notificacoes"] = {"notificacao_prazos": True, "alerta_status": True}
    config["notificacoes"].setdefault("notificacao_prazos", True)
    config["notificacoes"].setdefault("alerta_status", True)
    return config

def salvar_config(config: Dict[str, Any], nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Path:
    return salvar_json(nome_arquivo, config)

def salvar_notificacoes(notificacao_prazos: Optional[bool] = None, alerta_status: Optional[bool] = None, salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    if notificacao_prazos is not None:
        config["notificacoes"]["notificacao_prazos"] = bool(notificacao_prazos)
    if alerta_status is not None:
        config["notificacoes"]["alerta_status"] = bool(alerta_status)
    if salvar:
        salvar_config(config)
    return config["notificacoes"]

def criar_meta(tipo: str, nome: str, valor: float, periodo: str, descricao: str = "", salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    if config.get("meta_ativa") is not None:
        raise ValueError("Ja existe uma meta ativa ou aguardando exclusao.")
    try:
        valor = float(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError("O valor da meta deve ser numerico.") from erro
    if not nome or valor <= 0 or not periodo:
        raise ValueError("Nome, valor positivo e periodo sao obrigatorios.")
    meta = {
        "tipo": tipo,
        "nome": nome,
        "valor": valor,
        "periodo": periodo,
        "descricao": descricao,
        "status": "ativa"
    }
    config["meta_ativa"] = meta
    config["solicitacao_exclusao"] = None
    if salvar:
        salvar_config(config)
    return meta

def solicitar_exclusao_meta(salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    if config.get("meta_ativa") is None:
        raise ValueError("Nao existe uma meta para excluir.")
    solicitacao = {
        "status": "pendente",
        "meta": config["meta_ativa"]
    }
    config["solicitacao_exclusao"] = solicitacao
    config["meta_ativa"]["status"] = "exclusao_solicitada"
    if salvar:
        salvar_config(config)
    return solicitacao

def confirmar_exclusao_meta(salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    if config.get("solicitacao_exclusao") is None:
        raise ValueError("Nao existe uma solicitacao de exclusao pendente.")
    config["meta_ativa"] = None
    config["solicitacao_exclusao"] = None
    if salvar:
        salvar_config(config)
    return config

def avaliar_progresso_meta(consumo_atual_m3: float, salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    
    # Processa se o contexto recebido contiver acao de notificacoes ou metas
    try:
        ctx = carregar_contexto() if "carregar_contexto" in globals() else {}
        if isinstance(ctx, dict):
            if "body" in ctx and isinstance(ctx["body"], dict):
                for k, v in ctx["body"].items():
                    if k not in ctx:
                        ctx[k] = v
            if ctx.get("acao") == "salvar_notificacoes" or "notificacao_prazos" in ctx or "alerta_status" in ctx or "notificacoes" in ctx:
                notifs = ctx.get("notificacoes")
                alterou = False
                if isinstance(notifs, dict):
                    if "notificacao_prazos" in notifs:
                        config["notificacoes"]["notificacao_prazos"] = bool(notifs["notificacao_prazos"])
                        alterou = True
                    if "alerta_status" in notifs:
                        config["notificacoes"]["alerta_status"] = bool(notifs["alerta_status"])
                        alterou = True
                if "notificacao_prazos" in ctx:
                    config["notificacoes"]["notificacao_prazos"] = bool(ctx["notificacao_prazos"])
                    alterou = True
                if "alerta_status" in ctx:
                    config["notificacoes"]["alerta_status"] = bool(ctx["alerta_status"])
                    alterou = True
                if alterou and salvar:
                    salvar_config(config)

            if (ctx.get("acao") == "definir_meta" or ctx.get("nome")) and ctx.get("valor") is not None:
                periodo_meta = str(ctx.get("periodo") or ctx.get("data") or datetime.now().strftime("%Y-%m")).strip()
                mes_ref = periodo_meta[:7] if len(periodo_meta) >= 7 else datetime.now().strftime("%Y-%m")
                tipo_meta = str(ctx.get("tipo") or "consumo-mensal").strip()
                valor_meta = float(ctx.get("valor"))
                valor_litros = float(ctx.get("valor_litros")) if ctx.get("valor_litros") is not None else (valor_meta * 1000.0 if tipo_meta in ("consumo-mensal", "reducao_mensal") else None)
                nova_meta_obj = {
                    "tipo": tipo_meta,
                    "unidade": ctx.get("unidade") or ("L" if tipo_meta in ("consumo-mensal", "reducao_mensal") else "R$"),
                    "nome": ctx.get("nome", "Meta de Consumo"),
                    "valor": valor_meta,
                    "valor_litros": valor_litros,
                    "periodo": periodo_meta,
                    "mes_referencia": mes_ref,
                    "data_criacao": datetime.now().strftime("%Y-%m-%d"),
                    "descricao": ctx.get("descricao", ""),
                    "status": "ativa"
                }
                if not isinstance(config.get("metas_ativas_por_tipo"), dict):
                    config["metas_ativas_por_tipo"] = {}
                config["metas_ativas_por_tipo"][tipo_meta] = nova_meta_obj
                if tipo_meta in ("consumo-mensal", "reducao_mensal") or not config.get("meta_ativa"):
                    config["meta_ativa"] = nova_meta_obj
                if not isinstance(config.get("metas_por_mes"), dict):
                    config["metas_por_mes"] = {}
                reg_mes = config["metas_por_mes"].get(mes_ref)
                if not isinstance(reg_mes, dict):
                    reg_mes = {}
                if not isinstance(reg_mes.get("por_tipo"), dict):
                    reg_mes["por_tipo"] = {}
                reg_mes["por_tipo"][tipo_meta] = nova_meta_obj
                if tipo_meta in ("consumo-mensal", "reducao_mensal") or "valor" not in reg_mes:
                    reg_mes["nome"] = nova_meta_obj["nome"]
                    reg_mes["valor"] = nova_meta_obj["valor"]
                    reg_mes["valor_litros"] = valor_litros
                    reg_mes["periodo"] = periodo_meta
                    reg_mes["tipo"] = tipo_meta
                config["metas_por_mes"][mes_ref] = reg_mes
                config["solicitacao_exclusao"] = None
                if salvar:
                    salvar_config(config)
    except Exception:
        pass

    meta = config.get("meta_ativa")
    hoje = datetime.now()
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_restantes = max(0, ultimo_dia_mes - hoje.day)

    conf_notif = config.get("notificacoes", {"notificacao_prazos": True, "alerta_status": True})
    permite_status = conf_notif.get("alerta_status", True)
    permite_prazos = conf_notif.get("notificacao_prazos", True)

    alertas_ativos = []

    if not meta:
        situacao = "NORMAL"
        relatorio = {
            "meta_ativa": False,
            "mensagem": "Nenhuma meta ativa configurada.",
            "consumo_atual_m3": consumo_atual_m3,
            "situacao": situacao
        }
    else:
        limite = float(meta["valor"])
        porcentagem = round((consumo_atual_m3 / limite) * 100, 2)
        saldo_restante = round(limite - consumo_atual_m3, 2)
        if porcentagem >= 100:
            situacao = "ESTOURADA"
        elif porcentagem >= 80:
            situacao = "ALERTA_80"
        else:
            situacao = "NORMAL"
        relatorio = {
            "meta_ativa": True,
            "meta_nome": meta["nome"],
            "limite_m3": limite,
            "consumo_atual_m3": consumo_atual_m3,
            "percentual_atingido": porcentagem,
            "saldo_restante_m3": saldo_restante,
            "situacao": situacao,
            "periodo": meta.get("periodo", "")
        }

        # 1. Alerta de Status da Meta (80% ou Ultrapassada)
        if permite_status:
            if situacao == "ESTOURADA":
                alertas_ativos.append({
                    "id": "meta_estourada",
                    "tipo": "limite_estourado",
                    "severidade": "perigo",
                    "titulo": "Meta Ultrapassada!",
                    "mensagem": f"O consumo de {consumo_atual_m3:.2f} m³ ultrapassou a meta de {limite:.2f} m³ ({porcentagem:.1f}% atingido).",
                    "timestamp": hoje.isoformat()
                })
            elif situacao == "ALERTA_80":
                alertas_ativos.append({
                    "id": "meta_80",
                    "tipo": "alerta_80",
                    "severidade": "alerta",
                    "titulo": "Atenção: 80% da Meta Atingida",
                    "mensagem": f"O consumo atingiu {porcentagem:.1f}% da meta estabelecida ({consumo_atual_m3:.2f} m³ de {limite:.2f} m³).",
                    "timestamp": hoje.isoformat()
                })

    # 2. Alerta de Prazo Próximo (48h / <= 2 dias para o fechamento do mês)
    if permite_prazos and dias_restantes <= 2:
        msg_prazo = "Faltam menos de 24h para o encerramento do ciclo mensal da sua meta." if dias_restantes <= 1 else f"Faltam {dias_restantes} dias para o encerramento do ciclo mensal da sua meta."
        alertas_ativos.append({
            "id": "prazo_fim_mes",
            "tipo": "prazo_proximo",
            "severidade": "info",
            "titulo": "Prazo de Fechamento Próximo",
            "mensagem": msg_prazo,
            "timestamp": hoje.isoformat()
        })

    relatorio["alertas_ativos"] = alertas_ativos
    relatorio["notificacoes"] = conf_notif
    relatorio["dias_restantes_mes"] = dias_restantes

    if salvar:
        salvar_json(NOME_ARQUIVO_PROGRESSO, relatorio)
    return relatorio

if __name__ == "__main__":
    avaliar_progresso_meta(0.0)
