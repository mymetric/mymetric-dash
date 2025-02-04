import streamlit as st
import pandas as pd

def display_notices():
    
    with st.expander("🔔 Novidades", expanded=True):

        if pd.Timestamp.now().date() <= pd.Timestamp('2025-02-07').date():
        
            st.subheader("Gerenciamento de Usuários")
            st.write("Agora é possível criar usuários e gerenciar suas permissões. Verifique a aba de Configurações.")

        if pd.Timestamp.now().date() <= pd.Timestamp('2025-02-08').date():

            st.subheader("Login Persistente")
            st.write("Agora o login dura até 8 horas. Isso é muito útil para quando você está usando o MyMetricHUB várias vezes ao dia sem precisar ficar logando.")
    
