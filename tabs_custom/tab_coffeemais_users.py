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

    # Converter coluna de data e tratar valores nulos
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['pagbrasil_subscription_status'] = df['pagbrasil_subscription_status'].fillna('Não Definido')
    df['pagbrasil_order_status'] = df['pagbrasil_order_status'].fillna('Não Definido')
    df['pagbrasil_payment_date'] = pd.to_datetime(df['pagbrasil_payment_date'], errors='coerce')
    
    # Converter número da recorrência para numérico, tratando valores inválidos
    df['pagbrasil_recurrence_number'] = pd.to_numeric(df['pagbrasil_recurrence_number'], errors='coerce')

    # Adicionar campos de compra
    df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')
    df['first_purchase_date'] = pd.to_datetime(df['first_purchase_date'], errors='coerce')
    df['last_purchase_revenue'] = pd.to_numeric(df['last_purchase_revenue'], errors='coerce')
    df['first_purchase_revenue'] = pd.to_numeric(df['first_purchase_revenue'], errors='coerce')
    df['last_purchase_cluster'] = df['last_purchase_cluster'].fillna('Não Definido')
    df['first_purchase_cluster'] = df['first_purchase_cluster'].fillna('Não Definido')
    df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce').fillna(0)
    df['purchase_quantity'] = pd.to_numeric(df['purchase_quantity'], errors='coerce').fillna(0)

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

        # Sexta linha de filtros - Campos de compra
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro de data da última compra
            min_last_purchase = df['last_purchase_date'].min().date() if not df['last_purchase_date'].empty else None
            max_last_purchase = df['last_purchase_date'].max().date() if not df['last_purchase_date'].empty else None
            
            if min_last_purchase and max_last_purchase:
                selected_last_purchase_date = st.date_input(
                    'Data da Última Compra:',
                    value=(min_last_purchase, max_last_purchase),
                    min_value=min_last_purchase,
                    max_value=max_last_purchase
                )
            else:
                st.info("Sem dados de última compra disponíveis")
        
        with col2:
            # Filtro de data da primeira compra
            min_first_purchase = df['first_purchase_date'].min().date() if not df['first_purchase_date'].empty else None
            max_first_purchase = df['first_purchase_date'].max().date() if not df['first_purchase_date'].empty else None
            
            if min_first_purchase and max_first_purchase:
                selected_first_purchase_date = st.date_input(
                    'Data da Primeira Compra:',
                    value=(min_first_purchase, max_first_purchase),
                    min_value=min_first_purchase,
                    max_value=max_first_purchase
                )
            else:
                st.info("Sem dados de primeira compra disponíveis")
        
        with col3:
            # Dropdown para filtrar por cluster da última compra
            cluster_options = ['Todos'] + sorted(df['last_purchase_cluster'].dropna().unique().tolist())
            selected_last_cluster = st.selectbox('Cluster da Última Compra:', cluster_options)

        # Sétima linha de filtros - Mais campos de compra
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Dropdown para filtrar por cluster da primeira compra
            cluster_options = ['Todos'] + sorted(df['first_purchase_cluster'].dropna().unique().tolist())
            selected_first_cluster = st.selectbox('Cluster da Primeira Compra:', cluster_options)
        
        with col2:
            # Input para receita total
            min_revenue = df['total_revenue'].min()
            max_revenue = df['total_revenue'].max()
            
            if pd.notna(min_revenue) and pd.notna(max_revenue):
                col_revenue_min, col_revenue_max = st.columns(2)
                with col_revenue_min:
                    min_revenue_input = st.number_input(
                        'Receita Total Mínima:',
                        min_value=float(min_revenue),
                        max_value=float(max_revenue),
                        value=float(min_revenue),
                        step=1.0
                    )
                with col_revenue_max:
                    max_revenue_input = st.number_input(
                        'Receita Total Máxima:',
                        min_value=float(min_revenue),
                        max_value=float(max_revenue),
                        value=float(max_revenue),
                        step=1.0
                    )
                selected_revenue_range = (min_revenue_input, max_revenue_input)
            else:
                st.info("Sem dados de receita disponíveis")
        
        with col3:
            # Input para quantidade de compras
            min_quantity = df['purchase_quantity'].min()
            max_quantity = df['purchase_quantity'].max()
            
            if pd.notna(min_quantity) and pd.notna(max_quantity):
                col_quantity_min, col_quantity_max = st.columns(2)
                with col_quantity_min:
                    min_quantity_input = st.number_input(
                        'Quantidade Mínima:',
                        min_value=float(min_quantity),
                        max_value=float(max_quantity),
                        value=float(min_quantity),
                        step=1.0
                    )
                with col_quantity_max:
                    max_quantity_input = st.number_input(
                        'Quantidade Máxima:',
                        min_value=float(min_quantity),
                        max_value=float(max_quantity),
                        value=float(max_quantity),
                        step=1.0
                    )
                selected_quantity_range = (min_quantity_input, max_quantity_input)
            else:
                st.info("Sem dados de quantidade disponíveis")

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

    # Aplicar filtros de compra
    if 'selected_last_purchase_date' in locals() and len(selected_last_purchase_date) == 2:
        start_date, end_date = selected_last_purchase_date
        end_date = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[
            (filtered_df['last_purchase_date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['last_purchase_date'] <= pd.Timestamp(end_date))
        ]

    if 'selected_first_purchase_date' in locals() and len(selected_first_purchase_date) == 2:
        start_date, end_date = selected_first_purchase_date
        end_date = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[
            (filtered_df['first_purchase_date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['first_purchase_date'] <= pd.Timestamp(end_date))
        ]

    if selected_last_cluster != 'Todos':
        filtered_df = filtered_df[filtered_df['last_purchase_cluster'] == selected_last_cluster]

    if selected_first_cluster != 'Todos':
        filtered_df = filtered_df[filtered_df['first_purchase_cluster'] == selected_first_cluster]

    if 'selected_revenue_range' in locals():
        min_revenue, max_revenue = selected_revenue_range
        filtered_df = filtered_df[
            (filtered_df['total_revenue'] >= min_revenue) & 
            (filtered_df['total_revenue'] <= max_revenue)
        ]

    if 'selected_quantity_range' in locals():
        min_quantity, max_quantity = selected_quantity_range
        filtered_df = filtered_df[
            (filtered_df['purchase_quantity'] >= min_quantity) & 
            (filtered_df['purchase_quantity'] <= max_quantity)
        ]

    # Renomear colunas para exibição
    display_df = filtered_df.copy()
    
    # Mapeamento de colunas existentes
    column_mapping = {
        'updated_at': 'Data de Atualização',
        'email': 'E-mail',
        'name': 'Nome',
        'phone': 'Telefone',
        'first_lead_source': 'Origem do Lead',
        'first_lead_medium': 'Mídia do Lead',
        'first_lead_campaign': 'Campanha do Lead',
        'first_lead_content': 'Conteúdo do Lead',
        'first_lead_term': 'Termo do Lead',
        'first_lead_page_location': 'Página do Lead',
        'pagbrasil_recurrence_id': 'ID da Recorrência',
        'pagbrasil_recurrence_number': 'Número da Recorrência',
        'pagbrasil_subscription_link': 'Link da Assinatura',
        'pagbrasil_payment_date': 'Data do Pagamento',
        'pagbrasil_subscription_status': 'Status da Assinatura',
        'pagbrasil_order_status': 'Status do Pedido',
        'last_purchase_date': 'Data da Última Compra',
        'last_purchase_revenue': 'Receita da Última Compra',
        'last_purchase_cluster': 'Cluster da Última Compra',
        'first_purchase_date': 'Data da Primeira Compra',
        'first_purchase_revenue': 'Receita da Primeira Compra',
        'first_purchase_cluster': 'Cluster da Primeira Compra',
        'total_revenue': 'Total de Receita',
        'purchase_quantity': 'Quantidade de Compras'
    }
    
    # Renomear apenas as colunas que existem no DataFrame
    display_df = display_df.rename(columns={k: v for k, v in column_mapping.items() if k in display_df.columns})

    st.data_editor(display_df, use_container_width=True, hide_index=True)