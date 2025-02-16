import streamlit as st
from modules.load_data import load_last_orders

def display_tab_last_orders():
    st.title("🛒 Últimos Pedidos")
    st.markdown("""---""")


    df = load_last_orders()

    st.write(df)