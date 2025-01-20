import streamlit as st
from modules.load_data import load_holysoup_mautic_contacts

def display_tab_holysoup_crm():
    st.title("📊 Análise de Contatos do CRM")
    st.markdown("""---""")

    df = load_holysoup_mautic_contacts()
    st.write(df)

    # Dropdown para seleção de lista
    lists = ["Todas as Listas"] + sorted(df['list_name'].unique().tolist())
    selected_list = st.selectbox(
        "Selecione a Lista:",
        lists
    )

    # Filtrar dados baseado na lista selecionada
    if selected_list != "Todas as Listas":
        df_filtered = df[df['list_name'] == selected_list]
    else:
        df_filtered = df

    # Exibir métricas em colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        total_records = len(df_filtered)
        st.metric("Total de Registros", f"{total_records:,}")
        
    with col2:
        unique_emails = df_filtered['email'].nunique()
        st.metric("Emails Únicos", f"{unique_emails:,}")
        
    with col3:
        # Considerando que podem haver telefones vazios ou nulos
        unique_phones = df_filtered['phone'].dropna().nunique()
        st.metric("Telefones Únicos", f"{unique_phones:,}")

    # Exibir tabela bruta com todos os dados
    st.subheader("👨🏻‍💻 Exportar Contatos")
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True
    )

    # Botão para gerar link do Drive
    if st.button("🔗 Gerar Link de Exportação"):
        with st.spinner('Gerando link de exportação...'):
            filename = f'mautic_data_{selected_list.lower().replace(" ", "_")}.csv'
            drive_link = upload_to_drive(df_filtered, filename)
            if drive_link:
                st.success(f"Arquivo exportado com sucesso! [Clique aqui para acessar]({drive_link})")