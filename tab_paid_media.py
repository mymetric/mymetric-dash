import streamlit as st
import pandas as pd
from query_utils import run_query

def execute_query(client, query):
    return run_query(client, query)
    
def display_tab_paid_media(client, table, df_ads):

    


    # Unique options for dropdown filters
    platform_options = ["All"] + sorted(df_ads['Plataforma'].dropna().unique().tolist())
    campaign_options = ["All"] + sorted(df_ads['Campanha'].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_platform = st.selectbox("Plataforma:", platform_options)

    with col2:
        campaign_filter = st.text_input("Campanha:", "")

    if selected_platform != "All":
        df_ads = df_ads[df_ads['Plataforma'] == selected_platform]

    if campaign_filter:
        df_ads = df_ads[df_ads['Campanha'].str.contains(campaign_filter, case=False, na=False)]

    # Group by platform and campaign, aggregating relevant metrics
    df_ads_agg = df_ads.groupby(['Plataforma', 'Campanha']).agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Receita': 'sum'
    }).reset_index()

    # Calculate ROAS and CPV, adding them as new columns
    df_ads_agg['ROAS'] = (df_ads_agg['Receita'] / df_ads_agg['Investimento'].replace(0, float('nan'))).round(2)
    df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações'].replace(0, float('nan'))).round(2)

    # Round other numerical columns to 2 decimal places
    df_ads_agg[['Investimento', 'Impressões', 'Cliques', 'Transações', 'Receita']] = df_ads_agg[['Investimento', 'Impressões', 'Cliques', 'Transações', 'Receita']].round(2)

    # Order by revenue in descending order
    df_ads_agg = df_ads_agg.sort_values(by='Receita', ascending=False).reset_index(drop=True)

    # Display the aggregated data in Streamlit data editor
    st.data_editor(df_ads_agg, hide_index=1, use_container_width=1)



    summary_row = pd.DataFrame({
        'Investimento': [df_ads_agg['Investimento'].sum()],
        'Transações': [df_ads_agg['Transações'].sum()],
        'Receita': [df_ads_agg['Receita'].sum()],
        'ROAS': [df_ads_agg['Receita'].sum() / df_ads_agg['Investimento'].sum()]
    })
    st.write("Totais")
    st.data_editor(summary_row, hide_index=1, use_container_width=1)



    qa = f"""
        select

            sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`

        from `mymetric-hub-shopify.dbt_join.{table}_sessions_gclids`

        where

        event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
        and page_params like "%fbclid%"
    """

    qa = execute_query(client, qa)

    st.write(f"{qa['Cobertura'].sum().round(2):.1%} do tráfego de Meta está no padrão de tagueamento desejado. Leia sobre o [padrão de tagueamento](https://mymetric.notion.site/Parametriza-o-de-Meta-Ads-a32df743c4e046ccade33720f0faec3a)")




