"""
Módulo de Machine Learning para previsão de consumo de água e estimativa de fatura.
Utiliza RandomForestRegressor do scikit-learn.
Adaptado para a metodologia WEGnology / Jupyter Notebook.

Pode ser executado diretamente em uma célula do Jupyter Notebook,
por um script de automação, ou em lote dentro de um container WEGnology.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Garante que o diretório atual esteja no path para importar wegnology_adapter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto


NOME_ARQUIVO_ENTRADA = "conta_povoada.json"
NOME_ARQUIVO_SAIDA = "previsao_ml.json"
TARIFA_PADRAO = 59.6
ESTIMADORES_PADRAO = 250
RANDOM_STATE = 45


def carregar_dataframe(dados: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
    """Carrega os dados e converte para DataFrame do Pandas."""
    if dados is None:
        try:
            dados = carregar_json(NOME_ARQUIVO_ENTRADA)
        except FileNotFoundError:
            dados = carregar_json("conta.json", padrao=[])

    if not dados:
        raise ValueError("Nenhum dado encontrado para alimentar o modelo de Machine Learning.")

    df = pd.DataFrame(dados)
    return df


def preparar_dados(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], str]:
    """
    Higieniza, ordena e constrói as features temporais e de defasagem (lag).
    
    Features criadas:
    - mes: mês extraído do campo 'id' (formato AAAA-MM)
    - ano: ano extraído do campo 'id'
    - tempo_iniciofinal: contador cumulativo de meses desde a primeira medição
    - memoria_consumo: consumo do mês anterior (lag 1) agrupado por unidade consumidora
    """
    df = df.sort_values(by=["unidade_consumidora", "id"]).reset_index(drop=True)

    # Extrai ano e mês do campo 'id'
    df["ano"] = df["id"].astype(str).str.split("-").str[0].astype(int)
    df["mes"] = df["id"].astype(str).str.split("-").str[1].astype(int)

    ano_inicial = df["ano"].min()
    mes_inicial = df.loc[df["ano"] == ano_inicial, "mes"].min()

    # Tempo linear desde a primeira leitura
    df["tempo_iniciofinal"] = (df["ano"] - ano_inicial) * 12 + (df["mes"] - mes_inicial)

    # Cria variável de defasagem (memória de consumo do mês anterior)
    df["memoria_consumo"] = df.groupby("unidade_consumidora")["consumo_m3"].shift(1)

    # Remove primeiras linhas com NaN decorrentes do lag
    df_treino = df.dropna(subset=["memoria_consumo"]).copy()

    features_entrada = ["mes", "tempo_iniciofinal", "memoria_consumo"]
    variavel_saida = "consumo_m3"

    return df, df_treino, features_entrada, variavel_saida


def treinar_modelo(
    df_treino: pd.DataFrame,
    features_entrada: List[str],
    variavel_saida: str,
    n_estimators: int = ESTIMADORES_PADRAO,
    random_state: int = RANDOM_STATE
) -> RandomForestRegressor:
    """Treina o modelo RandomForestRegressor com os dados preparados."""
    x = df_treino[features_entrada]
    y = df_treino[variavel_saida]

    modelo = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    modelo.fit(x, y)
    return modelo


def prever_proximo_ciclo(
    modelo: RandomForestRegressor,
    df_completo: pd.DataFrame,
    features_entrada: List[str],
    tarifa: float = TARIFA_PADRAO
) -> Dict[str, Any]:
    """Calcula a previsão de consumo para o próximo mês e projeta o valor da fatura."""
    ultima_linha = df_completo.iloc[-1]

    ultimo_ano = int(ultima_linha["ano"])
    ultimo_mes = int(ultima_linha["mes"])
    ultimo_consumo = float(ultima_linha["consumo_m3"])
    ultimo_passo = int(ultima_linha["tempo_iniciofinal"])

    # Lógica de transição de ciclo (ano novo se mês 12)
    if ultimo_mes == 12:
        proximo_mes = 1
        proximo_ano = ultimo_ano + 1
    else:
        proximo_mes = ultimo_mes + 1
        proximo_ano = ultimo_ano

    proximo_passo = ultimo_passo + 1

    dados_previsao = pd.DataFrame(
        [[proximo_mes, proximo_passo, ultimo_consumo]],
        columns=features_entrada,
    )

    previsao_m3 = float(modelo.predict(dados_previsao)[0])
    valor_conta = round(previsao_m3 * tarifa, 2)

    return {
        "ano": proximo_ano,
        "mes": proximo_mes,
        "unidade_consumidora": int(ultima_linha["unidade_consumidora"]),
        "ultimo_consumo_registrado_m3": ultimo_consumo,
        "previsao_m3": round(previsao_m3, 2),
        "tarifa_m3": tarifa,
        "valor_estimado_conta": valor_conta,
        "modelo": "RandomForestRegressor",
    }


def executar_pipeline_ml(
    dados: Optional[List[Dict[str, Any]]] = None,
    tarifa: Optional[float] = None,
    salvar: bool = True,
    nome_arquivo_saida: str = NOME_ARQUIVO_SAIDA,
) -> Dict[str, Any]:
    """
    Executa o fluxo completo de Machine Learning:
    1. Carrega dados de entrada do INPUT_DIR (ou fallback local).
    2. Lê contexto do WEGnology (se houver parâmetro de tarifa ou n_estimators).
    3. Trata features e treina RandomForestRegressor.
    4. Gera previsão para o próximo ciclo de leitura.
    5. Salva o resultado no OUTPUT_DIR configurado.
    """
    contexto = carregar_contexto()

    if tarifa is None:
        tarifa = float(contexto.get("tarifa", TARIFA_PADRAO))

    df_bruto = carregar_dataframe(dados)
    df_completo, df_treino, features, alvo = preparar_dados(df_bruto)
    modelo = treinar_modelo(df_treino, features, alvo)
    resultado = prever_proximo_ciclo(modelo, df_completo, features, tarifa)

    if salvar:
        salvar_json(nome_arquivo_saida, resultado)

    return resultado


# Aliás para compatibilidade reversa com o app.py original
def iniciar_ml() -> Dict[str, Any]:
    """Ponto de entrada compatível com a chamada original de iniciar_ml()."""
    return executar_pipeline_ml()


if __name__ == "__main__":
    print("--- Executando Pipeline de Previsão de Machine Learning ---")
    previsao = executar_pipeline_ml()
    print("Resultado da Previsão:")
    for chave, valor in previsao.items():
        print(f"  {chave}: {valor}")
