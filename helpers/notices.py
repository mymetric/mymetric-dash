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

def show_feature_notices(username, meta_receita):
    """Exibe os avisos de novas features com opção de não mostrar novamente."""
    closed_notices = load_closed_notices(username)
    
    # Aviso de migração para hub.mymetric.app
    if not closed_notices.get('hub_migration_notice', False):
        st.info("""
        ### 🔄 Mudança de Endereço
        
        **Atenção:** Este aplicativo agora estará disponível exclusivamente em:
        
        **[hub.mymetric.app](https://hub.mymetric.app)**
        
        Por favor, atualize seus favoritos e utilize o novo endereço para acessar o MyMetric Hub.
        """)
        if st.button("Entendi", key="hub_migration_notice", type="primary"):
            closed_notices['hub_migration_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()
    
    # Aviso do Mapa de Calor
    if not closed_notices.get('heatmap_notice', False):
        st.info("""
        ### 🆕 Nova Feature: Mapa de Calor de Conversão
        
        Agora você pode visualizar suas taxas de conversão por hora do dia e dia da semana em um mapa de calor interativo.
        
        **Recursos disponíveis:**
        * Identificar os melhores horários para suas vendas
        * Otimizar suas campanhas de marketing
        * Entender o comportamento dos seus clientes
        * Filtrar por mínimo de sessões
        
        Acesse agora mesmo a aba "🔥 Mapa de Calor de Conversão"! 📈
        """)
        if st.button("Não mostrar novamente", key="heatmap_notice", type="primary"):
            closed_notices['heatmap_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

    # Aviso da feature de Cupons
    if not closed_notices.get('coupon_notice', False):
        st.info("""
        ### 🎟️ Nova Feature: Análise de Cupons
        
        Agora você pode analisar o desempenho dos seus cupons de desconto!
        
        **Novos recursos:**
        * Nova tabela de análise de cupons na Visão Geral
        * Filtro de cupons na barra lateral
        * Métricas detalhadas por cupom
        * Análise de conversão e receita por cupom
        
        Confira agora mesmo na aba "Visão Geral"! 💡
        """)
        if st.button("Não mostrar novamente", key="coupon_notice", type="primary"):
            closed_notices['coupon_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

    # Aviso de meta não cadastrada
    if meta_receita == 0:
        st.warning("""
        ⚠️ **Meta do Mês Não Cadastrada**
        
        Você ainda não cadastrou sua meta de receita para este mês.
        Para um melhor acompanhamento do seu desempenho, acesse a aba Configurações e cadastre sua meta mensal.
        """)

def initialize_notices():
    """Inicializa o estado dos avisos se não existir."""
    if 'closed_notices' not in st.session_state:
        st.session_state.closed_notices = {}

def show_feature_notices(username, meta_receita):
    """Exibe os avisos de novas features com opção de não mostrar novamente."""
    closed_notices = load_closed_notices(username)
    
    # Aviso de migração para hub.mymetric.app
    if not closed_notices.get('hub_migration_notice', False):
        st.info("""
        ### 🔄 Mudança de Endereço
        
        **Atenção:** Este aplicativo agora estará disponível exclusivamente em:
        
        **[hub.mymetric.app](https://hub.mymetric.app)**
        
        Por favor, atualize seus favoritos e utilize o novo endereço para acessar o MyMetric Hub.
        """)
        if st.button("Entendi", key="hub_migration_notice", type="primary"):
            closed_notices['hub_migration_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()
    
    # Aviso do Mapa de Calor
    if not closed_notices.get('heatmap_notice', False):
        st.info("""
        ### 🆕 Nova Feature: Mapa de Calor de Conversão
        
        Agora você pode visualizar suas taxas de conversão por hora do dia e dia da semana em um mapa de calor interativo.
        
        **Recursos disponíveis:**
        * Identificar os melhores horários para suas vendas
        * Otimizar suas campanhas de marketing
        * Entender o comportamento dos seus clientes
        * Filtrar por mínimo de sessões
        
        Acesse agora mesmo a aba "🔥 Mapa de Calor de Conversão"! 📈
        """)
        if st.button("Não mostrar novamente", key="heatmap_notice", type="primary"):
            closed_notices['heatmap_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

    # Aviso da feature de Cupons
    if not closed_notices.get('coupon_notice', False):
        st.success("""
        ### 🎟️ Nova Feature: Análise de Cupons
        
        Agora você pode analisar o desempenho dos seus cupons de desconto!
        
        **Novos recursos:**
        * Nova tabela de análise de cupons na Visão Geral
        * Filtro de cupons na barra lateral
        * Métricas detalhadas por cupom
        * Análise de conversão e receita por cupom
        
        Confira agora mesmo na aba "Visão Geral"! 💡
        """)
        if st.button("Não mostrar novamente", key="coupon_notice", type="primary"):
            closed_notices['coupon_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

    # Aviso de meta não cadastrada
    if meta_receita == 0:
        st.warning("""
        ⚠️ **Meta do Mês Não Cadastrada**
        
        Você ainda não cadastrou sua meta de receita para este mês.
        Para um melhor acompanhamento do seu desempenho, acesse a aba Configurações e cadastre sua meta mensal.
        """)

    if 'notices' in st.session_state:
        for notice_id, notice in st.session_state.notices.items():
            if not notice.get('shown', False):
                st.success(f"**{notice['title']}**\n\n{notice['message']}")
                if notice.get('dismissible', False):
                    st.session_state.notices[notice_id]['shown'] = True 