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

***Checagem***
pra checar fazer uma conexao com o data loader em sql postgree e dar um select na base que criamos.

# Configurando o GoogleBIgQuery no Mage
Agora vamos usar a cloud pra fazer o mesmo processo. Precisamos fazer algumas conexoes e etapas de autenticacao
[este e o video base](https://www.youtube.com/watch?v=00LP360iYvE&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=24)

* `Primeiro passo` Caso nao tenha criar um google cloud bucket
    - Criar uma google storage file system para o Mage
    
```bash
Adicionar um Google Cloud Bucket
Crie um cloud storage file system  em nuvem para o Mage interagir.
Na página de buckets de armazenamento em nuvem, clique em criar

    Defina um nome unico globalmente
    Location - escolha a regiao (Multi-region = EU) 
    Storage Class - mantenha o padrao 'standard'
    Access Control - mantenha o padrao de 'Uniform' e garante que 'Enforce public access prevention' esta selecionado
    Protection - none

```


* `Segundo passo` Adicionar uma conta de serviço Mage
Crie uma nova conta de serviço que o mage possa usar para se conectar ao projeto do GCP.
```bash
    Na pagina service account page, click 'create a new service account'
    Entre com um nome
    Set the role to Basic > Owner. Isto permite editar tudo no GCS and BigQuery. Voce talvez va querer algo mais restritivo
    Click Continue and Done
```
* `Terceito passo` Crie uma chave
```bash
    Clique na conta de serviço que acabou de ser criada
    Vá para a guia chaves e selecione `Add Key > Create new key`
    Select JSON e click Create. O arquivo JSON com as credenciais sera salvo no pc
    MOva a chave para o diretorio onde o Maje esta alocado. Este diretorio sera montado como um volume no container mage. `:/home/src/` faz as credenciais acessiveis ao container fazendo com que o Mage possa se conectar ao google
```


* `Quarto passo` autenticar usando credenciais

     Volte para o Mage para o arquivo io_config.yaml
     Existem 2 maneiras de configurar a autenticação neste arquivo
         Copie e cole todos os valores do arquivo de chave JSON nas variáveis GOOGLE_SERVICE_ACC_KEY
         OU Use o GOOGLE_SERVICE_ACC_KEY_FILEPATH (preferencial)
```bash
    # Google
    GOOGLE_SERVICE_ACC_KEY:
        type: service_account
        project_id: project-id
        private_key_id: key-id
        private_key: "-----BEGIN PRIVATE KEY-----\nyour_private_key\n-----END_PRIVATE_KEY"
        client_email: your_service_account_email
        auth_uri: "https://accounts.google.com/o/oauth2/auth"
        token_uri: "https://accounts.google.com/o/oauth2/token"
        auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email"
```
ou

```bash

    # Google
    GOOGLE_SERVICE_ACC_KEY_FILEPATH: "/home/src/key_file_name.json"

```

Agora teste a conexao com o bigquery usando um dataloader e uma query simples.

* Aqui ao invez de usar a query simples vamo rodar o `Example Pipeline` rodando a ultima caixinha `all upstream blocks` e ira escrever o arquivo `titanic_clean.csv`.
* Agora abra o googlecloud -> cloud storage `Buckets` -> Abra o nome do bucket name unico criado e arreste o csv
* Agora abra outro dataloader python -> google_cloud_storage no Mage, entre com o `bucket_name` e o nome do arquivo `titanic_clean.csv`

# ETL com API para GCS - Google Cloud Storage
Nesta secao iremos gravar dados no GoogleClous storage. Anteriormente ja haviamos gravado dados no postgres que e um banco de dados relacional, quanto que GCS 'e um sistema de arquivos em nuvem.

* Vamos criar um novo pipeline, que inclusive ja utilizamos anteriormente. Para isso va em new pipeline e arraste `` 

# Worflow com o Airflow
Aqui com o intuito de abordarmos uma outra tecnologia, o Airflow, e muito conhecida no mercado, mostraremos o uso do Apache Airflow, um orquestrador openSOurce que foi abordado no ano de 2022. Aqui o [link](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion) da ementa do foi e sera resumido aqui.

## O que ẽ um datalake
Data Lake é um repositórrio central de dados que armazena dados em grandes quantidade de diversas fontes, or recursos do datalake:
    * Ingere dados Estruturados
    * Ingere dados Nao estruturados
    * Armazena, protege dados em escala ilimitada
    * Nos permite acessar dados rapidamente sem pensar em esquemas (se nao cuidar pode virar um problemao)
Seu objetivo é armazenar o dado rapidamente e o tornar disponível para quem desejar usar.
O datalake deve ser seguro escalável

## Diferenca entre datalake e datawarehouse

* Processamento de dados:
    - *datalake* : dado bruto (raw) e geralmente com processamento minimo. E geralmente nao estruturado
    - *DataWarehouse* : dado ja tratado, e geralmente estruturado
* Tamanho
    - *datalake* : maior que o datawarehouse na ordem de petabytes , o dado geralmente fica armazenado e so e processado ao ser utilizado
    - *DataWarehouse* : usualmente menor que os datalakes o dado é sempre pre processado antes da ingestão
* Natureza do dado
    - *datalake* : schema geralmente nao é definido e usaod em uma grande variedade de processos
    - *DataWarehouse* : schema definido, dados históricos e relacionais
* Usuários e uso dos daods
    - *datalake* : geralmente cientistas de dados, analistas de dados, processos em streaming batch analises em tempo real ou near-real-time
    - *DataWarehouse* : geralmente batch, business inteligence, reportes

## ELT VS ETL
A diferença geralmente é que o ETL (extract transform and load) geralmente é aplicado em DWs enquanto que o ELT geralmente é aplicado em datalakes

## Problemas em um datalake
- virar um pantano de dados
    - dados sem versionamentos  
    - schemas incompativeis para o mesmo tipo de dado

## Data Lake Cloud Providers
- Google Cloud Platform > Cloud Storage
- Amazon Web Services > Amazon S3
- Microsoft Azure > Azure Blob Storage

# Workflow orquestration (Orquestramento do fluxo de trabalho)
Um datapipeline pode ser definido como um/uns scripts pegam o dado de alguma fonte, realizam algum tipo de tratamento e exportam para algum lugar.

O primeiro pipeline foi um exemplo rapido de aplicaçao mas que nao segue boas praticas:
    - ele basicamente era um codigo unico de extração tratamento e exportacao
Poderiamos melhorar o codigo quebrando em etapas como:
```bash
1 - Extração do csv com wget` 
2 - ingestao, tratamento e output
```
    - A melhoria nessa etapa seria que nao precisariamos baixar toda vez o arquivo e depois ingerir processar e escrever tudo
Mas aqui usando o Airflow pensaremos no seguinte fluxo:
```bash
1 - Extração do csv com wget
2 - Transformando csv em parquet
3 - Upando o arquivo para o GCS
4 - Exportar para Big Query
5 - Tabela no BigQuery
```

# AirFlow
Uma plataforma para monitorar e programar workflows como DAGS. O seu uso pode ser tanto via linha de comando quanto via UI, para monitorar pipelines, progressos e problemas.

## Arquitetura
* `WebServer/UI` que serve para inspecionar, schedular e monitorar pipelines diponivel no [https://localhots:8080)](https://localhots:8080)
* `Scheduler` Responsavel por schedular os jobs
* `Worker` Executa as tasks dada pelo scheduler
* `Metadata Database` Usado pelo werserve scheduler e worker para armazenar dados. Contem todo o historico de execuçao de cada DAG e Task assim como a configuraçao do Airflow
* `DAG` Directly acyclic Graph, especifica a dependência entre um conjunto de task com uma ordem de execuçao determinada
- Tasks: Uma unidade de trabalho definida. As próprias Tarefas descrevem o que fazer, seja buscar dados, executar análises, acionar outros sistemas ou mais. Tipos de tarefas comuns são:
    - oPERATORS (usados neste workshop) são tarefas predefinidas. Eles são os mais comuns.
    - Sensors são uma subclasse de operador que aguardam eventos externos.
    - TaskFlow decorators  (subclasses do BaseOperator do Airflow) são funções Python personalizadas empacotadas como tarefas.
* `flower`- Flower app para monitorar o ambiente. Disponivel at http://localhost:5555.

## Executando o Airflow com o docker
Os requisitos pra rodarmos o airflow com o docker provavelmente ja temos das semanas anteriores que são:
    - Docler IO
    - COnfigurara docker instance para 5GB (recomendado seria 8gb), caso use o docker desktop ir em *Preferencias -> Resources*
    - Instalar Docker Compose

## Airflow Setup
* Crie um subdiretorio no projeto chamado de `airflow`
* baixe a imagem atualizada do airflow
 ``` bash
 curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.2.3/docker-compose.yaml'\
 ```
    - [Aqui](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) tem o link com a documentacao oficial para rodar o airflow num container a quantiade de serviços descritas pode ser demais num primeiro momento, caso queira testar um docker compose mais readblw [neste link](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2022/week_2_data_ingestion/airflow/docker-compose-nofrills.yml) tem o yamml do docker compose pra uma versao mais lite do airflow


* Configure o `Airflow User`
    No linux o quick start precisa saber seu host user-id e precisa que o grupo seja ajustado para 0. Caso contrario os arquivos criados nos dags, logs, plugins serão criados com o usuário root tenha certeza de fazer a configuraçao para o docker compose

```bash
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
    usuários de MACos ou caso apareça uma mennsagem `("AIRFLOW_UID is not set")` crie um arquivo `.env` no mesmo diretorio do `docker-compose.yaml` como este conteudo

```bash
AIRFLOW_UID=50000
```

* Docker Build
     - no arquivo do docker-compose.yaml na seção build ele deve vir definindo a imagem, caso vá rodar localmente nao terá problemas, aqui só recomendadmos criar um arquivo txt `requirements.txt` e colocar as bibliotecas que precisara instalar.
     - caso vá rodar na cloud(GCP) na seçao build colocamos um contexto para ele chamar o arquivo `./Dockerfile` que estará na mesma pasta de destino. O arquivo /.DOckerfile, lã colocamos uma ferramenta que vai instalar o `gcloud` que vai conectar com o GCS bucket/data lake
     - lembre de colocar a variavel `AIRFLOW__CORE__LOAD_EXAMPLES: 'false'` para evitar de vir um monte de exemplo e gerar duvidas
     - Adicione um volume e aponte-o para a pasta onde você armazenou as credenciais do arquivo json. Supondo que você cumprisse os pré-requisitos e fosse movido e renomeado suas credenciais, adicione a seguinte linha após todos os outros volumes:

```bash
~/.google/credentials/:/.google/credentials:ro
```
    [link para outras variaveis](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#execution)

* Execucao
    -Construa a imagem, isso vai levar alguns minutos, porém voce só vai executar na primeira vez que rodar o Airflow ou se modificar o /Dockerfile ou o requirements.txt
```bash
    docker-compose build
```
Levante o container
```bash
docker-compose up airflow-init
```
Run Airflow
```bash
docker-compose up -d
```

agora voce pode acessar a GUI do airflow em `localhost:8080`. Com usuario e senha airflow
