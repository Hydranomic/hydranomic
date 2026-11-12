import sys
import calendar
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto

NOME_ARQUIVO_CONFIG = "config.json"
NOME_ARQUIVO_PROGRESSO = "progresso_meta.json"

TIPOS_CONSUMO = ("consumo-mensal", "reducao_mensal")
TIPOS_FINANCEIROS = ("gasto-maximo-mensal", "economia-mensal")


def obter_config_padrao() -> Dict[str, Any]:
    return {
        "meta_ativa": None,
        "metas_ativas_por_tipo": {},
        "metas_por_mes": {},
        "solicitacao_exclusao": None,
        "notificacoes": {
            "notificacao_prazos": True,
            "alerta_status": True
        },
        "notificacoes_usuarios": {}
    }


def carregar_config(nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Dict[str, Any]:
    try:
        config = carregar_json(nome_arquivo, padrao=obter_config_padrao())
    except Exception:
        config = obter_config_padrao()
    if not isinstance(config, dict):
        config = obter_config_padrao()

    config.setdefault("meta_ativa", None)
    if not isinstance(config.get("metas_ativas_por_tipo"), dict):
        config["metas_ativas_por_tipo"] = {}
    if not isinstance(config.get("metas_por_mes"), dict):
        config["metas_por_mes"] = {}
    config.setdefault("solicitacao_exclusao", None)

    if "notificacoes" not in config or not isinstance(config["notificacoes"], dict):
        config["notificacoes"] = {"notificacao_prazos": True, "alerta_status": True}
    config["notificacoes"].setdefault("notificacao_prazos", True)
    config["notificacoes"].setdefault("alerta_status", True)

    if not isinstance(config.get("notificacoes_usuarios"), dict):
        config["notificacoes_usuarios"] = {}

    # Sanitização: meta_ativa NUNCA pode ser financeira (ex: gasto-maximo-mensal ou economia-mensal)
    # pois meta_ativa é comparada diretamente com o consumo físico de água em m³.
    meta_ativa = config.get("meta_ativa")
    if isinstance(meta_ativa, dict):
        tipo_ma = str(meta_ativa.get("tipo", "")).strip()
        if tipo_ma in TIPOS_FINANCEIROS:
            if tipo_ma not in config["metas_ativas_por_tipo"]:
                config["metas_ativas_por_tipo"][tipo_ma] = dict(meta_ativa)
            c_cons = config["metas_ativas_por_tipo"].get("consumo-mensal") or config["metas_ativas_por_tipo"].get("reducao_mensal")
            config["meta_ativa"] = dict(c_cons) if isinstance(c_cons, dict) else None
        elif tipo_ma in TIPOS_CONSUMO:
            if tipo_ma not in config["metas_ativas_por_tipo"]:
                config["metas_ativas_por_tipo"][tipo_ma] = dict(meta_ativa)

    # Se meta_ativa for None mas existir uma de consumo ativa salva, restaura ela
    if not config.get("meta_ativa"):
        for tc in TIPOS_CONSUMO:
            if tc in config["metas_ativas_por_tipo"] and isinstance(config["metas_ativas_por_tipo"][tc], dict):
                config["meta_ativa"] = dict(config["metas_ativas_por_tipo"][tc])
                break

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
    try:
        valor = float(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError("O valor da meta deve ser numerico.") from erro
    if not nome or valor <= 0 or not periodo:
        raise ValueError("Nome, valor positivo e periodo sao obrigatorios.")

    periodo_str = str(periodo).strip()
    mes_ref = periodo_str[:7] if len(periodo_str) >= 7 else datetime.now().strftime("%Y-%m")
    eh_consumo = tipo in TIPOS_CONSUMO
    valor_litros = valor * 1000.0 if eh_consumo else None

    meta = {
        "tipo": tipo,
        "unidade": "L" if eh_consumo else "R$",
        "nome": nome,
        "valor": valor,
        "valor_litros": valor_litros,
        "periodo": periodo_str,
        "mes_referencia": mes_ref,
        "data_criacao": datetime.now().strftime("%Y-%m-%d"),
        "descricao": descricao,
        "status": "ativa"
    }

    # Salva isoladamente no dicionário por tipo (PRESERVA os outros tipos intactos!)
    config["metas_ativas_por_tipo"][tipo] = meta

    # Apenas metas de consumo físico viram meta_ativa
    if eh_consumo:
        config["meta_ativa"] = meta

    # Registra no histórico do mês preservando os outros tipos
    if mes_ref not in config["metas_por_mes"] or not isinstance(config["metas_por_mes"][mes_ref], dict):
        config["metas_por_mes"][mes_ref] = {}
    reg_mes = config["metas_por_mes"][mes_ref]
    if "por_tipo" not in reg_mes or not isinstance(reg_mes["por_tipo"], dict):
        reg_mes["por_tipo"] = {}
    reg_mes["por_tipo"][tipo] = meta

    # Atualiza raiz do mês apenas se for meta de consumo ou se a raiz estiver sem valor
    if eh_consumo or "valor" not in reg_mes or reg_mes.get("tipo") not in TIPOS_CONSUMO:
        if eh_consumo:
            reg_mes["nome"] = meta["nome"]
            reg_mes["valor"] = meta["valor"]
            reg_mes["valor_litros"] = valor_litros
            reg_mes["periodo"] = periodo_str
            reg_mes["tipo"] = tipo
        elif "valor" not in reg_mes:
            reg_mes["nome"] = meta["nome"]
            reg_mes["valor"] = meta["valor"]
            reg_mes["periodo"] = periodo_str
            reg_mes["tipo"] = tipo

    config["metas_por_mes"][mes_ref] = reg_mes
    config["solicitacao_exclusao"] = None
    if salvar:
        salvar_config(config)
    return meta


def solicitar_exclusao_meta(tipo: Optional[str] = None, salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    meta = None
    if tipo and config.get("metas_ativas_por_tipo", {}).get(tipo):
        meta = config["metas_ativas_por_tipo"][tipo]
    else:
        meta = config.get("meta_ativa")

    if not meta:
        raise ValueError("Nao existe uma meta para excluir.")

    solicitacao = {
        "status": "pendente",
        "tipo": meta.get("tipo", "consumo-mensal"),
        "meta": meta
    }
    config["solicitacao_exclusao"] = solicitacao
    meta["status"] = "exclusao_solicitada"
    if salvar:
        salvar_config(config)
    return solicitacao


def confirmar_exclusao_meta(salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()
    solic = config.get("solicitacao_exclusao")
    if not solic:
        raise ValueError("Nao existe uma solicitacao de exclusao pendente.")
    tipo = solic.get("tipo")
    if tipo and tipo in config.get("metas_ativas_por_tipo", {}):
        del config["metas_ativas_por_tipo"][tipo]
    if config.get("meta_ativa") and (not tipo or config["meta_ativa"].get("tipo") == tipo):
        config["meta_ativa"] = None
        for tc in TIPOS_CONSUMO:
            if tc in config.get("metas_ativas_por_tipo", {}):
                config["meta_ativa"] = dict(config["metas_ativas_por_tipo"][tc])
                break
    config["solicitacao_exclusao"] = None
    if salvar:
        salvar_config(config)
    return config


def avaliar_progresso_meta(consumo_atual_m3: Optional[float] = None, salvar: bool = True) -> Dict[str, Any]:
    config = carregar_config()

    # Processa se o contexto recebido contiver acao de notificacoes ou metas
    try:
        ctx = carregar_contexto() if "carregar_contexto" in globals() else {}
        if isinstance(ctx, dict):
            if "body" in ctx and isinstance(ctx["body"], dict):
                for k, v in ctx["body"].items():
                    if k not in ctx:
                        ctx[k] = v

            # 1. Tratamento de preferências de Notificação
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

                pref_usr = {
                    "notificacao_prazos": bool(config["notificacoes"]["notificacao_prazos"]),
                    "alerta_status": bool(config["notificacoes"]["alerta_status"])
                }
                chaves_usr = []
                for campo_u in ("usuario", "nome_usuario", "email", "user_id"):
                    val_u = str(ctx.get(campo_u) or "").strip().lower()
                    if val_u:
                        chaves_usr.append(val_u)
                        if "@" in val_u:
                            chaves_usr.append(val_u.split("@")[0].strip())
                if isinstance(ctx.get("chaves_usuario"), list):
                    for cu in ctx["chaves_usuario"]:
                        if cu:
                            chaves_usr.append(str(cu).strip().lower())
                for cu in set(chaves_usr):
                    if cu:
                        config["notificacoes_usuarios"][cu] = dict(pref_usr)
                        alterou = True
                if alterou and salvar:
                    salvar_config(config)

            # 2. Definição / Criação de Meta via Contexto
            if (ctx.get("acao") == "definir_meta" or ctx.get("nome")) and ctx.get("valor") is not None:
                periodo_meta = str(ctx.get("periodo") or ctx.get("data") or datetime.now().strftime("%Y-%m")).strip()
                mes_ref = periodo_meta[:7] if len(periodo_meta) >= 7 else datetime.now().strftime("%Y-%m")
                tipo_meta = str(ctx.get("tipo") or "consumo-mensal").strip()
                valor_meta = float(ctx.get("valor"))
                eh_consumo = tipo_meta in TIPOS_CONSUMO

                valor_litros = float(ctx.get("valor_litros")) if ctx.get("valor_litros") is not None else (valor_meta * 1000.0 if eh_consumo else None)

                nova_meta_obj = {
                    "tipo": tipo_meta,
                    "unidade": ctx.get("unidade") or ("L" if eh_consumo else "R$"),
                    "nome": ctx.get("nome", "Meta de Consumo" if eh_consumo else ("Gasto Máximo" if tipo_meta == "gasto-maximo-mensal" else "Meta de Economia")),
                    "valor": valor_meta,
                    "valor_litros": valor_litros,
                    "periodo": periodo_meta,
                    "mes_referencia": mes_ref,
                    "data_criacao": datetime.now().strftime("%Y-%m-%d"),
                    "descricao": ctx.get("descricao", ""),
                    "status": "ativa"
                }

                # PRESERVAÇÃO RIGOROSA: Guarda no dicionário específico do tipo sem tocar nos demais
                if not isinstance(config.get("metas_ativas_por_tipo"), dict):
                    config["metas_ativas_por_tipo"] = {}
                config["metas_ativas_por_tipo"][tipo_meta] = nova_meta_obj

                # Apenas metas de consumo (físico em m³) podem ocupar 'meta_ativa'
                if eh_consumo:
                    config["meta_ativa"] = nova_meta_obj

                # Atualiza estrutura no mês preservando os outros tipos
                if not isinstance(config.get("metas_por_mes"), dict):
                    config["metas_por_mes"] = {}
                reg_mes = config["metas_por_mes"].get(mes_ref)
                if not isinstance(reg_mes, dict):
                    reg_mes = {}
                if not isinstance(reg_mes.get("por_tipo"), dict):
                    reg_mes["por_tipo"] = {}
                reg_mes["por_tipo"][tipo_meta] = nova_meta_obj

                # Na raiz do mês (compatibilidade com telas legado), atualiza prioritariamente consumo
                if eh_consumo:
                    reg_mes["nome"] = nova_meta_obj["nome"]
                    reg_mes["valor"] = nova_meta_obj["valor"]
                    reg_mes["valor_litros"] = valor_litros
                    reg_mes["periodo"] = periodo_meta
                    reg_mes["tipo"] = tipo_meta
                elif "valor" not in reg_mes:
                    reg_mes["nome"] = nova_meta_obj["nome"]
                    reg_mes["valor"] = nova_meta_obj["valor"]
                    reg_mes["periodo"] = periodo_meta
                    reg_mes["tipo"] = tipo_meta

                config["metas_por_mes"][mes_ref] = reg_mes
                config["solicitacao_exclusao"] = None
                if salvar:
                    salvar_config(config)
    except Exception:
        pass

    # Se o consumo não for informado, tenta ler consumo_mes.json ou conta.json
    if consumo_atual_m3 is None:
        try:
            consumo_mes = carregar_json("consumo_mes.json", padrao={})
            consumo_atual_m3 = float(consumo_mes.get("consumo_acumulado_mes_m3", 0.0))
        except Exception:
            try:
                dados_conta = carregar_json("conta.json", padrao=[])
                if isinstance(dados_conta, list) and len(dados_conta) > 0:
                    consumo_atual_m3 = float(dados_conta[-1].get("consumo_m3", 0.0))
                else:
                    consumo_atual_m3 = 0.0
            except Exception:
                consumo_atual_m3 = 0.0

    consumo_val = float(consumo_atual_m3 or 0.0)

    # Identifica meta de consumo ativa para avaliação
    meta = config.get("meta_ativa")
    if not meta or meta.get("tipo") in TIPOS_FINANCEIROS:
        for tc in TIPOS_CONSUMO:
            if tc in config.get("metas_ativas_por_tipo", {}):
                meta = config["metas_ativas_por_tipo"][tc]
                break

    hoje = datetime.now()
    ultimo_dia_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_restantes = max(0, ultimo_dia_mes - hoje.day)

    conf_notif = config.get("notificacoes", {"notificacao_prazos": True, "alerta_status": True})
    permite_status = conf_notif.get("alerta_status", True)
    permite_prazos = conf_notif.get("notificacao_prazos", True)

    alertas_ativos = []

    if not meta or meta.get("tipo") in TIPOS_FINANCEIROS:
        situacao = "NORMAL"
        relatorio = {
            "meta_ativa": False,
            "mensagem": "Nenhuma meta de consumo ativa configurada no momento.",
            "consumo_atual_m3": consumo_val,
            "situacao": situacao,
            "metas_ativas_por_tipo": config.get("metas_ativas_por_tipo", {})
        }
    else:
        limite = float(meta.get("valor", 1.0))
        porcentagem = round((consumo_val / limite) * 100, 2) if limite > 0 else 0.0
        saldo_restante = round(limite - consumo_val, 2)
        if porcentagem >= 100:
            situacao = "ESTOURADA"
        elif porcentagem >= 80:
            situacao = "ALERTA_80"
        else:
            situacao = "NORMAL"

        relatorio = {
            "meta_ativa": True,
            "meta_nome": meta.get("nome", "Meta de Consumo"),
            "tipo": meta.get("tipo", "consumo-mensal"),
            "limite_m3": limite,
            "consumo_atual_m3": consumo_val,
            "percentual_atingido": porcentagem,
            "saldo_restante_m3": saldo_restante,
            "situacao": situacao,
            "periodo": meta.get("periodo", ""),
            "mes_referencia": meta.get("mes_referencia", str(meta.get("periodo", ""))[:7]),
            "metas_ativas_por_tipo": config.get("metas_ativas_por_tipo", {})
        }

        # 1. Alerta de Status da Meta (80% ou Ultrapassada)
        if permite_status:
            if situacao == "ESTOURADA":
                alertas_ativos.append({
                    "id": "meta_estourada",
                    "tipo": "limite_estourado",
                    "severidade": "perigo",
                    "titulo": "Meta Ultrapassada!",
                    "mensagem": f"O consumo de {consumo_val:.2f} m³ ultrapassou a meta de {limite:.2f} m³ ({porcentagem:.1f}% atingido).",
                    "timestamp": hoje.isoformat()
                })
            elif situacao == "ALERTA_80":
                alertas_ativos.append({
                    "id": "meta_80",
                    "tipo": "alerta_80",
                    "severidade": "alerta",
                    "titulo": "Atenção: 80% da Meta Atingida",
                    "mensagem": f"O consumo atingiu {porcentagem:.1f}% da meta estabelecida ({consumo_val:.2f} m³ de {limite:.2f} m³).",
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
    relatorio["notificacoes_config"] = conf_notif
    relatorio["notificacoes_usuarios"] = config.get("notificacoes_usuarios", {})
    relatorio["dias_restantes_mes"] = dias_restantes

    if salvar:
        salvar_json(NOME_ARQUIVO_PROGRESSO, relatorio)
    return relatorio


if __name__ == "__main__":
    avaliar_progresso_meta()
