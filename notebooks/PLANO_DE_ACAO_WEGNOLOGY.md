# Plano de Ação: Migração para WEGnology Notebooks & Persistência de Dados

Este documento descreve o plano de ação, a metodologia técnica e o guia passo a passo para execução e persistência dos dados dos scripts Python do projeto **Hydranomic** dentro do ecossistema de **Jupyter Notebooks da WEGnology**.

---

## 1. Onde e Como Salvar Dados e JSONs na WEGnology?

A plataforma WEGnology (baseada na arquitetura Losant) executa Notebooks em containers isolados (Docker). Arquivos salvos na máquina local do container são temporários e descartados após o término da execução. Para que seus arquivos JSON e previsões persistam na plataforma, a WEGnology disponibiliza **3 destinos principais**:

### Destino 1: WEGnology Application Files (Storage de Arquivos) — *Recomendado para JSONs*
* **O que é:** O repositório persistente de arquivos da sua aplicação (`Application -> Files` no console da WEGnology).
* **Como funciona via Notebook:**
  1. A WEGnology injeta a variável de ambiente `OUTPUT_DIR` (geralmente `/outputs`).
  2. Qualquer arquivo que o Python salvar dentro de `OUTPUT_DIR` (ex: `OUTPUT_DIR/grafico_anual.json` ou `OUTPUT_DIR/previsao_ml.json`) fica disponível na aba **Outputs** da configuração do Notebook no portal.
  3. Na aba **Outputs** do Notebook na WEGnology, você mapeia a regra:
     * **Source File Name:** `grafico_anual.json`
     * **Output Type:** `Application File`
     * **Destination Path:** `/workflows/grafico_anual.json`
  4. Quando o notebook termina de rodar, o arquivo é automaticamente salvo e atualizado no Application Files.
* **Vantagens:**
  * Os Workflows da WEGnology podem ler esses arquivos a qualquer momento com nós **File: Read**.
  * As telas de Experience (HTML/CSS/JS das pastas `experience/`) e Dashboards podem carregar o JSON diretamente via requisição HTTP/fetch (`https://files.wnology.io/<APPLICATION_ID>/workflows/grafico_anual.json`).

---

### Destino 2: WEGnology Data Tables (Tabelas de Dados Relacionais)
* **O que é:** Tabelas estruturadas tipo banco de dados nativas da plataforma (`Application -> Data Tables`).
* **Como funciona:**
  * **Via Outputs Tab:** Salvar um arquivo `.csv` no `OUTPUT_DIR` e configurar o Output do Notebook para inserir/atualizar linhas na tabela correspondente.
  * **Via API REST (`wegnology-rest`):** Inserir registros programaticamente durante a execução da célula do notebook via chamada de API (`client.data_table_row.create(...)`).
* **Quando usar:** Quando quiser manter um histórico cumulativo de previsões ao longo dos meses para auditoria.

---

### Destino 3: Device State / Virtual Device (Telemetria para Dashboards)
* **O que é:** Dispositivo virtual (`Application -> Devices`) com atributos numéricos (ex: `previsao_m3`, `valor_fatura`, `status_meta`).
* **Como funciona:**
  * O notebook pode atualizar os atributos de um dispositivo virtual através da biblioteca `wegnology-rest`:
    ```python
    import wegnology_rest
    client = wegnology_rest.Client()
    client.auth_token = os.environ.get("WEGNOLOGY_API_TOKEN")
    client.device.send_state(
        deviceId="ID_DO_DISPOSITIVO_VIRTUAL",
        applicationId="ID_DA_APLICACAO",
        deviceState={"data": {"previsao_consumo_m3": 315.4, "valor_conta": 18797.84}}
    )
    ```
* **Vantagens:** Permite criar blocos de velocímetro (Gauge), gráficos temporais e cartões de valor instantâneo nos Dashboards nativos da WEGnology sem precisar de código front-end adicional.

---

## 2. Diagnóstico dos Scripts Originais (`notebooks/scripts/`)

| Script Original | Problemas Identificados para o WEGnology | Solução Implementada em `notebooks/jupyter/` |
| :--- | :--- | :--- |
| `data_chart.py` | Caminho fixo relativo em string (`hydranomic/workflows/...`), não lia dinamicamente do `INPUT_DIR` nem persistia o JSON gerado em `OUTPUT_DIR`. | Modularizado em `processar_dados_grafico()`, busca em `INPUT_DIR` (ou local) e salva `grafico_anual.json` no `OUTPUT_DIR`. |
| `machinelearning.py` | Código executava treino solto no escopo global ao ser importado; caminho fixo; previsões geradas em memória sem persistência em arquivo. | Encapsulado em pipeline completo: `preparar_dados()`, `treinar_modelo()`, `prever_proximo_ciclo()` e salvamento de `previsao_ml.json` no `OUTPUT_DIR`. |
| `metas.py` | Caminho relativo fixo via `Path(__file__)`, não adaptado a `INPUT_DIR` / `OUTPUT_DIR`, sem cálculo de progresso/alerta de consumo. | Integrado com `wegnology_adapter.py`, adicionada função `avaliar_progresso_meta()` gerando `progresso_meta.json`. |
| `app.py` | Execução síncrona manual fixa (`estado_atual = 1`), chamada incorreta a `gerar_dados_grafico()` sem argumentos. | Suporte a `context.json` do WEGnology, despacho por parâmetros ou modo completo (`tudo`), gerando `sumario_execucao.json`. |

