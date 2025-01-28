import streamlit as st
from modules.load_data import load_detailed_data
# from views.tab_general import tables

def tables_detailed(df):

    st.title("💼 Visão Detalhada")
    st.markdown("""---""")

    # Tabela de Cluster de Origens
    st.header("Cluster de Origens")
    st.write("Modelo de atribuição padrão: último clique não direto.")
    
    with st.expander("ℹ️ Entenda os Clusters", expanded=False):
        st.markdown("""
            ### Explicação dos Clusters
            
            Os clusters são agrupamentos de origens de tráfego que ajudam a entender melhor a fonte dos seus visitantes:
            
            🟢 **Google Ads**
            - Tráfego pago vindo do Google Ads
            - Identificado por: origem=google e mídia=cpc
            
            🔵 **Meta Ads**
            - Tráfego pago vindo do Facebook/Instagram Ads
            - Identificado por: presença do parâmetro fbclid na URL
            
            🟣 **Social**
            - Tráfego orgânico das redes sociais
            - Identificado por: mídia=social
            
            🌳 **Google Orgânico**
            - Tráfego orgânico do Google
            - Identificado por: origem=google e mídia=organic
            
            🟡 **Direto**
            - Acessos diretos ao site
            - Identificado por: origem=direct
            
            ✉️ **CRM**
            - Tráfego vindo de e-mails e comunicações diretas
            - Identificado por: origem=crm
            
            🗒️ **Draft**
            - Pedidos criados manualmente na Shopify
            - Identificado por: origem=shopify_draft_order
            
            🍪 **Perda de Cookies**
            - Sessões sem identificação de origem
            - Identificado por: origem=not captured
            
            ◻️ **Outros**
            - Outras combinações de origem/mídia não classificadas acima
            - Formato: origem/mídia
        """)
        
    aggregated_df = df.groupby(['Cluster']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    aggregated_df['Tx Conversão'] = (aggregated_df['Pedidos'] / aggregated_df['Sessões'] * 100).round(2).astype(str) + '%'
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="detailed_cluster_origens")

    # tables(df)
    # Tabela de Origem e Mídia
    st.header("Origem e Mídia")
    
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    aggregated_df['Tx Conversão'] = (aggregated_df['Pedidos'] / aggregated_df['Sessões'] * 100).round(2).astype(str) + '%'
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="detailed_origem_midia")

    # Tabela de Campanhas
    st.header("Campanhas")
    
    campaigns = df.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    campaigns['Tx Conversão'] = (campaigns['Pedidos'] / campaigns['Sessões'] * 100).round(2).astype(str) + '%'
    campaigns['% Receita'] = ((campaigns['Receita'] / campaigns['Receita'].sum()) * 100).round(2).astype(str) + '%'
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(campaigns, hide_index=1, use_container_width=1, key="detailed_campanhas")

    # Tabela de Conteúdo
    st.header("Conteúdo")
    st.write("Valor do utm_content.")
    
    conteudo = df.groupby(['Conteúdo']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    conteudo['Tx Conversão'] = (conteudo['Pedidos'] / conteudo['Sessões'] * 100).round(2).astype(str) + '%'
    conteudo['% Receita'] = ((conteudo['Receita'] / conteudo['Receita'].sum()) * 100).round(2).astype(str) + '%'
    conteudo = conteudo.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(conteudo, hide_index=1, use_container_width=1, key="detailed_conteudo")

    # Tabela de Página de Entrada
    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    pagina_de_entrada['Tx Conversão'] = (pagina_de_entrada['Pedidos'] / pagina_de_entrada['Sessões'] * 100).round(2).astype(str) + '%'
    pagina_de_entrada['% Receita'] = ((pagina_de_entrada['Receita'] / pagina_de_entrada['Receita'].sum()) * 100).round(2).astype(str) + '%'
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1, key="detailed_pagina_entrada")

    # Tabela de Cupons
    st.header("Cupons")
    st.write("Análise dos cupons utilizados nos pedidos")
    
    cupons = df.groupby(['Cupom']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    cupons['Tx Conversão'] = (cupons['Pedidos'] / cupons['Sessões'] * 100).round(2).astype(str) + '%'
    cupons['% Receita'] = ((cupons['Receita'] / cupons['Receita'].sum()) * 100).round(2).astype(str) + '%'
    cupons = cupons.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(cupons, hide_index=1, use_container_width=1, key="detailed_cupons")

def display_tab_detailed():

    df = load_detailed_data()
    tables_detailed(df)