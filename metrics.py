import streamlit as st

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

    def big_number_box(data, label):
        st.markdown(f"""
            <div style="background-color:#C5EBC3;padding:20px;border-radius:10px;text-align:center;margin:5px">
                <p style="color:#666;line-height:1">{label}</h3>
                <p style="color:#666;line-height:1;font-size:40px;margin:0;">{data}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col1:
        
        big_number_box(f"{pedidos}", "Pedidos Capturados")
    
    with col2:
        big_number_box(f"{pedidos_pagos}", "Pedidos Pagos")
        

    with col3:
        big_number_box(f"R$ {total_receita_capturada:,.2f}", "Receita Capturada")

    with col4:
        big_number_box(f"R$ {total_receita_paga:,.2f}", "Receita Paga")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        big_number_box(f"{sessoes:,}", "Sessões")

    with col2:
        big_number_box(f"{tx_conv:.2f}%", "Tx Conversão")

    with col3:
        big_number_box(f"{tx_cookies:.2f}%", "Tx Perda de Cookies Hoje")

    with col4:
        big_number_box(f"{round(percentual_pago,2)}%", "% Pago")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento Ads'].sum() > 0:
            big_number_box(f"R$ {round(df_ads['Investimento Ads'].sum(),2):,}", "Investimento Total em Ads")
    with col2:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento Ads'].sum() > 0:
            big_number_box(f"{(df_ads['Investimento Ads'].sum() / total_receita_paga) * 100:.2f}%", "TACoS")

    # Filtra os dados para a plataforma google_ads
    if not df_ads.empty:
        df_google_ads = df_ads[df_ads['Plataforma'] == 'google_ads']
        df_meta_ads = df_ads[df_ads['Plataforma'] == 'meta_ads']

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_google_ads.empty and df_google_ads['Investimento Ads'].sum() > 0:
            with col3:
                big_number_box(
                    f"R$ {round(df_google_ads['Investimento Ads'].sum(), 2):,}".replace(",", "."), 
                    "Investimento Total em Google Ads"
                )

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_meta_ads.empty and df_meta_ads['Investimento Ads'].sum() > 0:
            with col4:
                big_number_box(
                    f"R$ {round(df_meta_ads['Investimento Ads'].sum(), 2):,}".replace(",", "."), 
                    "Investimento Total em Meta Ads"
                )


    st.markdown("---")