---

## 3. Estrutura dos Arquivos Criados em `notebooks/jupyter/`

```
notebooks/jupyter/
├── wegnology_adapter.py        # Módulo utilitário central: gerencia INPUT_DIR, OUTPUT_DIR, context.json e salvamento
├── machinelearning.py          # Módulo ML refatorado (RandomForestRegressor + exportação de previsao_ml.json)
├── data_chart.py               # Módulo de gráficos refatorado (exportação de grafico_anual.json)
├── metas.py                    # Módulo de metas refatorado (exportação de config.json e progresso_meta.json)
├── app.py                      # Orquestrador adaptado com leitura de contexto e execução em lote
├── hydranomic_pipeline.ipynb   # NOTEBOOK MASTER: Pipeline de produção com células de visualização e persistência
├── machine_learning.ipynb      # NOTEBOOK DEDICADO: Treinamento, métricas (MAE, RMSE, R²) e predições
├── data_chart.ipynb            # NOTEBOOK DEDICADO: Teste e renderização da série de 12 meses
└── metas.ipynb                 # NOTEBOOK DEDICADO: Simulação e validação de regras de meta
```

---

## 4. Passo a Passo para Configurar e Executar no Portal WEGnology

### Passo 1: Criar o Notebook no Console WEGnology
1. No menu lateral da sua aplicação WEGnology, acesse **Notebooks** -> **Add Notebook**.
2. Dê um nome (ex: `Hydranomic Consumption Analytics`).
3. Faça upload do arquivo `notebooks/jupyter/hydranomic_pipeline.ipynb` (ou cole o conteúdo das células).
4. No campo de ambiente de execução, selecione o container Python padrão com suporte a `pandas`, `scikit-learn` e `matplotlib`.

### Passo 2: Configurar a Aba "Inputs" (Entradas de Dados)
Na configuração do seu Notebook:
1. Adicione um **Input**:
   * **Input Type:** `Application File`
   * **Source File:** `/workflows/conta_povoada.json` (ou `/workflows/conta.json`)
   * **Target File Name:** `conta_povoada.json`
2. *(Opcional)* Se utilizar metas ativas:
   * **Input Type:** `Application File`
   * **Source File:** `/workflows/config.json`
   * **Target File Name:** `config.json`

> **Nota:** Durante a execução, o WEGnology colocará esses arquivos automaticamente no diretório apontado por `INPUT_DIR`, e o `wegnology_adapter.py` os lerá sem nenhum esforço.

### Passo 3: Configurar a Aba "Outputs" (Salvamento dos Dados)
Na aba **Outputs**, configure onde os JSONs gerados deverão ser salvos:
1. **Gráfico Anual:**
   * **Output Type:** `Application File`
   * **Source File Name:** `grafico_anual.json`
   * **Destination Path:** `/workflows/grafico_anual.json`
2. **Previsão de ML:**
   * **Output Type:** `Application File`
   * **Source File Name:** `previsao_ml.json`
   * **Destination Path:** `/workflows/previsao_ml.json`
3. **Progresso de Metas:**
   * **Output Type:** `Application File`
   * **Source File Name:** `progresso_meta.json`
   * **Destination Path:** `/workflows/progresso_meta.json`

### Passo 4: Automatizar a Execução (Workflow ou Agendamento)
Você tem duas opções para disparar a execução:
* **Opção A (Agendada - Cron):** Na aba **Schedule** do Notebook, defina para rodar todo dia 1º de cada mês (ex: `0 0 1 * *`).
* **Opção B (Via Workflow de Aplicação):**
  * Utilize o nó **Notebook: Execute** dentro de um Workflow de Aplicação.
  * Você pode passar parâmetros dinâmicos no campo **Context** (ex: `{"ano_referencia": 2026, "tarifa": 62.5}`). O notebook os lerá automaticamente via `context.json`.

---

## 5. Como o Front-end e Workflows Consomem os Dados

Com os arquivos salvos em **Application Files**, o ecossistema do Hydranomic fica 100% integrado:
1. **Workflows:** Podem disparar alertas de e-mail/SMS ou acionar a válvula do firmware se `progresso_meta.json` indicar `ESTOURADA`.
2. **Experience Pages (`experience/`):**
   * Em `experience/relatorio.html` ou `experience/index.html`, o JavaScript do navegador pode requisitar o JSON diretamente:
     ```javascript
     fetch('/workflows/grafico_anual.json')
       .then(response => response.json())
       .then(dados => renderizarGrafico(dados));
     ```
3. **Dashboards WEGnology:** Podem usar blocos de **Custom HTML / Chart** lendo o endpoint dos Application Files.
