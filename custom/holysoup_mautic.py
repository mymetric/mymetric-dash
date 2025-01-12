import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

def display_tab_holysoup_mautic(client, start_date, end_date, **filters):
    # Verificar se está rodando no Streamlit Cloud
    if 'streamlit.app' in st.get_option('server.address'):
        st.error("⚠️ Versão não autorizada!")
        st.warning("Por favor, acesse o dashboard através do endereço oficial:")
        st.markdown("[https://hub.mymetric.app](https://hub.mymetric.app/)")
        st.stop()
        
    st.title("✉️ Mautic")
    
    try:
        with st.spinner('Carregando dados do Mautic...'):
            # Query para buscar dados do HolySoup
            query = """
            SELECT 
                *
            FROM `holy-soup.mautic.export_segment`
            """
            
            df = client.query(query).to_dataframe()
            
            if df.empty:
                st.warning("Nenhum dado encontrado para HolySoup")
                return
            
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
            
            # Botão para download dos dados filtrados
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Exportar para CSV",
                data=csv,
                file_name=f'mautic_data_{selected_list.lower().replace(" ", "_")}.csv',
                mime='text/csv'
            )
            
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {str(e)}")
        st.error("""
        Sugestões:
        1. Verifique a conexão com o BigQuery
        2. Confirme se as permissões estão corretas
        3. Tente recarregar a página
        """) 