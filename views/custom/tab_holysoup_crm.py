import streamlit as st
from modules.load_data import load_holysoup_mautic_segments, load_holysoup_mautic_contacts, load_holysoup_email_stats
from googleapiclient.http import MediaIoBaseUpload
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from modules.components import big_number_box
import altair as alt
import pandas as pd


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
    st.title("📊 CRM")
    st.markdown("""---""")

    df = load_holysoup_email_stats()

    # Calculate monthly totals
    monthly_metrics = {
        'Total Enviados': df['Enviado'].sum(),
        'Total Abertos': df['Abertos'].sum(),
        'Total Cliques': df['Cliques'].sum(),
        'Receita Total': df['Receita'].sum(),
        'Custo Total': df['Custo'].round(2).sum()
    }

    # Calculate overall rates
    if monthly_metrics['Total Enviados'] > 0:
        monthly_metrics['Taxa de Abertura'] = (monthly_metrics['Total Abertos'] / monthly_metrics['Total Enviados'] * 100)
        monthly_metrics['Taxa de Clique'] = (monthly_metrics['Total Cliques'] / monthly_metrics['Total Enviados'] * 100)
    else:
        monthly_metrics['Taxa de Abertura'] = 0
        monthly_metrics['Taxa de Clique'] = 0

    # Calculate overall ROI
    if monthly_metrics['Custo Total'] > 0:
        monthly_metrics['ROI'] = ((monthly_metrics['Receita Total'] - monthly_metrics['Custo Total']) / monthly_metrics['Custo Total'])
    else:
        monthly_metrics['ROI'] = 0

    # Display metrics using big_number_box component
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"{monthly_metrics['Total Enviados']:,.0f}".replace(",", "."), 
            "Total de Disparos",
            hint="Número total de e-mails enviados no período"
        )
        big_number_box(
            f"{monthly_metrics['Taxa de Abertura']:.2f}%".replace(".", ","),
            "Taxa de Abertura",
            hint="Percentual de e-mails que foram abertos"
        )
    with col2:
        big_number_box(
            f"{monthly_metrics['Total Abertos']:,.0f}".replace(",", "."),
            "Total de Aberturas",
            hint="Número total de e-mails abertos"
        )
        big_number_box(
            f"{monthly_metrics['Taxa de Clique']:.2f}%".replace(".", ","),
            "Taxa de Clique",
            hint="Percentual de e-mails que receberam cliques"
        )
    with col3:
        big_number_box(
            f"R$ {monthly_metrics['Receita Total']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Receita Total",
            hint="Receita total gerada pelos e-mails"
        )
        big_number_box(
            f"{monthly_metrics['ROI']:.2f}x",
            "ROI",
            hint="Retorno sobre o investimento (Receita - Custo) / Custo"
        )
    with col4:
        big_number_box(
            f"R$ {monthly_metrics['Custo Total']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Custo Total",
            hint="Custo total dos disparos de e-mail. Cálculo baseado no custo da Amazon SES."
        )
        big_number_box(
            f"{monthly_metrics['Total Cliques']:,.0f}".replace(",", "."),
            "Total de Cliques",
            hint="Número total de cliques nos e-mails"
        )

    st.markdown("---")

    # Prepare data for timeline
    timeline_df = df.copy()
    timeline_df['Data'] = pd.to_datetime(timeline_df['Data'])

    # Create columns for the charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Revenue chart
        revenue_chart = alt.Chart(timeline_df).mark_bar(
            color='#28a745',
            opacity=0.7
        ).encode(
            x=alt.X('Data:T', title='Data', axis=alt.Axis(format='%d/%m')),
            y=alt.Y('Receita:Q',
                    title='Receita (R$)',
                    axis=alt.Axis(format=',.2f')),
            tooltip=[
                alt.Tooltip('Data:T', title='Data'),
                alt.Tooltip('Receita:Q', title='Receita', format=',.2f')
            ]
        ).properties(
            title='Receita por Data',
            height=400
        )
        
        st.altair_chart(revenue_chart, use_container_width=True)

    with chart_col2:
        # Dispatch chart
        dispatch_chart = alt.Chart(timeline_df).mark_bar(
            color='#17a2b8',
            opacity=0.7
        ).encode(
            x=alt.X('Data:T', title='Data', axis=alt.Axis(format='%d/%m')),
            y=alt.Y('Enviado:Q',
                    title='Disparos',
                    axis=alt.Axis(format=',d')),
            tooltip=[
                alt.Tooltip('Data:T', title='Data'),
                alt.Tooltip('Enviado:Q', title='Disparos', format=',d')
            ]
        ).properties(
            title='Disparos por Data',
            height=400
        )
        
        st.altair_chart(dispatch_chart, use_container_width=True)

    # Round the cost column and calculate metrics
    df['Custo'] = df['Custo'].round(2)
    df['Taxa de Abertura (%)'] = (df['Abertos'] / df['Enviado'] * 100).round(2)
    df['Taxa de Clique (%)'] = (df['Cliques'] / df['Enviado'] * 100).round(2)
    df['ROI'] = ((df['Receita'] - df['Custo']) / df['Custo']).round(2)

    # Display the data with the new metrics
    st.data_editor(df, hide_index=1, use_container_width=1)
    

    st.subheader("Exportar Segmentos do Mautic")
    with st.expander("Exportar Segmentos do Mautic"):

        df_segments = load_holysoup_mautic_segments()

        # Dropdown para seleção de lista
        lists = ["Todas as Listas"] + sorted(df_segments['list_name'].unique().tolist())
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

        st.write("A diferença entre o total de contatos exibido no segmento no Mautic e o total de contatos exibido aqui é devido aos descadastrados. E-mails com erro são exportados aqui a título de tentar atingir via WhatsApp.")
        # Botão para gerar link do Drive
        if st.button("🔗 Gerar Link de Exportação"):
            with st.spinner('Gerando link de exportação...'):
                filename = f'mautic_data_{selected_list.lower().replace(" ", "_")}.csv'
                
                drive_link = upload_to_drive(df_contacts, filename)
                if drive_link:
                    st.success(f"Arquivo exportado com sucesso! [Clique aqui para acessar]({drive_link})")