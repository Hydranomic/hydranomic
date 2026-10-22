import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto

NOME_ARQUIVO_CONFIG = "config.json"
NOME_ARQUIVO_PROGRESSO = "progresso_meta.json"

def obter_config_padrao() -> Dict[str, Any]:
    return {"meta_ativa": None, "solicitacao_exclusao": None}

def carregar_config(nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Dict[str, Any]:
    try:
        config = carregar_json(nome_arquivo, padrao=obter_config_padrao())
    except Exception:
        config = obter_config_padrao()
    config.setdefault("meta_ativa", None)
    config.setdefault("solicitacao_exclusao", None)
    return config

def salvar_config(config: Dict[str, Any], nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Path:
    return salvar_json(nome_arquivo, config)

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
    meta = config.get("meta_ativa")
    if not meta:
        relatorio = {
            "meta_ativa": False,
            "mensagem": "Nenhuma meta ativa configurada.",
            "consumo_atual_m3": consumo_atual_m3
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
            "situacao": situacao
        }
    if salvar:
        salvar_json(NOME_ARQUIVO_PROGRESSO, relatorio)
    return relatorio

if __name__ == "__main__":
    avaliar_progresso_meta(0.0)
