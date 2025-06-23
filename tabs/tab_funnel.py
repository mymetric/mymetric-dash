import streamlit as st
from modules.load_data import load_funnel_data, load_detailed_data, load_enhanced_ecommerce_funnel, load_intraday_ecommerce_funnel, load_enhanced_ecommerce_items_funnel
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

# Add custom CSS for the funnel tab
st.markdown("""
    <style>
        /* Card styles for metrics */
        .metric-card {
            background-color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Metric value styles */
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #1f2937;
            margin: 0.5rem 0;
        }
        
        /* Metric label styles */
        .metric-label {
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }
        
        /* Trend indicator styles */
        .trend-indicator {
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .trend-up {
            color: #059669;
        }
        
        .trend-down {
            color: #dc2626;
        }
        
        .trend-neutral {
            color: #6b7280;
        }
        
        /* Section header styles */
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* Table styles */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .dataframe th {
            background-color: #f8fafc;
            font-weight: 600;
            color: #1f2937;
        }
        
        .dataframe td {
            color: #4b5563;
        }
        
        /* Alert styles */
        .alert-box {
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .alert-warning {
            background-color: #fff7ed;
            border: 1px solid #fdba74;
        }
        
        .alert-success {
            background-color: #f0fdf4;
            border: 1px solid #86efac;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 1rem 0 2rem 0;
        }
        
        .metric-card {
            background-color: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 0.75rem;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #1f2937;
            margin: 0.5rem 0;
            line-height: 1.2;
        }
        
        .trend-indicator {
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.25rem;
            margin: 0.5rem 0;
        }
        
        .metric-footer {
            margin-top: auto;
            color: #6b7280;
            font-size: 0.8rem;
            padding-top: 0.5rem;
            border-top: 1px solid #e5e7eb;
        }
    </style>
""", unsafe_allow_html=True)

