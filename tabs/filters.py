import pandas as pd
import streamlit as st

def sort_by_sessions(series, df):
    session_counts = df.groupby(series).Sessões.sum().sort_values(ascending=False)
    return ["Selecionar Todos"] + session_counts.index.tolist()

def date_filters():
    today = pd.to_datetime("today").date()
    yesterday = today - pd.Timedelta(days=1)
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)
    first_day_of_month = today.replace(day=1)
    
    # Calcular primeiro e último dia do mês passado
    last_day_of_prev_month = first_day_of_month - pd.Timedelta(days=1)
    first_day_of_prev_month = last_day_of_prev_month.replace(day=1)
    
    with st.sidebar:
        if st.session_state.username == "mymetric":
            st.markdown("## MYMETRIC")
        else:
            st.markdown("## " + st.session_state.tablename.upper())

    # Inicializa o estado do botão ativo se não existir
    if 'active_button' not in st.session_state:
        st.session_state.active_button = "mes"
        st.session_state.start_date = first_day_of_month
        st.session_state.end_date = today
    
    # Filtro de datas interativo
    with st.sidebar.expander("Datas", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Hoje", 
                        type="secondary",
                        help="Dados de hoje",
                        use_container_width=True,
                        key="hoje"):
                st.session_state.active_button = "hoje"
                st.session_state.start_date = today
                st.session_state.end_date = today
            
            if st.button("Últimos 7 Dias",
                        type="secondary",
                        help="Dados dos últimos 7 dias",
                        use_container_width=True,
                        key="7d"):
                st.session_state.active_button = "7d"
                st.session_state.start_date = seven_days_ago
                st.session_state.end_date = today
            
            if st.button("Mês Atual",
                        type="secondary",
                        help="Dados do mês atual",
                        use_container_width=True,
                        key="mes"):
                st.session_state.active_button = "mes"
                st.session_state.start_date = first_day_of_month
                st.session_state.end_date = today
                
        with col2:
            if st.button("Ontem",
                        type="secondary",
                        help="Dados de ontem",
                        use_container_width=True,
                        key="ontem"):
                st.session_state.active_button = "ontem"
                st.session_state.start_date = yesterday
                st.session_state.end_date = yesterday
            
            if st.button("Últimos 30 Dias",
                        type="secondary",
                        help="Dados dos últimos 30 dias",
                        use_container_width=True,
                        key="30d"):
                st.session_state.active_button = "30d"
                st.session_state.start_date = thirty_days_ago
                st.session_state.end_date = today
            
            if st.button("Mês Passado",
                        type="secondary",
                        help="Dados do mês passado",
                        use_container_width=True,
                        key="mes_passado"):
                st.session_state.active_button = "mes_passado"
                st.session_state.start_date = first_day_of_prev_month
                st.session_state.end_date = last_day_of_prev_month

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            custom_start = st.date_input("Data Inicial", st.session_state.start_date, key="custom_start_date")
        with date_col2:
            custom_end = st.date_input("Data Final", st.session_state.end_date, key="custom_end_date")
        
        # Botão para aplicar período personalizado
        if st.button("Aplicar Período", 
                    type="primary",
                    help="Aplicar o período selecionado",
                    use_container_width=True):
            st.session_state.active_button = "custom"
            st.session_state.start_date = custom_start
            st.session_state.end_date = custom_end

    # Atualizar as variáveis locais com os valores da sessão
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

