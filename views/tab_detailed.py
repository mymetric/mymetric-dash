import streamlit as st
from modules.load_data import load_detailed_data
from views.tab_general import tables

def tables_detailed(df):

    st.title("💼 Visão Detalhada")
    st.markdown("""---""")

    tables(df)
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
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

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
    
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

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
    
    st.data_editor(conteudo, hide_index=1, use_container_width=1)

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
    
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)

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
    
    st.data_editor(cupons, hide_index=1, use_container_width=1)

def display_tab_detailed():
    
    df = load_detailed_data()
    tables_detailed(df)