def display_intraday_comparison():
    st.subheader("Comparativo Ontem vs Hoje por Hora")
    
    # Carregar dados do funil intraday
    df = load_intraday_ecommerce_funnel()
    
    # Converter hora para datetime para facilitar manipulação
    df['datetime'] = pd.to_datetime(df['event_date']) + pd.to_timedelta(df['hour'], unit='h')
    
    # Separar dados de hoje e ontem
    hoje = pd.Timestamp.now(tz='America/Sao_Paulo').date()
    ontem = hoje - pd.Timedelta(days=1)
    
    df_hoje = df[df['event_date'] == hoje]
    df_ontem = df[df['event_date'] == ontem]
    
    # Mapear nomes dos eventos para português
    event_names = {
        'view_item': 'Visualização de Item',
        'add_to_cart': 'Adicionar ao Carrinho',
        'begin_checkout': 'Iniciar Checkout',
        'add_shipping_info': 'Adicionar Informação de Frete',
        'add_payment_info': 'Adicionar Informação de Pagamento',
        'purchase': 'Pedido'
    }
    
    # Calcular totais por evento
    totais_hoje = df_hoje.groupby('event_name')['events'].sum()
    totais_ontem = df_ontem.groupby('event_name')['events'].sum()
    
    # Calcular taxas médias para hoje
    taxas_hoje = {
        'Visualização de Item → Carrinho': round(totais_hoje.get('add_to_cart', 0) / totais_hoje.get('view_item', 1) * 100, 2),
        'Carrinho → Checkout': round(totais_hoje.get('begin_checkout', 0) / totais_hoje.get('add_to_cart', 1) * 100, 2),
        'Checkout → Frete': round(totais_hoje.get('add_shipping_info', 0) / totais_hoje.get('begin_checkout', 1) * 100, 2),
        'Frete → Pagamento': round(totais_hoje.get('add_payment_info', 0) / totais_hoje.get('add_shipping_info', 1) * 100, 2),
        'Pagamento → Pedido': round(totais_hoje.get('purchase', 0) / totais_hoje.get('add_payment_info', 1) * 100, 2),
        'Visualização de Item → Pedido': round(totais_hoje.get('purchase', 0) / totais_hoje.get('view_item', 1) * 100, 2)
    }
    
    # Calcular taxas médias para ontem
    taxas_ontem = {
        'Visualização de Item → Carrinho': round(totais_ontem.get('add_to_cart', 0) / totais_ontem.get('view_item', 1) * 100, 2),
        'Carrinho → Checkout': round(totais_ontem.get('begin_checkout', 0) / totais_ontem.get('add_to_cart', 1) * 100, 2),
        'Checkout → Frete': round(totais_ontem.get('add_shipping_info', 0) / totais_ontem.get('begin_checkout', 1) * 100, 2),
        'Frete → Pagamento': round(totais_ontem.get('add_payment_info', 0) / totais_ontem.get('add_shipping_info', 1) * 100, 2),
        'Pagamento → Pedido': round(totais_ontem.get('purchase', 0) / totais_ontem.get('add_payment_info', 1) * 100, 2),
        'Visualização de Item → Pedido': round(totais_ontem.get('purchase', 0) / totais_ontem.get('view_item', 1) * 100, 2)
    }
    
    # Criar DataFrame para taxas
    df_taxas = pd.DataFrame({
        'Etapa': list(taxas_hoje.keys()),
        'Hoje (%)': list(taxas_hoje.values()),
        'Ontem (%)': list(taxas_ontem.values())
    })
    
    # Calcular variação percentual
    df_taxas['Variação'] = ((df_taxas['Hoje (%)'] - df_taxas['Ontem (%)']) / df_taxas['Ontem (%)'] * 100).round(2)
    
    # Exibir big numbers para cada taxa
    st.markdown("### Taxas de Conversão")
    
    # Criar grid de métricas para taxas
    cols = st.columns(3)
    for idx, (etapa, taxa_hoje, taxa_ontem, variacao) in enumerate(zip(
        df_taxas['Etapa'],
        df_taxas['Hoje (%)'],
        df_taxas['Ontem (%)'],
        df_taxas['Variação']
    )):
        with cols[idx % 3]:
            # Container para a métrica
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{etapa}</div>
                    <div class="metric-value">{taxa_hoje:.2f}%</div>
                    <div class="metric-trend" style="color: {'#2E7D32' if variacao > 0 else '#C62828' if variacao < 0 else '#666'}">
                        {'↑' if variacao > 0 else '↓' if variacao < 0 else '→'} {variacao:+.2f}%
                    </div>
                    <div class="metric-comparison">Ontem: {taxa_ontem:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Exibir big numbers para valores absolutos
    st.markdown("### Volumes Totais")
    
    # Criar grid de métricas para valores absolutos
    cols = st.columns(3)
    for idx, (event, name) in enumerate(event_names.items()):
        with cols[idx % 3]:
            valor_hoje = totais_hoje.get(event, 0)
            valor_ontem = totais_ontem.get(event, 0)
            variacao = ((valor_hoje - valor_ontem) / valor_ontem * 100).round(2) if valor_ontem > 0 else 0
            
            # Container para a métrica
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{name}</div>
                    <div class="metric-value">{valor_hoje:,.0f}</div>
                    <div class="metric-trend" style="color: {'#2E7D32' if variacao > 0 else '#C62828' if variacao < 0 else '#666'}">
                        {'↑' if variacao > 0 else '↓' if variacao < 0 else '→'} {variacao:+.2f}%
                    </div>
                    <div class="metric-comparison">Ontem: {valor_ontem:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Exibir gráficos de volumes
    st.markdown("### Volumes por Hora")
    
    # Criar subplots para cada evento
    fig = make_subplots(
        rows=3, 
        cols=2,
        subplot_titles=[event_names[event] for event in ['view_item', 'add_to_cart', 'begin_checkout', 'add_shipping_info', 'add_payment_info', 'purchase']],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Cores para hoje e ontem (usando as mesmas cores da timeline)
    colors = {
        'hoje': '#4B8BBE',  # Azul mais suave
        'ontem': '#ADD8E6'  # Azul claro
    }
    
    # Adicionar linha para cada evento
    for idx, event in enumerate(['view_item', 'add_to_cart', 'begin_checkout', 'add_shipping_info', 'add_payment_info', 'purchase']):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        # Dados de hoje
        df_hoje_event = df_hoje[df_hoje['event_name'] == event].sort_values('hour')
        # Dados de ontem
        df_ontem_event = df_ontem[df_ontem['event_name'] == event].sort_values('hour')
        
        # Adicionar linha para hoje
        fig.add_trace(
            go.Scatter(
                x=df_hoje_event['hour'],
                y=df_hoje_event['events'],
                name=f'Hoje - {event_names[event]}',
                mode='lines+markers',
                line=dict(color=colors['hoje'], width=3),
                marker=dict(size=6, color=colors['hoje']),
                showlegend=(idx == 0)  # Mostrar legenda apenas para o primeiro evento
            ),
            row=row,
            col=col
        )
        
        # Adicionar linha para ontem
        fig.add_trace(
            go.Scatter(
                x=df_ontem_event['hour'],
                y=df_ontem_event['events'],
                name=f'Ontem - {event_names[event]}',
                mode='lines+markers',
                line=dict(color=colors['ontem'], width=3),
                marker=dict(size=6, color=colors['ontem']),
                showlegend=(idx == 0)  # Mostrar legenda apenas para o primeiro evento
            ),
            row=row,
            col=col
        )
        
        # Atualizar layout de cada subplot
        fig.update_xaxes(
            title_text="Hora",
            row=row,
            col=col,
            range=[0, 23],
            showgrid=False,
            zeroline=False,
            dtick=2
        )
        fig.update_yaxes(
            title_text="Quantidade",
            row=row,
            col=col,
            showgrid=False,
            zeroline=False
        )
    
    # Atualizar layout geral
    fig.update_layout(
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#E5E5E5',
            borderwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(t=100)
    )
    
    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Exibir gráficos de taxas
    st.markdown("### Taxas de Conversão por Hora")
    
    # Criar subplots para taxas de conversão
    fig_taxas = make_subplots(
        rows=3, 
        cols=2,
        subplot_titles=[
            'Visualização de Item → Carrinho',
            'Carrinho → Checkout',
            'Checkout → Frete',
            'Frete → Pagamento',
            'Pagamento → Pedido',
            'Visualização de Item → Pedido'
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Calcular taxas por hora
    def calcular_taxa_por_hora(df, evento_atual, evento_anterior):
        df_atual = df[df['event_name'] == evento_atual].sort_values('hour')
        df_anterior = df[df['event_name'] == evento_anterior].sort_values('hour')
        
        # Garantir que temos todas as horas
        horas = pd.DataFrame({'hour': range(24)})
        df_atual = horas.merge(df_atual, on='hour', how='left').fillna(0)
        df_anterior = horas.merge(df_anterior, on='hour', how='left').fillna(0)
        
        # Calcular taxa
        taxa = (df_atual['events'] / df_anterior['events'].replace(0, 1) * 100).round(2)
        return df_atual['hour'], taxa
    
    # Mapear etapas do funil
    etapas = [
        ('add_to_cart', 'view_item'),
        ('begin_checkout', 'add_to_cart'),
        ('add_shipping_info', 'begin_checkout'),
        ('add_payment_info', 'add_shipping_info'),
        ('purchase', 'add_payment_info'),
        ('purchase', 'view_item')
    ]
    
    # Adicionar cada taxa em um subplot
    for idx, (evento_atual, evento_anterior) in enumerate(etapas):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        # Calcular taxas para hoje e ontem
        horas_hoje, taxas_hoje = calcular_taxa_por_hora(df_hoje, evento_atual, evento_anterior)
        horas_ontem, taxas_ontem = calcular_taxa_por_hora(df_ontem, evento_atual, evento_anterior)
        
        # Adicionar linha para hoje
        fig_taxas.add_trace(
            go.Scatter(
                x=horas_hoje,
                y=taxas_hoje,
                name='Hoje',
                mode='lines+markers',
                line=dict(color=colors['hoje'], width=3),
                marker=dict(size=6, color=colors['hoje']),
                showlegend=(idx == 0)
            ),
            row=row,
            col=col
        )
        
        # Adicionar linha para ontem
        fig_taxas.add_trace(
            go.Scatter(
                x=horas_ontem,
                y=taxas_ontem,
                name='Ontem',
                mode='lines+markers',
                line=dict(color=colors['ontem'], width=3),
                marker=dict(size=6, color=colors['ontem']),
                showlegend=(idx == 0)
            ),
            row=row,
            col=col
        )
        
        # Atualizar layout de cada subplot
        fig_taxas.update_xaxes(
            title_text="Hora",
            row=row,
            col=col,
            range=[0, 23],
            showgrid=False,
            zeroline=False,
            dtick=2
        )
        fig_taxas.update_yaxes(
            title_text="Taxa (%)",
            row=row,
            col=col,
            showgrid=False,
            zeroline=False
        )
    
    # Atualizar layout geral
    fig_taxas.update_layout(
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#E5E5E5',
            borderwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(t=100)
    )
    
    # Exibir gráfico de taxas
    st.plotly_chart(fig_taxas, use_container_width=True)

def display_long_term_analysis():
    df = load_funnel_data()

    # Calcular taxas de conversão
    df['Taxa View Product -> Cart'] = (df['Adicionar ao Carrinho'] / df['Visualização de Item'] * 100).round(2)
    df['Taxa Cart -> Checkout'] = (df['Iniciar Checkout'] / df['Adicionar ao Carrinho'] * 100).round(2)
    df['Taxa Checkout -> Frete'] = (df['Adicionar Informação de Frete'] / df['Iniciar Checkout'] * 100).round(2)
    df['Taxa Dados de Frete -> Dados de Pagamento'] = (df['Adicionar Informação de Pagamento'] / df['Adicionar Informação de Frete'] * 100).round(2)
    df['Taxa Dados de Pagamento -> Pedido'] = (df['Pedido'] / df['Adicionar Informação de Pagamento'] * 100).round(2)
    df['Taxa View Product -> Pedido'] = (df['Pedido'] / df['Visualização de Item'] * 100).round(2)
    df['Taxa Checkout -> Pedido'] = (df['Pedido'] / df['Iniciar Checkout'] * 100).round(2)

    # Calcular totais do período
    total_data = {
        'Visualização de Item': df['Visualização de Item'].sum(),
        'Adicionar ao Carrinho': df['Adicionar ao Carrinho'].sum(),
        'Iniciar Checkout': df['Iniciar Checkout'].sum(),
        'Adicionar Informação de Frete': df['Adicionar Informação de Frete'].sum(),
        'Adicionar Informação de Pagamento': df['Adicionar Informação de Pagamento'].sum(),
        'Pedido': df['Pedido'].sum()
    }

    # Calcular taxas médias do período
    total_taxas = {
        'Taxa View Product -> Cart': (total_data['Adicionar ao Carrinho'] / total_data['Visualização de Item'] * 100).round(2),
        'Taxa Cart -> Checkout': (total_data['Iniciar Checkout'] / total_data['Adicionar ao Carrinho'] * 100).round(2),
        'Taxa Checkout -> Frete': (total_data['Adicionar Informação de Frete'] / total_data['Iniciar Checkout'] * 100).round(2),
        'Taxa Dados de Frete -> Dados de Pagamento': (total_data['Adicionar Informação de Pagamento'] / total_data['Adicionar Informação de Frete'] * 100).round(2),
        'Taxa Dados de Pagamento -> Pedido': (total_data['Pedido'] / total_data['Adicionar Informação de Pagamento'] * 100).round(2)
    }

    # Criar o funil customizado
    funnel_html = f"""
    <style>
        .funnel-container {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            font-family: 'DM Sans', sans-serif;
        }}
        .funnel-step {{
            position: relative;
            margin: 10px 0;
            padding: 20px;
            border-radius: 8px;
            color: white;
            transition: all 0.3s ease;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .funnel-step:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .funnel-main {{
            flex: 1;
        }}
        .funnel-cost {{
            text-align: right;
            margin-left: 20px;
            padding-left: 20px;
            border-left: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .funnel-value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .funnel-label {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .funnel-cost-value {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .funnel-cost-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .funnel-divider {{
            height: 2px;
            background: rgba(255, 255, 255, 0.2);
            margin: 15px 0;
        }}
        .step-1 {{ background: linear-gradient(135deg, #1a73e8, #0d47a1); width: 100%; }}
        .step-2 {{ background: linear-gradient(135deg, #2196f3, #1976d2); width: 90%; }}
        .step-3 {{ background: linear-gradient(135deg, #42a5f5, #2196f3); width: 80%; }}
        .step-4 {{ background: linear-gradient(135deg, #64b5f6, #42a5f5); width: 70%; }}
        .step-5 {{ background: linear-gradient(135deg, #90caf9, #64b5f6); width: 60%; }}
        .step-6 {{ background: linear-gradient(135deg, #bbdefb, #90caf9); width: 50%; }}
    </style>
    <div class="funnel-container">
        <div class="funnel-step step-1">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Visualização de Item']:,.0f}</div>
                <div class="funnel-label">Visualização de Item</div>
            </div>
        </div>
        <div class="funnel-step step-2">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Adicionar ao Carrinho']:,.0f}</div>
                <div class="funnel-label">Adicionar ao Carrinho</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{total_taxas['Taxa View Product -> Cart']:.2f}%</div>
                <div class="funnel-cost-label">Taxa de Conversão</div>
            </div>
        </div>
        <div class="funnel-step step-3">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Iniciar Checkout']:,.0f}</div>
                <div class="funnel-label">Iniciar Checkout</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{total_taxas['Taxa Cart -> Checkout']:.2f}%</div>
                <div class="funnel-cost-label">Taxa de Conversão</div>
            </div>
        </div>
        <div class="funnel-step step-4">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Adicionar Informação de Frete']:,.0f}</div>
                <div class="funnel-label">Adicionar Informação de Frete</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{total_taxas['Taxa Checkout -> Frete']:.2f}%</div>
                <div class="funnel-cost-label">Taxa de Conversão</div>
            </div>
        </div>
        <div class="funnel-step step-5">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Adicionar Informação de Pagamento']:,.0f}</div>
                <div class="funnel-label">Adicionar Informação de Pagamento</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{total_taxas['Taxa Dados de Frete -> Dados de Pagamento']:.2f}%</div>
                <div class="funnel-cost-label">Taxa de Conversão</div>
            </div>
        </div>
        <div class="funnel-step step-6">
            <div class="funnel-main">
                <div class="funnel-value">{total_data['Pedido']:,.0f}</div>
                <div class="funnel-label">Pedido</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{total_taxas['Taxa Dados de Pagamento -> Pedido']:.2f}%</div>
                <div class="funnel-cost-label">Taxa de Conversão</div>
            </div>
        </div>
    </div>
    """

    st.markdown(funnel_html, unsafe_allow_html=True)

    # Calcular desvios da média dos últimos 30 dias
    st.markdown('<div class="section-header">Desvios da Média (Últimos 30 dias)</div>', unsafe_allow_html=True)
    
    # Criar colunas para os cards
    cols = st.columns(3)
    
    # Estilo específico para os cards de métricas
    st.markdown("""
        <style>
            .metric-container {
                background-color: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border: 1px solid #e5e7eb;
                margin-bottom: 1rem;
            }
            
            .metric-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: #6b7280;
                margin-bottom: 0.75rem;
                font-weight: 500;
            }
            
            .metric-value {
                font-size: 2rem;
                font-weight: 600;
                color: #1f2937;
                margin: 0.5rem 0;
                line-height: 1.2;
            }
            
            .trend-indicator {
                font-size: 0.9rem;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 0.25rem;
                margin: 0.5rem 0;
            }
            
            .metric-footer {
                margin-top: 0.5rem;
                color: #6b7280;
                font-size: 0.8rem;
                padding-top: 0.5rem;
                border-top: 1px solid #e5e7eb;
            }
        </style>
    """, unsafe_allow_html=True)

    conversion_rates = [
        'Taxa View Product -> Cart',
        'Taxa Cart -> Checkout',
        'Taxa Checkout -> Frete',
        'Taxa Dados de Frete -> Dados de Pagamento',
        'Taxa Dados de Pagamento -> Pedido',
        'Taxa View Product -> Pedido',
        'Taxa Checkout -> Pedido'
    ]

    rate_names = {
        'Taxa View Product -> Cart': 'Visualização → Carrinho',
        'Taxa Cart -> Checkout': 'Carrinho → Checkout',
        'Taxa Checkout -> Frete': 'Checkout → Frete',
        'Taxa Dados de Frete -> Dados de Pagamento': 'Frete → Pagamento',
        'Taxa Dados de Pagamento -> Pedido': 'Pagamento → Pedido',
        'Taxa View Product -> Pedido': 'Visualização → Pedido',
        'Taxa Checkout -> Pedido': 'Checkout → Pedido'
    }

    for idx, rate in enumerate(conversion_rates):
        # Pegar últimos 30 dias e hoje
        last_30_days = df.iloc[-31:-1][rate].mean()
        today_value = df.iloc[-1][rate]
        std_30_days = df.iloc[-31:-1][rate].std()
        
        # Calcular desvio em relação à média
        deviation_percent = ((today_value - last_30_days) / last_30_days * 100).round(2)
        
        # Calcular quantos desvios padrão de diferença
        if std_30_days > 0:
            deviation_sigma = (today_value - last_30_days) / std_30_days
        else:
            deviation_sigma = 0
        
        # Determinar cor e ícone baseado no desvio padrão
        if deviation_sigma >= 2:
            trend_class = "trend-up"
            icon = "↗↗"
            color = "#059669"
        elif deviation_sigma >= 1.75:
            trend_class = "trend-up"
            icon = "↗"
            color = "#059669"
        elif deviation_sigma <= -2:
            trend_class = "trend-down"
            icon = "↘↘"
            color = "#dc2626"
        elif deviation_sigma <= -1.75:
            trend_class = "trend-down"
            icon = "↘"
            color = "#dc2626"
        else:
            trend_class = "trend-neutral"
            icon = "→"
            color = "#6b7280"
        
        # Criar o card na coluna apropriada
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{rate_names[rate]}</div>
                    <div class="metric-value">{today_value:.2f}%</div>
                    <div class="trend-indicator" style="color: {color};">{icon} {deviation_percent:+.2f}% vs média 30d</div>
                    <div class="metric-footer">Média 30d: {last_30_days:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""---""")
    st.markdown('<div class="section-header">Taxas de Conversão ao Longo do Tempo</div>', unsafe_allow_html=True)
    
    # Criar gráficos individuais para cada taxa de conversão
    fig = make_subplots(
        rows=4, 
        cols=2,
        subplot_titles=conversion_rates,
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Cores para cada gráfico
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6']

    # Adicionar cada taxa em um subplot separado
    for idx, rate in enumerate(conversion_rates):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        fig.add_trace(
            go.Scatter(
                x=df['Data'],
                y=df[rate],
                name=rate,
                mode='lines+markers',
                line=dict(color=colors[idx], width=2),
                marker=dict(size=6),
                showlegend=False
            ),
            row=row,
            col=col
        )

        # Atualizar layout de cada subplot
        fig.update_xaxes(
            title_text="Data",
            row=row,
            col=col,
            showgrid=True,
            gridcolor='#f1f5f9',
            zeroline=False
        )
        fig.update_yaxes(
            title_text="Taxa (%)",
            row=row,
            col=col,
            showgrid=True,
            gridcolor='#f1f5f9',
            zeroline=False
        )

    # Atualizar layout geral
    fig.update_layout(
        height=1200,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Exibir tabela com todos os dados
    st.markdown('<div class="section-header">Dados Detalhados</div>', unsafe_allow_html=True)
    st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        height=400
    )

def display_tab_funnel():
    st.title("Funil de Conversão")
    
    # Criar abas para diferentes análises
    tab1, tab2, tab3 = st.tabs([
        "Análise Diária",
        "Comparativo Ontem vs Hoje",
        "Funil de Produtos"
    ])
    
    with tab1:
        display_long_term_analysis()
    
    with tab2:
        display_intraday_comparison()
    
    with tab3:
        df = load_enhanced_ecommerce_items_funnel()
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Get unique categories and add "Todos" option
            categorias = ['Todos'] + sorted(df['Categoria do Produto'].unique().tolist())
            categoria_selecionada = st.selectbox(
                'Filtrar por Categoria',
                categorias,
                index=0
            )
        
        with col2:
            # Get products based on selected category
            if categoria_selecionada == 'Todos':
                produtos = ['Todos'] + sorted(df['Nome do Produto'].unique().tolist())
            else:
                produtos = ['Todos'] + sorted(df[df['Categoria do Produto'] == categoria_selecionada]['Nome do Produto'].unique().tolist())
            
            produto_selecionado = st.selectbox(
                'Filtrar por Produto',
                produtos,
                index=0
            )
        
        # Apply filters
        if categoria_selecionada != 'Todos':
            df = df[df['Categoria do Produto'] == categoria_selecionada]
        if produto_selecionado != 'Todos':
            df = df[df['Nome do Produto'] == produto_selecionado]
        
        # Calculate total values for the funnel with filtered data
        total_data = {
            'Visualização de Item': df['Visualização de Item'].sum(),
            'Adicionar ao Carrinho': df['Adicionar ao Carrinho'].sum(),
            'Iniciar Checkout': df['Iniciar Checkout'].sum(),
            'Adicionar Informação de Frete': df['Adicionar Informação de Frete'].sum(),
            'Adicionar Informação de Pagamento': df['Adicionar Informação de Pagamento'].sum(),
            'Pedido': df['Pedido'].sum()
        }

        # Calculate conversion rates
        total_taxas = {
            'Taxa View Product -> Cart': (total_data['Adicionar ao Carrinho'] / total_data['Visualização de Item'] * 100).round(2),
            'Taxa Cart -> Checkout': (total_data['Iniciar Checkout'] / total_data['Adicionar ao Carrinho'] * 100).round(2),
            'Taxa Checkout -> Frete': (total_data['Adicionar Informação de Frete'] / total_data['Iniciar Checkout'] * 100).round(2),
            'Taxa Frete -> Pagamento': (total_data['Adicionar Informação de Pagamento'] / total_data['Adicionar Informação de Frete'] * 100).round(2),
            'Taxa Pagamento -> Pedido': (total_data['Pedido'] / total_data['Adicionar Informação de Pagamento'] * 100).round(2)
        }

        # Create funnel HTML
        funnel_html = f"""
        <style>
            .funnel-container {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto 2rem auto;
                font-family: 'DM Sans', sans-serif;
            }}
            .funnel-step {{
                position: relative;
                margin: 10px 0;
                padding: 20px;
                border-radius: 8px;
                color: white;
                transition: all 0.3s ease;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .funnel-step:hover {{
                transform: scale(1.02);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .funnel-main {{
                flex: 1;
            }}
            .funnel-cost {{
                text-align: right;
                margin-left: 20px;
                padding-left: 20px;
                border-left: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .funnel-value {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .funnel-label {{
                font-size: 16px;
                opacity: 0.9;
            }}
            .funnel-cost-value {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .funnel-cost-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .step-1 {{ background: linear-gradient(135deg, #1a73e8, #0d47a1); width: 100%; }}
            .step-2 {{ background: linear-gradient(135deg, #2196f3, #1976d2); width: 90%; }}
            .step-3 {{ background: linear-gradient(135deg, #42a5f5, #2196f3); width: 80%; }}
            .step-4 {{ background: linear-gradient(135deg, #64b5f6, #42a5f5); width: 70%; }}
            .step-5 {{ background: linear-gradient(135deg, #90caf9, #64b5f6); width: 60%; }}
            .step-6 {{ background: linear-gradient(135deg, #bbdefb, #90caf9); width: 50%; }}
        </style>
        <div class="funnel-container">
            <div class="funnel-step step-1">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Visualização de Item']:,.0f}</div>
                    <div class="funnel-label">Visualização de Item</div>
                </div>
            </div>
            <div class="funnel-step step-2">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Adicionar ao Carrinho']:,.0f}</div>
                    <div class="funnel-label">Adicionar ao Carrinho</div>
                </div>
                <div class="funnel-cost">
                    <div class="funnel-cost-value">{total_taxas['Taxa View Product -> Cart']:.2f}%</div>
                    <div class="funnel-cost-label">Taxa de Conversão</div>
                </div>
            </div>
            <div class="funnel-step step-3">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Iniciar Checkout']:,.0f}</div>
                    <div class="funnel-label">Iniciar Checkout</div>
                </div>
                <div class="funnel-cost">
                    <div class="funnel-cost-value">{total_taxas['Taxa Cart -> Checkout']:.2f}%</div>
                    <div class="funnel-cost-label">Taxa de Conversão</div>
                </div>
            </div>
            <div class="funnel-step step-4">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Adicionar Informação de Frete']:,.0f}</div>
                    <div class="funnel-label">Adicionar Informação de Frete</div>
                </div>
                <div class="funnel-cost">
                    <div class="funnel-cost-value">{total_taxas['Taxa Checkout -> Frete']:.2f}%</div>
                    <div class="funnel-cost-label">Taxa de Conversão</div>
                </div>
            </div>
            <div class="funnel-step step-5">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Adicionar Informação de Pagamento']:,.0f}</div>
                    <div class="funnel-label">Adicionar Informação de Pagamento</div>
                </div>
                <div class="funnel-cost">
                    <div class="funnel-cost-value">{total_taxas['Taxa Frete -> Pagamento']:.2f}%</div>
                    <div class="funnel-cost-label">Taxa de Conversão</div>
                </div>
            </div>
            <div class="funnel-step step-6">
                <div class="funnel-main">
                    <div class="funnel-value">{total_data['Pedido']:,.0f}</div>
                    <div class="funnel-label">Pedido</div>
                </div>
                <div class="funnel-cost">
                    <div class="funnel-cost-value">{total_taxas['Taxa Pagamento -> Pedido']:.2f}%</div>
                    <div class="funnel-cost-label">Taxa de Conversão</div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(funnel_html, unsafe_allow_html=True)
        
        # First plot - Views vs Sales
        st.markdown("### Relação entre Visualizações e Vendas")
        
        # Create scatter plot for views vs orders
        fig_views = go.Figure()
        
        fig_views.add_trace(
            go.Scatter(
                x=df['Visualização de Item'],
                y=df['Pedido'],
                mode='markers',
                marker=dict(
                    size=8,
                    color='#3B82F6',
                    opacity=0.7
                ),
                text=df['Nome do Produto'],  # Add item names as hover text
                hovertemplate="<b>%{text}</b><br>" +
                            "Visualizações: %{x}<br>" +
                            "Vendas: %{y}<br>" +
                            "<extra></extra>"  # This removes the secondary box in the hover
            )
        )
        
        # Update layout for views plot
        fig_views.update_layout(
            xaxis_title='Número de Visualizações',
            yaxis_title='Número de Vendas',
            plot_bgcolor='white',
            height=500,  # Fixed height for better visualization
            showlegend=False
        )
        
        # Add grid lines for views plot
        fig_views.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f1f5f9',
            zeroline=False
        )
        fig_views.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f1f5f9',
            zeroline=False
        )
        
        # Display the views plot
        st.plotly_chart(fig_views, use_container_width=True)
        
        # Second plot - Checkout vs Sales
        st.markdown("### Relação entre Checkout e Vendas")
        
        # Create scatter plot for checkout vs orders
        fig_checkout = go.Figure()
        
        fig_checkout.add_trace(
            go.Scatter(
                x=df['Iniciar Checkout'],
                y=df['Pedido'],
                mode='markers',
                marker=dict(
                    size=8,
                    color='#10B981',  # Different color for distinction
                    opacity=0.7
                ),
                text=df['Nome do Produto'],  # Add item names as hover text
                hovertemplate="<b>%{text}</b><br>" +
                            "Checkouts: %{x}<br>" +
                            "Vendas: %{y}<br>" +
                            "<extra></extra>"
            )
        )
        
        # Update layout for checkout plot
        fig_checkout.update_layout(
            xaxis_title='Número de Checkouts',
            yaxis_title='Número de Vendas',
            plot_bgcolor='white',
            height=500,  # Fixed height for better visualization
            showlegend=False
        )
        
        # Add grid lines for checkout plot
        fig_checkout.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f1f5f9',
            zeroline=False
        )
        fig_checkout.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f1f5f9',
            zeroline=False
        )
        
        # Display the checkout plot
        st.plotly_chart(fig_checkout, use_container_width=True)
        
        # Calculate conversion rates for each product
        df_display = df.copy()
        df_display['Taxa Visualização -> Carrinho (%)'] = (df_display['Adicionar ao Carrinho'] / df_display['Visualização de Item'] * 100).round(2)
        df_display['Taxa Carrinho -> Checkout (%)'] = (df_display['Iniciar Checkout'] / df_display['Adicionar ao Carrinho'] * 100).round(2)
        df_display['Taxa Checkout -> Frete (%)'] = (df_display['Adicionar Informação de Frete'] / df_display['Iniciar Checkout'] * 100).round(2)
        df_display['Taxa Frete -> Pagamento (%)'] = (df_display['Adicionar Informação de Pagamento'] / df_display['Adicionar Informação de Frete'] * 100).round(2)
        df_display['Taxa Pagamento -> Pedido (%)'] = (df_display['Pedido'] / df_display['Adicionar Informação de Pagamento'] * 100).round(2)
        df_display['Taxa Visualização -> Pedido (%)'] = (df_display['Pedido'] / df_display['Visualização de Item'] * 100).round(2)
        
        # Reorder columns for better visualization
        columns_order = [
            'ID do Produto',
            'Nome do Produto',
            'Categoria do Produto',
            'Visualização de Item',
            'Taxa Visualização -> Carrinho (%)',
            'Adicionar ao Carrinho',
            'Taxa Carrinho -> Checkout (%)',
            'Iniciar Checkout',
            'Taxa Checkout -> Frete (%)',
            'Adicionar Informação de Frete',
            'Taxa Frete -> Pagamento (%)',
            'Adicionar Informação de Pagamento',
            'Taxa Pagamento -> Pedido (%)',
            'Pedido',
            'Taxa Visualização -> Pedido (%)'
        ]
        
        df_display = df_display[columns_order]
        
        # Display the data table below both plots
        st.markdown("### Dados Detalhados")
        st.dataframe(
            df_display,
            hide_index=True,
            use_container_width=True
        )
