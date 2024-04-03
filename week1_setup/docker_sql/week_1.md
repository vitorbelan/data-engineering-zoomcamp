# Introducao ao docker

# Docker
- é um software de containerizacao que nos permite  isolar aplicacoes e recursos dentro da máquina host
- Docker image 
  - é um determinado software/sistema operacional/ que usamos para criar um container
- Isolamento
  - conteinerizacao das imagens permite que o que é feito dentro de um container nao impacte na maquina host ou em outros container e viceversa

Exemplos de comandos:
  - docker containre run -it ubuntu (inicio um container com uma imamgem ubuntu e attach "entro dentro do container")
  - docker run -it python:3.9
  - docker run -it --entrypoint=bash python:3.9 (entro no bash do container)
    - pip install pandas (instalo a library pandas nesse container)
    - python (inicio um codigo python dentro desse container)

ao criar um container python se nao dermos um nome ao container ele sempre criará um container diferente e nesse novo container nao teremos a biblioteca pandas.
Para contonrnar isso temos 2 modos:

1 criar o container com um nome e acessa-lo (nao está nesta parte incial do curso)
```bash
  1- docker run --name python_pandas -it --entrypoint=bash python:3.9
  2- docker container start python_padas
  3- docker container attach python_padas
```
2 criar um dockerfile (contemplado no curso)
```bash  
  FROM python:3.9 -- imagem que estou criando

  RUN pip install pandas  -- comando que estou mandando executar no bash

  WORKDIR /app    -- diretorio dentro da imagem do container onde estarei copiando o arquivo da pipeline
  COPY pipeline.py pipeline.py

  ENTRYPOINT ["bash"] -- local a entrar quando conectar na maquina
```
para executar esse dockerfile é necessário que esteja dentro do diretorio em que foi criado
  * docker build -t test:pandas . (comando para construir a imagem)
  * docker run -it test:pandas (para entrar no container)
  * cd /app (vai para o diretorio)
  * ls -la (lista os arquivos dentro do diretorio)
  * python pipeline.py (executa o codigo python)


para executar automaticamente o codigo python alteraremos o entrypooint no dockerfile
```bash
  FROM python:3.9

  RUN pip install pandas

  WORKDIR /app
  COPY pipeline.py pipeline.py

  ENTRYPOINT ["python", "pipeline.py"]
```
# postgres
  - Nesta parte do video, para realizarmos um teste básico de ingestao, iremos construir um container usando uma imagem PostgreSQL, só que ao invez de usar um docker Composer ou built, iremos setar direto na linha de comando a criaçao do container.
  - A ideia é se familiarizar ja que usaremos o AirFlow para orquestraçao e o ele usa o PostgreSQL internamente

### exemplo de um docker compose para o postgres

```bash
  services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    restart: always
```

### Exemplo do comando para criar um container com imagem postgres diretamente via cli
#### Windows
```bash
winpty docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v c:/Users/Vitor\ Belan/Documents/GitHub/MeusProjetos/data-engineering-zoomcamp/data-engineering-zoomcamp/week1_setup/docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
   postgres:13

```
#### Linux macos
```bash
  docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB:"ny_taxi" \
    -v $(pwd):/var/lib/postgresql/data
    -p 5432:5432 \
   postgres:13

```
* Para rodar o container com essa imagem é necessário algumas variaveis de ambiente:
  * POSTGRES_USER - foi usado o root no curso
  * POSTGRES_PASSWORD - foi usado root no curso
  * POSTGRES_DB - nome do database que iriamos criar

#### Conectando ao database dentro do container

Usando o pgcli que é  uma interface de linha do comando interativa para o PostgreSQL

```bash
pip install pgcli
```
entre com o comando para conectar no database

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Caso esteja com problemas na conexao via linha de comando, como eu tive, execute o comando abaixo em um jupyter notebook

```bash
# import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

print(engine.connect())

querry = """ 
  SELECT 1 AS NUMBER;
"""

pd.read_sql(querry, con=engine)
```

