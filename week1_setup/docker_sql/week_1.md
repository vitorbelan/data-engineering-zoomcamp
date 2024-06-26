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
    ```
    *obs lembrando que para rodar esse comando voce precisa estar no mesmo diretorio que ele aparece
    *obs caso esteja usando windows, pode ser que nao consiga rodar esse comando, entao tente instalar o jupyter rodando pip install jupyter
    caso mesmo assim nao consiga, rode o comando jupyter --version e veja o que é necessário instalar
    

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

  * Criaremos a imagem a partir do arquivo chamado Dockerfile onde contem o diretorio de onde salvará e de onde criará a imagem a ser construida

  * Agora vamos conteinizar esse comando, primerio criaremos uma imagem para esse comando através do comando:

  ```bash
  docker build -t taxi_ingest:v001 .
  ```
  Depois que criar a imagem é só rodar um container olhando para essa imagem. lembrar de colocar o container pra rodar na mesma rede construída para os dois container `pg-database & pgadmin`

  ```bash
docker run -it \
  --network=docker_sql_pg-network-admin \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz"
  ```

  * segunda ingestao
  para a segunda ingestao eu criei uma rede na hora de rodar os container do docker compose pra ficar mais fácil de identificar e também criei uma outra imagem para a segunda versao

  ```bash
