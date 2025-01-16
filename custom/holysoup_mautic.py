import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import altair as alt

def upload_to_drive(df, filename):
    """Faz upload do DataFrame para o Google Drive e retorna o link de compartilhamento."""
    try:
        # Usar as credenciais do service account
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Criar serviço do Drive
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Converter DataFrame para CSV em memória
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Preparar o upload
        media = MediaIoBaseUpload(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            resumable=True
        )
        
        # Criar arquivo no Drive
        file_metadata = {'name': filename}
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        # Configurar permissão de visualização pública
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(
            fileId=file['id'],
            body=permission
        ).execute()
        
        # Gerar link de compartilhamento
        file_id = file['id']
        return f'https://drive.google.com/file/d/{file_id}/view'
        
    except Exception as e:
        st.error(f"Erro ao fazer upload para o Drive: {str(e)}")
        return None

def display_tab_holysoup_mautic(client, start_date, end_date, **filters):
    st.title("✉️ CRM")
    
    try:
        # Query para análise de clientes
        query_clientes = """
        select
            date_diff(current_date, last_purchase_date, MONTH) meses,
            transactions,
            count(1) clientes
        from `holy-soup.crm.clientes`
        where 
            date_diff(current_date, last_purchase_date, MONTH) <= 12
            and transactions <= 10
        group by all
        order by meses, transactions
        """
        
        df_clientes = client.query(query_clientes).to_dataframe()
        
        if not df_clientes.empty:
            st.header("📊 Análise de Clientes")
            
            # Criar um gráfico de bolhas usando Altair
            # Criar o gráfico
            chart = alt.Chart(df_clientes).mark_circle(opacity=0.8).encode(
                x=alt.X('meses:Q', 
                       title='Meses desde Última Compra',
                       axis=alt.Axis(tickMinStep=1)),
                y=alt.Y('transactions:Q', 
                       title='Total de Compras',
                       axis=alt.Axis(tickMinStep=1)),
                size=alt.Size('clientes:Q',
                            title='Quantidade de Clientes',
                            scale=alt.Scale(range=[100, 2000])),
                tooltip=[
                    alt.Tooltip('meses:Q', title='Meses desde Última Compra'),
                    alt.Tooltip('transactions:Q', title='Total de Compras'),
                    alt.Tooltip('clientes:Q', title='Quantidade de Clientes', format=',')
                ]
            ).properties(
                width=700,
                height=400,
                title='Distribuição de Clientes por Recência e Frequência'
            ).configure_mark(
                color='#17a2b8'
            )
            
            # Exibir o gráfico
            st.altair_chart(chart, use_container_width=True)
            
            # Adicionar espaço entre as seções
            st.markdown("---")
        
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
            
            # Seção de exportação de segmentos
            st.header("📤 Exportar Segmentos do Mautic")
            
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
            
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {str(e)}")
        st.error("""
        Sugestões:
        1. Verifique a conexão com o BigQuery
        2. Confirme se as permissões estão corretas
        3. Tente recarregar a página
        """) 