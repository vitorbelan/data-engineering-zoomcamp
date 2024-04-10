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