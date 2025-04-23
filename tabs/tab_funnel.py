import streamlit as st
from modules.load_data import load_funnel_data, load_detailed_data, load_enhanced_ecommerce_funnel
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

def items_performance():
    st.subheader("Análise de Produtos")
    col1, col2 = st.columns(2)
    with col1:
        desvios = st.number_input('Desvios padrão para alertas:', min_value=0.1, max_value=3.0, value=0.5, step=0.1, help='Número de desvios padrão abaixo da média para gerar alerta')
    with col2:
        min_cart_adds = st.number_input('Mínimo de adições ao carrinho:', min_value=1, value=10, step=1, help='Número mínimo de adições ao carrinho para considerar na análise')

    df = load_enhanced_ecommerce_funnel()

    df = df[df['Adicionar ao Carrinho'] >= min_cart_adds]
        
    # Calcular média e desvio padrão da taxa de adição ao carrinho por produto
    df_stats = df.groupby('Nome do Produto')['Taxa de Visualização para Adição ao Carrinho'].agg(['mean', 'std']).reset_index()
    df_stats.columns = ['Nome do Produto', 'Média', 'Desvio Padrão']

    # Pegar apenas dados de hoje
    df_hoje = df[df['Data'] == df['Data'].max()]
    
    # Filtrar apenas produtos que tiveram adições ao carrinho hoje
    df_hoje = df_hoje[df_hoje['Adicionar ao Carrinho'] > 0]

    # Juntar com as estatísticas
    df_hoje = df_hoje.merge(df_stats, on='Nome do Produto', how='left')

    # Identificar produtos com taxa abaixo de 2 desvios padrão
    df_anomalias = df_hoje[
        (df_hoje['Taxa de Visualização para Adição ao Carrinho'] < (df_hoje['Média'] - desvios * df_hoje['Desvio Padrão'])) &
        (df_hoje['Desvio Padrão'].notna()) & 
        (df_hoje['Desvio Padrão'] > 0)
    ][['Nome do Produto', 'Taxa de Visualização para Adição ao Carrinho', 'Média', 'Desvio Padrão', 'Adicionar ao Carrinho']]

    if not df_anomalias.empty:
        st.warning('⚠️ Produtos com taxa de adição ao carrinho anormalmente baixa hoje:')
        st.dataframe(
            df_anomalias.sort_values('Adicionar ao Carrinho', ascending=False).style.format({
                'Taxa de Visualização para Adição ao Carrinho': '{:.2%}',
                'Média': '{:.2%}',
                'Desvio Padrão': '{:.2%}',
                'Adicionar ao Carrinho': '{:.0f}'
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success('✅ Nenhum produto com taxa de adição ao carrinho anormalmente baixa hoje')

def display_tab_funnel():
        
    st.title("Funil de Conversão")
    st.markdown("""---""")

    
    with st.expander("Entenda as Taxas de Conversão", expanded=False):
        st.markdown("""
            ### Como interpretar as taxas de conversão:
            
            1. **Taxa View Product -> Cart** (Visualização de Produto para Carrinho):
                - Porcentagem de usuários que adicionaram produtos ao carrinho após visualizar um item
                - Indica o interesse inicial no produto
            
            2. **Taxa Cart -> Checkout** (Carrinho para Checkout):
                - Porcentagem de usuários que iniciaram o checkout após adicionar ao carrinho
                - Mostra quantos carrinhos avançam para a compra
            
            3. **Taxa Checkout -> Dados de Frete** (Checkout para Dados de Frete):
                - Porcentagem de usuários que preencheram informações de frete após iniciar checkout
                - Indica progresso no processo de compra
            
            4. **Taxa Dados de Frete -> Dados de Pagamento** (Dados de Frete para Dados de Pagamento):
                - Porcentagem de usuários que avançaram para pagamento após informar frete
                - Mostra aceitação das opções de frete
            
            5. **Taxa Dados de Pagamento -> Pedido** (Dados de Pagamento para Pedido):
                - Porcentagem de usuários que completaram o pedido após informar pagamento
                - Indica sucesso na finalização da compra
            
            6. **Taxa View Product -> Pedido** (Visualização de Produto para Pedido):
                - Porcentagem total de conversão desde a visualização até o pedido
                - Mostra a eficiência geral do funil de vendas
            
            💡 **Dica**: Taxas muito baixas em uma etapa específica podem indicar:
            - Problemas técnicos no rastreamento
            - Gargalos no processo de compra
            - Oportunidades de otimização
        """)

    df = load_funnel_data()

    # Calcular taxas de conversão
    df['Taxa View Product -> Cart'] = (df['Adicionar ao Carrinho'] / df['Visualização de Item'] * 100).round(2)
    df['Taxa Cart -> Checkout'] = (df['Iniciar Checkout'] / df['Adicionar ao Carrinho'] * 100).round(2)
    df['Taxa Checkout -> Frete'] = (df['Adicionar Informação de Frete'] / df['Iniciar Checkout'] * 100).round(2)
    df['Taxa Dados de Frete -> Dados de Pagamento'] = (df['Adicionar Informação de Pagamento'] / df['Adicionar Informação de Frete'] * 100).round(2)
    df['Taxa Dados de Pagamento -> Pedido'] = (df['Pedido'] / df['Adicionar Informação de Pagamento'] * 100).round(2)
    df['Taxa View Product -> Pedido'] = (df['Pedido'] / df['Visualização de Item'] * 100).round(2)
    df['Taxa Checkout -> Pedido'] = (df['Pedido'] / df['Iniciar Checkout'] * 100).round(2)

    # Calcular desvios da média dos últimos 30 dias
    st.subheader("Desvios da Média (Últimos 30 dias)")
    
    # Criar colunas para os big numbers
    cols = st.columns(3)
    
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
            color = "#2E7D32"  # Verde escuro
            bg_color = "#E8F5E9"  # Verde claro bg
            icon = "↗↗"
        elif deviation_sigma >= 1.75:
            color = "#4CAF50"  # Verde claro
            bg_color = "#F1F8E9"  # Verde muito claro bg
            icon = "↗"
        elif deviation_sigma <= -2:
            color = "#C62828"  # Vermelho escuro
            bg_color = "#FFEBEE"  # Vermelho claro bg
            icon = "↘↘"
        elif deviation_sigma <= -1.75:
            color = "#EF5350"  # Vermelho claro
            bg_color = "#FFF3F3"  # Vermelho muito claro bg
            icon = "↘"
        else:
            color = "gray"
            bg_color = "#f0f2f6"  # Cinza claro padrão
            icon = "→"
        
        # Criar o big number com média dos últimos 30 dias
        with cols[idx % 3]:
            st.markdown(f"""
                <div style='padding: 1rem; background-color: {bg_color}; border-radius: 0.5rem; margin-bottom: 1rem;'>
                    <div style='font-size: 0.9rem; color: #666;'>{rate_names[rate]}</div>
                    <div style='font-size: 1.8rem; font-weight: bold;'>{today_value:.2f}%</div>
                    <div style='color: {color}; font-size: 0.9rem;'>
                        {icon} {deviation_percent:+.2f}% vs média 30d
                    </div>
                    <div style='color: #666; font-size: 0.8rem;'>
                        Média 30d: {last_30_days:.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""---""")
    st.subheader("Taxas de Conversão ao Longo do Tempo")
    
    # Criar gráficos individuais para cada taxa de conversão
    fig = make_subplots(
        rows=4, 
        cols=2,
        subplot_titles=conversion_rates,
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Cores para cada gráfico
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

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
                line=dict(color=colors[idx]),
                showlegend=False
            ),
            row=row,
            col=col
        )

        # Atualizar layout de cada subplot
        fig.update_xaxes(title_text="Data", row=row, col=col)
        fig.update_yaxes(title_text="Taxa (%)", row=row, col=col)

    # Atualizar layout geral
    fig.update_layout(
        height=1200,  # Increased height to accommodate 4 rows
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Exibir tabela com todos os dados
    st.subheader("Dados Detalhados")
    st.data_editor(df, hide_index=1, use_container_width=1)
    
    st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
    items_performance()