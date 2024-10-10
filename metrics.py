import streamlit as st

def display_metrics(df, tx_cookies):
    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()

    st.header("Big Numbers")

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.metric("Sessões", f"{sessoes:,}")

    with col2:
        st.metric("Pedidos", f"{pedidos}")
    
    with col3:
        st.metric("Pedidos Pagos", f"{pedidos_pagos}")

    with col4:
        st.metric("Tx Perda de Cookies Hoje", f"{tx_cookies:.2f}%")
    
    with col5:
        st.metric("Tx Conversão", f"{tx_conv:.2f}%")

    with col6:
        st.metric("Receita Capturada", f"R$ {total_receita_capturada:,.2f}")

    with col7:
        st.metric("Receita Paga", f"R$ {total_receita_paga:,.2f}")