
# 💧 Hydranomic 

## 1.Contextualização

O projeto consiste no desenvolvimento de um mecanismo de macromedição hídrica integrado a um sistema de monitoramento, capaz de medir a vazão, o volume de água consumido pelo estabelecimento e estipular uma previsão de consumo dos meses seguintes. A solução permitirá acompanhar o consumo, identificar possíveis vazamentos, reduzir desperdícios e estabelecer metas para otimizar o uso da água.

A proposta busca solucionar problemas relacionados ao consumo excessivo e ao desperdício de recursos hídricos, proporcionando maior controle e eficiência na gestão da água, além de contribuir para seu uso mais consciente e sustentável.

## 1.1 Objetivo do manual
Este manual tem como objetivo apresentar os procedimentos técnicos necessários para a instalação, configuração, utilização, manutenção e continuidade do desenvolvimento do Hydranomic.

São documentadas as tecnologias empregadas, a organização dos arquivos, os requisitos de funcionamento e a integração entre os módulos que compõem o sistema.

## 1.2 Público-alvo
O documento destina-se a desenvolvedores de software, técnicos de informática, profissionais responsáveis pela instalação, configuração e manutenção do sistema, além de administradores e coordenadores de instituições que buscam implementar nosso sistema.

## 1.4 Requisitos de conhecimento
Para acompanhar os procedimentos apresentados, recomenda-se conhecimento básico em:
- Lógica de programação;
- Linguagem C++;
- Desenvolvimento web (HTML, CSS e JavaScript);
- Linguagem Python;
- Sistemas embarcados e microcontroladores;
- Gerenciamento de dados e plataformas em nuvem.

## 2. ARQUITETURA DO SISTEMA
O Hydranomic é organizado em módulos integrados, cada um responsável por uma etapa do funcionamento do sistema.

| Módulo | Responsabilidade |
| :--- | :---: |
| Hardware | Coleta e transmissão das informações de consumo |
| Back-end | Processamento, gerenciamento e armazenamento dos dados | 
| Front-end | Apresentação das informações ao usuário | 
| Machine Learning | Apresentação das informações ao usuário | 

A comunicação entre esses componentes permite que as informações coletadas pelo dispositivo sejam encaminhadas para processamento e posteriormente disponibilizadas na interface de monitoramento.


<img width="427" height="136" alt="image" src="https://github.com/user-attachments/assets/afd03c93-ad9f-4113-9ad6-3510d079b607" />


----------------------------

## 3. TECNOLOGIAS UTILIZADAS
| Tecnologia | Finalidade |
| :--- | :---: |
| C++ | Programação do microcontrolador |
| ESP32 | Processamento e comunicação do hardware | 
| Wegnology | Gerenciamento de dados e workflows | 
| Python | Processamento e análise preditiva | 
| HTML5 | Estruturação das páginas | 
| CSS3 | Estilização da interface | 
| JavaScript | Funcionalidades e interatividade | 
| Bootstrap | Componentes e recursos visuais, quando utilizados | 

As versões específicas das ferramentas e bibliotecas devem ser registradas conforme o ambiente utilizado no desenvolvimento.

## 4. ESTRUTURA DO PROJETO
O código-fonte do Hydranomic está organizado em diretórios que separam as responsabilidades de cada módulo, facilitando a manutenção e a evolução do sistema.

A estrutura principal do repositório é composta por:
hydranomic/
│
├── assets/
├── experience/
├── firmware/
├── notebooks/
└── workflows/

Descrição dos diretórios:
- assets: reúne recursos utilizados pelo projeto, como imagens, arquivos gráficos e outros elementos de apoio.
- experience: contém os arquivos relacionados à experiência e à interface da aplicação na plataforma.
- firmware: armazena o código responsável pelo funcionamento do microcontrolador ESP32.
- notebooks: reúne os notebooks utilizados no desenvolvimento e na análise dos dados por meio de Python.
- workflows: contém os fluxos responsáveis pelo processamento e pela integração das informações na Wegnology.
A separação dos diretórios permite que cada módulo seja desenvolvido e mantido de maneira independente, respeitando sua função dentro da arquitetura geral.

