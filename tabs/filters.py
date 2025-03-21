import pandas as pd
import streamlit as st
from modules.load_data import load_detailed_data, load_basic_data

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

    # Sempre inicializa com o mês atual
    start_date = first_day_of_month
    end_date = today
    
    # Inicializa o estado do botão ativo se não existir
    if 'active_button' not in st.session_state:
        st.session_state.active_button = "mes"
    
    # Filtro de datas interativo
    with st.sidebar.expander("Datas", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Hoje", 
                        type="secondary",
                        help="Dados de hoje",
                        use_container_width=True,
                        key="hoje_button"):
                start_date = today
                end_date = today
                st.session_state.active_button = "hoje"
            
            if st.button("Últimos 7 Dias",
                        type="secondary",
                        help="Dados dos últimos 7 dias",
                        use_container_width=True,
                        key="7d_button"):
                start_date = seven_days_ago
                end_date = today
                st.session_state.active_button = "7d"
            
            if st.button("Mês Atual",
                        type="secondary",
                        help="Dados do mês atual",
                        use_container_width=True,
                        key="mes_button"):
                start_date = first_day_of_month
                end_date = today
                st.session_state.active_button = "mes"
                
        with col2:
            if st.button("Ontem",
                        type="secondary",
                        help="Dados de ontem",
                        use_container_width=True,
                        key="ontem_button"):
                start_date = yesterday
                end_date = yesterday
                st.session_state.active_button = "ontem"
            
            if st.button("Últimos 30 Dias",
                        type="secondary",
                        help="Dados dos últimos 30 dias",
                        use_container_width=True,
                        key="30d_button"):
                start_date = thirty_days_ago
                end_date = today
                st.session_state.active_button = "30d"
            
            if st.button("Mês Passado",
                        type="secondary",
                        help="Dados do mês passado",
                        use_container_width=True,
                        key="mes_passado_button"):
                start_date = first_day_of_prev_month
                end_date = last_day_of_prev_month
                st.session_state.active_button = "mes_passado"

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            custom_start = st.date_input("Data Inicial", start_date, key="custom_start_date")
        with date_col2:
            custom_end = st.date_input("Data Final", end_date, key="custom_end_date")
        
        if custom_start != start_date or custom_end != end_date:
            start_date = custom_start
            end_date = custom_end
            st.session_state.active_button = "custom"

    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

def traffic_filters():

    if "cluster_selected" not in st.session_state:
        st.session_state.cluster_selected = ["Selecionar Todos"]
        st.session_state.origem_selected = ["Selecionar Todos"]
        st.session_state.midia_selected = ["Selecionar Todos"]
        st.session_state.campanha_selected = ["Selecionar Todos"]
        st.session_state.conteudo_selected = ["Selecionar Todos"]
        st.session_state.pagina_de_entrada_selected = ["Selecionar Todos"]
        st.session_state.cupom_selected = ["Selecionar Todos"]

    df = load_basic_data()

    with st.sidebar:

        # Filtros existentes
        with st.expander("Filtros Básicos", expanded=True):
            
            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_clusters = sort_by_sessions('Cluster', df)
            all_origins = sort_by_sessions('Origem', df)
            all_media = sort_by_sessions('Mídia', df)
            
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
            
            st.session_state.cluster_selected = cluster_selected
            st.session_state.origem_selected = origem_selected
            st.session_state.midia_selected = midia_selected


def attribution_filters():

    with st.sidebar:
        with st.expander("Modelos de Atribuição", expanded=True):
            # Adiciona opções de atribuição
            all_attribution = ["Último Clique Não Direto", "Primeiro Clique"]
            
            attribution_model = st.radio(
                "Modelo de Atribuição",
                options=all_attribution,
                index=0,
                help="Escolha o modelo de atribuição para análise dos dados"
            )
            
            st.session_state.attribution_model = attribution_model

            # Inicializa o estado se não existir
            if 'show_attribution_info' not in st.session_state:
                st.session_state.show_attribution_info = False

            # Botão para mostrar/ocultar
            if st.button('Sobre Modelos de Atribuição'):
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

def traffic_filters_detailed():

    df = load_detailed_data()

    with st.sidebar:
        # Filtros existentes
        with st.expander("Filtros Avançados", expanded=False):

            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_campaigns = sort_by_sessions('Campanha', df)
            all_content = sort_by_sessions('Conteúdo', df)
            all_pages = sort_by_sessions('Página de Entrada', df)
            all_coupons = sort_by_sessions('Cupom', df)
            
            # Criar os elementos de filtro
            
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
            
            st.session_state.campanha_selected = campanha_selected
            st.session_state.conteudo_selected = conteudo_selected
            st.session_state.pagina_de_entrada_selected = pagina_de_entrada_selected
            st.session_state.cupom_selected = cupom_selected

    