import streamlit as st
import pandas as pd
from modules.load_data import load_coffeemais_cohort
from datetime import datetime, timedelta

def display_cohort_analysis():
    """Display cohort analysis for Coffeemais"""
    st.title("Cohort")
    
    # Load data
    df = load_coffeemais_cohort()
    
    if df.empty:
        st.error("Não foi possível carregar os dados.")
        return
    
    # Convert month to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['month']):
        df['month'] = pd.to_datetime(df['month'])
    
    # Filter by date range from session state
    start_date = pd.to_datetime(st.session_state.start_date)
    end_date = pd.to_datetime(st.session_state.end_date)
    df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    
    # Add cluster filter (excluding 'global')
    clusters = sorted([c for c in df['sessions_cluster'].unique() if c != 'global'])
    selected_cluster = st.selectbox(
        "Filtrar Cluster:",
        ["Todos"] + clusters
    )
    
    # Filter data by selected cluster plus global
    df_filtered = df.copy()
    if selected_cluster != "Todos":
        df_filtered = df[df['sessions_cluster'].isin([selected_cluster, 'global'])]
    
    # Add global and specific orders
    global_by_purchase = df_filtered[df_filtered['sessions_cluster'] == 'global'].groupby('purchase_number')['orders'].sum().reset_index()
    specific_by_purchase = df_filtered[df_filtered['sessions_cluster'] != 'global'].groupby('purchase_number')['orders'].sum().reset_index()
    
    # Merge with safe handling of missing data
    purchase_analysis = global_by_purchase.rename(columns={'orders': 'orders_global'}).merge(
        specific_by_purchase.rename(columns={'orders': 'orders_specific'}),
        on='purchase_number',
        how='outer'
    )
    
    # Fill NaN values with 0
    purchase_analysis = purchase_analysis.fillna(0)
    
    # Calculate conversion rate
    purchase_analysis['conversion_rate'] = (purchase_analysis['orders_specific'] / purchase_analysis['orders_global'] * 100)
    purchase_analysis['conversion_rate'] = purchase_analysis['conversion_rate'].fillna(0)
    
    # Rename columns
    purchase_analysis = purchase_analysis.rename(columns={
        'purchase_number': 'Número da Compra',
        'orders_global': 'Base 12 Meses',
        'orders_specific': 'Base Atual',
        'conversion_rate': 'Conversão'
    })
    
    # Format numbers
    purchase_analysis['Base 12 Meses'] = purchase_analysis['Base 12 Meses'].apply(lambda x: f"{x:,.0f}")
    purchase_analysis['Base Atual'] = purchase_analysis['Base Atual'].apply(lambda x: f"{x:,.0f}")
    purchase_analysis['Conversão'] = purchase_analysis['Conversão'].apply(lambda x: f"{x:.2f}%")
    
    # Display purchase number analysis
    st.data_editor(
        purchase_analysis,
        hide_index=True,
        use_container_width=True
    )

def display_tab_coffeemais_cohort():
    """Main function to display the Coffeemais cohort tab"""
    display_cohort_analysis() 