import streamlit as st
import pandas as pd
import altair as alt
from modules.load_data import load_kaisan_erp_orders
from modules.components import big_number_box

# Adiciona CSS para evitar quebra de linha nos big numbers
st.markdown("""
<style>
.big-number {
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

def display_tab_kaisan_erp():
    st.title("ERP")
    st.markdown("""---""")

    # Load data
    df = load_kaisan_erp_orders()

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtros na Sidebar
    with st.sidebar:
        st.subheader("Filtros")
        
        # Filtro de Data
        min_date = df['date'].min()
        max_date = df['date'].max()
        default_start_date = max_date - pd.Timedelta(days=30)
        selected_dates = st.date_input(
            "Período",
            value=(default_start_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        st.markdown("""---""")
        
        # Filtro de Status
        status_options = sorted(df['status'].unique())
        status_options.insert(0, "Selecionar Todos")
        selected_status = st.multiselect(
            "Status",
            options=status_options,
            default=["Selecionar Todos"]
        )
        if "Selecionar Todos" in selected_status:
            selected_status = status_options[1:]  # Remove "Selecionar Todos" e usa todas as opções
        
        # Filtro de Método de Pagamento
        payment_options = sorted(df['metodo_pagamento'].unique())
        payment_options.insert(0, "Selecionar Todos")
        selected_payment = st.multiselect(
            "Método de Pagamento",
            options=payment_options,
            default=["Selecionar Todos"]
        )
        if "Selecionar Todos" in selected_payment:
            selected_payment = payment_options[1:]  # Remove "Selecionar Todos" e usa todas as opções
        
        # Filtro de Transportadora
        shipping_options = sorted(df['transportadora'].unique())
        shipping_options.insert(0, "Selecionar Todos")
        selected_shipping = st.multiselect(
            "Transportadora",
            options=shipping_options,
            default=["Selecionar Todos"]
        )
        if "Selecionar Todos" in selected_shipping:
            selected_shipping = shipping_options[1:]  # Remove "Selecionar Todos" e usa todas as opções
        
        # Filtro de Estado
        state_options = sorted(df['estado'].unique())
        state_options.insert(0, "Selecionar Todos")
        selected_state = st.multiselect(
            "Estado",
            options=state_options,
            default=["Selecionar Todos"]
        )
        if "Selecionar Todos" in selected_state:
            selected_state = state_options[1:]  # Remove "Selecionar Todos" e usa todas as opções
        
        # Filtro de Cidade
        city_options = sorted(df['cidade'].unique())
        city_options.insert(0, "Selecionar Todos")
        selected_city = st.multiselect(
            "Cidade",
            options=city_options,
            default=["Selecionar Todos"]
        )
        if "Selecionar Todos" in selected_city:
            selected_city = city_options[1:]  # Remove "Selecionar Todos" e usa todas as opções
    
    # Aplicar filtros
    if len(selected_dates) == 2:
        df = df[
            (df['date'].dt.date >= selected_dates[0]) &
            (df['date'].dt.date <= selected_dates[1])
        ]
    
    if selected_status:
        df = df[df['status'].isin(selected_status)]
    
    if selected_payment:
        df = df[df['metodo_pagamento'].isin(selected_payment)]
    
    if selected_shipping:
        df = df[df['transportadora'].isin(selected_shipping)]
    
    if selected_state:
        df = df[df['estado'].isin(selected_state)]
    
    if selected_city:
        df = df[df['cidade'].isin(selected_city)]
    
    st.markdown("""---""")
    
    # Calculate metrics
    total_orders = df['pedidos'].sum()
    total_revenue = df['receita'].sum()
    total_items = df['itens_vendidos'].sum()
    total_cost = df['custo'].sum()
    total_discounts = df['descontos'].sum()
    
    # Calculate billed metrics (excluding cancelled orders)
    billed_orders = df[df['status'] != 'Pedido Cancelado']['pedidos'].sum()
    billed_revenue = df[df['status'] != 'Pedido Cancelado']['receita'].sum()
    billed_cost = df[df['status'] != 'Pedido Cancelado']['custo'].sum()
    
    # Calculate derived metrics
    itens_por_pedido = total_items / total_orders if total_orders > 0 else 0
    ticket_medio = total_revenue / total_orders if total_orders > 0 else 0
    cpv_percentage = (billed_cost / billed_revenue * 100) if billed_revenue > 0 else 0
    
    # Display key metrics using big_number_box
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"{total_orders:,.0f}".replace(",", "."),
            label="Pedidos Captados",
            hint="Número total de pedidos no período"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"R$ {total_revenue:,.0f}".replace(",", "."),
            label="Receita Capturada",
            hint="Valor total de receita no período"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"{billed_orders:,.0f}".replace(",", "."),
            label="Pedidos Faturados",
            hint="Número de pedidos não cancelados"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"R$ {billed_revenue:,.0f}".replace(",", "."),
            label="Receita Faturada",
            hint="Valor total de receita não cancelada"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"{total_items:,.0f}".replace(",", "."),
            label="Itens Vendidos",
            hint="Número total de itens vendidos no período"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display derived metrics
    col6, col7, col8, col9 = st.columns(4)
    
    with col6:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"{itens_por_pedido:.2f}".replace(".", ","),
            label="Itens por Pedido",
            hint="Média de itens por pedido"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col7:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"R$ {ticket_medio:,.0f}".replace(",", "."),
            label="Ticket Médio",
            hint="Valor médio por pedido"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col8:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"{cpv_percentage:.1f}%".replace(".", ","),
            label="% CPV",
            hint="Percentual do custo de produtos vendidos sobre a receita"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with col9:
        st.markdown('<div style="white-space: nowrap;">', unsafe_allow_html=True)
        big_number_box(
            data=f"R$ {total_discounts:,.0f}".replace(",", "."),
            label="Descontos",
            hint="Valor total de descontos aplicados"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""---""")
    
    # Daily evolution chart
    st.subheader("Evolução Diária")
    
    # Aggregate data by date first
    daily_data = df.groupby('date').agg({
        'pedidos': 'sum',
        'receita': 'sum',
        'itens_vendidos': 'sum',
        'custo': 'sum',
        'descontos': 'sum'
    }).reset_index()
    
    # Formata os valores para o tooltip
    daily_data['pedidos_fmt'] = daily_data['pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    daily_data['receita_fmt'] = daily_data['receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    daily_data['itens_vendidos_fmt'] = daily_data['itens_vendidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    daily_data['itens_por_pedido'] = daily_data['itens_vendidos'] / daily_data['pedidos']
    daily_data['itens_por_pedido_fmt'] = daily_data['itens_por_pedido'].apply(lambda x: f"{x:.2f}".replace(".", ","))
    
    # Cria o gráfico de Pedidos com a cor #3B82F6 (azul)
    line_orders = alt.Chart(daily_data).mark_line(color='#3B82F6', strokeWidth=2.5).encode(
        x=alt.X('date:T', 
                title='Data',
                axis=alt.Axis(format='%d/%m', labelAngle=0)),
        y=alt.Y('pedidos:Q', 
                axis=alt.Axis(title='Pedidos',
                             format=',.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('date:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('pedidos_fmt:N', title='Pedidos')
        ]
    )

    # Cria o gráfico de Receita com barras estilosas
    bar_receita = alt.Chart(daily_data).mark_bar(color='#E5E7EB', size=20).encode(
        x=alt.X('date:T', title='Data'),
        y=alt.Y('receita:Q', 
                axis=alt.Axis(title='Receita',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('date:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('receita_fmt:N', title='Receita')
        ]
    )

    # Combine os dois gráficos com melhorias visuais
    daily_chart = alt.layer(
        bar_receita,
        line_orders
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Evolução de Pedidos e Receita',
            fontSize=16,
            font='DM Sans',
            anchor='start',
            dy=-10
        )
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

    # Exibe o gráfico no Streamlit
    st.altair_chart(daily_chart, use_container_width=True)

    # Adiciona legenda manual com design melhorado
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                <span style="color: #4B5563; font-size: 14px;">Pedidos</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                <span style="color: #4B5563; font-size: 14px;">Receita</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Timeline de Itens
    st.subheader("Evolução de Itens")
    
    # Cria o gráfico de Itens Vendidos com a cor #10B981 (verde)
    line_items = alt.Chart(daily_data).mark_line(color='#10B981', strokeWidth=2.5).encode(
        x=alt.X('date:T', 
                title='Data',
                axis=alt.Axis(format='%d/%m', labelAngle=0)),
        y=alt.Y('itens_vendidos:Q', 
                axis=alt.Axis(title='Itens Vendidos',
                             format=',.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('date:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('itens_vendidos_fmt:N', title='Itens Vendidos')
        ]
    )

    # Cria o gráfico de Itens por Pedido com a cor #F59E0B (laranja)
    line_items_per_order = alt.Chart(daily_data).mark_line(color='#F59E0B', strokeWidth=2.5).encode(
        x=alt.X('date:T', title='Data'),
        y=alt.Y('itens_por_pedido:Q', 
                axis=alt.Axis(title='Itens por Pedido',
                             format='.2f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('date:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('itens_por_pedido_fmt:N', title='Itens por Pedido')
        ]
    )

    # Combine os dois gráficos com melhorias visuais
    items_chart = alt.layer(
        line_items,
        line_items_per_order
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Evolução de Itens Vendidos e Itens por Pedido',
            fontSize=16,
            font='DM Sans',
            anchor='start',
            dy=-10
        )
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

    # Exibe o gráfico no Streamlit
    st.altair_chart(items_chart, use_container_width=True)

    # Adiciona legenda manual com design melhorado
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #10B981;"></div>
                <span style="color: #4B5563; font-size: 14px;">Itens Vendidos</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #F59E0B;"></div>
                <span style="color: #4B5563; font-size: 14px;">Itens por Pedido</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Daily metrics table
    st.subheader("Métricas Diárias")
    daily_metrics = daily_data.copy()
    daily_metrics['date'] = daily_metrics['date'].dt.strftime('%d/%m/%Y')
    daily_metrics = daily_metrics.sort_values('date', ascending=False)
    
    # Calcular métricas derivadas
    daily_metrics['Ticket Médio'] = daily_metrics['receita'] / daily_metrics['pedidos']
    daily_metrics['Itens por Pedido'] = daily_metrics['itens_vendidos'] / daily_metrics['pedidos']
    
    # Remover colunas de formatação e métricas não desejadas
    columns_to_drop = ['pedidos_fmt', 'receita_fmt', 'itens_vendidos_fmt', 'itens_por_pedido_fmt', 'custo', 'descontos']
    daily_metrics = daily_metrics.drop(columns=[col for col in columns_to_drop if col in daily_metrics.columns], axis=1)
    
    # Renomear colunas
    column_mapping = {
        'date': 'Data',
        'pedidos': 'Pedidos',
        'receita': 'Receita',
        'itens_vendidos': 'Itens Vendidos',
        'Ticket Médio': 'Ticket Médio',
        'Itens por Pedido': 'Itens por Pedido'
    }
    daily_metrics = daily_metrics.rename(columns=column_mapping)
    
    st.data_editor(
        daily_metrics,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Receita': st.column_config.NumberColumn(
                'Receita',
                format="R$ %.2f"
            ),
            'Ticket Médio': st.column_config.NumberColumn(
                'Ticket Médio',
                format="R$ %.2f"
            ),
            'Itens por Pedido': st.column_config.NumberColumn(
                'Itens por Pedido',
                format="%.2f"
            )
        }
    )
    
    st.markdown("""---""")
    
    # Status, Payment Method and Shipping sections
    st.subheader("Status dos Pedidos")
    status_col1, status_col2 = st.columns([1, 2])
    
    with status_col1:
        # Aggregate data by status
        status_data = df.groupby('status').agg({
            'pedidos': 'sum',
            'receita': 'sum',
            'itens_vendidos': 'sum'
        }).reset_index()
        
        # Calcular métricas derivadas
        status_data['Ticket Médio'] = status_data['receita'] / status_data['pedidos']
        status_data['Itens por Pedido'] = status_data['itens_vendidos'] / status_data['pedidos']
        
        # Renomear colunas
        status_data.columns = ['Status', 'Pedidos', 'Receita', 'Itens Vendidos', 'Ticket Médio', 'Itens por Pedido']
        
        # Status distribution pie chart
        status_pie = alt.Chart(status_data).mark_arc(
            innerRadius=50,
            outerRadius=100
        ).encode(
            theta=alt.Theta(field='Pedidos', type='quantitative', stack=True),
            color=alt.Color(field='Status', type='nominal'),
            tooltip=[
                alt.Tooltip('Status:N', title='Status'),
                alt.Tooltip('Pedidos:Q', title='Pedidos', format=',d'),
                alt.Tooltip('Receita:Q', title='Receita', format='$,.2f')
            ]
        ).properties(
            title=alt.TitleParams(
                text='Distribuição por Status',
                fontSize=16,
                font='DM Sans',
                anchor='start',
                dy=-10
            ),
            height=400
        )
        
        st.altair_chart(status_pie, use_container_width=True)
    
    with status_col2:
        # Status metrics table
        st.subheader("Métricas por Status")
        status_metrics = status_data.sort_values('Pedidos', ascending=False)
        
        st.data_editor(
            status_metrics,
            hide_index=True,
            use_container_width=True,
            column_config={
                'Receita': st.column_config.NumberColumn(
                    'Receita',
                    format="R$ %.2f"
                ),
                'Ticket Médio': st.column_config.NumberColumn(
                    'Ticket Médio',
                    format="R$ %.2f"
                ),
                'Itens por Pedido': st.column_config.NumberColumn(
                    'Itens por Pedido',
                    format="%.2f"
                )
            }
        )
    
    st.markdown("""---""")
    
    st.subheader("Métodos de Pagamento")
    payment_col1, payment_col2 = st.columns([1, 2])
    
    with payment_col1:
        # Payment method metrics table
        payment_metrics = df.groupby('metodo_pagamento').agg({
            'pedidos': 'sum',
            'receita': 'sum',
            'itens_vendidos': 'sum'
        }).reset_index()
        
        # Calcular métricas derivadas
        payment_metrics['Ticket Médio'] = payment_metrics['receita'] / payment_metrics['pedidos']
        payment_metrics['Itens por Pedido'] = payment_metrics['itens_vendidos'] / payment_metrics['pedidos']
        
        # Renomear colunas
        payment_metrics.columns = ['Método de Pagamento', 'Pedidos', 'Receita', 'Itens Vendidos', 'Ticket Médio', 'Itens por Pedido']
        
        # Payment method distribution
        payment_pie = alt.Chart(payment_metrics).mark_arc(
            innerRadius=50,
            outerRadius=100
        ).encode(
            theta=alt.Theta(field='Pedidos', type='quantitative', stack=True),
            color=alt.Color(field='Método de Pagamento', type='nominal'),
            tooltip=[
                alt.Tooltip('Método de Pagamento:N', title='Método de Pagamento'),
                alt.Tooltip('Pedidos:Q', title='Pedidos', format=',d'),
                alt.Tooltip('Receita:Q', title='Receita', format='$,.2f')
            ]
        ).properties(
            title=alt.TitleParams(
                text='Distribuição por Método de Pagamento',
                fontSize=16,
                font='DM Sans',
                anchor='start',
                dy=-10
            ),
            height=400
        )
        
        st.altair_chart(payment_pie, use_container_width=True)
    
    with payment_col2:
        # Payment method metrics table
        st.subheader("Métricas por Método de Pagamento")
        payment_metrics = payment_metrics.sort_values('Pedidos', ascending=False)
        
        st.data_editor(
            payment_metrics,
            hide_index=True,
            use_container_width=True,
            column_config={
                'Receita': st.column_config.NumberColumn(
                    'Receita',
                    format="R$ %.2f"
                ),
                'Ticket Médio': st.column_config.NumberColumn(
                    'Ticket Médio',
                    format="R$ %.2f"
                ),
                'Itens por Pedido': st.column_config.NumberColumn(
                    'Itens por Pedido',
                    format="%.2f"
                )
            }
        )
    
    st.markdown("""---""")
    
    st.subheader("Transportadoras")
    shipping_col1, shipping_col2 = st.columns([1, 2])
    
    with shipping_col1:
        # Aggregate data by shipping carrier
        shipping_data = df.groupby('transportadora').agg({
            'pedidos': 'sum',
            'receita': 'sum',
            'itens_vendidos': 'sum'
        }).reset_index()
        
        # Calcular métricas derivadas
        shipping_data['Ticket Médio'] = shipping_data['receita'] / shipping_data['pedidos']
        shipping_data['Itens por Pedido'] = shipping_data['itens_vendidos'] / shipping_data['pedidos']
        
        # Renomear colunas
        shipping_data.columns = ['Transportadora', 'Pedidos', 'Receita', 'Itens Vendidos', 'Ticket Médio', 'Itens por Pedido']
        
        # Shipping carrier distribution pie chart
        shipping_pie = alt.Chart(shipping_data).mark_arc(
            innerRadius=50,
            outerRadius=100
        ).encode(
            theta=alt.Theta(field='Pedidos', type='quantitative', stack=True),
            color=alt.Color(field='Transportadora', type='nominal'),
            tooltip=[
                alt.Tooltip('Transportadora:N', title='Transportadora'),
                alt.Tooltip('Pedidos:Q', title='Pedidos', format=',d'),
                alt.Tooltip('Receita:Q', title='Receita', format='$,.2f')
            ]
        ).properties(
            title=alt.TitleParams(
                text='Distribuição por Transportadora',
                fontSize=16,
                font='DM Sans',
                anchor='start',
                dy=-10
            ),
            height=400
        )
        
        st.altair_chart(shipping_pie, use_container_width=True)
    
    with shipping_col2:
        # Shipping carrier metrics table
        st.subheader("Métricas por Transportadora")
        shipping_metrics = shipping_data.sort_values('Pedidos', ascending=False)
        
        st.data_editor(
            shipping_metrics,
            hide_index=True,
            use_container_width=True,
            column_config={
                'Receita': st.column_config.NumberColumn(
                    'Receita',
                    format="R$ %.2f"
                ),
                'Ticket Médio': st.column_config.NumberColumn(
                    'Ticket Médio',
                    format="R$ %.2f"
                ),
                'Itens por Pedido': st.column_config.NumberColumn(
                    'Itens por Pedido',
                    format="%.2f"
                )
            }
        )

    st.markdown("""---""")
    
    st.subheader("Estados")
    
    # Aggregate data by state
    states_data = df.groupby('estado').agg({
        'pedidos': 'sum',
        'receita': 'sum',
        'itens_vendidos': 'sum'
    }).reset_index()
    
    # Calcular métricas derivadas
    states_data['Ticket Médio'] = states_data['receita'] / states_data['pedidos']
    states_data['Itens por Pedido'] = states_data['itens_vendidos'] / states_data['pedidos']
    
    # Renomear colunas
    states_data.columns = ['Estado', 'Pedidos', 'Receita', 'Itens Vendidos', 'Ticket Médio', 'Itens por Pedido']
    
    # States metrics table
    states_metrics = states_data.sort_values('Pedidos', ascending=False)
    
    st.data_editor(
        states_metrics,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Receita': st.column_config.NumberColumn(
                'Receita',
                format="R$ %.2f"
            ),
            'Ticket Médio': st.column_config.NumberColumn(
                'Ticket Médio',
                format="R$ %.2f"
            ),
            'Itens por Pedido': st.column_config.NumberColumn(
                'Itens por Pedido',
                format="%.2f"
            )
        }
    )
    
    st.markdown("""---""")
    
    st.subheader("Cidades")
    
    # Aggregate data by city
    cities_data = df.groupby('cidade').agg({
        'pedidos': 'sum',
        'receita': 'sum',
        'itens_vendidos': 'sum'
    }).reset_index()
    
    # Calcular métricas derivadas
    cities_data['Ticket Médio'] = cities_data['receita'] / cities_data['pedidos']
    cities_data['Itens por Pedido'] = cities_data['itens_vendidos'] / cities_data['pedidos']
    
    # Renomear colunas
    cities_data.columns = ['Cidade', 'Pedidos', 'Receita', 'Itens Vendidos', 'Ticket Médio', 'Itens por Pedido']
    
    # Cities metrics table
    cities_metrics = cities_data.sort_values('Pedidos', ascending=False)
    
    st.data_editor(
        cities_metrics,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Receita': st.column_config.NumberColumn(
                'Receita',
                format="R$ %.2f"
            ),
            'Ticket Médio': st.column_config.NumberColumn(
                'Ticket Médio',
                format="R$ %.2f"
            ),
            'Itens por Pedido': st.column_config.NumberColumn(
                'Itens por Pedido',
                format="%.2f"
            )
        }
    )

