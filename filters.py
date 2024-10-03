import pandas as pd
import streamlit as st

def date_filters(today, yesterday, seven_days_ago, thirty_days_ago):
    with st.sidebar:
        st.markdown(f"## {st.session_state.username.upper()}")

    # Filtro de datas interativo
    with st.sidebar.expander("Datas Fáceis", expanded=True):
        # Variáveis para definir os valores das datas
        start_date = seven_days_ago
        end_date = today

        # Botões de datas predefinidas
        if st.button("Hoje"):
            start_date = today
            end_date = today
        if st.button("Ontem"):
            start_date = yesterday
            end_date = yesterday
        if st.button("Últimos 7 Dias"):
            start_date = seven_days_ago
            end_date = today
        if st.button("Últimos 30 Dias"):
            start_date = thirty_days_ago
            end_date = today
    
    with st.sidebar.expander("Datas Personalizadas"):
        # Date pickers para selecionar manualmente as datas
        start_date = st.date_input("Data Inicial", start_date)
        end_date = st.date_input("Data Final", end_date)

    return start_date, end_date

def traffic_filters(df):
    origem_options = ["Selecionar Todos"] + df['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + df['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + df['Campanha'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + df['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Fontes de Tráfego", expanded=False):
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    # Aplicar os filtros
    if "Selecionar Todos" in origem_selected:
        origem_selected = df['Origem'].unique().tolist()
    if "Selecionar Todos" in midia_selected:
        midia_selected = df['Mídia'].unique().tolist()
    if "Selecionar Todos" in campanha_selected:
        campanha_selected = df['Campanha'].unique().tolist()
    if "Selecionar Todos" in pagina_de_entrada_selected:
        pagina_de_entrada_selected = df['Página de Entrada'].unique().tolist()

    df = df[df['Origem'].isin(origem_selected)]
    df = df[df['Mídia'].isin(midia_selected)]
    df = df[df['Campanha'].isin(campanha_selected)]
    df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]

    return df
