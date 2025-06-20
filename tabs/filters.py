import pandas as pd
import streamlit as st
import time

def sort_by_sessions(series, df):
    if 'Sessões' in df.columns:
        session_counts = df.groupby(series).Sessões.sum().sort_values(ascending=False)
    else:
        session_counts = df.groupby(series).Quantidade.sum().sort_values(ascending=False)
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
        with st.form(key="date_filters_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                hoje_clicked = st.form_submit_button("Hoje", 
                            type="secondary",
                            help="Dados de hoje",
                            use_container_width=True)
                if hoje_clicked:
                    st.session_state.active_button = "hoje"
                    st.session_state.start_date = today
                    st.session_state.end_date = today
                    st.rerun()
                
                sete_dias_clicked = st.form_submit_button("Últimos 7 Dias",
                            type="secondary",
                            help="Dados dos últimos 7 dias",
                            use_container_width=True)
                if sete_dias_clicked:
                    st.session_state.active_button = "7d"
                    st.session_state.start_date = seven_days_ago
                    st.session_state.end_date = today
                    st.rerun()
                
                mes_atual_clicked = st.form_submit_button("Mês Atual",
                            type="secondary",
                            help="Dados do mês atual",
                            use_container_width=True)
                if mes_atual_clicked:
                    st.session_state.active_button = "mes"
                    st.session_state.start_date = first_day_of_month
                    st.session_state.end_date = today
                    st.rerun()
                    
            with col2:
                ontem_clicked = st.form_submit_button("Ontem",
                            type="secondary",
                            help="Dados de ontem",
                            use_container_width=True)
                if ontem_clicked:
                    st.session_state.active_button = "ontem"
                    st.session_state.start_date = yesterday
                    st.session_state.end_date = yesterday
                    st.rerun()
                
                trinta_dias_clicked = st.form_submit_button("Últimos 30 Dias",
                            type="secondary",
                            help="Dados dos últimos 30 dias",
                            use_container_width=True)
                if trinta_dias_clicked:
                    st.session_state.active_button = "30d"
                    st.session_state.start_date = thirty_days_ago
                    st.session_state.end_date = today
                    st.rerun()
                
                mes_passado_clicked = st.form_submit_button("Mês Passado",
                            type="secondary",
                            help="Dados do mês passado",
                            use_container_width=True)
                if mes_passado_clicked:
                    st.session_state.active_button = "mes_passado"
                    st.session_state.start_date = first_day_of_prev_month
                    st.session_state.end_date = last_day_of_prev_month
                    st.rerun()

            date_col1, date_col2 = st.columns(2)
            with date_col1:
                custom_start = st.date_input("Data Inicial", st.session_state.start_date, key="custom_start_date")
            with date_col2:
                custom_end = st.date_input("Data Final", st.session_state.end_date, key="custom_end_date")
            
            # Botão para aplicar período personalizado
            custom_submitted = st.form_submit_button("Aplicar Período", type="primary", use_container_width=True)
            
            if custom_submitted:
                st.session_state.active_button = "custom"
                st.session_state.start_date = custom_start
                st.session_state.end_date = custom_end
                st.rerun()

    # Atualizar as variáveis locais com os valores da sessão
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

def traffic_filters(df):
    with st.sidebar:
        # Initialize session state variables if they don't exist
        if 'cluster_selected' not in st.session_state:
            st.session_state.cluster_selected = ["Selecionar Todos"]
            
        # Filtros Básicos
        with st.expander("Filtros Básicos", expanded=True):
            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_clusters = sort_by_sessions('Cluster', df)
            
            # Criar o formulário
            with st.form(key="basic_filters_form"):
                # Criar os elementos de filtro
                cluster_selected = st.multiselect(
                    "Cluster",
                    options=all_clusters,
                    default=st.session_state.cluster_selected,
                    key="cluster_select"
                )
                
                # Botão para aplicar filtros básicos
                submitted = st.form_submit_button("Aplicar Filtros Básicos", type="primary", use_container_width=True)
                
                if submitted:
                    st.session_state.cluster_selected = cluster_selected
                    st.rerun()

