import streamlit as st
from modules.load_data import save_coupons, load_coupons


def display_tab_coupons():
    st.title("Gerenciamento de Cupons")
    
    coupons = load_coupons()

    st.data_editor(coupons, use_container_width=True, hide_index=True)