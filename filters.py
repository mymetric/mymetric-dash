import streamlit as st

def create_sidebar_filters(df):
    origem_options = ["Selecionar Todos"] + df['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + df['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + df['Campanha'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + df['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Filtros de Tráfego", expanded=False):
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    if "Selecionar Todos" in origem_selected:
        origem_selected = df['Origem'].unique().tolist()

    if "Selecionar Todos" in midia_selected:
        midia_selected = df['Mídia'].unique().tolist()

    if "Selecionar Todos" in campanha_selected:
        campanha_selected = df['Campanha'].unique().tolist()

    if "Selecionar Todos" in pagina_de_entrada_selected:
        pagina_de_entrada_selected = df['Página de Entrada'].unique().tolist()

    # Aplicar os filtros ao dataframe
    df = apply_filters(df, origem_selected, midia_selected, campanha_selected, pagina_de_entrada_selected)

    return df, origem_selected, midia_selected


def apply_filters(df, origem_selected, midia_selected, campanha_selected, pagina_de_entrada_selected):
    if origem_selected:
        df = df[df['Origem'].isin(origem_selected)]
    if midia_selected:
        df = df[df['Mídia'].isin(midia_selected)]
    if campanha_selected:
        df = df[df['Campanha'].isin(campanha_selected)]
    if pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]
    return df
