import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from modules.load_data import load_coffeemais_users
from modules.components import big_number_box

def display_tab_coffeemais_users():
    st.title("Usuários")

    # Load data
    df = load_coffeemais_users()
    
    # Converter coluna de data e tratar valores nulos
    df['Data de Atualização'] = pd.to_datetime(df['Data de Atualização'])
    df['Status da Assinatura'] = df['Status da Assinatura'].fillna('Não Definido')

    st.subheader("Assinantes PagBrasil")
    st.write("Dados atualizados uma vez ao dia de manhã")

    # Criar colunas para os big numbers
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        active_users = len(df[df['Status da Assinatura'] == 'Active'])
        big_number_box(active_users, "Assinantes Ativos", hint="Assinantes que estão ativos no momento")
    
    with col2:
        cancelled_users = len(df[df['Status da Assinatura'] == 'Inactive'])
        big_number_box(cancelled_users, "Assinantes Inativos", hint="Assinantes que não estão ativos no momento")

    with col3:
        pending_payment = len(df[df['Status da Assinatura'] == 'Pending payment'])
        big_number_box(pending_payment, "Pendentes", hint="Assinantes que ainda não pagaram a assinatura")

    with col4:
        paused_users = len(df[df['Status da Assinatura'] == 'Paused'])
        big_number_box(paused_users, "Pausados", hint="Assinantes que estão pausados no momento")

    with col5:
        total_users = len(df)
        big_number_box(total_users, "Total", hint="Total de assinantes")

    st.divider()

    # Filtros em três colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Dropdown para filtrar por status
        status_options = ['Todos'] + sorted(df['Status da Assinatura'].unique().tolist())
        selected_status = st.selectbox('Filtrar por Status da Assinatura:', status_options)
    
    with col2:
        # Campo de busca por email
        search_email = st.text_input('Buscar por Email:', '')
        
    with col3:
        # Filtro de data
        min_date = df['Data de Atualização'].min().date()
        max_date = df['Data de Atualização'].max().date()
        selected_date = st.date_input(
            'Filtrar por Data de Atualização:',
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    # Aplicar filtros
    if selected_status != 'Todos':
        filtered_df = df[df['Status da Assinatura'] == selected_status]
    else:
        filtered_df = df

    if search_email:
        filtered_df = filtered_df[filtered_df['E-mail'].str.contains(search_email, case=False, na=False)]
        
    # Aplicar filtro de data se duas datas foram selecionadas
    if len(selected_date) == 2:
        start_date, end_date = selected_date
        # Ajustar end_date para incluir todo o dia
        end_date = datetime.combine(end_date, datetime.max.time())
        filtered_df = filtered_df[
            (filtered_df['Data de Atualização'] >= pd.Timestamp(start_date)) & 
            (filtered_df['Data de Atualização'] <= pd.Timestamp(end_date))
        ]

    st.data_editor(filtered_df, use_container_width=True, hide_index=True)