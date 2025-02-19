import streamlit as st
from modules.load_data import load_last_login

def display_tab_master():
    st.title("🧙🏻‍♂️ Master")

    df = load_last_login()

    st.data_editor(df, hide_index=True, use_container_width=True)

