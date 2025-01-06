import streamlit as st
from filters import date_filters, traffic_filters
from helpers.components import atribuir_cluster, section_title

def display_tab_last_orders(df2, **filters):

    
    # Aplicar a função usando apply
    df2['Cluster'] = df2.apply(atribuir_cluster, axis=1)

    # Criar colunas para os filtros
    col1, col2, col3 = st.columns(3)

    # Adiciona o campo de entrada para filtrar pelo ID da Transação na primeira coluna
    with col1:
        id_transacao_input = st.text_input("ID da Transação")

    # Adiciona o campo de seleção para o Status na segunda coluna
    with col2:
        status_selected = st.multiselect("Status", options=df2['Status'].unique())

    # Adiciona o campo de seleção para o Canal na terceira coluna
    with col3:
        canal_selected = st.multiselect("Canal", options=df2['Canal'].unique())

    # Aplica os filtros anteriores
    df_filtered2 = traffic_filters(df2, **filters)
    
    # Filtra pelo ID da Transação, se o valor estiver preenchido
    if id_transacao_input:
        df_filtered2 = df_filtered2[df_filtered2['ID da Transação'].astype(str).str.contains(id_transacao_input, na=False)]

    # Filtra pelo Status se algum status for selecionado
    if status_selected:
        df_filtered2 = df_filtered2[df_filtered2['Status'].isin(status_selected)]

    # Filtra pelo Canal se algum canal for selecionado
    if canal_selected:
        df_filtered2 = df_filtered2[df_filtered2['Canal'].isin(canal_selected)]

    # Exibe os dados filtrados
    section_title("Últimos Pedidos")
    st.data_editor(df_filtered2, hide_index=True, use_container_width=True)