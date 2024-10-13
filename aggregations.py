import pandas as pd
import streamlit as st
from google.cloud import bigquery

def display_aggregations(df):
    # Agrega os dados por Origem e Mídia
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Pedidos Pagos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Origem e Mídia")
    st.write("Modelo de atribuição padrão: último clique não direto.")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    # Agrega os dados por Campanha
    campaigns = df.groupby(['Campanha']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)

    st.header("Campanhas")
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

    # Agrega os dados por Página de Entrada
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)

    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)
