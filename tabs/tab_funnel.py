import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import plotly.graph_objects as go
from helpers.components import section_title
from plotly.subplots import make_subplots
import altair as alt


def display_tab_funnel(client, table, query_general, start_date, end_date, **filters):
        
    st.title("🎯 Funil de Conversão")
    
    try:
        with st.spinner('Carregando dados ...'):
            # Query para buscar dados do HolySoup
            query = f"""
            SELECT 
                event_date `Data`,
                view_item `Visualização de Item`,
                add_to_cart `Adicionar ao Carrinho`,
                begin_checkout `Iniciar Checkout`,
                add_shipping_info `Adicionar Informação de Frete`,
                add_payment_info `Adicionar Informação de Pagamento`,
                purchase `Pedido`
            FROM `mymetric-hub-shopify.dbt.{table}_daily_metrics`
            WHERE event_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY event_date
            """
            
            df = client.query(query).to_dataframe()

            if df.empty:
                st.warning("Nenhum dado encontrado para o período selecionado")
                return

            # Mostrar período selecionado
            st.caption(f"Período: {start_date} até {end_date}")

            # Explicação das taxas de conversão
            with st.expander("ℹ️ Entenda as Taxas de Conversão", expanded=False):
                st.markdown("""
                    ### Como interpretar as taxas de conversão:
                    
                    1. **Taxa View -> Cart** (Visualização para Carrinho):
                       - Porcentagem de usuários que adicionaram produtos ao carrinho após visualizar um item
                       - Indica o interesse inicial no produto
                    
                    2. **Taxa Cart -> Checkout** (Carrinho para Checkout):
                       - Porcentagem de usuários que iniciaram o checkout após adicionar ao carrinho
                       - Mostra quantos carrinhos avançam para a compra
                    
                    3. **Taxa Checkout -> Frete** (Checkout para Frete):
                       - Porcentagem de usuários que preencheram informações de frete após iniciar checkout
                       - Indica progresso no processo de compra
                    
                    4. **Taxa Frete -> Pagamento** (Frete para Pagamento):
                       - Porcentagem de usuários que avançaram para pagamento após informar frete
                       - Mostra aceitação das opções de frete
                    
                    5. **Taxa Pagamento -> Pedido** (Pagamento para Pedido):
                       - Porcentagem de usuários que completaram o pedido após informar pagamento
                       - Indica sucesso na finalização da compra
                    
                    6. **Taxa Geral** (Visualização para Pedido):
                       - Porcentagem total de conversão desde a visualização até o pedido
                       - Mostra a eficiência geral do funil de vendas
                    
                    💡 **Dica**: Taxas muito baixas em uma etapa específica podem indicar:
                    - Problemas técnicos no rastreamento
                    - Gargalos no processo de compra
                    - Oportunidades de otimização
                """)

            # Calcular taxas de conversão
            df['Taxa View -> Cart'] = (df['Adicionar ao Carrinho'] / df['Visualização de Item'] * 100).round(2)
            df['Taxa Cart -> Checkout'] = (df['Iniciar Checkout'] / df['Adicionar ao Carrinho'] * 100).round(2)
            df['Taxa Checkout -> Frete'] = (df['Adicionar Informação de Frete'] / df['Iniciar Checkout'] * 100).round(2)
            df['Taxa Frete -> Pagamento'] = (df['Adicionar Informação de Pagamento'] / df['Adicionar Informação de Frete'] * 100).round(2)
            df['Taxa Pagamento -> Pedido'] = (df['Pedido'] / df['Adicionar Informação de Pagamento'] * 100).round(2)
            df['Taxa Geral'] = (df['Pedido'] / df['Visualização de Item'] * 100).round(2)

            # Criar gráficos individuais para cada taxa de conversão
            st.subheader("📈 Taxas de Conversão ao Longo do Tempo")
            
            conversion_rates = [
                'Taxa View -> Cart',
                'Taxa Cart -> Checkout',
                'Taxa Checkout -> Frete',
                'Taxa Frete -> Pagamento',
                'Taxa Pagamento -> Pedido',
                'Taxa Geral'
            ]

            # Criar subplots
            fig = make_subplots(
                rows=3, 
                cols=2,
                subplot_titles=conversion_rates,
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )

            # Cores para cada gráfico
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

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
                height=900,
                showlegend=False,
                title_text="Evolução das Taxas de Conversão por Etapa",
                title_x=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Exibir tabela com todos os dados
            st.subheader("📊 Dados Detalhados")
            st.data_editor(df, hide_index=1, use_container_width=1)
            
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {str(e)}")
        st.error("""
        Sugestões:
        1. Verifique a conexão com o BigQuery
        2. Confirme se as permissões estão corretas
        3. Tente recarregar a página
        """)
    


    df = query_general
    section_title("Mapa de Calor de Taxa de Conversão")
    st.write("Visualize a taxa de conversão por hora do dia e dia da semana")
    
    # Adiciona filtro de mínimo de sessões
    min_sessions = st.number_input(
        "Mínimo de sessões a considerar",
        min_value=1,
        max_value=1000,
        value=50,
        help="Apenas horários com número de sessões maior ou igual a este valor serão considerados"
    )
    
    # Adiciona coluna de dia da semana
    conv_rate = df.copy()
    conv_rate['Dia da Semana'] = pd.to_datetime(conv_rate['Data']).dt.day_name()
    
    # Agrupa por dia da semana e hora
    conv_rate = conv_rate.groupby(['Dia da Semana', 'Hora']).agg({
        'Sessões': 'sum',
        'Pedidos': 'sum'
    }).reset_index()
    
    # Filtra por mínimo de sessões
    conv_rate = conv_rate[conv_rate['Sessões'] >= min_sessions]
    
    # Calcula taxa de conversão
    conv_rate['Taxa de Conversão'] = (conv_rate['Pedidos'] / conv_rate['Sessões'] * 100).round(2)
    
    # Formata a hora para exibição (00:00 - 23:00)
    conv_rate['Hora_Formatada'] = conv_rate['Hora'].apply(lambda x: f"{x:02d}:00")
    
    # Reordena os dias da semana em português
    dias_ordem = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    conv_rate['Dia da Semana'] = conv_rate['Dia da Semana'].map(dias_ordem)
    
    if not conv_rate.empty:
        # Cria o heatmap usando Altair com um design mais limpo
        heatmap = alt.Chart(conv_rate).mark_rect(
            height=18  # Aumenta a altura de cada célula
        ).encode(
            x=alt.X('Dia da Semana:N', 
                    title=None,  # Remove título do eixo X
                    sort=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']),
            y=alt.Y('Hora_Formatada:O', 
                    title='Hora do Dia',  # Adiciona título do eixo Y
                    sort=list(f"{h:02d}:00" for h in range(24)),
                    bandPosition=0.5),  # Centraliza o texto
            color=alt.Color('Taxa de Conversão:Q',
                           scale=alt.Scale(scheme='greens'),  # Usa tons de verde
                           legend=alt.Legend(
                               orient='right',
                               title='Taxa de Conversão (%)',
                               gradientLength=300
                           )),
            tooltip=[
                alt.Tooltip('Dia da Semana:N', title='Dia'),
                alt.Tooltip('Hora_Formatada:O', title='Hora'),
                alt.Tooltip('Taxa de Conversão:Q', title='Taxa de Conversão', format='.2f'),
                alt.Tooltip('Sessões:Q', title='Sessões', format=','),
                alt.Tooltip('Pedidos:Q', title='Pedidos', format=',')
            ]
        ).properties(
            width=650,
            height=600,  # Aumenta a altura total do gráfico
            title=alt.TitleParams(
                text='Taxa de Conversão por Hora do Dia e Dia da Semana',
                fontSize=16,
                anchor='middle'
            )
        ).configure_view(
            strokeWidth=0,  # Remove borda
        ).configure_axis(
            labelFontSize=11,
            grid=False,  # Remove grid
            domain=False,  # Remove linhas dos eixos
            labelPadding=8  # Aumenta o espaço entre os rótulos e as células
        ).configure_legend(
            labelFontSize=11,
            titleFontSize=12,
            padding=10
        )

        # Adiciona espaço em branco para melhor alinhamento
        st.write("")
        
        # Exibe o heatmap
        st.altair_chart(heatmap, use_container_width=True)
        
        # Adiciona explicação
        st.markdown("""
            <div style="font-size: 0.9em; color: #666; margin-top: 10px;">
                * As linhas mostram as horas do dia (00:00 até 23:00).<br>
                * As colunas representam os dias da semana.<br>
                * As células são coloridas em tons de verde de acordo com a taxa de conversão.<br>
                * Células em branco indicam horários sem dados suficientes (abaixo do mínimo de sessões).<br>
                * Os valores mostram a taxa de conversão (Pedidos/Sessões) em porcentagem.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Não há dados suficientes para exibir o mapa de calor com o mínimo de sessões selecionado.") 