def traffic_filters_detailed(df):
    with st.sidebar:
        # Initialize all session state variables if they don't exist
        if 'origem_selected' not in st.session_state:
            st.session_state.origem_selected = ["Selecionar Todos"]
        if 'midia_selected' not in st.session_state:
            st.session_state.midia_selected = ["Selecionar Todos"]
        if 'campanha_selected' not in st.session_state:
            st.session_state.campanha_selected = ["Selecionar Todos"]
        if 'conteudo_selected' not in st.session_state:
            st.session_state.conteudo_selected = ["Selecionar Todos"]
        if 'pagina_de_entrada_selected' not in st.session_state:
            st.session_state.pagina_de_entrada_selected = ["Selecionar Todos"]
        if 'categoria_produto_selected' not in st.session_state:
            st.session_state.categoria_produto_selected = ["Selecionar Todos"]
        if 'nome_produto_selected' not in st.session_state:
            st.session_state.nome_produto_selected = ["Selecionar Todos"]
            
        # Filtros existentes
        with st.expander("Filtros Avançados", expanded=False):
            # Adiciona "Selecionar Todos" como primeira opção em cada filtro
            all_origins = sort_by_sessions('Origem', df)
            all_media = sort_by_sessions('Mídia', df)
            all_campaigns = sort_by_sessions('Campanha', df)
            all_content = sort_by_sessions('Conteúdo', df)
            all_pages = sort_by_sessions('Página de Entrada', df)
            
            # Verificar se a coluna 'Categoria do Produto' existe antes de usá-la
            if 'Categoria do Produto' in df.columns:
                all_categories = sort_by_sessions('Categoria do Produto', df)
            else:
                all_categories = ["Selecionar Todos"]
            
            # Verificar se a coluna 'Nome do Produto' existe antes de usá-la
            if 'Nome do Produto' in df.columns:
                all_products = sort_by_sessions('Nome do Produto', df)
            else:
                all_products = ["Selecionar Todos"]
            
            # Criar o formulário
            with st.form(key="advanced_filters_form"):
                # Criar os elementos de filtro
                origem_selected = st.multiselect(
                    "Origem",
                    options=all_origins,
                    default=st.session_state.origem_selected,
                    key="origem_select"
                )
                
                midia_selected = st.multiselect(
                    "Mídia",
                    options=all_media,
                    default=st.session_state.midia_selected,
                    key="midia_select"
                )
                
                campanha_selected = st.multiselect(
                    "Campanha",
                    options=all_campaigns,
                    default=st.session_state.campanha_selected,
                    key="campanha_select"
                )
                
                conteudo_selected = st.multiselect(
                    "Conteúdo",
                    options=all_content,
                    default=st.session_state.conteudo_selected,
                    key="conteudo_select"
                )
                
                pagina_de_entrada_selected = st.multiselect(
                    "Página de Entrada",
                    options=all_pages,
                    default=st.session_state.pagina_de_entrada_selected,
                    key="pagina_de_entrada_select"
                )
                
                # Só mostrar o filtro de categoria se a coluna existir
                if 'Categoria do Produto' in df.columns:
                    categoria_produto_selected = st.multiselect(
                        "Categoria do Produto",
                        options=all_categories,
                        default=st.session_state.categoria_produto_selected,
                        key="categoria_produto_select"
                    )
                else:
                    categoria_produto_selected = ["Selecionar Todos"]
                
                # Só mostrar o filtro de nome do produto se a coluna existir
                if 'Nome do Produto' in df.columns:
                    nome_produto_selected = st.multiselect(
                        "Nome do Produto",
                        options=all_products,
                        default=st.session_state.nome_produto_selected,
                        key="nome_produto_select"
                    )
                else:
                    nome_produto_selected = ["Selecionar Todos"]
                
                # Botão para aplicar filtros avançados
                submitted = st.form_submit_button("Aplicar Filtros Avançados", type="primary", use_container_width=True)
                
                if submitted:
                    st.session_state.origem_selected = origem_selected
                    st.session_state.midia_selected = midia_selected
                    st.session_state.campanha_selected = campanha_selected
                    st.session_state.conteudo_selected = conteudo_selected
                    st.session_state.pagina_de_entrada_selected = pagina_de_entrada_selected
                    st.session_state.categoria_produto_selected = categoria_produto_selected
                    st.session_state.nome_produto_selected = nome_produto_selected
                    st.rerun()

def apply_filters(df):
    """
    Aplica filtros ao DataFrame baseado nas seleções do usuário.
    Não cria elementos UI - apenas aplica a lógica de filtragem.
    """
    # Verificar se o DataFrame está vazio
    if df.empty:
        return df
        
    # Aplicar filtros de cluster
    if "Selecionar Todos" not in st.session_state.cluster_selected:
        df = df[df['Cluster'].isin(st.session_state.cluster_selected)]
    
    # Aplicar filtros de origem
    if "Selecionar Todos" not in st.session_state.origem_selected:
        df = df[df['Origem'].isin(st.session_state.origem_selected)]
    
    # Aplicar filtros de mídia
    if "Selecionar Todos" not in st.session_state.midia_selected:
        df = df[df['Mídia'].isin(st.session_state.midia_selected)]
    
    # Aplicar filtros de campanha
    if "Selecionar Todos" not in st.session_state.campanha_selected:
        df = df[df['Campanha'].isin(st.session_state.campanha_selected)]
    
    # Aplicar filtros de conteúdo
    if "Selecionar Todos" not in st.session_state.conteudo_selected:
        df = df[df['Conteúdo'].isin(st.session_state.conteudo_selected)]
    
    # Aplicar filtros de página de entrada
    if "Selecionar Todos" not in st.session_state.pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(st.session_state.pagina_de_entrada_selected)]
    
    # Aplicar filtros de categoria do produto (só se a coluna existir)
    if 'Categoria do Produto' in df.columns and "Selecionar Todos" not in st.session_state.categoria_produto_selected:
        df = df[df['Categoria do Produto'].isin(st.session_state.categoria_produto_selected)]
    
    # Aplicar filtros de nome do produto (só se a coluna existir)
    if 'Nome do Produto' in df.columns and "Selecionar Todos" not in st.session_state.nome_produto_selected:
        df = df[df['Nome do Produto'].isin(st.session_state.nome_produto_selected)]
    
    return df

    