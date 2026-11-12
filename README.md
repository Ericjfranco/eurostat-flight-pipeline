# Eurostat Flight Data Pipeline

Pipeline de dados públicos de transporte aéreo com Python, Pandas, Apache Airflow, PostgreSQL e Docker.

## Fonte de dados

- Dataset inicial: `ttr00017` — Air transport of passengers by airport and type of transport (monthly data).
- Endpoint: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ttr00017?lang=EN`
- A API Statistics entrega JSON-stat 2.0. O projeto interpreta dimensões e valores antes de transformar em linhas.
- O dataset é agregado por aeroporto e tipo de transporte; não representa voos individuais nem rotas origem-destino.

## Arquitetura

O projeto utiliza uma arquitetura ETL (Extract, Transform, Load),
orquestrada pelo Apache Airflow e executada em containers Docker.

O fluxo inicia com a consulta à API do Eurostat, responsável
pelo fornecimento dos dados públicos de transporte aéreo.

### Fluxo de processamento

1. **Extract:** Python e Requests consultam a API do Eurostat
   e recebem os dados no formato JSON-stat 2.0.

2. **Raw Storage:** os dados originais são armazenados em
   arquivos JSON para permitir auditoria e reprocessamento.

3. **Transform:** Pandas realiza a conversão, padronização,
   limpeza e validação dos dados.

4. **Processed Storage:** os dados transformados são
   armazenados em arquivos CSV.

5. **Load:** Psycopg2 realiza a conexão com o PostgreSQL
   e persiste os registros tratados.

6. **Database:** os dados são armazenados no banco
   `flight_data`, na tabela `fact_air_traffic`.

### Orquestração

O Apache Airflow controla as etapas do pipeline por meio
da DAG `eurostat_flight_pipeline`.

O Scheduler agenda as execuções, enquanto o Webserver
disponibiliza a interface de monitoramento e gerenciamento.

### Infraestrutura

Todos os serviços são executados com Docker Compose.

O PostgreSQL hospeda dois bancos lógicos:
- `airflow`: metadados e informações de execução do Airflow.
- `flight_data`: dados processados pelo projeto.


## Estrutura do Repositório

eurostat-flight-pipeline/
├── dags/
│   └── eurostat_flight_pipeline.py
├── src/
│   ├── extract/
│   ├── transform/
│   ├── load/
│   ├── config.py
│   └── pipeline.py
├── sql/
│   ├── init/
│   └── schema.sql
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md

## Serviços

- `postgres`: PostgreSQL. O banco `airflow` guarda metadados do Airflow; `flight_data` guarda os dados do projeto.
- `airflow-init`: prepara o banco do Airflow e cria o usuário administrador.
- `airflow-webserver`: interface web em `http://localhost:8080`.
- `airflow-scheduler`: agenda e executa a DAG.

## Como iniciar

1. Copie `.env.example` para `.env` e altere as senhas.
2. Para um primeiro teste, mantenha `EUROSTAT_LAST_PERIODS=3`.
3. Execute:

```bash
docker compose up --build -d
```

4. Entre em `http://localhost:8080` com as credenciais do `.env`.
5. Ative e execute a DAG `eurostat_flight_pipeline`.

## Teste manual

```bash
docker compose exec airflow-webserver python -m src.pipeline
```

## Consultar PostgreSQL

```bash
docker compose exec postgres psql -U pipeline -d flight_data
```

```sql
SELECT period, geo_code, geo_label, value, dimensions
FROM fact_air_traffic ORDER BY period DESC LIMIT 20;
```

## Configuração

| Variável | Padrão | Finalidade |
|---|---|---|
| `EUROSTAT_DATASET` | `ttr00017` | Código do dataset |
| `EUROSTAT_LANGUAGE` | `EN` | Idioma da resposta |
| `EUROSTAT_LAST_PERIODS` | `3` | Número de períodos recentes; 0 solicita sem limitar |
| `DATA_DB_NAME` | `flight_data` | Banco do projeto |

## Observações

- O JSON original é salvo em `data/raw/`; o CSV tratado fica em `data/processed/`.
- Todas as dimensões originais são preservadas em colunas JSONB para não perder informação do dataset.
- A carga usa `ON CONFLICT DO UPDATE`, permitindo reexecução sem duplicar a mesma observação e atualizando revisões.
- O script SQL que cria `flight_data` roda apenas na primeira inicialização do volume PostgreSQL. Se o volume já existia, crie o banco manualmente ou recrie o volume.
- `docker compose down -v` apaga o volume do banco;