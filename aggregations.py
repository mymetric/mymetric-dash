import pandas as pd
import streamlit as st
from google.cloud import bigquery

def display_aggregations(df):

    aggregated_df = df.groupby(['Cluster']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Pedidos Pagos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Cluster de Origens")
    st.write("Modelo de atribuição padrão: último clique não direto.")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)


    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Pedidos Pagos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Origem e Mídia")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    # Agrega os dados por Campanha
    campaigns = df.groupby(['Campanha']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    campaigns['% Receita'] = ((campaigns['Receita'] / campaigns['Receita'].sum()) * 100).round(2).astype(str) + '%'
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)

    st.header("Campanhas")
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

    # Agrega os dados por Conteúdo
    conteudo = df.groupby(['Conteúdo']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    conteudo['% Receita'] = ((conteudo['Receita'] / conteudo['Receita'].sum()) * 100).round(2).astype(str) + '%'
    conteudo = conteudo.sort_values(by='Pedidos', ascending=False)

    st.header("Conteúdo")
    st.write("Valor do utm_content.")
    st.data_editor(conteudo, hide_index=1, use_container_width=1)


    # Agrega os dados por Página de Entrada
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    pagina_de_entrada['% Receita'] = ((pagina_de_entrada['Receita'] / pagina_de_entrada['Receita'].sum()) * 100).round(2).astype(str) + '%'
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)

    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)
