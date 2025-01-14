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

def traffic_filters(df, cluster_selected=None, origem_selected=None, midia_selected=None, campanha_selected=None, conteudo_selected=None, pagina_de_entrada_selected=None, cupom_selected=None):
    """
    Aplica filtros ao DataFrame baseado nas seleções do usuário.
    Não cria elementos UI - apenas aplica a lógica de filtragem.
    """
    
    # Aplicar filtros apenas se houver seleção e não incluir "Selecionar Todos"
    if cluster_selected and "Selecionar Todos" not in cluster_selected:
        df = df[df['Cluster'].isin(cluster_selected)]
    if origem_selected and "Selecionar Todos" not in origem_selected:
        df = df[df['Origem'].isin(origem_selected)]
    if midia_selected and "Selecionar Todos" not in midia_selected:
        df = df[df['Mídia'].isin(midia_selected)]
    if campanha_selected and "Selecionar Todos" not in campanha_selected:
        df = df[df['Campanha'].isin(campanha_selected)]
    if conteudo_selected and "Selecionar Todos" not in conteudo_selected:
        df = df[df['Conteúdo'].isin(conteudo_selected)]
    if pagina_de_entrada_selected and "Selecionar Todos" not in pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]
    if cupom_selected and "Selecionar Todos" not in cupom_selected:
        df = df[df['Cupom'].isin(cupom_selected)]
    
    return df

def create_traffic_filters(df):
    """
    Cria e retorna os elementos de filtro da sidebar.
    """
    with st.sidebar:
        # Filtros existentes
        with st.expander("Filtros", expanded=True):
            # Função para tratar valores nulos na ordenação
            def sort_with_nulls(series):
                # Substitui valores nulos por string vazia para ordenação
                cleaned_series = series.fillna('')
                return ["Selecionar Todos"] + sorted(cleaned_series.unique().tolist())

            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_clusters = sort_with_nulls(df['Cluster'])
            all_origins = sort_with_nulls(df['Origem'])
            all_media = sort_with_nulls(df['Mídia'])
            all_campaigns = sort_with_nulls(df['Campanha'])
            all_content = sort_with_nulls(df['Conteúdo'])
            all_pages = sort_with_nulls(df['Página de Entrada'])
            all_coupons = sort_with_nulls(df['Cupom'])

            # Criar os elementos de filtro
            cluster_selected = st.multiselect(
                "Cluster",
                options=all_clusters,
                default=["Selecionar Todos"]
            )
            
            origem_selected = st.multiselect(
                "Origem",
                options=all_origins,
                default=["Selecionar Todos"]
            )
            
            midia_selected = st.multiselect(
                "Mídia",
                options=all_media,
                default=["Selecionar Todos"]
            )
            
            campanha_selected = st.multiselect(
                "Campanha",
                options=all_campaigns,
                default=["Selecionar Todos"]
            )
            
            conteudo_selected = st.multiselect(
                "Conteúdo",
                options=all_content,
                default=["Selecionar Todos"]
            )
            
            pagina_de_entrada_selected = st.multiselect(
                "Página de Entrada",
                options=all_pages,
                default=["Selecionar Todos"]
            )

            cupom_selected = st.multiselect(
                "Cupom",
                options=all_coupons,
                default=["Selecionar Todos"]
            )

            return {
                'cluster_selected': cluster_selected,
                'origem_selected': origem_selected,
                'midia_selected': midia_selected,
                'campanha_selected': campanha_selected,
                'conteudo_selected': conteudo_selected,
                'pagina_de_entrada_selected': pagina_de_entrada_selected,
                'cupom_selected': cupom_selected
            }
