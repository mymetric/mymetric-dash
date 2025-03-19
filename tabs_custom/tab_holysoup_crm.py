import streamlit as st
from modules.load_data import load_holysoup_mautic_segments, load_holysoup_mautic_contacts, load_holysoup_email_stats, load_holysoup_crm_optout, load_detailed_data
from googleapiclient.http import MediaIoBaseUpload
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from modules.components import big_number_box
import altair as alt
import pandas as pd
from datetime import datetime
from partials.run_rate import load_table_metas
from modules.load_data import save_goals
from google.cloud import bigquery


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
    st.title("CRM")
    st.markdown("""---""")

    df = load_holysoup_email_stats()
    df_detailed = load_detailed_data()

    # Calcular métricas do WhatsApp
    whatsapp_revenue = df_detailed[
        (df_detailed['Cluster'] == '💬 WhatsApp - Direto') & 
        (df_detailed['Pedidos Pagos'] > 0)
    ]['Receita Paga'].sum()

    whatsapp_revenue_groups = df_detailed[
        (df_detailed['Cluster'] == '💬 WhatsApp - Grupos') & 
        (df_detailed['Pedidos Pagos'] > 0)
    ]['Receita Paga'].sum()

    # Calcular total de pedidos do WhatsApp
    whatsapp_orders = df_detailed[
        (df_detailed['Cluster'] == '💬 WhatsApp - Direto') & 
        (df_detailed['Pedidos Pagos'] > 0)
    ]['Pedidos Pagos'].sum()

    whatsapp_orders_groups = df_detailed[
        (df_detailed['Cluster'] == '💬 WhatsApp - Grupos') & 
        (df_detailed['Pedidos Pagos'] > 0)
    ]['Pedidos Pagos'].sum()

    # Carregar dados de mensagens e custo do mês atual
    current_metas = load_table_metas()
    current_month = datetime.now().strftime("%Y-%m")
    whatsapp_messages = current_metas.get('metas_mensais', {}).get(current_month, {}).get('whatsapp_messages', 0)
    cost_per_message = current_metas.get('metas_mensais', {}).get(current_month, {}).get('whatsapp_cost_per_message', 0.0)
    total_cost = whatsapp_messages * cost_per_message
    whatsapp_roi = ((whatsapp_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

    if df.empty:
        st.error("Não há dados para exibir.")
        return
    else:
        # Calculate monthly totals
        monthly_metrics = {
            'Total Enviados': df['Enviado'].sum(),
            'Total Abertos': df['Abertos'].sum(),
            'Total Cliques': df['Cliques'].sum(),
            'Total Pedidos': df['Pedidos'].sum(),
            'Pedidos Último Clique': df['Pedidos Último Clique'].sum(),
            'Receita Total': df['Receita'].sum(),
            'Receita Último Clique': df['Receita Último Clique'].sum(),
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
            monthly_metrics['ROI'] = ((monthly_metrics['Receita Total'] - monthly_metrics['Custo Total']) / monthly_metrics['Custo Total'] * 100)
            monthly_metrics['ROI Último Clique'] = ((monthly_metrics['Receita Último Clique'] - monthly_metrics['Custo Total']) / monthly_metrics['Custo Total'] * 100)
        else:
            monthly_metrics['ROI'] = 0
            monthly_metrics['ROI Último Clique'] = 0

        # Display metrics using big_number_box component
        st.subheader("E-mail Marketing")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            big_number_box(
                f"{monthly_metrics['Total Enviados']:,.0f}".replace(",", "."), 
                "Total de Disparos",
                hint="Número total de e-mails enviados no período"
            )
            big_number_box(
                f"{monthly_metrics['Total Pedidos']:,.0f}".replace(",", "."),
                "Total de Pedidos",
                hint="Número total de pedidos gerados pelos e-mails"
            )
            big_number_box(
                f"{monthly_metrics['Pedidos Último Clique']:,.0f}".replace(",", "."),
                "Pedidos Último Clique",
                hint="Número de pedidos atribuídos ao último clique"
            )
        with col2:
            big_number_box(
                f"{monthly_metrics['Total Abertos']:,.0f}".replace(",", "."),
                "Total de Aberturas",
                hint="Número total de e-mails abertos"
            )
            big_number_box(
                f"R$ {monthly_metrics['Receita Total']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Receita Total",
                hint="Receita total gerada pelos e-mails"
            )
            big_number_box(
                f"R$ {monthly_metrics['Receita Último Clique']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Receita Último Clique",
                hint="Receita total gerada pelos pedidos atribuídos ao último clique"
            )
        with col3:
            big_number_box(
                f"{monthly_metrics['Total Cliques']:,.0f}".replace(",", "."),
                "Total de Cliques",
                hint="Número total de cliques nos e-mails"
            )
            big_number_box(
                f"{monthly_metrics['ROI']:,.1f}%".replace(",", "*").replace(".", ",").replace("*", "."),
                "ROI",
                hint="Retorno sobre o investimento ((Receita - Custo) / Custo) × 100"
            )
            big_number_box(
                f"{monthly_metrics['ROI Último Clique']:,.1f}%".replace(",", "*").replace(".", ",").replace("*", "."),
                "ROI Último Clique",
                hint="Retorno sobre o investimento do último clique ((Receita Último Clique - Custo) / Custo) × 100"
            )
        with col4:
            big_number_box(
                f"{monthly_metrics['Taxa de Abertura']:.2f}%".replace(".", ","),
                "Taxa de Abertura",
                hint="Percentual de e-mails que foram abertos"
            )
            big_number_box(
                f"{monthly_metrics['Taxa de Clique']:.2f}%".replace(".", ","),
                "Taxa de Clique",
                hint="Percentual de e-mails que receberam cliques"
            )
            big_number_box(
                f"R$ {monthly_metrics['Custo Total']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Custo Total",
                hint="Custo total dos disparos de e-mail. Cálculo baseado no custo da Amazon SES."
            )

        with st.expander("Modelo de Atribuição - E-mail Marketing"):
            st.write("Último e-mail enviado, até 7 dias antes da compra, independentemente se foi aberto ou clicado.")

        st.markdown("---")
        
        # Display WhatsApp metrics
        st.subheader("WhatsApp")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            big_number_box(
                f"{whatsapp_messages:,.0f}".replace(",", "."),
                "Total de Mensagens",
                hint="Número total de mensagens de WhatsApp enviadas no mês"
            )
        with col2:
            big_number_box(
                f"R$ {whatsapp_messages * cost_per_message:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Custo Total",
                hint="Custo total das mensagens de WhatsApp no período"
            )
        with col3:
            big_number_box(
                f"R$ {whatsapp_revenue:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Receita WhatsApp Direto",
                hint="Receita total gerada pelo WhatsApp direto no período"
            )
        with col4:
            big_number_box(
                f"{whatsapp_orders:,.0f}".replace(",", "."),
                "Pedidos WhatsApp Direto",
                hint="Número total de pedidos gerados pelo WhatsApp direto no período"
            )
        with col5:
            big_number_box(
                f"R$ {whatsapp_revenue_groups:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
                "Receita WhatsApp Grupos",
                hint="Receita total gerada pelos grupos de WhatsApp no período"
            )
        with col6:
            big_number_box(
                f"{whatsapp_orders_groups:,.0f}".replace(",", "."),
                "Pedidos WhatsApp Grupos",
                hint="Número total de pedidos gerados pelos grupos de WhatsApp no período"
            )

        with st.expander("Modelo de Atribuição - WhatsApp"):
            st.write("Último clique do cliente antes de comprar, tende a ser menos generoso que a atribuição do e-mail marketing.")

        st.markdown("---")

        with st.expander("E-mail Marketing - Detalhes", expanded=False):
            # Prepare data for timeline
            timeline_df = df.copy()
            timeline_df['Data'] = pd.to_datetime(timeline_df['Data'])

            # Create columns for the charts
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                # Revenue chart
                revenue_chart = alt.Chart(timeline_df).mark_bar(
                    color='#E5E7EB',
                    size=20
                ).encode(
                    x=alt.X('Data:T', 
                           title='Data', 
                           axis=alt.Axis(format='%d/%m', labelAngle=0)),
                    y=alt.Y('Receita:Q',
                           title='Receita',
                           axis=alt.Axis(format='$,.2f',
                                       titlePadding=10)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Receita:Q', title='Receita', format='$,.2f')
                    ]
                ).properties(
                    title=alt.TitleParams(
                        text='Evolução de Receita',
                        fontSize=16,
                        font='DM Sans',
                        anchor='start',
                        dy=-10
                    ),
                    height=400
                ).configure_axis(
                    grid=True,
                    gridOpacity=0.1,
                    labelFontSize=12,
                    titleFontSize=13,
                    labelFont='DM Sans',
                    titleFont='DM Sans'
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(revenue_chart, use_container_width=True)

            with chart_col2:
                # Dispatch chart
                dispatch_chart = alt.Chart(timeline_df).mark_bar(
                    color='#E5E7EB',
                    size=20
                ).encode(
                    x=alt.X('Data:T', 
                           title='Data', 
                           axis=alt.Axis(format='%d/%m', labelAngle=0)),
                    y=alt.Y('Enviado:Q',
                           title='Disparos',
                           axis=alt.Axis(format=',d',
                                       titlePadding=10)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Enviado:Q', title='Disparos', format=',d')
                    ]
                ).properties(
                    title=alt.TitleParams(
                        text='Evolução de Disparos',
                        fontSize=16,
                        font='DM Sans',
                        anchor='start',
                        dy=-10
                    ),
                    height=400
                ).configure_axis(
                    grid=True,
                    gridOpacity=0.1,
                    labelFontSize=12,
                    titleFontSize=13,
                    labelFont='DM Sans',
                    titleFont='DM Sans'
                ).configure_view(
                    strokeWidth=0
                )
                
                st.altair_chart(dispatch_chart, use_container_width=True)

            # Round the cost column and calculate metrics
            df['Custo'] = df['Custo'].round(2)
            df['Taxa de Abertura (%)'] = (df['Abertos'] / df['Enviado'] * 100).round(2)
            df['Taxa de Clique (%)'] = (df['Cliques'] / df['Enviado'] * 100).round(2)
            df['ROI'] = ((df['Receita'] - df['Custo']) / df['Custo']).round(2)

            # Display the data with the new metrics
            st.data_editor(df, hide_index=1, use_container_width=1)


            df_optout = load_holysoup_crm_optout()

            # Campo de entrada para filtro mínimo de envios
            min_enviados = st.number_input(
                "Filtro mínimo de envios para cálculo das taxas",
                value=5000,
                step=1000,
                help="Apenas dias com envios acima deste valor serão considerados no cálculo das taxas"
            )
            
            # Converter colunas para numérico, tratando possíveis erros
            numeric_columns = ['enviado', 'descadastro', 'rejeicao']
            for col in numeric_columns:
                df_optout[col] = pd.to_numeric(df_optout[col], errors='coerce')

            # Converter a coluna de data
            df_optout['Data'] = pd.to_datetime(df_optout['data'])

            # Filtrar por mínimo de envios e calcular taxas
            df_optout['Taxa de Rejeição'] = df_optout.apply(
                lambda row: (row['rejeicao'] / row['enviado']) if row['enviado'] >= min_enviados else None, 
                axis=1
            )
            df_optout['Taxa de Descadastro'] = df_optout.apply(
                lambda row: (row['descadastro'] / row['enviado']) if row['enviado'] >= min_enviados else None, 
                axis=1
            )

            # Remover linhas onde as taxas são None para o gráfico
            df_optout_filtered = df_optout.dropna(subset=['Taxa de Rejeição', 'Taxa de Descadastro'])
            
            # Criar colunas para os gráficos
            timeline_col1, timeline_col2 = st.columns(2)

            with timeline_col1:
                if not df_optout_filtered.empty:
                    # Gráfico combinado de taxa e valor absoluto de rejeição
                    base = alt.Chart(df_optout_filtered).encode(
                        x=alt.X('Data:T', title='Data', axis=alt.Axis(format='%d/%m'))
                    )

                    # Linha para taxa de rejeição
                    line_bounce = base.mark_line(
                        color='#3B82F6',
                        strokeWidth=2.5
                    ).encode(
                        y=alt.Y('Taxa de Rejeição:Q',
                               title='Taxa de Rejeição (%)',
                               axis=alt.Axis(format='.1%',
                                           titlePadding=10)),
                        tooltip=[
                            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                            alt.Tooltip('Taxa de Rejeição:Q', title='Taxa de Rejeição', format='.1%'),
                            alt.Tooltip('rejeicao:Q', title='Rejeições', format=',d')
                        ]
                    )

                    # Barras para valor absoluto de rejeições
                    bar_bounce = base.mark_bar(
                        color='#E5E7EB',
                        size=20
                    ).encode(
                        y=alt.Y('rejeicao:Q',
                               title='Rejeições',
                               axis=alt.Axis(format=',d',
                                           titlePadding=10)),
                        tooltip=[
                            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                            alt.Tooltip('rejeicao:Q', title='Rejeições', format=',d'),
                            alt.Tooltip('Taxa de Rejeição:Q', title='Taxa de Rejeição', format='.1%')
                        ]
                    )

                    # Combinar os gráficos com escalas diferentes
                    bounce_chart = alt.layer(line_bounce, bar_bounce).resolve_scale(
                        y='independent'
                    ).properties(
                        title=alt.TitleParams(
                            text='Evolução de Taxa de Rejeição',
                            fontSize=16,
                            font='DM Sans',
                            anchor='start',
                            dy=-10
                        ),
                        height=400
                    ).configure_axis(
                        grid=True,
                        gridOpacity=0.1,
                        labelFontSize=12,
                        titleFontSize=13,
                        labelFont='DM Sans',
                        titleFont='DM Sans'
                    ).configure_view(
                        strokeWidth=0
                    )
                    
                    st.altair_chart(bounce_chart, use_container_width=True)

                    # Adiciona legenda manual com design melhorado
                    st.markdown("""
                        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Taxa de Rejeição</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Rejeições</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            with timeline_col2:
                if not df_optout_filtered.empty:
                    # Gráfico combinado de taxa e valor absoluto de descadastro
                    base = alt.Chart(df_optout_filtered).encode(
                        x=alt.X('Data:T', title='Data', axis=alt.Axis(format='%d/%m'))
                    )

                    # Linha para taxa de descadastro
                    line_unsub = base.mark_line(
                        color='#3B82F6',
                        strokeWidth=2.5
                    ).encode(
                        y=alt.Y('Taxa de Descadastro:Q',
                               title='Taxa de Descadastro (%)',
                               axis=alt.Axis(format='.1%',
                                           titlePadding=10)),
                        tooltip=[
                            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                            alt.Tooltip('Taxa de Descadastro:Q', title='Taxa de Descadastro', format='.1%'),
                            alt.Tooltip('descadastro:Q', title='Descadastros', format=',d')
                        ]
                    )

                    # Barras para valor absoluto de descadastros
                    bar_unsub = base.mark_bar(
                        color='#E5E7EB',
                        size=20
                    ).encode(
                        y=alt.Y('descadastro:Q',
                               title='Descadastros',
                               axis=alt.Axis(format=',d',
                                           titlePadding=10)),
                        tooltip=[
                            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                            alt.Tooltip('descadastro:Q', title='Descadastros', format=',d'),
                            alt.Tooltip('Taxa de Descadastro:Q', title='Taxa de Descadastro', format='.1%')
                        ]
                    )

                    # Combinar os gráficos com escalas diferentes
                    unsubscribe_chart = alt.layer(line_unsub, bar_unsub).resolve_scale(
                        y='independent'
                    ).properties(
                        title=alt.TitleParams(
                            text='Evolução de Taxa de Descadastro',
                            fontSize=16,
                            font='DM Sans',
                            anchor='start',
                            dy=-10
                        ),
                        height=400
                    ).configure_axis(
                        grid=True,
                        gridOpacity=0.1,
                        labelFontSize=12,
                        titleFontSize=13,
                        labelFont='DM Sans',
                        titleFont='DM Sans'
                    ).configure_view(
                        strokeWidth=0
                    )
                    
                    st.altair_chart(unsubscribe_chart, use_container_width=True)

                    # Adiciona legenda manual com design melhorado
                    st.markdown("""
                        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Taxa de Descadastro</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Descadastros</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        with st.expander("WhatsApp - Direto - Detalhes"):
            # Calcular quantidade de grupos do WhatsApp
            whatsapp_groups = df_detailed[df_detailed['Cluster'] == '💬 WhatsApp - Direto']
            
            # Criar filtros
            col1, col2 = st.columns(2)
            with col1:
                # Lista única de campanhas
                campanhas = ["Todas as Campanhas"] + sorted(whatsapp_groups['Campanha'].unique().tolist())
                campanha_selecionada = st.selectbox(
                    "Filtrar por Campanha",
                    campanhas,
                    key="whatsapp_direct_campaign"
                )
            
            with col2:
                # Lista única de conteúdos
                conteudos = ["Todos os Conteúdos"] + sorted(whatsapp_groups['Conteúdo'].unique().tolist())
                conteudo_selecionado = st.selectbox(
                    "Filtrar por Conteúdo",
                    conteudos,
                    key="whatsapp_direct_content"
                )

            # Aplicar filtros
            if campanha_selecionada != "Todas as Campanhas":
                whatsapp_groups = whatsapp_groups[whatsapp_groups['Campanha'] == campanha_selecionada]
            if conteudo_selecionado != "Todos os Conteúdos":
                whatsapp_groups = whatsapp_groups[whatsapp_groups['Conteúdo'] == conteudo_selecionado]
            
            # Agrupar dados do WhatsApp por campanha e conteúdo
            whatsapp_campaign = whatsapp_groups.groupby(['Campanha', 'Conteúdo']).agg({
                'Sessões': 'sum',
                'Pedidos': 'sum',
                'Pedidos Pagos': 'sum',
                'Receita': 'sum',
                'Receita Paga': 'sum'
            }).reset_index()

            # Ordenar por receita paga em ordem decrescente
            whatsapp_campaign = whatsapp_campaign.sort_values('Receita Paga', ascending=False)

            # Exibir tabela agrupada
            st.subheader("Desempenho por Campanha e Conteúdo (utm_campaign e utm_content)")
            st.data_editor(
                whatsapp_campaign,
                hide_index=True,
                use_container_width=True,
                column_config={
                    'Receita': st.column_config.NumberColumn(
                        "Receita",
                        format="R$ %.2f"
                    ),
                    'Receita Paga': st.column_config.NumberColumn(
                        "Receita Paga", 
                        format="R$ %.2f"
                    )
                }
            )

        with st.expander("WhatsApp - Grupos - Detalhes"):
            # Calcular quantidade de grupos do WhatsApp
            whatsapp_groups = df_detailed[df_detailed['Cluster'] == '💬 WhatsApp - Grupos']
            
            # Criar filtros
            col1, col2 = st.columns(2)
            with col1:
                # Lista única de campanhas
                campanhas = ["Todas as Campanhas"] + sorted(whatsapp_groups['Campanha'].unique().tolist())
                campanha_selecionada = st.selectbox(
                    "Filtrar por Campanha",
                    campanhas,
                    key="whatsapp_groups_campaign"
                )
            
            with col2:
                # Lista única de conteúdos
                conteudos = ["Todos os Conteúdos"] + sorted(whatsapp_groups['Conteúdo'].unique().tolist())
                conteudo_selecionado = st.selectbox(
                    "Filtrar por Conteúdo",
                    conteudos,
                    key="whatsapp_groups_content"
                )

            # Aplicar filtros
            if campanha_selecionada != "Todas as Campanhas":
                whatsapp_groups = whatsapp_groups[whatsapp_groups['Campanha'] == campanha_selecionada]
            if conteudo_selecionado != "Todos os Conteúdos":
                whatsapp_groups = whatsapp_groups[whatsapp_groups['Conteúdo'] == conteudo_selecionado]
            
            # Agrupar dados do WhatsApp por campanha e conteúdo
            whatsapp_campaign = whatsapp_groups.groupby(['Campanha', 'Conteúdo']).agg({
                'Sessões': 'sum',
                'Pedidos': 'sum',
                'Pedidos Pagos': 'sum',
                'Receita': 'sum',
                'Receita Paga': 'sum'
            }).reset_index()

            # Ordenar por receita paga em ordem decrescente
            whatsapp_campaign = whatsapp_campaign.sort_values('Receita Paga', ascending=False)

            # Exibir tabela agrupada
            st.subheader("Desempenho por Campanha e Conteúdo (utm_campaign e utm_content)")
            st.data_editor(
                whatsapp_campaign,
                hide_index=True,
                use_container_width=True,
                column_config={
                    'Receita': st.column_config.NumberColumn(
                        "Receita",
                        format="R$ %.2f"
                    ),
                    'Receita Paga': st.column_config.NumberColumn(
                        "Receita Paga", 
                        format="R$ %.2f"
                    )
                }
            )

        st.markdown("""---""")
        st.subheader("Controle de Envios de WhatsApp")
        with st.expander("Registrar Envios de WhatsApp", expanded=False):
            # Carregar configurações existentes
            current_metas = load_table_metas()
            
            # Lista dos últimos 12 meses para seleção
            months = []
            for i in range(12):
                month = (datetime.now() - pd.DateOffset(months=i)).strftime("%Y-%m")
                months.append(month)
            
            selected_month = st.selectbox(
                "Mês de Referência",
                options=months,
                format_func=lambda x: pd.to_datetime(x).strftime("%B/%Y").capitalize(),
                key="whatsapp_month"
            )
            
            # Pegar o valor atual de mensagens de WhatsApp e custo para o mês selecionado
            current_whatsapp = current_metas.get('metas_mensais', {}).get(selected_month, {}).get('whatsapp_messages', 0)
            current_cost = current_metas.get('metas_mensais', {}).get(selected_month, {}).get('whatsapp_cost_per_message', 0.0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                whatsapp_messages = st.number_input(
                    "Quantidade de Mensagens de WhatsApp Enviadas",
                    min_value=0,
                    step=100,
                    help="Digite o número total de mensagens de WhatsApp enviadas no mês",
                    value=int(current_whatsapp)
                )
                
            with col2:
                cost_per_message = st.number_input(
                    "Custo por Mensagem (R$)",
                    min_value=0.0,
                    step=0.001,
                    format="%.3f",
                    help="Digite o custo por mensagem de WhatsApp",
                    value=float(current_cost)
                )

            # Calcular métricas do WhatsApp
            df_detailed = load_detailed_data()
            whatsapp_revenue = df_detailed[
                (df_detailed['Cluster'] == '💬 WhatsApp') & 
                (df_detailed['Pedidos Pagos'] > 0)
            ]['Receita Paga'].sum()
            
            total_cost = whatsapp_messages * cost_per_message
            roi = ((whatsapp_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            # Mostrar métricas
            st.markdown("### Métricas do Mês")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Custo Total", f"R$ {total_cost:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
            with col2:
                st.metric("Receita", f"R$ {whatsapp_revenue:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
            with col3:
                st.metric("ROI", f"{roi:,.1f}%".replace(",", "*").replace(".", ",").replace("*", "."))

            if st.button("Salvar Envios de WhatsApp"):
                # Garantir que a estrutura existe
                if 'metas_mensais' not in current_metas:
                    current_metas['metas_mensais'] = {}
                    
                # Atualizar ou criar o registro para o mês selecionado
                if selected_month not in current_metas['metas_mensais']:
                    current_metas['metas_mensais'][selected_month] = {}
                
                # Preservar meta de receita se existir
                meta_receita = current_metas.get('metas_mensais', {}).get(selected_month, {}).get('meta_receita_paga', 0)
                current_metas['metas_mensais'][selected_month]['meta_receita_paga'] = meta_receita
                
                # Salvar mensagens de WhatsApp e custo
                current_metas['metas_mensais'][selected_month]['whatsapp_messages'] = whatsapp_messages
                current_metas['metas_mensais'][selected_month]['whatsapp_cost_per_message'] = cost_per_message

                save_goals(current_metas)
                st.toast(f"Salvando envios de WhatsApp... {whatsapp_messages}")
                st.success("Quantidade de envios e custo salvos com sucesso!")

        st.subheader("Exportar Segmentos do Mautic")
        with st.expander("Exportar Segmentos do Mautic"):

            df_segments = load_holysoup_mautic_segments()

            # Dropdown para seleção de lista
            lists = ["Todas as Listas"] + sorted(df_segments['list_name'].unique().tolist())
            selected_list = st.selectbox(
                "Selecione a Lista:",
                lists
            )

            if selected_list and selected_list != "Todas as Listas":
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