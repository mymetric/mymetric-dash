import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from modules.load_data import load_coffeemais_users
from modules.components import big_number_box

def display_tab_coffeemais_users():
    st.title("Usuários")

    # Exibir mensagem de loading
    loading_placeholder = st.empty()
    loading_placeholder.info("Carregando dados dos usuários...")

    # Carregar dados
    df = load_coffeemais_users()
    
    # Remover mensagem de loading
    loading_placeholder.empty()

    # Exibir citação aleatória
    with st.container():
        st.markdown(f"*{get_random_quote()}*")
        st.divider()

    # Converter coluna de data e tratar valores nulos
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['pagbrasil_subscription_status'] = df['pagbrasil_subscription_status'].fillna('Não Definido')
    df['pagbrasil_order_status'] = df['pagbrasil_order_status'].fillna('Não Definido')
    df['pagbrasil_payment_date'] = pd.to_datetime(df['pagbrasil_payment_date'], errors='coerce')
    
    # Converter número da recorrência para numérico, tratando valores inválidos
    df['pagbrasil_recurrence_number'] = pd.to_numeric(df['pagbrasil_recurrence_number'], errors='coerce')

    # Adicionar seção colapsável com os big numbers existentes
    with st.expander("Assinantes PagBrasil - Big Numbers", expanded=False):
        st.subheader("Assinantes PagBrasil")

        # Criar colunas para os big numbers
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            active_users = len(df[df['pagbrasil_subscription_status'] == 'Active'])
            big_number_box(active_users, "Assinantes Ativos", hint="Assinantes que estão ativos no momento")
        
        with col2:
            cancelled_users = len(df[df['pagbrasil_subscription_status'] == 'Inactive'])
            big_number_box(cancelled_users, "Assinantes Inativos", hint="Assinantes que não estão ativos no momento")

        with col3:
            pending_payment = len(df[df['pagbrasil_subscription_status'] == 'Pending payment'])
            big_number_box(pending_payment, "Pendentes", hint="Assinantes que ainda não pagaram a assinatura")

        with col4:
            paused_users = len(df[df['pagbrasil_subscription_status'] == 'Paused'])
            big_number_box(paused_users, "Pausados", hint="Assinantes que estão pausados no momento")

        with col5:
            total_users = len(df)
            big_number_box(total_users, "Total", hint="Total de assinantes")

    st.divider()

    # Filtros em expanders
    with st.expander("Filtros", expanded=True):
        # Primeira linha de filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Dropdown para filtrar por status da assinatura
            status_options = ['Todos'] + sorted(df['pagbrasil_subscription_status'].unique().tolist())
            selected_status = st.selectbox('Status da Assinatura:', status_options)
        
        with col2:
            # Dropdown para filtrar por status do pedido
            order_status_options = ['Todos'] + sorted(df['pagbrasil_order_status'].unique().tolist())
            selected_order_status = st.selectbox('Status do Pedido:', order_status_options)
        
        with col3:
            # Campo de busca por email
            search_email = st.text_input('Buscar por Email:', '')
        
        # Segunda linha de filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Dropdown para filtrar por origem do lead
            source_options = ['Todos'] + sorted(df['first_lead_source'].dropna().unique().tolist())
            selected_source = st.selectbox('Origem do Lead:', source_options)
        
        with col2:
            # Dropdown para filtrar por mídia do lead
            medium_options = ['Todos'] + sorted(df['first_lead_medium'].dropna().unique().tolist())
            selected_medium = st.selectbox('Mídia do Lead:', medium_options)
        
        with col3:
            # Dropdown para filtrar por campanha do lead
            campaign_options = ['Todos'] + sorted(df['first_lead_campaign'].dropna().unique().tolist())
            selected_campaign = st.selectbox('Campanha do Lead:', campaign_options)
        
        # Terceira linha de filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Campo de busca por nome
            search_name = st.text_input('Buscar por Nome:', '')
        
        with col2:
            # Campo de busca por telefone
            search_phone = st.text_input('Buscar por Telefone:', '')
        
        with col3:
            # Filtro de data de atualização
            min_date = df['updated_at'].min().date()
            max_date = df['updated_at'].max().date()
            selected_date = st.date_input(
                'Data de Atualização:',
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Quarta linha de filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Dropdown para filtrar por conteúdo do lead
            content_options = ['Todos'] + sorted(df['first_lead_content'].dropna().unique().tolist())
            selected_content = st.selectbox('Conteúdo do Lead:', content_options)
        
        with col2:
            # Dropdown para filtrar por termo do lead
            term_options = ['Todos'] + sorted(df['first_lead_term'].dropna().unique().tolist())
            selected_term = st.selectbox('Termo do Lead:', term_options)
        
        with col3:
            # Dropdown para filtrar por página do lead
            page_options = ['Todos'] + sorted(df['first_lead_page_location'].dropna().unique().tolist())
            selected_page = st.selectbox('Página do Lead:', page_options)
        
        # Quinta linha de filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Campo de busca por ID da recorrência
            search_recurrence_id = st.text_input('Buscar por ID da Recorrência:', '')
        
        with col2:
            # Range slider para número da recorrência
            min_recurrence = df['pagbrasil_recurrence_number'].min()
            max_recurrence = df['pagbrasil_recurrence_number'].max()
            
            if pd.notna(min_recurrence) and pd.notna(max_recurrence):
                selected_recurrence_range = st.slider(
                    'Número da Recorrência:',
                    min_value=float(min_recurrence),
                    max_value=float(max_recurrence),
                    value=(float(min_recurrence), float(max_recurrence)),
                    step=1.0
                )
            else:
                st.info("Sem dados de recorrência disponíveis")
        
        with col3:
            # Filtro de data de pagamento
            min_payment_date = df['pagbrasil_payment_date'].min().date() if not df['pagbrasil_payment_date'].empty else None
            max_payment_date = df['pagbrasil_payment_date'].max().date() if not df['pagbrasil_payment_date'].empty else None
            
            if min_payment_date and max_payment_date:
                selected_payment_date = st.date_input(
                    'Data do Pagamento:',
                    value=(min_payment_date, max_payment_date),
                    min_value=min_payment_date,
                    max_value=max_payment_date
                )
            else:
                st.info("Sem dados de pagamento disponíveis")

    # Aplicar filtros
    filtered_df = df.copy()

    if selected_status != 'Todos':
        filtered_df = filtered_df[filtered_df['pagbrasil_subscription_status'] == selected_status]
    
    if selected_order_status != 'Todos':
        filtered_df = filtered_df[filtered_df['pagbrasil_order_status'] == selected_order_status]

    if search_email:
        filtered_df = filtered_df[filtered_df['email'].str.contains(search_email, case=False, na=False)]
    
    if search_name:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]
    
    if search_phone:
        filtered_df = filtered_df[filtered_df['phone'].str.contains(search_phone, case=False, na=False)]
    
    if selected_source != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_source'] == selected_source]
    
    if selected_medium != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_medium'] == selected_medium]
    
    if selected_campaign != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_campaign'] == selected_campaign]
    
    if selected_content != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_content'] == selected_content]
    
    if selected_term != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_term'] == selected_term]
    
    if selected_page != 'Todos':
        filtered_df = filtered_df[filtered_df['first_lead_page_location'] == selected_page]
    
    if search_recurrence_id:
        filtered_df = filtered_df[filtered_df['pagbrasil_recurrence_id'].str.contains(search_recurrence_id, case=False, na=False)]
    
    # Aplicar filtro de número da recorrência
    if 'selected_recurrence_range' in locals():
        min_recurrence, max_recurrence = selected_recurrence_range
        filtered_df = filtered_df[
            (filtered_df['pagbrasil_recurrence_number'] >= min_recurrence) & 
            (filtered_df['pagbrasil_recurrence_number'] <= max_recurrence)
        ]
        
    # Aplicar filtro de data de atualização se duas datas foram selecionadas
    if len(selected_date) == 2:
        start_date, end_date = selected_date
        # Ajustar end_date para incluir todo o dia
        end_date = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[
            (filtered_df['updated_at'] >= pd.Timestamp(start_date)) & 
            (filtered_df['updated_at'] <= pd.Timestamp(end_date))
        ]
    
    # Aplicar filtro de data de pagamento se duas datas foram selecionadas
    if 'selected_payment_date' in locals() and len(selected_payment_date) == 2:
        start_date, end_date = selected_payment_date
        # Ajustar end_date para incluir todo o dia
        end_date = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[
            (filtered_df['pagbrasil_payment_date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['pagbrasil_payment_date'] <= pd.Timestamp(end_date))
        ]

    # Renomear colunas para exibição
    display_df = filtered_df.copy()
    display_df.columns = [
        'Data de Atualização',
        'E-mail',
        'Nome',
        'Telefone',
        'Origem do Lead',
        'Mídia do Lead',
        'Campanha do Lead',
        'Conteúdo do Lead',
        'Termo do Lead',
        'Página do Lead',
        'ID da Recorrência',
        'Número da Recorrência',
        'Link da Assinatura',
        'Data do Pagamento',
        'Status da Assinatura',
        'Status do Pedido'
    ]

    st.data_editor(display_df, use_container_width=True, hide_index=True)