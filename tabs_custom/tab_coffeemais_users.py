import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from modules.load_data import load_coffeemais_users
from modules.components import big_number_box
import locale

def display_tab_coffeemais_users():
    st.title("Usuários")

    # Configurar locale para formato brasileiro
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')

    # Exibir mensagem de loading
    loading_placeholder = st.empty()
    loading_placeholder.info("Carregando dados dos usuários...")

    # Carregar dados
    df = load_coffeemais_users()
    
    # Remover mensagem de loading
    loading_placeholder.empty()

    # Converter coluna de data e tratar valores nulos
    date_columns = [
        'updated_at',
        'pagbrasil_payment_date',
        'last_purchase_date',
        'first_purchase_date',
        'second_purchase_date'
    ]
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Converter colunas numéricas
    numeric_columns = [
        'pagbrasil_recurrence_number',
        'last_purchase_revenue',
        'first_purchase_revenue',
        'second_purchase_revenue',
        'total_revenue',
        'purchase_quantity',
        'last_total_items_distinct',
        'last_total_items_quantity',
        'lifetime_total_items_distinct',
        'lifetime_total_items_quantity'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Tratar valores nulos em colunas de texto
    text_columns = [
        'pagbrasil_subscription_status',
        'pagbrasil_order_status',
        'last_purchase_cluster',
        'first_purchase_cluster',
        'second_purchase_cluster'
    ]
    
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('Não Definido')

    # Exibir total de usuários como big number principal
    total_users = len(df)
    formatted_total = "{:,}".format(total_users).replace(',', '.')
    st.markdown("### Total de Usuários")
    big_number_box(formatted_total, "Total de Usuários", hint="Número total de usuários cadastrados")
    
    st.divider()

    # Adicionar seção colapsável com os big numbers do PagBrasil
    with st.expander("Assinantes PagBrasil - Big Numbers", expanded=False):
        st.subheader("Assinantes PagBrasil")

        # Criar colunas para os big numbers
        col1, col2, col3, col4 = st.columns(4)

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

    st.divider()

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
        
        # Purchase metrics
        'total_revenue': 'Total de Receita',
        'purchase_quantity': 'Quantidade de Compras',
        
        # Purchase timeline
        'first_purchase_date': 'Data da Primeira Compra',
        'first_purchase_revenue': 'Receita da Primeira Compra',
        'first_purchase_cluster': 'Cluster da Primeira Compra',
        'second_purchase_date': 'Data da Segunda Compra',
        'second_purchase_revenue': 'Receita da Segunda Compra',
        'second_purchase_cluster': 'Cluster da Segunda Compra',
        'last_purchase_date': 'Data da Última Compra',
        'last_purchase_revenue': 'Receita da Última Compra',
        'last_purchase_cluster': 'Cluster da Última Compra',
        
        # Item metrics
        'last_total_items_distinct': 'Itens Distintos (Última)',
        'last_total_items_quantity': 'Quantidade Itens (Última)',
        'lifetime_total_items_distinct': 'Itens Distintos (Total)',
        'lifetime_total_items_quantity': 'Quantidade Itens (Total)',
        
        # PagBrasil subscription info
        'pagbrasil_subscription_id': 'ID da Assinatura',
        'pagbrasil_recurrence_id': 'ID da Recorrência',
        'pagbrasil_recurrence_number': 'Número da Recorrência',
        'pagbrasil_subscription_link': 'Link da Assinatura',
        'pagbrasil_payment_date': 'Data do Pagamento',
        'pagbrasil_subscription_status': 'Status da Assinatura',
        'pagbrasil_order_status': 'Status do Pedido'
    }

    # Criar uma cópia do DataFrame e renomear as colunas
    display_df = df.copy()
    display_df = display_df.rename(columns={k: v for k, v in column_mapping.items() if k in display_df.columns})

    # Configuração das colunas
    column_config = {}
    
    # Configurar colunas de data
    for old_col, new_col in column_mapping.items():
        if old_col in date_columns:
            column_config[new_col] = st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")
        elif old_col in ['last_purchase_revenue', 'first_purchase_revenue', 'second_purchase_revenue', 'total_revenue']:
            column_config[new_col] = st.column_config.NumberColumn(format="R$ %.2f")
        elif old_col in ['purchase_quantity', 'pagbrasil_recurrence_number', 'last_total_items_distinct', 'last_total_items_quantity', 'lifetime_total_items_distinct', 'lifetime_total_items_quantity']:
            column_config[new_col] = st.column_config.NumberColumn(format="%d")
        elif old_col == 'pagbrasil_subscription_link':
            column_config[new_col] = st.column_config.LinkColumn()

    # Exibir o DataFrame
    st.dataframe(
        display_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )