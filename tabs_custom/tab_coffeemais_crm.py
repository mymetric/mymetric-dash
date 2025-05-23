import streamlit as st
from modules.load_data import load_coffeemais_crm, load_coffeemais_gupshup_errors, load_coffeemais_crm_detailed
from modules.components import big_number_box
import pandas as pd

def display_tab_coffeemais_crm():
    # Load the data
    df = load_coffeemais_crm()
    
    # Load notification to segment mapping
    with open('mappings/coffeemais_notification_segment_mapping.txt', 'r') as f:
        mapping_lines = f.readlines()
    
    # Create notification to segment mapping dictionary
    segment_mapping = {}
    for line in mapping_lines:
        if line.strip():
            notification, segment = line.strip().split('\t')
            segment_mapping[notification] = segment
    
    # Load segment type mapping
    with open('mappings/coffeemais_segment_type_mapping.txt', 'r') as f:
        type_mapping_lines = f.readlines()
    
    # Create segment type mapping dictionary
    type_mapping = {}
    for line in type_mapping_lines:
        if line.strip():
            key, value = line.strip().split('\t')
            type_mapping[key] = value
    
    # Load disparo type mapping
    with open('mappings/coffeemais_disparo_type_mapping.txt', 'r') as f:
        disparo_mapping_lines = f.readlines()
    
    # Create disparo type mapping dictionary
    disparo_mapping = {}
    for line in disparo_mapping_lines:
        if line.strip():
            key, value = line.strip().split('\t')
            disparo_mapping[key] = value
    
    # Function to find matching segment
    def find_segment(name):
        for key, value in segment_mapping.items():
            if key in name:
                return value
        return 'Outros'
    
    # Function to find matching segment type
    def find_segment_type(name):
        for key, value in type_mapping.items():
            if key in name:
                return value
        return 'Outros'
    
    # Function to find matching disparo type
    def find_disparo_type(name):
        for key, value in disparo_mapping.items():
            if key in name:
                return value
        return 'Campanha'
    
    # Add segment, segment type and disparo type columns to dataframe
    df['segment'] = df['name'].apply(find_segment)
    df['segment_type'] = df['name'].apply(find_segment_type)
    df['disparo_type'] = df['name'].apply(find_disparo_type)
    
    # Add a title
    st.title("CRM")
    
    # Add attribution model explanation in a collapsible section
    with st.expander("Sobre o Modelo de Atribuição"):
        st.info("""
        Os dados apresentados neste dashboard seguem o seguinte modelo de atribuição:
        - A conversão é atribuída ao envio da mensagem (e-mail ou WhatsApp)
        - O prazo de conversão considerado é de até 7 dias após o envio da mensagem
        - Pedidos realizados após 7 dias do envio não são contabilizados nesta análise
        - Se mais de uma mensagem for enviada nesse prazo e o cliente comprar, apenas a última mensagem será considerada como responsável pela venda
        """)
    
    # Create tabs for main view and errors
    tab_principal, tab_erros = st.tabs(["Métricas", "Erros WhatsApp"])
    
    with tab_principal:
        # Calculate metrics for all channels
        total_sent = df['sent'].sum()
        total_orders = df['orders'].sum()
        total_revenue = df['revenue'].sum()
        conversion_rate = (total_orders / total_sent * 100) if total_sent > 0 else 0
        avg_revenue_per_order = (total_revenue / total_orders) if total_orders > 0 else 0
        
        # Calculate email metrics
        df_email = df[df['channel'] == 'email']
        email_sent = df_email['sent'].sum()
        email_orders = df_email['orders'].sum()
        email_revenue = df_email['revenue'].sum()
        email_conversion = (email_orders / email_sent * 100) if email_sent > 0 else 0
        email_avg_order = (email_revenue / email_orders) if email_orders > 0 else 0
        
        # Calculate WhatsApp metrics
        df_whatsapp = df[df['channel'] == 'whatsapp']
        whatsapp_sent = df_whatsapp['sent'].sum()
        whatsapp_orders = df_whatsapp['orders'].sum()
        whatsapp_revenue = df_whatsapp['revenue'].sum()
        whatsapp_conversion = (whatsapp_orders / whatsapp_sent * 100) if whatsapp_sent > 0 else 0
        whatsapp_avg_order = (whatsapp_revenue / whatsapp_orders) if whatsapp_orders > 0 else 0
        
        # Load detailed data for hours calculation
        df_detailed = load_coffeemais_crm_detailed()
        total_avg_hours = df_detailed['hours_between'].mean()
        email_avg_hours = df_detailed[df_detailed['channel'] == 'email']['hours_between'].mean()
        whatsapp_avg_hours = df_detailed[df_detailed['channel'] == 'whatsapp']['hours_between'].mean()
        
        # Display total metrics
        st.subheader("📊 Métricas Totais")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            big_number_box(
                data=f"{total_sent:,.0f}".replace(",", "."),
                label="Total de Mensagens",
                hint="Número total de mensagens enviadas no período"
            )
        
        with col2:
            big_number_box(
                data=f"{total_orders:,.0f}".replace(",", "."),
                label="Total de Pedidos",
                hint="Número total de pedidos gerados pelas mensagens"
            )
        
        with col3:
            big_number_box(
                data=f"{conversion_rate:.2f}%".replace(".", ","),
                label="Taxa de Conversão",
                hint="Percentual de mensagens que geraram pedidos"
            )
        
        with col4:
            big_number_box(
                data=f"R$ {total_revenue:,.2f}".replace(",", "."),
                label="Receita Total",
                hint="Valor total gerado pelas mensagens"
            )
        
        with col5:
            big_number_box(
                data=f"R$ {avg_revenue_per_order:,.2f}".replace(",", "."),
                label="Ticket Médio",
                hint="Valor médio por pedido"
            )

        with col6:
            big_number_box(
                data=f"{total_avg_hours:.1f}".replace(".", ","),
                label="Média de Horas até a Compra",
                hint="Tempo médio em horas entre o envio da mensagem e a realização da compra"
            )
        
        # Display email metrics
        st.subheader("📧 Métricas de E-mail")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            big_number_box(
                data=f"{email_sent:,.0f}".replace(",", "."),
                label="Mensagens Enviadas",
                hint="Número total de e-mails enviados no período"
            )
        
        with col2:
            big_number_box(
                data=f"{email_orders:,.0f}".replace(",", "."),
                label="Pedidos",
                hint="Número de pedidos gerados por e-mail"
            )
        
        with col3:
            big_number_box(
                data=f"{email_conversion:.2f}%".replace(".", ","),
                label="Taxa de Conversão",
                hint="Percentual de e-mails que geraram pedidos"
            )
        
        with col4:
            big_number_box(
                data=f"R$ {email_revenue:,.2f}".replace(",", "."),
                label="Receita",
                hint="Valor total gerado por e-mails"
            )
        
        with col5:
            big_number_box(
                data=f"R$ {email_avg_order:,.2f}".replace(",", "."),
                label="Ticket Médio",
                hint="Valor médio por pedido via e-mail"
            )

        with col6:
            big_number_box(
                data=f"{email_avg_hours:.1f}".replace(".", ","),
                label="Média de Horas até a Compra",
                hint="Tempo médio em horas entre o envio do e-mail e a realização da compra"
            )
        
        # Display WhatsApp metrics
        st.subheader("💬 Métricas de WhatsApp")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            big_number_box(
                data=f"{whatsapp_sent:,.0f}".replace(",", "."),
                label="Mensagens Enviadas",
                hint="Número total de mensagens de WhatsApp enviadas"
            )
        
        with col2:
            big_number_box(
                data=f"{whatsapp_orders:,.0f}".replace(",", "."),
                label="Pedidos",
                hint="Número de pedidos gerados por WhatsApp"
            )
        
        with col3:
            big_number_box(
                data=f"{whatsapp_conversion:.2f}%".replace(".", ","),
                label="Taxa de Conversão",
                hint="Percentual de mensagens de WhatsApp que geraram pedidos"
            )
        
        with col4:
            big_number_box(
                data=f"R$ {whatsapp_revenue:,.2f}".replace(",", "."),
                label="Receita",
                hint="Valor total gerado por WhatsApp"
            )
        
        with col5:
            big_number_box(
                data=f"R$ {whatsapp_avg_order:,.2f}".replace(",", "."),
                label="Ticket Médio",
                hint="Valor médio por pedido via WhatsApp"
            )

        with col6:
            big_number_box(
                data=f"{whatsapp_avg_hours:.1f}".replace(".", ","),
                label="Média de Horas até a Compra",
                hint="Tempo médio em horas entre o envio da mensagem de WhatsApp e a realização da compra"
            )
        
        # Add spacing
        st.markdown("---")
        
        # Add filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filter by channel
            channel_names = ['Todos'] + sorted(df['channel'].unique().tolist())
            channel_labels = {
                'Todos': 'Todos os Canais',
                'email': '📧 E-mail',
                'whatsapp': '💬 WhatsApp'
            }
            selected_channel = st.selectbox(
                'Filtrar por Canal:',
                channel_names,
                format_func=lambda x: channel_labels.get(x, x)
            )
        
        with col2:
            # Filter by segment
            segment_names = ['Todos'] + sorted(df['segment'].unique().tolist())
            selected_segment = st.selectbox('Filtrar por Segmento:', segment_names)
        
        with col3:
            # Filter by segment type
            segment_types = ['Todos'] + sorted(df['segment_type'].unique().tolist())
            selected_segment_type = st.selectbox('Filtrar por Tipo de Segmento:', segment_types)
        
        with col4:
            # Filter by disparo type
            disparo_types = ['Todos'] + sorted(df['disparo_type'].unique().tolist())
            selected_disparo_type = st.selectbox('Filtrar por Tipo de Disparo:', disparo_types)
        
        # Add notification filter in a new line with full width
        # Filter by notification name
        notification_names = ['Todos'] + sorted(df['name'].unique().tolist())
        selected_notification = st.selectbox('Filtrar por Nome da Notificação:', notification_names)
        
        # Filter the dataframe
        filtered_df = df.copy()
        
        # Apply channel filter
        if selected_channel != 'Todos':
            filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
        
        # Apply segment filter
        if selected_segment != 'Todos':
            filtered_df = filtered_df[filtered_df['segment'] == selected_segment]
        
        # Apply segment type filter
        if selected_segment_type != 'Todos':
            filtered_df = filtered_df[filtered_df['segment_type'] == selected_segment_type]
        
        # Apply disparo type filter
        if selected_disparo_type != 'Todos':
            filtered_df = filtered_df[filtered_df['disparo_type'] == selected_disparo_type]
        
        # Apply notification filter
        if selected_notification != 'Todos':
            filtered_df = filtered_df[filtered_df['name'] == selected_notification]
        
        # Calculate conversion rate for each row
        filtered_df['conversion_rate'] = (filtered_df['orders'] / filtered_df['sent'] * 100).round(2)
        
        # Calculate open rate and failure rate
        filtered_df['open_rate'] = (filtered_df['read'] / filtered_df['sent'] * 100).round(2)
        filtered_df['failure_rate'] = (filtered_df['failed'] / filtered_df['sent'] * 100).round(2)
        
        # Format the dates
        filtered_df['date_first_sent'] = pd.to_datetime(filtered_df['date_first_sent']).dt.strftime('%d/%m/%Y %H:%M')
        filtered_df['date_last_sent'] = pd.to_datetime(filtered_df['date_last_sent']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Rename columns for better presentation
        filtered_df = filtered_df.rename(columns={
            'channel': 'Canal',
            'date_first_sent': 'Primeiro Envio',
            'date_last_sent': 'Último Envio',
            'days_between': 'Dias Entre Envios',
            'name': 'Nome da Notificação',
            'segment': 'Nome do Segmento',
            'segment_type': 'Tipo de Segmento',
            'disparo_type': 'Tipo de Disparo',
            'sent': 'Mensagens Enviadas',
            'orders': 'Pedidos',
            'revenue': 'Receita',
            'conversion_rate': 'Taxa de Conversão (%)',
            'open_rate': 'Taxa de Abertura (%)',
            'failure_rate': 'Taxa de Falha (%)'
        })
        
        # Reorder columns
        columns_order = [
            'Canal',
            'Tipo de Disparo',
            'Nome do Segmento',
            'Tipo de Segmento',
            'Nome da Notificação',
            'Primeiro Envio',
            'Último Envio',
            'Mensagens Enviadas',
            'Pedidos',
            'Taxa de Conversão (%)',
            'Taxa de Abertura (%)',
            'Taxa de Falha (%)',
            'Receita'
        ]
        filtered_df = filtered_df[columns_order]
        
        # Display the dataframe with sorting enabled
        st.data_editor(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Receita': st.column_config.NumberColumn(
                    'Receita',
                    format="R$ %.2f",
                    help="Valor total da receita"
                ),
                'Taxa de Conversão (%)': st.column_config.NumberColumn(
                    'Taxa de Conversão (%)',
                    format="%.2f%%",
                    help="Percentual de mensagens que geraram pedidos"
                ),
                'Taxa de Abertura (%)': st.column_config.NumberColumn(
                    'Taxa de Abertura (%)',
                    format="%.2f%%",
                    help="Percentual de mensagens que foram abertas"
                ),
                'Taxa de Falha (%)': st.column_config.NumberColumn(
                    'Taxa de Falha (%)',
                    format="%.2f%%",
                    help="Percentual de mensagens que falharam no envio"
                ),
                'Mensagens Enviadas': st.column_config.NumberColumn(
                    'Mensagens Enviadas',
                    format="%.0f",
                    help="Número total de mensagens enviadas"
                ),
                'Pedidos': st.column_config.NumberColumn(
                    'Pedidos',
                    format="%.0f",
                    help="Número total de pedidos"
                )
            }
        )

        with st.spinner("Carregando dados detalhados de envio..."):
            df_detailed = load_coffeemais_crm_detailed()
            
            # Format dates
            df_detailed['date_first_sent'] = pd.to_datetime(df_detailed['date_first_sent']).dt.strftime('%d/%m/%Y %H:%M')
            df_detailed['date_last_sent'] = pd.to_datetime(df_detailed['date_last_sent']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Add title
            st.subheader("Detalhamento de Mensagens")
            
            # Add email search filter
            email_search = st.text_input('Buscar por E-mail:', '')
            if email_search:
                df_detailed = df_detailed[df_detailed['email'].str.contains(email_search, case=False, na=False)]
            
            # Sort by date_first_sent in descending order
            df_detailed = df_detailed.sort_values('date_first_sent', ascending=False)
            
            # Rename columns
            df_detailed = df_detailed.rename(columns={
                'channel': 'Canal',
                'id_notificacao': 'ID da Notificação',
                'id_disparo': 'ID do Disparo',
                'email': 'E-mail',
                'date_first_sent': 'Data do Envio',
                'name': 'Nome da Notificação',
                'sent': 'Mensagens Enviadas',
                'delivered': 'Mensagens Entregues',
                'failed': 'Mensagens com Falha',
                'read': 'Mensagens Lidas',
                'order_id': 'ID Pedido',
                'orders': 'Pedidos',
                'revenue': 'Receita',
                'hours_between': 'Horas até a Compra'
            })
            
            # Reorder columns
            columns_order = [
                'Canal',
                'ID da Notificação',
                'ID do Disparo',
                'E-mail',
                'Nome da Notificação',
                'Data do Envio',
                'Horas até a Compra',
                'Mensagens Enviadas',
                'Mensagens Entregues',
                'Mensagens com Falha',
                'Mensagens Lidas',
                'ID Pedido',
                'Pedidos',
                'Receita'
            ]
            df_detailed = df_detailed[columns_order]
            
            # Display the dataframe with sorting enabled
            st.data_editor(
                df_detailed,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Receita': st.column_config.NumberColumn(
                        'Receita',
                        format="R$ %.2f",
                        help="Valor total da receita"
                    ),
                    'Horas até a Compra': st.column_config.NumberColumn(
                        'Horas até a Compra',
                        format="%.0f",
                        help="Tempo em horas entre o envio e a compra"
                    ),
                    'Mensagens Enviadas': st.column_config.NumberColumn(
                        'Mensagens Enviadas',
                        format="%.0f",
                        help="Número total de mensagens enviadas"
                    ),
                    'Mensagens Entregues': st.column_config.NumberColumn(
                        'Mensagens Entregues',
                        format="%.0f",
                        help="Número de mensagens entregues com sucesso"
                    ),
                    'Mensagens com Falha': st.column_config.NumberColumn(
                        'Mensagens com Falha',
                        format="%.0f",
                        help="Número de mensagens que falharam no envio"
                    ),
                    'Mensagens Lidas': st.column_config.NumberColumn(
                        'Mensagens Lidas',
                        format="%.0f",
                        help="Número de mensagens que foram lidas"
                    ),
                    'Pedidos': st.column_config.NumberColumn(
                        'Pedidos',
                        format="%.0f",
                        help="Número total de pedidos"
                    )
                }
            )

    # Display WhatsApp errors analysis
    with tab_erros:
        # Load WhatsApp errors data
        df_errors = load_coffeemais_gupshup_errors()
        
        if not df_errors.empty:
            # Convert datetime to date for better grouping
            df_errors['date'] = pd.to_datetime(df_errors['datetime']).dt.date
            
            # Filter by date range from session state
            start_date = pd.to_datetime(st.session_state.start_date).date()
            end_date = pd.to_datetime(st.session_state.end_date).date()
            df_errors = df_errors[
                (df_errors['date'] >= start_date) & 
                (df_errors['date'] <= end_date)
            ]
            
            if not df_errors.empty:
                # Calculate total errors
                total_errors = len(df_errors)
                
                # Calculate number of days in the period
                days_in_period = (end_date - start_date).days + 1
                
                # Group by fail reason
                errors_by_reason = df_errors.groupby('fail_reason').size().reset_index(name='count')
                errors_by_reason = errors_by_reason.sort_values('count', ascending=False)
                
                # Group by date
                errors_by_date = df_errors.groupby('date').size().reset_index(name='count')
                
                # Display metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    big_number_box(
                        data=f"{total_errors:,}".replace(",", "."),
                        label="Total de Erros",
                        hint=f"Número total de erros no período selecionado ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')})"
                    )
                
                with col2:
                    big_number_box(
                        data=f"{(total_errors/days_in_period):.1f}".replace(".", ","),
                        label="Média Diária de Erros",
                        hint=f"Média de erros por dia no período selecionado"
                    )
                
                # Display error reasons table
                st.subheader("Distribuição de Erros por Motivo")
                st.dataframe(
                    errors_by_reason.rename(columns={
                        'fail_reason': 'Motivo do Erro',
                        'count': 'Quantidade'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Display error evolution chart
                st.subheader("Evolução de Erros ao Longo do Tempo")
                
                # Add error type filter
                error_types = ['Todos'] + sorted(df_errors['fail_reason'].unique().tolist())
                selected_error = st.selectbox('Filtrar por Tipo de Erro:', error_types)
                
                # Filter errors by type if selected
                if selected_error != 'Todos':
                    df_errors_filtered = df_errors[df_errors['fail_reason'] == selected_error]
                    errors_by_date = df_errors_filtered.groupby('date').size().reset_index(name='count')
                else:
                    errors_by_date = df_errors.groupby('date').size().reset_index(name='count')
                
                # Format date for better display
                errors_by_date['date'] = pd.to_datetime(errors_by_date['date']).dt.strftime('%d/%m/%Y')
                
                # Create bar chart
                st.bar_chart(
                    errors_by_date.set_index('date'),
                    use_container_width=True,
                    height=400
                )
                
                # Display detailed error log
                st.subheader("Log Detalhado de Erros")
                st.dataframe(
                    df_errors.rename(columns={
                        'datetime': 'Data/Hora',
                        'message_id': 'ID da Mensagem',
                        'fail_reason': 'Motivo do Erro',
                        'phone_destination': 'Telefone de Destino'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"Não foram encontrados erros de envio de WhatsApp no período selecionado ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}).")
        else:
            st.info("Não foram encontrados erros de envio de WhatsApp no período.")