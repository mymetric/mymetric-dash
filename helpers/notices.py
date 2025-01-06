import streamlit as st
from datetime import date, datetime
import json
from google.cloud import bigquery
from google.oauth2 import service_account

def get_bigquery_client():
    """Cria um cliente BigQuery com as credenciais corretas."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

def load_closed_notices(username):
    """Carrega os avisos fechados do BigQuery."""
    client = get_bigquery_client()
    
    query = f"""
    SELECT notices
    FROM `mymetric-hub-shopify.dbt_config.user_notices`
    WHERE username = '{username}'
    LIMIT 1
    """
    
    try:
        query_job = client.query(query)
        rows = list(query_job.result())
        if rows:
            notices_str = rows[0]['notices']
            return json.loads(notices_str) if notices_str else {}
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar avisos: {str(e)}")
        return {}

def save_closed_notices(username, notices):
    """Salva os avisos fechados no BigQuery."""
    client = get_bigquery_client()
    
    # Converte o dicionário de avisos para JSON
    notices_json = json.dumps(notices)
    
    # Query para inserir ou atualizar os avisos
    query = f"""
    MERGE `mymetric-hub-shopify.dbt_config.user_notices` AS target
    USING (SELECT '{username}' as username, '{notices_json}' as notices) AS source
    ON target.username = source.username
    WHEN MATCHED THEN
        UPDATE SET notices = source.notices, updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (username, notices, created_at, updated_at)
        VALUES (source.username, source.notices, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
    """
    
    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao salvar avisos: {str(e)}")

def show_new_year_notice(username):
    """Exibe a mensagem de ano novo com botão de fechar estilizado."""
    closed_notices = load_closed_notices(username)
    
    if not closed_notices.get('new_year_2025', False):
        st.info(f"""
        ### 🎉 Feliz 2025, {username.upper()}!
        
        Que este ano seja repleto de insights valiosos e métricas positivas. Boas análises! 📊
        """)
        if st.button("Obrigado, vamos juntos!", key="close_new_year", type="primary"):
            closed_notices['new_year_2025'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

def show_feature_notices(username, meta_receita=0):
    """Exibe os avisos de novas features com opção de não mostrar novamente."""
    closed_notices = load_closed_notices(username)
    
    # Aviso de metas
    if not closed_notices.get('meta_notice', False) and meta_receita == 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            ### 🎯 Configure suas Metas de Faturamento!
            
            Agora você pode definir e acompanhar suas metas mensais de receita.
            
            Para começar:
            1. Acesse a aba "⚙️ Configurações"
            2. Defina sua meta mensal
            3. Acompanhe o progresso aqui na aba "Visão Geral"
            
            Comece agora mesmo a trackear seus objetivos! 📈
            """)
            if st.button("Não mostrar novamente", key="meta_notice", type="primary"):
                closed_notices['meta_notice'] = True
                save_closed_notices(username, closed_notices)
                st.rerun()

        with col2:
            st.info("""
            ### 📊 Nova Aba de Análise do Dia!
            
            Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
            
            Recursos disponíveis:
            - Acompanhamento hora a hora
            - Comparação com dias anteriores
            - Acompanhamento de meta diária
            
            Confira agora mesmo! 🚀
            """)
            if st.button("Não mostrar novamente", key="today_notice", type="primary"):
                closed_notices['today_notice'] = True
                save_closed_notices(username, closed_notices)
                st.rerun()

    # Aviso da aba de análise do dia
    elif not closed_notices.get('today_notice', False):
        st.info("""
        ### 📊 Nova Aba de Análise do Dia!
        
        Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
        
        Recursos disponíveis:
        - Acompanhamento hora a hora
        - Comparação com dias anteriores
        - Principais fontes de tráfego do dia
        
        Confira agora mesmo! 🚀
        """)
        if st.button("Não mostrar novamente", key="today_notice", type="primary"):
            closed_notices['today_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

def initialize_notices():
    """Inicializa o estado dos avisos se não existir."""
    if 'closed_notices' not in st.session_state:
        st.session_state.closed_notices = {} 