import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

def display_tab_funnel(client, table, start_date, end_date, **filters):

        
    st.title("🎯 Funil de Conversão")
    
    try:
        with st.spinner('Carregando dados ...'):
            # Query para buscar dados do HolySoup
            query = f"""
            SELECT 
                event_date `Data`,
                view_item `Visualização de Item`,
                add_to_cart `Adicionar ao Carrinho`,
                begin_checkout `Iniciar Checkout`,
                add_shipping_info `Adicionar Informação de Frete`,
                add_payment_info `Adicionar Informação de Pagamento`,
                purchase `Pedido`
            FROM `mymetric-hub-shopify.dbt.{table}_daily_metrics`
            """
            
            df = client.query(query).to_dataframe()

            st.data_editor(df, hide_index=1, use_container_width=1)
            
            
            if df.empty:
                st.warning("Nenhum dado encontrado")
                return
            
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {str(e)}")
        st.error("""
        Sugestões:
        1. Verifique a conexão com o BigQuery
        2. Confirme se as permissões estão corretas
        3. Tente recarregar a página
        """) 