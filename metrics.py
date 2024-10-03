import streamlit as st

def display_metrics(df):
    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()

    st.header("Big Numbers")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Sessões", f"{sessoes:,}")

    with col2:
        st.metric("Pedidos", f"{pedidos}")

    with col3:
        st.metric("Tx Conversão", f"{tx_conv:.2f}%")

    with col4:
        st.metric("Receita Capturada", f"R$ {total_receita_capturada:,.2f}%")

    with col5:
        st.metric("Receita Paga", f"R$ {total_receita_paga:,.2f}")