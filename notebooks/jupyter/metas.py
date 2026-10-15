"""
Módulo de Gestão de Metas de Consumo de Água.
Adaptado para a metodologia WEGnology / Jupyter Notebook.

Permite carregar, criar, avaliar e salvar metas de consumo,
integrando-se ao sistema de Application Files do WEGnology via
INPUT_DIR e OUTPUT_DIR.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Garante que o diretório atual esteja no path para importar wegnology_adapter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto


NOME_ARQUIVO_CONFIG = "config.json"


def obter_config_padrao() -> Dict[str, Any]:
    """Retorna a estrutura vazia padrão do arquivo de configuração."""
    return {"meta_ativa": None, "solicitacao_exclusao": None}


def carregar_config(nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Dict[str, Any]:
    """Carrega a configuração de metas a partir do INPUT_DIR ou local."""
    try:
        config = carregar_json(nome_arquivo, padrao=obter_config_padrao())
    except Exception:
        config = obter_config_padrao()

    config.setdefault("meta_ativa", None)
    config.setdefault("solicitacao_exclusao", None)
    return config


def salvar_config(config: Dict[str, Any], nome_arquivo: str = NOME_ARQUIVO_CONFIG) -> Path:
    """Salva a configuração no OUTPUT_DIR do WEGnology para persistência."""
    return salvar_json(nome_arquivo, config)


def criar_meta(
    tipo: str,
    nome: str,
    valor: float,
    periodo: str,
    descricao: str = "",
    salvar: bool = True
) -> Dict[str, Any]:
    """
    Cria uma meta de consumo de água, impedindo mais de uma meta ativa simultaneamente.
    """
    config = carregar_config()

    if config.get("meta_ativa") is not None:
        raise ValueError("Já existe uma meta ativa ou aguardando exclusão.")

    try:
        valor = float(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError("O valor da meta deve ser numérico.") from erro

    if not nome or valor <= 0 or not periodo:
        raise ValueError("Nome, valor positivo e período são obrigatórios.")

    meta = {
        "tipo": tipo,
        "nome": nome,
        "valor": valor,
        "periodo": periodo,
        "descricao": descricao,
        "status": "ativa",
    }

    config["meta_ativa"] = meta
    config["solicitacao_exclusao"] = None

    if salvar:
        salvar_config(config)

    return meta


def solicitar_exclusao_meta(salvar: bool = True) -> Dict[str, Any]:
    """Registra a solicitação para excluir a meta atual."""
    config = carregar_config()

    if config.get("meta_ativa") is None:
        raise ValueError("Não existe uma meta para excluir.")

    solicitacao = {
        "status": "pendente",
        "meta": config["meta_ativa"],
    }
    config["solicitacao_exclusao"] = solicitacao
    config["meta_ativa"]["status"] = "exclusao_solicitada"

    if salvar:
        salvar_config(config)

    return solicitacao


def confirmar_exclusao_meta(salvar: bool = True) -> Dict[str, Any]:
    """Confirma o pedido e remove a meta ativa."""
    config = carregar_config()

    if config.get("solicitacao_exclusao") is None:
        raise ValueError("Não existe uma solicitação de exclusão pendente.")

    config["meta_ativa"] = None
    config["solicitacao_exclusao"] = None

    if salvar:
        salvar_config(config)

    return config


def avaliar_progresso_meta(consumo_atual_m3: float) -> Optional[Dict[str, Any]]:
    """
    Compara o consumo atual com a meta ativa e gera métricas de acompanhamento.
    Útil para painéis de monitoramento e alertas automáticos na WEGnology.
    """
    config = carregar_config()
    meta = config.get("meta_ativa")

    if not meta:
        return None

    limite = float(meta["valor"])
    porcentagem = round((consumo_atual_m3 / limite) * 100, 2)
    saldo_restante = round(limite - consumo_atual_m3, 2)

    if porcentagem >= 100:
        situacao = "ESTOURADA"
    elif porcentagem >= 80:
        situacao = "ALERTA_80"
    else:
        situacao = "NORMAL"

    relatorio_meta = {
        "meta_nome": meta["nome"],
        "limite_m3": limite,
        "consumo_atual_m3": consumo_atual_m3,
        "percentual_atingido": porcentagem,
        "saldo_restante_m3": saldo_restante,
        "situacao": situacao,
    }

    # Salva relatório de progresso para a WEGnology
    salvar_json("progresso_meta.json", relatorio_meta)
    return relatorio_meta


if __name__ == "__main__":
    print("--- Verificando Configuração de Metas ---")
    cfg = carregar_config()
    print("Meta Ativa:", cfg.get("meta_ativa"))
    print("Solicitação de Exclusão:", cfg.get("solicitacao_exclusao"))