def traffic_filters(df):
    if "cluster_selected" not in st.session_state:
        st.session_state.cluster_selected = ["Selecionar Todos"]
        st.session_state.origem_selected = ["Selecionar Todos"]
        st.session_state.midia_selected = ["Selecionar Todos"]
        st.session_state.campanha_selected = ["Selecionar Todos"]
        st.session_state.conteudo_selected = ["Selecionar Todos"]
        st.session_state.pagina_de_entrada_selected = ["Selecionar Todos"]

    with st.sidebar:
        # Filtros Básicos
        with st.expander("Filtros Básicos", expanded=True):
            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_clusters = sort_by_sessions('Cluster', df)
            
            # Criar os elementos de filtro
            cluster_selected = st.multiselect(
                "Cluster",
                options=all_clusters,
                default=["Selecionar Todos"]
            )
            
            st.session_state.cluster_selected = cluster_selected

        # Filtro de atribuição (sempre por último)
        with st.expander("Modelos de Atribuição", expanded=True):
            # Adiciona opções de atribuição
            all_attribution = ["Último Clique Não Direto", "Primeiro Clique"]
            
            attribution_model = st.radio(
                "Modelo de Atribuição",
                options=all_attribution,
                index=0,
                help="Escolha o modelo de atribuição para análise dos dados",
                key="attribution_model_radio"
            )
            
            # Força recarregamento dos dados quando o modelo muda
            if 'last_attribution_model' not in st.session_state:
                st.session_state.last_attribution_model = attribution_model
            
            if st.session_state.last_attribution_model != attribution_model:
                st.session_state.last_attribution_model = attribution_model
                st.session_state.attribution_model = attribution_model
                # Limpa o cache antes de recarregar
                if 'cache_data' in st.session_state:
                    st.session_state.cache_data = {}
                if 'cache_timestamps' in st.session_state:
                    st.session_state.cache_timestamps = {}
                if 'background_tasks' in st.session_state:
                    st.session_state.background_tasks = {}
                st.rerun()
            else:
                st.session_state.attribution_model = attribution_model

            # Inicializa o estado se não existir
            if 'show_attribution_info' not in st.session_state:
                st.session_state.show_attribution_info = False

            # Botão para mostrar/ocultar
            if st.button('Sobre Modelos de Atribuição', key='attribution_info_button'):
                st.session_state.show_attribution_info = not st.session_state.show_attribution_info

            # Conteúdo que será mostrado/ocultado
            if st.session_state.show_attribution_info:
                st.markdown("""
                    ### ℹ️ Modelos de Atribuição
                    
                    Os modelos de atribuição determinam como o crédito por uma conversão é distribuído entre os diferentes pontos de contato:
                    
                    🎯 **Último Clique Não Direto**
                    - Atribui 100% do crédito ao último canal não direto que o usuário interagiu antes da conversão
                    - Ignora acessos diretos posteriores
                    - Mais comum para análise de campanhas de curto prazo
                    
                    1️⃣ **Primeiro Clique**
                    - Atribui 100% do crédito ao primeiro canal que trouxe o usuário ao site
                    - Valoriza a descoberta inicial
                    - Útil para entender quais canais são mais eficientes em trazer novos usuários
                """)

def traffic_filters_detailed(df):
    with st.sidebar:
        # Filtros existentes
        with st.expander("Filtros Avançados", expanded=False):
            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_origins = sort_by_sessions('Origem', df)
            all_media = sort_by_sessions('Mídia', df)
            all_campaigns = sort_by_sessions('Campanha', df)
            all_content = sort_by_sessions('Conteúdo', df)
            all_pages = sort_by_sessions('Página de Entrada', df)
            
            # Criar os elementos de filtro
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
            
            st.session_state.origem_selected = origem_selected
            st.session_state.midia_selected = midia_selected
            st.session_state.campanha_selected = campanha_selected
            st.session_state.conteudo_selected = conteudo_selected
            st.session_state.pagina_de_entrada_selected = pagina_de_entrada_selected

def apply_filters(df):
    """
    Aplica filtros ao DataFrame baseado nas seleções do usuário.
    Não cria elementos UI - apenas aplica a lógica de filtragem.
    """
    # Verificar se o DataFrame está vazio
    if df.empty:
        return df
        
    # Criar uma cópia do DataFrame para não modificar o original
    df_filtered = df.copy()

    # Lista de filtros para aplicar
    filters = [
        ('cluster_selected', 'Cluster'),
        ('origem_selected', 'Origem'),
        ('midia_selected', 'Mídia'),
        ('campanha_selected', 'Campanha'),
        ('conteudo_selected', 'Conteúdo'),
        ('pagina_de_entrada_selected', 'Página de Entrada')
    ]

    # Aplicar cada filtro
    for state_key, column in filters:
        selected_values = st.session_state.get(state_key, [])
        if selected_values and "Selecionar Todos" not in selected_values:
            # Garantir que a coluna existe antes de filtrar
            if column in df_filtered.columns:
                # Converter valores para string para evitar problemas de tipo
                df_filtered[column] = df_filtered[column].astype(str)
                selected_values = [str(val) for val in selected_values]
                df_filtered = df_filtered[df_filtered[column].isin(selected_values)]
    
    return df_filtered

    