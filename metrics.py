import streamlit as st
from helpers import components

def display_metrics(df, tx_cookies, df_ads):


    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (total_receita_paga / total_receita_capturada) * 100

    st.header("Big Numbers")

    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        
        components.big_number_box(f"{pedidos:,}", "Pedidos Capturados")
    
    with col2:
        components.big_number_box(f"{pedidos_pagos:,}", "Pedidos Pagos")

    with col3:
        components.big_number_box(f"R$ {total_receita_capturada:,.0f}", "Receita Capturada")

    with col4:
        components.big_number_box(f"R$ {total_receita_paga:,.0f}", "Receita Paga")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        components.big_number_box(f"{sessoes:,}", "Sessões")

    with col2:
        components.big_number_box(f"{tx_conv:.2f}%", "Tx Conversão")

    with col3:
        components.big_number_box(f"{tx_cookies:.2f}%", "Tx Perda de Cookies Hoje")

    with col4:
        components.big_number_box(f"{round(percentual_pago,2)}%", "% Pago")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(f"R$ {round(df_ads['Investimento'].sum(),2):,}", "Investimento Total em Ads")
    with col2:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(f"{(df_ads['Investimento'].sum() / total_receita_paga) * 100:.2f}%", "TACoS")

    # Filtra os dados para a plataforma google_ads
    if not df_ads.empty:
        df_google_ads = df_ads[df_ads['Plataforma'] == 'google_ads']
        df_meta_ads = df_ads[df_ads['Plataforma'] == 'meta_ads']

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_google_ads.empty and df_google_ads['Investimento'].sum() > 0:
            with col3:
                gads_connect_rate = df[df['Cluster'] == "🟢 Google Ads"]["Sessões"].sum()/df_ads[df_ads['Plataforma'] =="google_ads"]["Cliques"].sum()*100
                components.big_number_box(
                    f"R$ {round(df_google_ads['Investimento'].sum(), 2):,}".replace(",", "."), 
                    "Investimento em Google Ads"
                )

                components.big_number_box(f"{gads_connect_rate:.1f}%", "Connect Rate Google Ads")

                st.toast("Nova Métrica: Connect Rate", icon="👀")

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_meta_ads.empty and df_meta_ads['Investimento'].sum() > 0:
            with col4:
                mads_connect_rate = df[df['Cluster'] == "🔵 Meta Ads"]["Sessões"].sum()/df_ads[df_ads['Plataforma'] =="meta_ads"]["Cliques"].sum()*100
                components.big_number_box(
                    f"R$ {round(df_meta_ads['Investimento'].sum(), 2):,}".replace(",", "."), 
                    "Investimento em Meta Ads"
                )
                components.big_number_box(f"{mads_connect_rate:.1f}%", "Connect Rate Meta Ads")


    st.markdown("---")
