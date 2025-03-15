import streamlit as st
from modules.load_data import load_coffeemais_crm
from modules.components import big_number_box
import pandas as pd

def display_tab_coffeemais_crm():
    # Load the data
    df = load_coffeemais_crm()
    
    # Add a title
    st.title("CRM")
    
    # Add attribution model explanation in a collapsible section
    with st.expander("Sobre o Modelo de Atribuição"):
        st.info("""
        Os dados apresentados neste dashboard seguem o seguinte modelo de atribuição:
        - A conversão é atribuída ao envio da mensagem (e-mail ou WhatsApp)
        - O prazo de conversão considerado é de até 7 dias após o envio da mensagem
        - Pedidos realizados após 7 dias do envio não são contabilizados nesta análise
        """)
    
    # Create tabs for different views
    tab_geral, tab_email, tab_whatsapp = st.tabs(["Geral", "E-mail", "WhatsApp"])
    
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
    
    # Display metrics in General tab
    with tab_geral:
        col1, col2, col3, col4, col5 = st.columns(5)
        
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
    
    # Display metrics in Email tab
    with tab_email:
        col1, col2, col3, col4, col5 = st.columns(5)
        
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
    
    # Display metrics in WhatsApp tab
    with tab_whatsapp:
        col1, col2, col3, col4, col5 = st.columns(5)
        
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
    
    # Add spacing
    st.markdown("---")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
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
        # Filter by notification name
        notification_names = ['Todos'] + sorted(df['name'].unique().tolist())
        selected_notification = st.selectbox('Filtrar por Nome da Notificação:', notification_names)
    
    with col3:
        # Sort options
        sort_options = {
            'Mensagens Enviadas (Maior)': ('sent', False),
            'Mensagens Enviadas (Menor)': ('sent', True),
            'Receita (Maior)': ('revenue', False),
            'Receita (Menor)': ('revenue', True),
            'Taxa de Conversão (Maior)': ('conversion_rate', False),
            'Taxa de Conversão (Menor)': ('conversion_rate', True)
        }
        selected_sort = st.selectbox('Ordenar por:', list(sort_options.keys()))
    
    # Filter the dataframe
    filtered_df = df.copy()
    
    # Apply channel filter
    if selected_channel != 'Todos':
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
    
    # Apply notification filter
    if selected_notification != 'Todos':
        filtered_df = filtered_df[filtered_df['name'] == selected_notification]
    
    # Calculate conversion rate for each row
    filtered_df['conversion_rate'] = (filtered_df['orders'] / filtered_df['sent'] * 100).round(2)
    
    # Sort the dataframe
    sort_column, ascending = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
    
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
        'sent': 'Mensagens Enviadas',
        'orders': 'Pedidos',
        'revenue': 'Receita',
        'conversion_rate': 'Taxa de Conversão (%)'
    })
    
    # Reorder columns
    columns_order = [
        'Canal',
        'Nome da Notificação',
        'Primeiro Envio',
        'Último Envio',
        'Mensagens Enviadas',
        'Pedidos',
        'Taxa de Conversão (%)',
        'Receita'
    ]
    filtered_df = filtered_df[columns_order]
    
    # Display the dataframe
    st.data_editor(
        filtered_df.reset_index(drop=True),
        num_rows="dynamic",
        height=500,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Receita': st.column_config.NumberColumn(
                'Receita',
                format="R$ %.2f"
            ),
            'Taxa de Conversão (%)': st.column_config.NumberColumn(
                'Taxa de Conversão (%)',
                format="%.2f%%"
            )
        }
    )