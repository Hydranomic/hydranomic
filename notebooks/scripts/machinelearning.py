import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wegnology_adapter import carregar_json, salvar_json, carregar_contexto

NOME_ARQUIVO_ENTRADA = "conta_povoada.json"
NOME_ARQUIVO_SAIDA = "previsao_ml.json"
TARIFA_PADRAO = 59.6
ESTIMADORES_PADRAO = 250
RANDOM_STATE = 45

def carregar_dataframe(dados: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
    if dados is None:
        try:
            dados = carregar_json(NOME_ARQUIVO_ENTRADA)
        except Exception:
            dados = carregar_json("conta.json", padrao=[])
    if not dados:
        raise ValueError("Dados insuficientes para treino do modelo.")
    return pd.DataFrame(dados)

def preparar_dados(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], str]:
    df = df.sort_values(by=["unidade_consumidora", "id"]).reset_index(drop=True)
    df["ano"] = df["id"].astype(str).str.split("-").str[0].astype(int)
    df["mes"] = df["id"].astype(str).str.split("-").str[1].astype(int)
    ano_inicial = df["ano"].min()
    mes_inicial = df.loc[df["ano"] == ano_inicial, "mes"].min()
    df["tempo_iniciofinal"] = (df["ano"] - ano_inicial) * 12 + (df["mes"] - mes_inicial)
    df["memoria_consumo"] = df.groupby("unidade_consumidora")["consumo_m3"].shift(1)
    df_treino = df.dropna(subset=["memoria_consumo"]).copy()
    features_entrada = ["mes", "tempo_iniciofinal", "memoria_consumo"]
    variavel_saida = "consumo_m3"
    return df, df_treino, features_entrada, variavel_saida

def treinar_modelo(df_treino: pd.DataFrame, features_entrada: List[str], variavel_saida: str, n_estimators: int = ESTIMADORES_PADRAO, random_state: int = RANDOM_STATE) -> RandomForestRegressor:
    x = df_treino[features_entrada]
    y = df_treino[variavel_saida]
    modelo = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    modelo.fit(x, y)
    return modelo

def prever_proximo_ciclo(modelo: RandomForestRegressor, df_completo: pd.DataFrame, features_entrada: List[str], tarifa: float = TARIFA_PADRAO) -> Dict[str, Any]:
    ultima_linha = df_completo.iloc[-1]
    ultimo_ano = int(ultima_linha["ano"])
    ultimo_mes = int(ultima_linha["mes"])
    ultimo_consumo = float(ultima_linha["consumo_m3"])
    ultimo_passo = int(ultima_linha["tempo_iniciofinal"])
    if ultimo_mes == 12:
        proximo_mes = 1
        proximo_ano = ultimo_ano + 1
    else:
        proximo_mes = ultimo_mes + 1
        proximo_ano = ultimo_ano
    proximo_passo = ultimo_passo + 1
    dados_previsao = pd.DataFrame([[proximo_mes, proximo_passo, ultimo_consumo]], columns=features_entrada)
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
        "data_treinamento": datetime.now().isoformat(),
        "data_treinamento_formatada": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

def executar_pipeline_ml(dados: Optional[List[Dict[str, Any]]] = None, tarifa: Optional[float] = None, salvar: bool = True, nome_arquivo_saida: str = NOME_ARQUIVO_SAIDA) -> Dict[str, Any]:
    contexto = carregar_contexto()
    if tarifa is None:
        tarifa = float(contexto.get("tarifa", TARIFA_PADRAO))
    hoje = datetime.now()
    data_treinamento = hoje.isoformat()
    data_formatada = hoje.strftime("%d/%m/%Y %H:%M:%S")

    try:
        df_bruto = carregar_dataframe(dados)
        df_completo, df_treino, features, alvo = preparar_dados(df_bruto)
        modelo = treinar_modelo(df_treino, features, alvo)
        resultado = prever_proximo_ciclo(modelo, df_completo, features, tarifa)
    except Exception as e:
        df_bruto = pd.DataFrame(dados) if dados else pd.DataFrame()
        media_consumo = float(df_bruto["consumo_m3"].mean()) if not df_bruto.empty and "consumo_m3" in df_bruto.columns else 300.0
        ultimo_val = float(df_bruto.iloc[-1]["consumo_m3"]) if not df_bruto.empty and "consumo_m3" in df_bruto.columns else media_consumo
        uc = int(df_bruto.iloc[-1]["unidade_consumidora"]) if not df_bruto.empty and "unidade_consumidora" in df_bruto.columns else 14079
        mes_prox = (hoje.month % 12) + 1
        ano_prox = hoje.year if hoje.month < 12 else hoje.year + 1
        previsao_fallback = round((media_consumo + ultimo_val) / 2.0, 2)
        resultado = {
            "ano": ano_prox,
            "mes": mes_prox,
            "unidade_consumidora": uc,
            "ultimo_consumo_registrado_m3": round(ultimo_val, 2),
            "previsao_m3": previsao_fallback,
            "tarifa_m3": tarifa,
            "valor_estimado_conta": round(previsao_fallback * tarifa, 2),
            "modelo": "Fallback_MediaMovel",
            "aviso": str(e),
            "data_treinamento": data_treinamento,
            "data_treinamento_formatada": data_formatada
        }

    if salvar:
        salvar_json(nome_arquivo_saida, resultado)
    return resultado

def iniciar_ml() -> Dict[str, Any]:
    return executar_pipeline_ml()

if __name__ == "__main__":
    executar_pipeline_ml()