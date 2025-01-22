import streamlit as st
from modules.load_data import load_holysoup_mautic_segments, load_holysoup_mautic_contacts
from googleapiclient.http import MediaIoBaseUpload
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build


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

def display_tab_holysoup_crm():
    st.title("📊 Exportar Contatos do CRM")
    st.markdown("""---""")

    df = load_holysoup_mautic_segments()

    # Dropdown para seleção de lista
    lists = ["Todas as Listas"] + sorted(df['list_name'].unique().tolist())
    selected_list = st.selectbox(
        "Selecione a Lista:",
        lists
    )

    if selected_list:
        df_contacts = load_holysoup_mautic_contacts(selected_list)
        total_contacts = len(df_contacts)
        
        st.metric(
            label="Total de Contatos",
            value=f"{total_contacts:,}".replace(",", ".")
        )

    # Botão para gerar link do Drive
    if st.button("🔗 Gerar Link de Exportação"):
        with st.spinner('Gerando link de exportação...'):
            filename = f'mautic_data_{selected_list.lower().replace(" ", "_")}.csv'
            
            drive_link = upload_to_drive(df_contacts, filename)
            if drive_link:
                st.success(f"Arquivo exportado com sucesso! [Clique aqui para acessar]({drive_link})")