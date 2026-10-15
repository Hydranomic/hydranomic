"""
Módulo utilitário para adaptação ao ecossistema de Notebooks da WEGnology / Losant.

Detecta automaticamente se a execução está ocorrendo dentro do container
da plataforma WEGnology (via variáveis de ambiente INPUT_DIR e OUTPUT_DIR)
ou em ambiente local (desenvolvimento / VS Code / Jupyter local).
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


def obter_caminho_raiz() -> Path:
    """Retorna o caminho raiz do repositório/projeto."""
    # Como este arquivo fica em notebooks/jupyter, subimos 2 níveis
    return Path(__file__).resolve().parents[2]


def obter_diretorio_input() -> Path:
    """
    Retorna o diretório de entrada para leitura de dados.
    No WEGnology Container: os.environ.get('INPUT_DIR') (geralmente /inputs)
    No ambiente Local: pasta workflows/ ou notebooks/scripts/
    """
    if "INPUT_DIR" in os.environ and os.path.isdir(os.environ["INPUT_DIR"]):
        return Path(os.environ["INPUT_DIR"])
    
    # Fallback local: pasta workflows na raiz do repositório
    raiz = obter_caminho_raiz()
    caminho_workflows = raiz / "workflows"
    if caminho_workflows.is_dir():
        return caminho_workflows
    
    return Path(".")


def obter_diretorio_output() -> Path:
    """
    Retorna o diretório de saída para gravação de artefatos.
    No WEGnology Container: os.environ.get('OUTPUT_DIR') (geralmente /outputs)
    No ambiente Local: pasta workflows/ na raiz
    """
    if "OUTPUT_DIR" in os.environ:
        caminho = Path(os.environ["OUTPUT_DIR"])
        caminho.mkdir(parents=True, exist_ok=True)
        return caminho

    # Fallback local: pasta workflows na raiz do repositório
    raiz = obter_caminho_raiz()
    caminho_workflows = raiz / "workflows"
    caminho_workflows.mkdir(parents=True, exist_ok=True)
    return caminho_workflows


def resolver_caminho_entrada(nome_arquivo: str) -> Path:
    """
    Localiza o arquivo de entrada buscando na seguinte ordem:
    1. INPUT_DIR (definido pelo WEGnology)
    2. workflows/<nome_arquivo> (relativo à raiz)
    3. Diretório atual de trabalho
    """
    # 1. Tentar INPUT_DIR
    dir_input = obter_diretorio_input()
    candidato = dir_input / nome_arquivo
    if candidato.exists():
        return candidato

    # 2. Tentar workflows na raiz
    raiz = obter_caminho_raiz()
    candidato = raiz / "workflows" / nome_arquivo
    if candidato.exists():
        return candidato

    # 3. Tentar caminho relativo direto
    candidato = Path(nome_arquivo)
    if candidato.exists():
        return candidato

    # Retorna o caminho em INPUT_DIR como padrão
    return dir_input / nome_arquivo


def resolver_caminho_saida(nome_arquivo: str) -> Path:
    """Retorna o caminho de saída no OUTPUT_DIR do WEGnology ou pasta local."""
    dir_output = obter_diretorio_output()
    return dir_output / nome_arquivo


def carregar_json(nome_arquivo: str, padrao: Any = None) -> Any:
    """Lê um arquivo JSON do ambiente de entrada do WEGnology ou local."""
    caminho = resolver_caminho_entrada(nome_arquivo)
    if not caminho.exists() or caminho.stat().st_size == 0:
        if padrao is not None:
            return padrao
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(nome_arquivo: str, dados: Any, indent: int = 2) -> Path:
    """
    Grava os dados em formato JSON no OUTPUT_DIR do WEGnology.
    Qualquer arquivo gravado no OUTPUT_DIR pode ser automaticamente
    persistido nos 'Application Files' ou 'Data Tables' do WEGnology
    configurados na aba 'Outputs' do Notebook.
    """
    caminho = resolver_caminho_saida(nome_arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=indent)

    print(f"[WEGnology Output] Arquivo salvo com sucesso em: {caminho}")
    return caminho


def carregar_contexto() -> Dict[str, Any]:
    """
    Carrega o arquivo context.json injetado pelo WEGnology quando o
    notebook é acionado por um Workflow (nó Notebook: Execute).
    """
    try:
        return carregar_json("context.json", padrao={})
    except Exception:
        return {}


def enviar_estado_dispositivo(
    device_id: str,
    dados_estado: Dict[str, Any],
    app_id: Optional[str] = None,
    api_token: Optional[str] = None
) -> bool:
    """
    Opcional: Envia telemetria diretamente para a API REST do WEGnology
    usando a biblioteca wegnology-rest (se disponível e com credenciais).
    """
    try:
        import wegnology_rest
        
        token = api_token or os.environ.get("WEGNOLOGY_API_TOKEN")
        application_id = app_id or os.environ.get("WEGNOLOGY_APP_ID")

        if not token:
            print("[WEGnology API] Token de API não configurado. Pulando envio direto via REST.")
            return False

        client = wegnology_rest.Client()
        client.auth_token = token
        resposta = client.device.send_state(
            deviceId=device_id,
            applicationId=application_id,
            deviceState={"data": dados_estado}
        )
        print(f"[WEGnology API] Estado enviado ao dispositivo {device_id}: {resposta}")
        return True
    except ImportError:
        print("[WEGnology API] Pacote 'wegnology-rest' não instalado. O resultado foi mantido em arquivo JSON.")
        return False
    except Exception as e:
        print(f"[WEGnology API] Erro ao enviar estado para o dispositivo: {e}")
        return False
