import json
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st

def get_bigquery_client():
    """Cria um cliente BigQuery com as credenciais corretas."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

def load_table_metas(table_name):
    """
    Carrega as metas para uma tabela específica do BigQuery.
    Se não existir, cria com valores padrão.
    """
    client = get_bigquery_client()
    
    query = f"""
    SELECT goals
    FROM `mymetric-hub-shopify.dbt_config.user_goals`
    WHERE username = '{table_name}'
    LIMIT 1
    """
    
    try:
        query_job = client.query(query)
        rows = list(query_job.result())
        if rows and rows[0]['goals']:
            return json.loads(rows[0]['goals'])
    except Exception as e:
        st.error(f"Erro ao carregar metas: {str(e)}")
    
    # Se não encontrou ou deu erro, retorna valores padrão
    default_metas = {
        "metas_mensais": {
            datetime.now().strftime("%Y-%m"): {
                "meta_receita_paga": 0
            }
        }
    }
    
    # Salva os valores padrão no BigQuery
    save_table_metas(table_name, default_metas)
    
    return default_metas

def save_table_metas(table_name, metas):
    """
    Salva as metas para uma tabela específica no BigQuery.
    """
    client = get_bigquery_client()
    
    # Converte o dicionário de metas para JSON
    metas_json = json.dumps(metas)
    
    # Query para inserir ou atualizar as metas
    query = f"""
    MERGE `mymetric-hub-shopify.dbt_config.user_goals` AS target
    USING (SELECT '{table_name}' as username, '{metas_json}' as goals) AS source
    ON target.username = source.username
    WHEN MATCHED THEN
        UPDATE SET goals = source.goals, updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (username, goals, created_at, updated_at)
        VALUES (source.username, source.goals, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
    """
    
    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao salvar metas: {str(e)}") 