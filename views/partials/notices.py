import streamlit as st
import pandas as pd

def display_notices():
    
    with st.expander("🔔 Novidades", expanded=True):

        if pd.Timestamp.now().date() <= pd.Timestamp('2025-02-07').date():
            st.subheader("Gerenciamento de Usuários")
        
            st.write("Agora é possível criar usuários e gerenciar suas permissões. Verifique a aba de Configurações.")
    