## 5. REQUISITOS PARA INSTALAÇÃO
Para realizar a instalação e trabalhar com o código-fonte do Hydranomic, é necessário preparar um ambiente de desenvolvimento compatível com as tecnologias utilizadas.
## 5.1. Requisitos de hardware
Recomenda-se a utilização de um computador com:
- Sistema operacional Windows, Linux ou macOS;
- Conexão com a internet;
- Porta USB disponível para conexão com o ESP32;
- Memória RAM suficiente para executar as ferramentas de desenvolvimento;
- Microcontrolador ESP32 e componentes eletrônicos utilizados no projeto.
## 5.2. Softwares necessários
Software	Finalidade
Git	Obter e atualizar o código-fonte
Visual Studio Code	Editar e organizar os arquivos
Python	Executar os módulos de análise de dados
Arduino IDE ou PlatformIO	Desenvolver e carregar o firmware, conforme o ambiente utilizado
Navegador web	Acessar a interface do sistema
Wegnology	Acessar e gerenciar os recursos da plataforma

Observação: as versões e extensões específicas devem ser conferidas nos arquivos de configuração do repositório e no ambiente original de desenvolvimento.
## 6. INSTALAÇÃO E CONFIGURAÇÃO DO PROJETO
## 6.1. Obtenção do código-fonte
O primeiro procedimento consiste em obter os arquivos do projeto disponibilizados no GitHub.

1º passo — Instalar o Git
Acesse o site oficial do Git e realize o download da versão compatível com seu sistema operacional:

