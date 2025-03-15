import streamlit as st
from modules.load_data import load_popup_leads

def display_tab_leads():

    st.title("Leads")
    st.write("Leads coletados a partir do popup de cadastro.")

    popup_leads = load_popup_leads()
    col1, col2 = st.columns([1,5])
    with col1:
        csv = popup_leads.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name="leads.csv",
            mime="text/csv"
        )

    st.data_editor(
        popup_leads,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data do Cadastro": st.column_config.DatetimeColumn(
                "Data do Cadastro",
                format="DD/MM/YYYY HH:mm:ss"
            ),
            "Data da Compra": st.column_config.DatetimeColumn(
                "Data da Compra", 
                format="DD/MM/YYYY HH:mm:ss"
            )
        }
    )