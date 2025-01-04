import pandas as pd
import streamlit as st

def date_filters(today, yesterday, seven_days_ago, thirty_days_ago):
    first_day_of_month = today.replace(day=1)
    
    with st.sidebar:
        st.markdown(f"## {st.session_state.username.upper()}")

    # Sempre inicializa com o mês atual
    start_date = first_day_of_month
    end_date = today
    
    # Inicializa o estado do botão ativo se não existir
    if 'active_button' not in st.session_state:
        st.session_state.active_button = 'mes'
    
    # Filtro de datas interativo
    with st.sidebar.expander("Datas", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Hoje", 
                        type="primary" if st.session_state.active_button == "hoje" else "secondary",
                        help="Dados de hoje",
                        use_container_width=True,
                        key="hoje"):
                start_date = today
                end_date = today
                st.session_state.active_button = "hoje"
            
            if st.button("Últimos 7 Dias",
                        type="primary" if st.session_state.active_button == "7d" else "secondary",
                        help="Dados dos últimos 7 dias",
                        use_container_width=True,
                        key="7d"):
                start_date = seven_days_ago
                end_date = today
                st.session_state.active_button = "7d"
                
        with col2:
            if st.button("Ontem",
                        type="primary" if st.session_state.active_button == "ontem" else "secondary",
                        help="Dados de ontem",
                        use_container_width=True,
                        key="ontem"):
                start_date = yesterday
                end_date = yesterday
                st.session_state.active_button = "ontem"
            
            if st.button("Últimos 30 Dias",
                        type="primary" if st.session_state.active_button == "30d" else "secondary",
                        help="Dados dos últimos 30 dias",
                        use_container_width=True,
                        key="30d"):
                start_date = thirty_days_ago
                end_date = today
                st.session_state.active_button = "30d"
        
        if st.button("Mês Atual",
                    type="primary" if st.session_state.active_button == "mes" else "secondary",
                    help="Dados do mês atual",
                    use_container_width=True,
                    key="mes"):
            start_date = first_day_of_month
            end_date = today
            st.session_state.active_button = "mes"

    with st.sidebar.expander("Datas Personalizadas", expanded=False):
        custom_start = st.date_input("Data Inicial", start_date)
        custom_end = st.date_input("Data Final", end_date)
        
        if custom_start != start_date or custom_end != end_date:
            start_date = custom_start
            end_date = custom_end
            st.session_state.active_button = "custom"

    return start_date, end_date

def traffic_filters(df, cluster_selected, origem_selected, midia_selected, campanha_selected, conteudo_selected, pagina_de_entrada_selected):
    
    # Adiciona filtro de cluster
    if "Selecionar Todos" not in cluster_selected:
        df = df[df['Cluster'].isin(cluster_selected)]
    
    # Se "Selecionar Todos" não estiver em origem_selected, aplica o filtro
    if "Selecionar Todos" not in origem_selected:
        df = df[df['Origem'].isin(origem_selected)]
    
    if "Selecionar Todos" not in midia_selected:
        df = df[df['Mídia'].isin(midia_selected)]
    
    if "Selecionar Todos" not in campanha_selected:
        df = df[df['Campanha'].isin(campanha_selected)]
    
    if "Selecionar Todos" not in conteudo_selected:
        df = df[df['Conteúdo'].isin(conteudo_selected)]
    
    if "Selecionar Todos" not in pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]

    return df
