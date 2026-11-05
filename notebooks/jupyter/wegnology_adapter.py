import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

def obter_caminho_raiz() -> Path:
    for p in [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1], Path(__file__).resolve().parents[2]]:
        if (p / "workflows").is_dir() or (p / "hydranomic" / "workflows").is_dir():
            return p
    return Path.cwd()

def obter_diretorio_input() -> Path:
    if "INPUT_DIR" in os.environ and os.path.isdir(os.environ["INPUT_DIR"]):
        return Path(os.environ["INPUT_DIR"])
    raiz = obter_caminho_raiz()
    if (raiz / "workflows").is_dir():
        return raiz / "workflows"
    if (raiz / "hydranomic" / "workflows").is_dir():
        return raiz / "hydranomic" / "workflows"
    return Path.cwd()

def obter_diretorio_output() -> Path:
    if "OUTPUT_DIR" in os.environ:
        caminho = Path(os.environ["OUTPUT_DIR"])
        caminho.mkdir(parents=True, exist_ok=True)
        return caminho
    raiz = obter_caminho_raiz()
    caminho = raiz / "workflows" if (raiz / "workflows").is_dir() else raiz / "hydranomic" / "workflows"
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho

def resolver_caminho_entrada(nome_arquivo: str) -> Path:
    dir_input = obter_diretorio_input()
    candidatos = [
        dir_input / nome_arquivo,
        obter_caminho_raiz() / "workflows" / nome_arquivo,
        obter_caminho_raiz() / "hydranomic" / "workflows" / nome_arquivo,
        Path.cwd() / "workflows" / nome_arquivo,
        Path.cwd() / "hydranomic" / "workflows" / nome_arquivo,
        Path.cwd() / nome_arquivo
    ]
    for c in candidatos:
        if c.exists():
            return c
    return dir_input / nome_arquivo

def resolver_caminho_saida(nome_arquivo: str) -> Path:
    dir_output = obter_diretorio_output()
    return dir_output / nome_arquivo

def carregar_json(nome_arquivo: str, padrao: Any = None) -> Any:
    caminho = resolver_caminho_entrada(nome_arquivo)
    if not caminho.exists() or caminho.stat().st_size == 0:
        if padrao is not None:
            return padrao
        raise FileNotFoundError(f"Arquivo {nome_arquivo} nao encontrado em {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(nome_arquivo: str, dados: Any, indent: int = 2) -> Path:
    caminho = resolver_caminho_saida(nome_arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=indent)
    return caminho

def carregar_contexto() -> Dict[str, Any]:
    try:
        return carregar_json("context.json", padrao={})
    except Exception:
        return {}