[Download Git](https://git-scm.com/install/?utm_source=chatgpt.com)

Após a instalação, abra o terminal e execute:
`git --version`

O comando permite verificar se o Git foi instalado corretamente.

2º passo — Clonar o repositório
Abra o terminal na pasta em que deseja armazenar o projeto e execute:
`git clone https://github.com/Hydranomic/hydranomic.git`

Esse comando realiza o download do repositório para o computador.

3º passo — Acessar a pasta
`cd hydranomic`

4º passo — Abrir o projeto no Visual Studio Code
Caso o Visual Studio Code esteja instalado, execute:
`code .`

Também é possível abrir o programa manualmente e selecionar a pasta hydranomic.
[Download VSCode](https://code.visualstudio.com/)

## 6.2. Configuração do ambiente Python
O módulo de análise preditiva utiliza Python para processamento e desenvolvimento dos modelos de Machine Learning.

1º passo — Instalar o Python
Acesse o site oficial e instale uma versão compatível com as dependências do projeto.

[Download do Python](https://www.python.org/downloads/?utm_source=chatgpt.com)

Durante a instalação no Windows, habilite a opção de adicionar o Python ao PATH, quando disponível.

2º passo — Verificar a instalação
No terminal, execute:
`python --version`

Em alguns ambientes Windows, também pode ser necessário utilizar:
`py --version`


3º passo — Criar um ambiente virtual
Dentro da pasta do projeto, execute:
`python -m venv venv`

O ambiente virtual permite manter as bibliotecas do projeto separadas das demais instalações do computador.

4º passo — Ativar o ambiente virtual
No Windows:
venv\Scripts\activate

No Linux ou macOS:
source venv/bin/activate

5º passo — Instalar as dependências
Caso exista um arquivo requirements.txt no módulo Python, execute:
`pip install -r requirements.txt`

Esse comando instala as bibliotecas listadas no arquivo.

Caso o arquivo não exista, as dependências deverão ser instaladas individualmente, de acordo com as importações utilizadas nos notebooks e códigos Python.
## 6.3. Configuração do ambiente de desenvolvimento do ESP32
O firmware é responsável pelo funcionamento do microcontrolador e pela comunicação dos dados coletados com a plataforma utilizada pelo sistema.

Caso o projeto utilize o ambiente Arduino, siga os procedimentos abaixo.

1º passo — Instalar a Arduino IDE

Acesse o site oficial:

[Download da Arduino IDE.](https://www.arduino.cc/en/software/?utm_source=chatgpt.com)

2º passo — Configurar a placa ESP32

Após abrir a IDE, acesse as preferências e localize o campo destinado às URLs adicionais do gerenciador de placas.
Adicione a URL oficial do pacote de placas ESP32, conforme a documentação da Espressif.

[Documentação oficial de instalação do ESP32](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html?utm_source=chatgpt.com)

3º passo — Instalar o pacote ESP32
- Abra o Gerenciador de Placas.
- Pesquise por ESP32.
- Instale o pacote disponibilizado pela Espressif.
- Aguarde a conclusão da instalação.

4º passo — Abrir o firmware
Localize a pasta firmware no repositório e abra o arquivo principal do programa na IDE compatível.

5º passo — Selecionar a placa
Conecte o ESP32 ao computador por meio de um cabo USB compatível.
Selecione a placa correspondente ao modelo utilizado e a porta de comunicação identificada pelo computador.

6º passo — Compilar e carregar o programa
Após verificar as configurações e as dependências do firmware, utilize a opção de compilação para verificar possíveis erros.
Estando tudo correto, realize o carregamento do programa para o microcontrolador.

Importante: esse procedimento é aplicável se o firmware tiver sido desenvolvido com Arduino. Se o repositório utilizar PlatformIO, a configuração deverá ser feita pelo arquivo platformio.ini e pelas ferramentas correspondentes.
## 6.4. Configuração da plataforma Wegnology
A Wegnology é utilizada como plataforma de gerenciamento e integração dos dados do sistema.

Para trabalhar com essa parte do projeto:
1. Acesse a plataforma Wegnology.
2. Entre na conta autorizada para o projeto.
3. Localize a aplicação correspondente ao Hydranomic.
4. Verifique a disponibilidade dos workflows e das configurações de dispositivos.
5. Confira as configurações de comunicação utilizadas pelo ESP32.
6. Verifique os recursos responsáveis pelo recebimento, processamento e armazenamento dos dados.
Acesse:

[Wegnology — Plataforma oficial](https://www.hugedomains.com/domain_profile.cfm?d=wegnology.com)

Atenção: o acesso aos recursos da aplicação depende das permissões concedidas à conta. Não compartilhe tokens, chaves de API ou credenciais de autenticação.
## 6.5. Execução da interface web
A interface web é responsável pela apresentação dos dados e pela interação com os usuários.
Como o projeto utiliza HTML, CSS e JavaScript, é necessário executar os arquivos em um ambiente que permita o carregamento correto dos recursos e das requisições da aplicação.

Procedimento:
1. Abra o Visual Studio Code.
2. Localize a pasta experience ou o diretório em que os arquivos da interface estão armazenados.
3. Identifique o arquivo HTML responsável pela página inicial.
4. Verifique se os caminhos dos arquivos CSS, JavaScript e imagens estão corretos.
5. Configure as integrações necessárias com a plataforma.
6. Inicie a aplicação utilizando o servidor de desenvolvimento previsto para o projeto.
Se a interface for composta por arquivos estáticos, sem um servidor próprio, é possível utilizar a extensão Live Server do Visual Studio Code para executá-la localmente.

Outra possibilidade é utilizar:
`python -m http.server 8000`

Depois, acesse no navegador:
`http://localhost:8000`

O endereço e a pasta inicial devem corresponder à localização dos arquivos da interface.

A execução local da interface não significa que o backend esteja funcionando. Para visualizar dados reais, a comunicação com a plataforma deve estar configurada e disponível.
## 7. UTILIZAÇÃO DO SISTEMA
## 7.1. Acesso à aplicação
O acesso ao Hydranomic é realizado por meio da interface web.

Para utilizar o sistema:
1. Abra o navegador de internet.
2. Acesse o endereço disponibilizado para a aplicação.
3. Aguarde o carregamento da página inicial.
4. Informe as credenciais de acesso fornecidas pelo responsável pelo sistema.
5. Selecione a opção de entrada para acessar o ambiente de monitoramento.
O acesso ao sistema pelos usuários é concedido pelo coordenador, a partir da criação de novos usuários no próprio sistema. 

## 7.2. Painel principal
Após a autenticação, o usuário é direcionado ao painel principal, no qual são disponibilizadas informações relacionadas ao monitoramento hídrico.

O painel concentra indicadores que permitem acompanhar o comportamento do consumo e consultar os dados disponibilizados pelo sistema.

Entre os indicadores e recursos previstos na interface estão:
- Vazão de água;
- Status do monitoramento;
- Volume de água consumido;
- Previsões de consumo;
- Metas de consumo;
- Indicadores financeiros relacionados ao consumo.

## 7.3. Monitoramento do consumo
A funcionalidade de monitoramento permite acompanhar as informações referentes à utilização de água pelo estabelecimento.
Os dados recebidos pelo sistema são processados e apresentados na interface por meio de indicadores e elementos gráficos.
O usuário pode consultar as informações disponibilizadas para acompanhar alterações no consumo e identificar possíveis comportamentos fora do padrão.

## 7.4. Visualização das previsões
O sistema também contempla um módulo de análise preditiva, desenvolvido com Python e técnicas de Machine Learning.
Esse recurso tem como finalidade analisar os registros disponíveis e produzir estimativas relacionadas ao comportamento futuro do consumo hídrico.
As previsões são apresentadas na interface para auxiliar o acompanhamento e o planejamento do consumo.

## 7.5. Acompanhamento das metas
A funcionalidade de metas permite acompanhar o consumo em relação aos objetivos estabelecidos para o estabelecimento.
Por meio dos indicadores apresentados, é possível verificar o progresso da meta e comparar o consumo registrado com o valor planejado.

## 7.6. Encerramento da sessão
Para encerrar o acesso ao sistema, o usuário deverá utilizar a opção de sair ou encerrar sessão disponibilizada na interface.
Esse procedimento finaliza a sessão autenticada e retorna o usuário à tela de acesso.

## 8. FUNCIONAMENTO DO HARDWARE
O módulo de hardware é responsável pela coleta das informações relacionadas ao fluxo de água.
O ESP32 atua como unidade de processamento e comunicação, recebendo os sinais provenientes dos componentes eletrônicos utilizados no mecanismo de medição.
Após a aquisição das informações, o firmware realiza o processamento necessário e encaminha os dados para a plataforma de gerenciamento.

[Diagrama eletrônico do sistema]<img width="417" height="257" alt="Captura de tela 2026-11-05 141052" src="https://github.com/user-attachments/assets/d921d807-66c0-4870-a308-63126caee441" />

## 8.1. Firmware
O firmware corresponde ao conjunto de instruções executadas pelo microcontrolador.
Sua implementação em C++ permite controlar os componentes eletrônicos e realizar as operações necessárias para o funcionamento do mecanismo de medição.
O código deve ser consultado no diretório firmware.

Para realizar modificações, recomenda-se:
1. Abrir os arquivos do firmware.
2. Identificar as configurações de comunicação.
3. Verificar as funções responsáveis pela aquisição dos dados.
4. Conferir as configurações de conexão.
5. Realizar as alterações necessárias.
6. Compilar e testar o programa.

## 8.2. Comunicação dos dados
Após a coleta, as informações são encaminhadas à plataforma responsável pelo processamento e gerenciamento.
A comunicação depende das configurações implementadas no firmware e dos recursos disponibilizados na Wegnology.


## 9. FUNCIONAMENTO DO BACKEND
O backend corresponde à parte responsável pelo processamento e gerenciamento das informações recebidas pelo sistema.
No Hydranomic, a plataforma Wegnology desempenha essa função por meio de recursos de integração, workflows e gerenciamento de dados.

## 9.1. Workflows
Os workflows representam fluxos de execução responsáveis por realizar operações específicas dentro da plataforma.
Eles permitem organizar as etapas de processamento e comunicação dos dados, de acordo com as regras estabelecidas durante o desenvolvimento.
Os arquivos relacionados aos workflows estão organizados no diretório workflows.

## 9.2. Processamento e armazenamento
Os dados recebidos são encaminhados para os recursos de processamento e armazenamento configurados na plataforma.
Essa etapa permite manter as informações disponíveis para consulta e utilização pelos demais módulos do sistema.

## 9.3. Integração com o frontend
A comunicação entre o backend e o frontend permite que as informações processadas sejam apresentadas na interface web.
Dessa maneira, os indicadores exibidos no dashboard dependem da disponibilidade dos dados e do funcionamento correto das integrações configuradas.

## 10. MÓDULO DE MACHINE LEARNING
O módulo de Machine Learning utiliza Python para desenvolver análises relacionadas ao comportamento do consumo hídrico.
Os arquivos desse módulo estão organizados no diretório notebooks.

## 10.1. Organização dos notebooks
Os notebooks permitem executar códigos Python de maneira organizada, facilitando a análise dos dados, a realização de testes e o desenvolvimento dos modelos.
Para trabalhar com esses arquivos, recomenda-se utilizar o Jupyter Notebook ou o JupyterLab, conforme as dependências do projeto.

## 10.2. Execução dos notebooks
Após configurar o ambiente Python e instalar as dependências necessárias, acesse a pasta dos notebooks pelo terminal.

Caso o Jupyter esteja instalado, execute:
`jupyter notebook`
Ou:
`jupyter lab`

O ambiente será disponibilizado no navegador, permitindo abrir os arquivos com extensão .ipynb.
Selecione o notebook desejado e execute as células na sequência indicada.

## 10.3. Análise preditiva
O processo de análise preditiva envolve a utilização de dados disponíveis para identificar padrões e estimar comportamentos futuros.
A implementação específica depende do modelo, das variáveis e dos procedimentos definidos nos notebooks do projeto.

## 11. MANUTENÇÃO DO SISTEMA
A manutenção tem como objetivo preservar o funcionamento adequado do Hydranomic, corrigindo possíveis falhas e garantindo a continuidade da comunicação entre seus componentes.

## 11.1. Atualização do código-fonte
Para obter as atualizações mais recentes disponibilizadas no repositório, execute:
`git pull origin main`
Esse comando atualiza os arquivos locais com as alterações presentes na branch principal do GitHub.

Antes de atualizar, recomenda-se verificar se existem modificações locais que ainda não foram salvas ou enviadas ao repositório.

## 11.2. Verificação do funcionamento
Recomenda-se realizar verificações periódicas nos seguintes componentes:
- ESP32 e componentes eletrônicos;
- Conexão de rede;
- Comunicação com a Wegnology;
- Execução dos workflows;
- Disponibilidade dos dados;
- Funcionamento da interface web;
- Execução do módulo de Machine Learning.
- 
## 11.3. Solução de problemas
| Problema identificado | Possível procedimento |
|---|---|
| Sistema não abre | Verificar o endereço de acesso e a conexão com a internet. |
| Falha no login | Conferir as credenciais e as permissões do usuário. |
| Dados não aparecem | Verificar a comunicação entre o ESP32 e a plataforma. |
| Informações desatualizadas | Conferir o recebimento e o processamento dos registros. |
| Falha na interface | Verificar os arquivos JavaScript e CSS, além das requisições realizadas no navegador. |
| Erro na execução do Python | Verificar o ambiente virtual e as dependências instaladas. |
| Firmware não carrega | Verificar a conexão USB, a placa selecionada e a porta de comunicação. |

## 12. SEGURANÇA E CONTROLE DE ACESSO
A segurança do sistema deve ser considerada durante sua instalação, utilização e manutenção.

Recomenda-se adotar as seguintes práticas:
- Não compartilhar credenciais de acesso.
- Não disponibilizar tokens ou chaves de API no código público.
- Conceder permissões somente aos usuários autorizados.
- Manter os ambientes e bibliotecas atualizados.
- Evitar alterações diretamente no ambiente de produção sem testes prévios.
- Realizar cópias de segurança dos arquivos e configurações importantes.
O gerenciamento dos usuários deve respeitar as permissões definidas para cada perfil dentro da aplicação.

## 13. CONSIDERAÇÕES FINAIS
O presente manual técnico reúne as principais orientações para compreender, instalar, configurar e manter o sistema Hydranomic.
A documentação da arquitetura, dos componentes eletrônicos, dos recursos de software e dos mecanismos de integração permite que futuros desenvolvedores tenham uma referência para realizar modificações, identificar possíveis problemas e dar continuidade ao desenvolvimento do projeto.
A manutenção desta documentação é importante para acompanhar futuras atualizações e garantir que as informações apresentadas permaneçam compatíveis com a implementação do sistema.

## 14. REFERÊNCIAS TÉCNICAS
- Repositório oficial do Hydranomic: [GitHub — Hydranomic.](https://github.com/Hydranomic/hydranomic?utm_source=chatgpt.com)
- Git — [Documentação oficial.](https://git-scm.com/docs?utm_source=chatgpt.com)
- Visual Studio Code — [Documentação.] 
- Python — [Documentação oficial.](https://www.python.org/doc/?utm_source=chatgpt.com)
- Espressif — [Documentação ESP32.](https://docs.espressif.com/projects/arduino-esp32/en/latest/?utm_source=chatgpt.com)
- Wegnology — [Plataforma oficial.](https://www.hugedomains.com/domain_profile.cfm?d=wegnology.com)
