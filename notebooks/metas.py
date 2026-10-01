############################################

# CÓDIGO FINALIZADO 1.0 - 24/09/2026 #
# FALTANDO INTEGRAÇÃO WEGNOLOGY E FRONT-END #

############################################

import json
from pathlib import Path


CAMINHO_CONFIG = Path(__file__).resolve().parents[1] / "workflows" / "config.json"


def carregar_config(caminho_config=CAMINHO_CONFIG):
	"""Carrega a configuração ou cria a estrutura inicial do arquivo."""
	caminho_config = Path(caminho_config)

	if not caminho_config.exists() or caminho_config.stat().st_size == 0:
		return {"meta_ativa": None, "solicitacao_exclusao": None}

	with caminho_config.open("r", encoding="utf-8") as arquivo:
		config = json.load(arquivo)

	config.setdefault("meta_ativa", None)
	config.setdefault("solicitacao_exclusao", None)
	return config


def salvar_config(config, caminho_config=CAMINHO_CONFIG):
	"""Salva a configuração no arquivo JSON."""
	caminho_config = Path(caminho_config)
	caminho_config.parent.mkdir(parents=True, exist_ok=True)

	with caminho_config.open("w", encoding="utf-8") as arquivo:
		json.dump(config, arquivo, ensure_ascii=False, indent=2)


def criar_meta(tipo, nome, valor, periodo, descricao="", caminho_config=CAMINHO_CONFIG):
	"""Cria uma meta, impedindo mais de uma meta ativa."""
	config = carregar_config(caminho_config)

	if config["meta_ativa"] is not None:
		raise ValueError("Já existe uma meta ativa ou aguardando exclusão.")

	try:
		valor = float(valor)
	except (TypeError, ValueError) as erro:
		raise ValueError("O valor da meta deve ser numérico.") from erro

	if not nome or valor <= 0 or not periodo:
		raise ValueError("Nome, valor positivo e período são obrigatórios.")

	config["meta_ativa"] = {
		"tipo": tipo,
		"nome": nome,
		"valor": valor,
		"periodo": periodo,
		"descricao": descricao,
		"status": "ativa",
	}
	config["solicitacao_exclusao"] = None
	salvar_config(config, caminho_config)
	return config["meta_ativa"]


def solicitar_exclusao_meta(caminho_config=CAMINHO_CONFIG):
	"""Registra o pedido do usuário para excluir a meta atual."""
	config = carregar_config(caminho_config)

	if config["meta_ativa"] is None:
		raise ValueError("Não existe uma meta para excluir.")

	config["solicitacao_exclusao"] = {
		"status": "pendente",
		"meta": config["meta_ativa"],
	}
	config["meta_ativa"]["status"] = "exclusao_solicitada"
	salvar_config(config, caminho_config)
	return config["solicitacao_exclusao"]


def confirmar_exclusao_meta(caminho_config=CAMINHO_CONFIG):
	"""Confirma o pedido e remove a meta do arquivo de configuração."""
	config = carregar_config(caminho_config)

	if config["solicitacao_exclusao"] is None:
		raise ValueError("Não existe uma solicitação de exclusão pendente.")

	config["meta_ativa"] = None
	config["solicitacao_exclusao"] = None
	salvar_config(config, caminho_config)
	return config

