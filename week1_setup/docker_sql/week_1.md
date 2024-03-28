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

### Exemplo do comando para criar um container com imagem postgres diretamente via clii
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

# Ingerindo data para o PostGreSQL com Python

Estaremos construindo o código python que ingere os dados que no caso estao na nossa máquina host, aqui usamos de exemplo os dados das viagens de taxi em Nova Iorque https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page para arquivos do tipo .parquet e https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow para arquivos do tipo .csv