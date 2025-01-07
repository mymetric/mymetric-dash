import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

def create_tables():
    # Cria o cliente BigQuery
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    
    # Cria o dataset se não existir
    dataset_id = "mymetric-hub-shopify.dbt_config"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {dataset_id} criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar dataset: {str(e)}")
    
    # SQL para criar as tabelas
    tables_sql = """
    -- Tabela de avisos dos usuários
    CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_notices` (
        username STRING NOT NULL,
        notices STRING,  -- JSON com os avisos fechados
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        PRIMARY KEY(username) NOT ENFORCED
    );

    -- Tabela de metas dos usuários
    CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_goals` (
        username STRING NOT NULL,
        goals STRING,  -- JSON com as metas
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        PRIMARY KEY(username) NOT ENFORCED
    );

    -- Tabela de configurações gerais dos usuários
    CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_settings` (
        username STRING NOT NULL,
        settings STRING,  -- JSON com as configurações
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        PRIMARY KEY(username) NOT ENFORCED
    );

    -- Tabela de eventos de usuário
    CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.user_events` (
        username STRING,
        event_type STRING,
        event_data STRING,  -- JSON com os dados do evento
        created_at TIMESTAMP
    );
    """
    
    # Executa cada comando SQL separadamente
    for sql in tables_sql.split(';'):
        if sql.strip():
            try:
                client.query(sql)
                print(f"Query executada com sucesso: {sql[:50]}...")
            except Exception as e:
                print(f"Erro ao executar query: {str(e)}")
                print(f"Query com erro: {sql}")

if __name__ == "__main__":
    create_tables() 