docker run -it \
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
  * Lembre-se de conectar o pgadmin ao postgressdatabase [link, no minuto 06:42](https://www.youtube.com/watch?v=hKI6PkPhpa0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=9) video onde pode relembrar como fazer isso 
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
  * geralmente precisamos inputar a  version do docker-compose no inicio ddo docher-compose file, porém se nao colocarmos ao executar ée pego a ultima versao
  * aqui para salvar as configuraçoes de entrada e do server do PgAdmin criamos um volume referenciando a máquina host com o pgAdmin.
  > lembrando que ao rodar o comando do doccker container, é necessário que ele esteja no mesmo diretório em que salvou ou vai rodar as pastas do volume que configuramos. Para evitar o problema de rodar o comando do docker compose coloque o diretório completo nos volumes.

  * Para criarmos o container a partir do arquivo `docker-compose.yaml` basta executar o seguinte comando, lembrando que precisamos estar no mesmo diretorio que o arquivo `docker-compose.yaml` se encontra, pois nao colocamos todos diretórios completos:
  * caso voce tenha problemas de permissoes ao iniciar os containers tente alguns desses links e opcoes: 
    - [link1](https://www.reddit.com/r/docker/comments/11xr3gc/help_with_pgadmin_volume_mount/) ou 
    - [link2](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html#mapped-files-and-directories) 
    - encontrado aqui [link3](https://stackoverflow.com/questions/64781245/permission-denied-var-lib-pgadmin-sessions-in-docker)

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


# Terraform
Uma ferramenta Iaas Infrastructure as a code que permite definir recursos on-cloud e onpremises em arquivos de configuraçoes mais legiveis
[fonte](developer.hashicorp.com/terraform/intro)

  * Terraform divide as informções em blocos que sao definidos com `{}` parecido com Java. Porém nao necessita de `;` para finalizar um bloco, usa quebra de linha.
  * Existem 3 principais blocos `terraform`, `provider` e `resource`. Só pode existir um único bloco chamado `terraform` quanto que `provider` e `resource` podem ser vários.
  * O bloco `terraform` contém as seguintes configuraçoes 
    - o sub-bloco `required_providers` que especifica o provedor requerido para a configuraçao nesse exemplo utilizamos um único provider que que chamamos de  google. 
      - O provider é um plugin para criar e gerenciar recursos.
      - Cada provider precisa de um sorce com o intuito de instalar um o plugin certo. Por padrao usamos o Hashicorp repositório parecido com o repositório do docker images
      - `hashicorp/google` é a abreviação de `registry.terraform.io/hashicorp/google`
      - opcionalmente o provider pode ter uma versao descrita. Se nao for especificada é cosiderada a versao mais recente.
  * O bloco `provider` configura um provedor espeifico. Como só temos acesso a um provedor que no caso é a Google Cloud, no nosso comando teremos somente um bloco `provider` apontando para o google.
    - Essas configurações dentro do prvoedor sao especificas para cada um e fornecidas pelo próprio provedor. A deste exemplo é fornecida pela GCP, Azure e AWS poderão ser diferentes e trerao suas próprias configurações.
    - As configuraçoes das credenciais e zonas podem ser oferecidas de varias formas como abaixo.
  * O bloco `resource` define o componente da nossa insfraestrutura. Neste exemplo temos um único recurso
      - o bloco referente ao `resource` possui duas strings antes do bloco que sao : ***type*** e ***name*** do recurso, juntas criam o ***reource ID*** identificado po `type.name`
        - O primeiro prefixo do tipo de recurso é mapeado para o nome do provedor. Por exemplo, o tipo de recurso `google_compute_network` tem o prefixo google e, portanto, é mapeado para o provedor google.
        - Os tipos de recursos são definidos na documentação do Terraform e referem-se aos recursos que os provedores de nuvem oferecem. Em nosso exemplo, `google_compute_network` [link](https://cloud.google.com/vpc?hl=pt_br) refere-se ao serviço [Virtual Private Cloud do GCP](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_network).
        - Os nomes dos recursos são os nomes internos que usamos em nossas configurações do Terraform para nos referirmos a cada recurso e não têm impacto na infraestrutura real.
        - O conteúdo de um bloco de recursos é específico do tipo de recurso. [Verifique a documentação do Terraform](https://registry.terraform.io/browse/providers) para ver uma lista de tipos de recursos por provedor.
          - Neste exemplo, o tipo de recurso `google_compute_network` possui um único argumento obrigatório chamado name, que é o nome que o recurso terá na infraestrutura do GCP.
            - Obs Não confunda o nome do recurso com o argumento nome!
      
Além desses 3 blocoss tem-se blocos adicionais que podem ser referenciados a partir de uma rquivo chamado variables.
  - Os tipos de blocos de variáveis de entrada são úteis para personalizar aspectos de outros blocos sem alterar o código-fonte dos outros blocos. Eles são frequentemente chamados simplesmente de variáveis. Eles são passados em tempo de execução.

```bash
variable "region" {
description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
default     = "europe-west6"
type        = string
}
```

Descrição:
    - Um bloco de variável de entrada começa com a variável de tipo seguida por um nome de nossa escolha.
    - O bloco pode conter vários campos. Neste exemplo utilizamos os campos descrição, tipo e padrão.
    - ***description*** contém uma descrição simples para fins de documentação.
    - ***type*** especifica os tipos de valores aceitos para a variável
    - Se o campo padrão for definido, a variável se tornará opcional porque um valor padrão já foi fornecido por este campo. Caso contrário, um valor deverá ser fornecido ao executar a configuração do Terraform.
    - Para campos adicionais, verifique a documentação do Terraform.
  - As variáveis devem ser acessadas com a palavra-chave var. e depois o nome da variável.

```bash
region = var.region
```
- Variaveis locais se comportam mais como constantes e sao acessadas com a palavra `local` **sem usar o s no final**
  - Definindo as variaveis locais
  ```bash
  locals{
      region  = "us-central1"
      zone    = "us-central1-c"
  }
  ```
  - referenciando as variaceis locais
  ```bash
      region = local.region
      zone = local.zone
  ```
- aqui como exemplo irei inserir o arquivo variables.tf e chamarei essas variáveis dentro o main.tf


## Comandos chaves Terraform

  * Init 
    - Ao definir meu provedor  o init irá trazer o code para maquina local e fazer a comunicacao com o provedor
  * Plan
    - Recursos que serao criados (Oque estou para fazer?)
  * Apply
    - Executa o que está escrito nos arquivos tf
  * Destroy
    - Remove tudo definido nos arquivos tf
### Usando o terraform para criar uma insfraestrutura na GCP
* Caso quiser uma extensao para o terraform ao escrever um terraform file, para lhe auxiliar caso use o Vscode, recomendo o do HashiCorp Terraform

```bash
  terraform {
    required_providers {
      google = {
        source = "hashicorp/google"
        version = "3.5.0"
      }
    }
  }

  provider "google" {
    credentials = file("<NAME>.json")

    project = "<PROJECT_ID>"
    region  = "us-central1"
    zone    = "us-central1-c"
  }

  resource "google_compute_network" "vpc_network" {
    name = "terraform-network"
  }
```

para pegar as crendencias além do arquivo direto (o que nao é bom):
  - se tiver com o gcloud instalado usar o comando `gcloud default auth-login`
  ou
  - `export GOOGLE_CREDENTIALS='<diretorio da credencial> ` testando pra ver se deu certo com: echo $GOOGLE_CREDENTIALS


# Configurando um ambiente de desenvolvimento com uma VM no Google Cloud

Para criar as instancias da VM seguimos esse caminho. Mas antes disso precisamos gerar uma SSH [LINK](https://cloud.google.com/compute/docs/connect/create-ssh-keys)

  `cd .ssh/` <-caso nao senha sse diretorio crie um
  `ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048`

  * Ao rodar esse comando ele gera duas chaves uma com nome e oupra com `<nome.pub>` a publica voce usara para se conectar a maquina e a outra nao mostre a ninguém

  `cat ssh_key.pub` ao colocar isso significa que todas maquinas que eu criar terao essa ssh pub key
  
  Ir em 3 barrinhas compute engine -> Metadata -> SSHkeys -> add

## Criando uma instancia 
Ir em 3 barrinhas compute engine -> Vm Instances -> 3 pontinhos na barra superior -> create instance
coloque o nome, regiao, zona, escolha a instancia no caso E2 OU ALGUMA OUTRA
altere o BOOT disk e escolha a imagem que pretende usar.
Assim que criar a vm pegue o IP

```bash
ssh -i ~/ .shh/<chave nao publica> <nomeaseconectar>@<ip_publico> para logar
logout ou ctrl+d para sair
```

`htop` -> comando para ver o tipo de maquina

criando um arquivo config para configurar o ssh dentror da pasta que esta a chave e usar um comando ssh chamando esse arquivo cmd: `ssh de-zoocamp`

#### Usando VsCode com SSH
Caso queira pode usar o vscode para conectar na maquina remota Para isso baixe a extensao Remote - SSH
Na pagina inicial da extensao va no canto inferior esquerdo numa seta verde `><` e clique em `connect host` com o arquivo de conexao crado selecione ele e use-o para entrar na VM 

```bash
Host de-zoocamp
    HostName <externalIP>
    User <usuario que fez para gerar as ley>
    IdentityFile <endereco onde esta alocado o arquivo ssh gerado>
```

  * baixando e instalando o ***anaconda***  `wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh` 
  * baixando e instalando o ***docker***    `sudo apt-get install docker.io`
    * caso o docker de problema link: https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md  
  * baixando o instalando ***docker-compose*** [link de como fazer](https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=15&ab_channel=DataTalksClub%E2%AC%9B)
  * atualizando os apps                     `sudo apt-get update`
  * baixando o git                          `git clone <url do git>`
  * instalando o conda `conda install -c conda-forge pgcli`


### Como statar o jupyter notebook na VM pela maq host
  * rode o comando `cmd: jupyter notebook` e ela dará uma url para acessar o notebook adicione a porta que a maquina irá mostrar em oports do connect host

### Instalando terraform no linux
  * [link para download e comandos](https://www.terraform/io/downloads)
  * configurando google cloud para a VM [video link 41s](https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=15&ab_channel=DataTalksClub%E2%AC%9B)