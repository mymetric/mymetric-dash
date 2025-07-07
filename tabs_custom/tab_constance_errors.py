import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import json

from modules.load_data import load_constance_errors
from modules.components import big_number_box
from partials.run_rate import display_run_rate
from partials.pendings import display_pendings
from partials.performance import display_performance
from partials.notices import display_notices

def calculate_lost_revenue(df):
    """
    Calcula a projeção de vendas perdidas baseada na taxa de abandono e ticket médio
    """
    if df.empty:
        return 0, 0
    
    # Calcular vendas perdidas por erro
    # Vendas perdidas = quantidade de erros * taxa de abandono * ticket médio
    df_with_lost = df.copy()
    df_with_lost['lost_revenue'] = df_with_lost['errors'] * (df_with_lost['dropoff_rate'] / 100) * df_with_lost['purchase_revenue']
    
    # Soma total de vendas perdidas
    total_lost_revenue = df_with_lost['lost_revenue'].sum()
    
    # Projeção para 30 dias (assumindo que os dados são diários)
    # Se não temos informação sobre o período, assumimos que é o período atual do dashboard
    projection_30_days = total_lost_revenue * 30
    
    return total_lost_revenue, projection_30_days

def display_tab_constance_errors():
    """
    Função principal para exibir a aba de erros do cliente constance
    """
    st.title("Análise de Erros")
    st.markdown("<span style='font-size:16px;'>Erros que ocorrem no checkout e afetam a experiência do usuário. Dados de hoje.</span>", unsafe_allow_html=True)
    
    # Verificar se é o cliente correto
    if st.session_state.get('tablename') != 'constance':
        st.error("Esta aba está disponível apenas para o cliente Constance.")
        return
    
    # Carregar dados de erros
    with st.spinner("Carregando dados de erros..."):
        df = load_constance_errors()
    
    if df is not None and not df.empty:
        # Corrigir dropoff_rate para exibição (multiplicar por 100)
        df = df.copy()
        df['dropoff_rate'] = df['dropoff_rate'] * 100
        
        # Calcular vendas perdidas
        lost_revenue, projection_30_days = calculate_lost_revenue(df)
        
        # Exibir resumo
        display_error_summary(df, lost_revenue, projection_30_days)
        # Exibir tabela
        display_error_table(df)
    else:
        st.warning("Não foi possível carregar dados de erros. Verifique se a tabela `constance-421122.views.error` existe e contém dados.")

def display_error_summary(df, lost_revenue, projection_30_days):
    """
    Exibe resumo dos erros com métricas principais
    """
    if df.empty:
        st.warning("Nenhum dado de erro encontrado.")
        return
    
    # Calcular métricas principais
    total_errors = df['errors'].sum()
    avg_dropoff_rate = df['dropoff_rate'].mean()
    avg_ticket = df['purchase_revenue'].mean()
    unique_errors = len(df)
    
    st.header("Resumo de Erros")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        big_number_box(
            f"{total_errors:,.0f}".replace(",", "."),
            "Total de Erros",
            hint="Soma total de todos os erros registrados"
        )
    
    with col2:
        big_number_box(
            f"{unique_errors:,.0f}".replace(",", "."),
            "Tipos de Erro Únicos",
            hint="Número de tipos diferentes de erro"
        )
    
    with col3:
        big_number_box(
            f"{avg_dropoff_rate:.2f}%".replace(".", ","),
            "Taxa de Abandono Média",
            hint="Taxa de abandono média entre todos os erros"
        )
    
    with col4:
        big_number_box(
            f"R$ {lost_revenue:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Perdas Projetadas Hoje",
            hint="Valor estimado de vendas perdidas devido aos erros de hoje"
        )
    
    with col5:
        big_number_box(
            f"R$ {projection_30_days:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Projeção 30 Dias",
            hint="Projeção de vendas perdidas para os próximos 30 dias baseada nos dados de hoje"
        )
    
    st.markdown("---")

def display_error_table(df):
    """
    Exibe tabela detalhada dos erros
    """
    if df.empty:
        return
    
    st.subheader("Tabela Detalhada de Erros")
    
    # Calcular vendas perdidas por linha
    df_with_lost = df.copy()
    df_with_lost['lost_revenue'] = df_with_lost['errors'] * (df_with_lost['dropoff_rate'] / 100) * df_with_lost['purchase_revenue']
    
    # Calcular projeção de 30 dias para cada erro
    df_with_lost['projection_30_days'] = df_with_lost['lost_revenue'] * 30
    
    # Preparar dados para exibição mantendo valores numéricos para sorting
    display_df = df_with_lost.copy()
    
    # Renomear colunas para português
    display_df = display_df.rename(columns={
        'error_message': 'Mensagem de Erro',
        'errors': 'Quantidade',
        'dropoff_rate': 'Taxa de Abandono',
        'purchase_revenue': 'Ticket Médio',
        'lost_revenue': 'Vendas Perdidas',
        'projection_30_days': 'Projeção 30 Dias'
    })
    
    # Reordenar as colunas
    display_df = display_df[[
        'Mensagem de Erro',
        'Quantidade',
        'Taxa de Abandono',
        'Ticket Médio',
        'Vendas Perdidas',
        'Projeção 30 Dias'
    ]]
    
    # Ordenar por vendas perdidas em ordem decrescente
    display_df = display_df.sort_values(by='Vendas Perdidas', ascending=False)
    
    # Aplicar formatação usando pandas styling (mantém valores numéricos para sorting)
    styled_df = display_df.style.format({
        'Quantidade': lambda x: f"{int(x):,}".replace(",", "."),
        'Taxa de Abandono': lambda x: f"{float(x):.2f}%".replace(".", ","),
        'Ticket Médio': lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
        'Vendas Perdidas': lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
        'Projeção 30 Dias': lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", ".")
    })
    
    # Exibir tabela com formatação
    st.dataframe(styled_df, hide_index=True, use_container_width=True) 