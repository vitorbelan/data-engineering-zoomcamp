# Orquestração do workflow
Utilizaremos a orquestração com o merge, um framework hibrido ee decodigo aberto para transformação e integração de dados. [Documentação](https://docs.mage.ai/introduction/overview)

Bibliografia Understanding ETL Data pipelines for modern data architectures

A ideia final desta estapa é pegar um dataset, o exemplo do taxi de nova york continua o mesmo, fazer algumas transformaçoes carregar no postgrees,no google cloud storage, depois fazer mais algumas transformaçoes usando apacche arrow, pandas sql e carregar no big querry

## Arquitetura
Extrair
    - Pegar dados de uma fonte (API - NYC TAXI DATASET)
Transform
    - Data cleaning, transformation e partitioning
Load
    - Api to mage, Mage to PostGRES, GCS, BigQuery

## O que é orchestration?
É um processo de gerenciamento de dependências, facilitado por processos de atuomação
O orquestrador de dados gerencia: agendamento, acionamento, monitoramento e até mesmo alocação de recursos.
Todo workflow requer passos sequenciais
Transformações mal sequenciadas criam uma tempestade muito mais amarga.
#### Com o que se parece um bom orquestrador
    * Gerenciamento do workflow
    * Automação
    * Error handling
    * Recovery
    * Monitoramento e alerta
    * Otimizacao de recursos
    * Observabilidade (enxergar cada parte do pipeline)
    * Debugging
    * Auditoria e Compliance
# O que é o Mage
Uma ferramenta de pipeline open source para orquestraçao transformacao e integraçao de dados
Conceito principal
    1 - Projeto
    2 - Pipeline
    3 - Blocos
    3.1. - Load
    3.2. - Transformacao
    3.3. - Exportacao

Ambiente Hibridos
    - Use o GUI para desenvolvimento interativo ou nao com o VSCODE
    - Use blocos como partes de código testáveis e reutilizáveis.
    - DevEx aprimorado
    - Codifique e teste em paralelo.
    - Reduza suas dependências, troque menos de ferramentas, seja eficiente
    - test e debug inline
# Conceitos principais
## um projeto
    * Um projeto forma a base para todo o trabalho que você pode fazer no Mage – você pode pensar nele como um repositório GitHub.
    * Ele contém o código de todos os seus pipelines, blocos e outros ativos.
    * Uma instância do Mage tem um ou mais projetos
## Pipelines
    * Um pipeline é um fluxo de trabalho que executa alguma operação de dados – talvez extrair, transformar e carregar dados de uma API. Eles também são chamados de DAGs em outras plataformas
    * No Mage, os pipelines podem conter blocos (escritos em SQL, Python ou R) e gráficos.
    * Cada pipeline é representado por um arquivo YAML na pasta “pipelines” do seu projeto.
## Block
    * Um bloco é um arquivo que pode ser executado de forma independente ou dentro de um pipeline.
    * Juntos, os blocos formam Gráficos Acíclicos Direcionados (DAGs), que chamamos de pipelines.
    * Um bloco não começará a ser executado em um pipeline até que todas as suas dependências upstream sejam atendidas.
    * Blocos são pedaços de código reutilizáveis que executam determinadas ações.
    * Alterar um bloco irá alterá-lo em todos os lugares em que for usado, mas não se preocupe, é fácil desanexar blocos em instâncias separadas, se necessário.
    * Os blocos podem ser usados para realizar uma variedade de ações, desde simples transformações de dados até modelos complexos de aprendizado de máquina.
    Sequencia basica da anatomia de um bloco
        * import das bibliotecas
        * identificador
        * Funcao que retorna um dataframe
        * Teste ou Assertion
# Configurando Mage
Iremos clonar um repositorio para o mage [link github](https://github.com/mage-ai/mage-zoomcamp);
    ```bash
    git clone https://github.com/mage-ai/mage-zoomcamp.git mage-zoomcamp
    ```

vá para o repositorio onde baixou

    ```bash
    cd mage-data-engineering-zoomcamp
    ```

renomei `dev.env para .env`, estranho que no video ele move o arquivo

    ```bash
    cp dev.env .env
    ```

Construa o container

    ```bash
    docker compose build
    ```

Start o container

    ```bash
    docker compose up
    ```

Para abrir o Mage vai no navegador e digite `http://localhost:6789` para abrir o mage