# Ingerindo dados para o PostGreSQL com Python

Estaremos construindo o código python que ingere os dados que no caso estao na nossa máquina host, aqui usamos de exemplo os dados das viagens de taxi em Nova Iorque https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page para arquivos do tipo .parquet e https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow para arquivos do tipo .csv

[O código necessário se encontra aqui: ](data-engineering-zoomcamp/week1_setup/docker_sql/upload-data.ipynb)

# Usando a aplicaçao pgadmin ao invez do cli

Usar a biblioteca pgcli via linha de comando é algo muito interessante, porém nao muito útil no dia a dia por isso utilizaremos o pgAdmin uma web-based GUI para o PostgreSQL via docker.
Documentaçao e site do PgAdmin [pagina oficial](https://www.pgadmin.org/), [documentaçao do container](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html) 


comando para criar o container com a imagem do pgadmin:

```bash
docker run -it \
  -e "PGADMIN_DEFAULT_EMAIL=admin@admin.com" \
  -e "PGADMIN_DEFAULT_PASSWORD=root" \
  -p 8080:80 \
  dpage/pgadmin4

```

Ao rodarmos esse comando acima e fazermos a conexao do pgadmin com o postgreSQL tomaremos um erro de conexao de network, isso acontece pq ao rodar o comando acim criamos um outro container para o pgAdmin que nao contem o database do postgreSQL que criamos em outro container. para isso precisamos colcoar uma rede entre esses dois containers para que eles se comuniquem entre si

  * criaremos uma network com o nome `pg-network` para colcoar os dois containers nela [documentaçao](https://docs.docker.com/reference/cli/docker/network/create/)

```bash
docker network create pg-network
```

  * aqui recriaremos o container do database, mas agora com o referencia para a network criada `pg-network` e nomeamos o container para `pg-database`

```bash
winpty docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v c:/Users/Vitor\ Belan/Documents/GitHub/MeusProjetos/data-engineering-zoomcamp/data-engineering-zoomcamp/week1_setup/docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13
```

e também precisamor rodar novamente o container do pgadmin na mesma network que criamos

```bash
winpty docker run -it \
  -e "PGADMIN_DEFAULT_EMAIL=admin@admin.com" \
  -e "PGADMIN_DEFAULT_PASSWORD=root" \
  -p 8080:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4

```

  * agora com a network criada va para seu navegador no [endereço](http://localhost:8080/) 
  * vai em servers -> register -> connection
  * entre com a porta usuário e senha e o nome da rede criada em host/name

  ![print](week1_setup/docker_sql/pgadmin_e_pgdatabase.png)

  # Conteinerizando o Scrip de ingestao de dados
    * Agora iremos orquestrar o scrip num jupyter notebook em python, para termos nossa primeira datapipeline, nesse primeiro momento faremos em container sem usar um orquestrador para entendermos os conceitos básicos por trás dos sistemas. Posteriormente usaremos o airflow para orquestração dos dados.

    - 1 primeiramente converteremos o [script notebook de ingestao de dados upload-data.ipynb](data-engineering-zoomcamp/week1_setup/docker_sql/upload-data.ipynb) para [upload_data.py](data-engineering-zoomcamp/week1_setup/docker_sql/ingest_data.py)

    ```bash
    jupyter nbconvert --to=script upload-data.ipynb

    *obs lembrando que para rodar esse comando voce precisa estar no mesmo diretorio que ele aparece
    *obs caso esteja usando windows, pode ser que nao consiga rodar esse comando, entao tente instalar o jupyter rodando pip install jupyter
    caso mesmo assim nao consiga, rode o comando jupyter --version e veja o que é necessário instalar
    ```

  * A ingestao por pandas de uma dada massa de dados para nosso posgreSQL nao é algo muito bom, mas usamos para entender o processo todo. arqui colocaremos também a biblioteca `argparse` [doc](https://docs.python.org/3/library/argparse.html) que utilizaremos para passar argumentos para nosso pipeline, seja de usuário, senha, data, local do arquivo algum outro dado; como se estivemos num orquestrador de pipelines, assim como faremos mais pra frente de um outro modo no airflow

  Aqui sao os parametros 
      - Username `usuario a logar no pgadmin` 
      - Password `senha do pgadmin`
      - Host  `nome do container que estamos referenciando`
      - Port  `porta da rede do container`
      - Database name `nome do database`
      - Table name `nome da tabela`
      - URL for the CSV file `downlod`

  * num primeiro teste, podemos dropar a tabela que contruimos para inserir-lá novamente

  * depois de dropar podemos executar um pipeline de teste

  ```bash
  python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz"
  ```

    - após a execução deste comando  tabela ingerida ![figura](data-engineering-zoomcamp/week1_setup/docker_sql/ingest_table_taxi_trips.png)


  * Agora vamos conteinizar esse comando, primerio criaremos uma imagem para esse comando através do comando:

  ```bash
  docker build -t taxi_ingest:v001 .
  ```
  Depois que criar a imagem é só rodar um container olhando para essa imagem. lembrar de colocar o container pra rodar na mesma rede construída para os dois container `pg-database & pgadmin`

  ```bash
    docker run -it \
      --network=pg-network \
      taxi_ingest:v001 \
      --user=root \
      --password=root \
      --host=pg-database \
      --port=5432 \
      --db=ny_taxi \
      --table_name=yellow_taxi_trips \
      --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz"
  ```

  * segunda ingestao
  para a segunda ingestao eu criei uma rede na hora de rodar os container do docker compose pra ficar mais fácil de identificar e também criei uma outra imagem para a segunda versao

  ```bash
    winpty docker run -it \
      --network=docker_sql_pg-network-admin \
      taxi_ingest:v002 \
      --user=root \
      --password=root \
      --host=pgdatabase \
      --port=5432 \
      --db=ny_taxi \
      --table_name=zones \
      --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
  ```


  # Usando docker compose para rodar o PostGress e pgAdmin
    * Em poucas palavras o docker compose é uma ferramenta em que colocamos as configurações de multiplos containers em um único arquivo ao invez de rodar vários comandos separados de `docker run`. Abaixo está o o comando do docker compose que usamos para criar o [arquivo](docker-compose.yaml).
    `Lembre-se de parar a execucao dos containers que estao rodando anteriormente antes de rodar o comando abaixo`

  ```bash
  services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      -"./ny_taxi_postgres_data:/var/lib/postgresql/data"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      -"./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
  ```

    * ao criar os containers pelo docker compose não precisamos criar a network e referencia-las como fizemos ao criarmos separadamente os containers anteriormente.
    * geralmente precisamos inputas a  version do doccker-compose no inicio ddo docher-compose file, porém se nao colocarmos ao executar ée pego a ultima versao
    * aqui para salvar as configuraçoes de entrada e do server do PgAdmin criamos um volume referenciando a máquina host com o pgAdmin.
    > lembrando que ao rodar o comando do doccker container, é necessário que ele esteja no mesmo diretório em que salvou ou vai rodar as pastas do volume que configuramos. Para evitar o problema de rodar o comando do docker compose coloque o diretório completo nos volumes.

    * Para criarmos o container a partir do arquivo `docker-compose.yaml` basta executar o seguinte comando, lembrando que precisamos estar no mesmo diretorio que o arquivo `docker-compose.yaml` se encontra, pois nao colocamos todos diretórios completos:

    ```bash
    docker-compose up
    ```

    Caso deseja encerrar o container, além do comando `Ctrl+C` voce pode usar o seguinte comando:
    ```bash
    docker-compose down
    ```

    Além disso se quiser levantar o container e ainda usar o mesmo terminal iterativamente pode roda o seuginte comando

    ```bash
    docker-compose up -d
    ```