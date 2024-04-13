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
    2 - Pipeline s
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
    docker pull mageai/mageai:latest
    ```

Start o container

    ```bash
    docker compose up
    ```

Para abrir o Mage vai no navegador e digite `http://localhost:6789` para abrir o mage

# Configurando o PostGres com o Mage
Estaremos alterando as configuracoes do arquivo por questo de seguranca pra que ele pegue as variaveis de ambiente no caso locamente sem que facamos a subida dessas variavies pro git, ja que estaremos colocando o arquivo que a contem dentro do gitignore


Na GUI do mage va em files e coloque em ultimo a seguinte configuracao pra que ele tbm pegue os dados de conexao via arquivo de config_yaml

```bash
dev:
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: "{{ env_var('POSTGRES_DBNAME') }}"
  POSTGRES_SCHEMA: "{{ env_var('POSTGRES_SCHEMA') }}"
  POSTGRES_USER: "{{ env_var('POSTGRES_USER') }}"
  POSTGRES_PASSWORD: "{{ env_var('POSTGRES_PASSWORD') }}"
  POSTGRES_HOST: "{{ env_var('POSTGRES_HOST') }}"
  POSTGRES_PORT: "{{ env_var('POSTGRES_PORT') }}"
```
## pra testarmos a conexao
* vamos criar uma pipeline teste
    Abra o mage localmente e `http://localhost:6789/pipelines `e crie uma nova pipelina `New->Standart(Batch):`
* crie uma data loader a partir de uma query SQL `SQL Data Loader`
* Selecione uma conexao (PostgreSQL), o perfil (dev) e "Use a raw SQL"
* Rode um simples select `SELECT 1;` somente para testar  a conexao

# Escrevendo uma simples pipeline de ingestao API de ingestao para o postegres
Aqui iremos ler um arquivo a partir de um dado endereco no caso de uma url.
Depois iremos fazer o tratamento dos dados, ajustando os tipos de dados, removendo dados que nao aparentam ser uteis
Por ultimo enviaremos os dados para uma tabela no postgres

***leitura***

```bash
    import io
    import pandas as pd
    import requests
    if 'data_loader' not in globals():
        from mage_ai.data_preparation.decorators import data_loader
    if 'test' not in globals():
        from mage_ai.data_preparation.decorators import test


    @data_loader
    def load_data_from_api(*args, **kwargs):
        """
        Template for loading data from API
        """
        url_yellow_taxi = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'
        url_green_taxi = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz'

        taxi_dtypes = {
            'VendorID': 'Int64',
            'store_and_fwd_flag': 'str',
            'RatecodeID': 'Int64',
            'PULocationID': 'Int64',
            'DOLocationID': 'Int64',
            'passenger_count': 'Int64',
            'trip_distance': 'float64',
            'fare_amount': 'float64',
            'extra': 'float64',
            'mta_tax': 'float64',
            'tip_amount': 'float64',
            'tolls_amount': 'float64',
            'ehail_fee': 'float64',
            'improvement_surcharge': 'float64',
            'total_amount': 'float64',
            'payment_type': 'float64',
            'trip_type': 'float64',
            'congestion_surcharge': 'float64'
        }

        parse_dates_green_taxi = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']
        parse_dates_yellow_taxi = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']

        return pd.read_csv(url_yellow_taxi, sep=',', compression='gzip', dtype=taxi_dtypes, parse_dates=parse_yellow_green_taxi)


    @test
    def test_output(output, *args) -> None:
        """
        Template code for testing the output of the block.
        """
        assert output is not None, 'The output is undefined'

``` 

***tratamento***
```bash
    def transform(data, *args, **kwargs):
        # PRINT COUNTS OF RECORDS WITH 
        print(f"Preprocessing: rows with zero passengers:{data['passenger_count'].isin([0]).sum()}")

        # RETURN FILTERED DATA SET
        return data[data['passenger_count']>0]

    @test
    # CHECK THAT THERE ARE NO RECORDS WITH 0 PASSENGER COUNT
    def test_output(output, *args):
        assert output['passenger_count'].isin([0]).sum() ==0, 'There are rides with zero passengers'
```

***Export dos dados***

```bash
    from mage_ai.settings.repo import get_repo_path
    from mage_ai.io.config import ConfigFileLoader
    from mage_ai.io.postgres import Postgres
    from pandas import DataFrame
    from os import path

    if 'data_exporter' not in globals():
        from mage_ai.data_preparation.decorators import data_exporter

    @data_exporter
    def export_data_to_postgres(df: DataFrame, **kwargs) -> None:

        schema_name = 'ny_taxi'  # Specify the name of the schema to export data to
        table_name = 'yellow_taxi_data'  # Specify the name of the table to export data to
        config_path = path.join(get_repo_path(), 'io_config.yaml')
        config_profile = 'dev'

        with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
            loader.export(
                df,
                schema_name,
                table_name,
                index=False,  # Specifies whether to include index in exported table
                if_exists='replace',  # Specify resolution policy if table name already exists
            )

```

# Configurando o GoogleBIgQuery no Mage
