import streamlit as st
from datetime import datetime
from helpers.components import send_discord_message
from analytics.logger import log_event

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            
            # Registra o evento de login
            log_event(st.session_state.username, 'login')
            
            # Envia mensagem de login para o Discord
            login_msg = f"""
🔐 **Novo Login no Dashboard**

**Usuário:** `{st.session_state.username}`
**Data/Hora:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`
"""
            send_discord_message(login_msg)
            
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True 