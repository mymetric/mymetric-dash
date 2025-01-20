import streamlit as st
from modules.load_data import load_gringa_product_submited

def display_tab_gringa_product_submitted():
    st.title("📊 Análise de Cadastros de Produtos")
    st.markdown("""---""")

    df = load_gringa_product_submited()

    aggregated_df = df.groupby(['Data']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.line_chart(aggregated_df, x = "Data", y = "Cadastros")

    st.header("Cluster")

    aggregated_df = df.groupby(['Cluster']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    st.header("Campanha")

    aggregated_df = df.groupby(['Campanha']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)
