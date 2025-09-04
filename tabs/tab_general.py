import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

from modules.load_data import load_basic_data, apply_filters, load_paid_media, load_leads_popup, load_costs, load_revenue_by_traffic_category, save_costs, delete_cost, load_traffic_categories, load_havaianas_daily_scores
from modules.components import big_number_box
from partials.run_rate import display_run_rate
from partials.pendings import display_pendings
from partials.performance import display_performance
from partials.notices import display_notices
from streamlit_cookies_controller import CookieController


def big_numbers(df):

    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    adicoes_carrinho = df["Adições ao Carrinho"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    novos_clientes = df["Novos Clientes"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100 if df["Sessões"].sum() > 0 else 0
    tx_adicao = (adicoes_carrinho/sessoes)*100 if sessoes > 0 else 0
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (pedidos_pagos / pedidos) * 100 if total_receita_capturada > 0 else 0
    rps = total_receita_paga / sessoes if sessoes > 0 else 0
    tx_novos_clientes = (novos_clientes / pedidos_pagos * 100) if pedidos_pagos > 0 else 0

    st.header("Big Numbers")

    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        big_number_box(
            f"{pedidos:,.0f}".replace(",", "."), 
            "Pedidos Capturados",
            hint="Total de pedidos registrados no período, incluindo pagos e não pagos"
        )
    
    with col2:
        big_number_box(
            f"{pedidos_pagos:,.0f}".replace(",", "."), 
            "Pedidos Pagos",
            hint="Total de pedidos que foram efetivamente pagos no período"
        )

    with col3:
        big_number_box(
            f"R$ {total_receita_capturada:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita Capturada",
            hint="Valor total dos pedidos capturados, incluindo pagos e não pagos"
        )

    with col4:
        big_number_box(
            f"R$ {total_receita_paga:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita Paga",
            hint="Valor total dos pedidos que foram efetivamente pagos. Fórmula: Valor Total com Status Pago - Descontos + Frete"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        big_number_box(
            f"{sessoes:,.0f}".replace(",", "."), 
            "Sessões",
            hint="Número total de visitas ao site no período selecionado"
        )

    with col2:
        big_number_box(
            f"{tx_conv:.2f}".replace(".", ",") + "%", 
            "Tx Conversão",
            hint="Percentual de sessões que resultaram em pedidos (Pedidos/Sessões)"
        )

    with col3:
        big_number_box(
            f"{percentual_pago:.1f}%", 
            "% Receita Paga/Capturada",
            hint="Percentual da receita total capturada que foi efetivamente paga"
        )
    
    leads = load_leads_popup()
    if leads is not None and not leads.empty:
        with col4:
            big_number_box(
                f"{leads['E-mails'].sum():,.0f}".replace(",", "."), 
                "Leads",
                hint="Total de leads capturados via popup no período"
            )
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        big_number_box(
            f"{adicoes_carrinho:,.0f}".replace(",", "."), 
            "Adições ao Carrinho",
            hint="Total de produtos adicionados ao carrinho no período"
        )
        
    with col2:
        big_number_box(
            f"{tx_adicao:.2f}%", 
            "Tx Adição ao Carrinho",
            hint="Percentual de sessões que resultaram em adições ao carrinho"
        )

    with col3:
        big_number_box(
            f"R$ {rps:.2f}".replace(".", ","), 
            "RPS",
            hint="Receita por Sessão (Receita Paga/Sessões)"
        )

    with col4:
        big_number_box(
            f"{novos_clientes:,.0f}".replace(",", "."), 
            "Novos Clientes",
            hint="Total de pedidos pagos de clientes que fizeram sua primeira compra no período"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        big_number_box(
            f"{tx_novos_clientes:.1f}%", 
            "% Novos Clientes",
            hint="Percentual de pedidos pagos que vieram de novos clientes"
        )

    st.markdown("---")
    
    # Carrega dados de mídia paga
    df_paid = load_basic_data()

    if df_paid is not None and not df_paid.empty:
    
        total_investimento = df_paid["Investimento"].sum()
        receita = df_paid["Receita"].sum()
        investimento_google = df_paid[df_paid["Cluster"] == "🟢 Google Ads"]["Investimento"].sum()
        investimento_meta = df_paid[df_paid["Cluster"] == "🔵 Meta Ads"]["Investimento"].sum()
        tacos = (total_investimento/total_receita_paga * 100) if total_receita_paga > 0 else 0
        roas_geral = total_receita_paga/total_investimento if total_investimento > 0 else 0
        roas_especifico = receita/total_investimento if total_investimento > 0 else 0
    
        st.subheader("Mídia Paga")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            big_number_box(
                f"R$ {total_investimento:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
                "Total Investido",
                hint="Total investido em mídia paga no período (Google Ads + Meta Ads)"
            )
        
        with col2:
            big_number_box(
                f"R$ {investimento_google:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
                "Google Ads",
                hint="Total investido em Google Ads no período"
            )
        
        with col3:
            big_number_box(
                f"R$ {investimento_meta:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
                "Meta Ads",
                hint="Total investido em Meta Ads (Facebook/Instagram) no período"
            )
        
        with col4:
            big_number_box(
                f"{tacos:.2f}%", 
                "TACoS",
                hint="Percentual de investimento em relação à receita total"
            )
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            big_number_box(
                f"{roas_geral:.2f}", 
                "ROAS Geral",
                hint="Considera a receita geral do e-commerce"
            )

        with col2:
            big_number_box(
                f"{roas_especifico:.2f}", 
                "ROAS Específico",
                hint="Considera apenas o que foi atribuído em last click a Mídia Paga"
            )
        
        st.markdown("---")

    # Carregar custos
    costs_df = load_costs()
    
    if costs_df is not None and not costs_df.empty:
        st.markdown("---")

def tables(df):

    df['Data'] = pd.to_datetime(df['Data']).dt.date  # Converte para apenas a data (sem horas)
    df_grouped = df.groupby('Data').agg({'Sessões': 'sum', 'Receita Paga': 'sum'}).reset_index()

    # Formata os valores para o tooltip
    df_grouped['Sessões_fmt'] = df_grouped['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    df_grouped['Receita_fmt'] = df_grouped['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Cria o gráfico de Sessões com a cor #3B82F6 (azul)
    line_sessions = alt.Chart(df_grouped).mark_line(color='#3B82F6', strokeWidth=2.5).encode(
        x=alt.X('Data:T', 
                title='Data',
                axis=alt.Axis(format='%d/%m', labelAngle=0)),
        y=alt.Y('Sessões:Q', 
                axis=alt.Axis(title='Sessões',
                             format=',.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('Sessões_fmt:N', title='Sessões')
        ]
    )

    # Cria o gráfico de Receita Paga com barras estilosas
    bar_receita = alt.Chart(df_grouped).mark_bar(color='#E5E7EB', size=20).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Receita Paga:Q', 
                axis=alt.Axis(title='Receita Paga',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('Receita_fmt:N', title='Receita')
        ]
    )

    # Combine os dois gráficos com melhorias visuais
    combined_chart = alt.layer(
        bar_receita,
        line_sessions
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Evolução de Sessões e Receita',
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
    st.altair_chart(combined_chart, use_container_width=True)

    # Adiciona legenda manual com design melhorado
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                <span style="color: #4B5563; font-size: 14px;">Sessões</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                <span style="color: #4B5563; font-size: 14px;">Receita</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Tabela de Cluster de Origens
    st.header("Cluster de Origens")
    
    with st.expander("Entenda os Clusters", expanded=False):
        st.markdown("""
            ### Explicação dos Clusters
            
            Os clusters são agrupamentos de origens de tráfego que ajudam a entender melhor a fonte dos seus visitantes:
            
            🟢 **Google Ads**
            - Tráfego pago vindo do Google Ads
            - Identificado por: origem=google e mídia=cpc
            
            🔵 **Meta Ads**
            - Tráfego pago vindo do Facebook/Instagram Ads
            - Identificado por: presença do parâmetro fbclid na URL
            
            🟣 **Social**
            - Tráfego orgânico das redes sociais
            - Identificado por: mídia=social
            
            🌳 **Google Orgânico**
            - Tráfego orgânico do Google
            - Identificado por: origem=google e mídia=organic
            
            🟡 **Direto**
            - Acessos diretos ao site
            - Identificado por: origem=direct
            
            ✉️ **CRM**
            - Tráfego vindo de e-mails e comunicações diretas
            - Identificado por: origem=crm
            
            🗒️ **Draft**
            - Pedidos criados manualmente na Shopify
            - Identificado por: origem=shopify_draft_order
            
            🌳 **Orgânico**
            - Sessões sem identificação de origem
            - Identificado por: origem=not captured
            
            ◻️ **Outros**
            - Outras combinações de origem/mídia não classificadas acima
            - Formato: origem/mídia
        """)
        
    aggregated_df = df.groupby(['Cluster']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum',
        'Novos Clientes': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    aggregated_df['Tx Conversão'] = aggregated_df.apply(
        lambda x: (x['Pedidos'] / x['Sessões'] * 100) if x['Sessões'] > 0 else 0,
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    aggregated_df['RPS'] = aggregated_df.apply(
        lambda x: (x['Receita Paga'] / x['Sessões']) if x['Sessões'] > 0 else 0,
        axis=1
    )

    # Calcula percentual de novos clientes em relação aos pedidos pagos
    aggregated_df['% Novos Clientes'] = aggregated_df.apply(
        lambda x: (x['Novos Clientes'] / x['Pedidos Pagos'] * 100) if x['Pedidos Pagos'] > 0 else 0,
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = aggregated_df['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        aggregated_df['Tx Adições ao Carrinho'] = aggregated_df.apply(
            lambda x: (x['Adições ao Carrinho'] / total_adicoes) * 100,
            axis=1
        )
    else:
        aggregated_df['Tx Adições ao Carrinho'] = 0
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = aggregated_df['Receita'].sum()
    if total_receita > 0:
        aggregated_df['% Receita'] = aggregated_df.apply(
            lambda x: (x['Receita'] / total_receita) * 100,
            axis=1
        )
    else:
        aggregated_df['% Receita'] = 0
    
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    # Remover linhas onde Sessões e Pedidos são iguais a 0
    aggregated_df = aggregated_df[~((aggregated_df['Sessões'] == 0) & (aggregated_df['Pedidos'] == 0))]
    
    # Formatar os números antes de exibir
    display_df = aggregated_df.copy()
    
    # Reordenar as colunas
    display_df = display_df[[
        'Cluster', 
        'Sessões',
        'Adições ao Carrinho',
        'Tx Adições ao Carrinho',
        'Pedidos',
        'Tx Conversão',
        'Pedidos Pagos',
        'Novos Clientes',
        '% Novos Clientes',
        'Receita',
        'Receita Paga',
        'RPS',
        '% Receita'
    ]]
    
    # Aplicar formatação usando pandas styling
    styled_df = display_df.style.format({
        'Sessões': lambda x: f"{int(x):,}".replace(",", "."),
        'Adições ao Carrinho': lambda x: f"{int(x):,}".replace(",", "."),
        'Tx Adições ao Carrinho': lambda x: f"{float(x):.2f}%".replace(".", ","),
        'Pedidos': lambda x: f"{int(x):,}".replace(",", "."),
        'Tx Conversão': lambda x: f"{float(x):.2f}%".replace(".", ","),
        'Pedidos Pagos': lambda x: f"{int(x):,}".replace(",", "."),
        'Novos Clientes': lambda x: f"{int(x):,}".replace(",", "."),
        '% Novos Clientes': lambda x: f"{float(x):.1f}%".replace(".", ","),
        'Receita': lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
        'Receita Paga': lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
        'RPS': lambda x: f"R$ {float(x):.2f}".replace(".", ","),
        '% Receita': lambda x: f"{float(x):.2f}%".replace(".", ",")
    })
    
    # Exibir a tabela
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Gráfico de Scores Diários (apenas para Havaianas)
    if st.session_state.get('tablename') == 'havaianas':
        with st.spinner("🔄 Carregando scores diários..."):
            scores_df = load_havaianas_daily_scores()
            
            if scores_df is not None and not scores_df.empty:
                st.header("Timeline: Receita vs Size Score")
                
                # Converter Size Score para porcentagem (multiplicar por 100)
                scores_df['Size_Score_Pct'] = scores_df['Size_Score'] * 100
                
                # Calcular médias móveis de 7 dias
                scores_df['Revenue_MA7'] = scores_df['Revenue'].rolling(window=7, min_periods=1).mean()
                scores_df['Size_Score_MA7'] = scores_df['Size_Score_Pct'].rolling(window=7, min_periods=1).mean()
                
                # Formatar os valores para o tooltip
                scores_df['Revenue_fmt'] = scores_df['Revenue'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                scores_df['Revenue_MA7_fmt'] = scores_df['Revenue_MA7'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                scores_df['Size_Score_fmt'] = scores_df['Size_Score_Pct'].apply(lambda x: f"{x:.2f}%")
                scores_df['Size_Score_MA7_fmt'] = scores_df['Size_Score_MA7'].apply(lambda x: f"{x:.2f}%")

                # Criar gráfico de linha para Size Score (dados originais)
                line_size = alt.Chart(scores_df).mark_line(color='#3B82F6', strokeWidth=1.5, opacity=0.7).encode(
                    x=alt.X('Data:T', 
                            title='Data',
                            axis=alt.Axis(format='%d/%m', labelAngle=0)),
                    y=alt.Y('Size_Score_Pct:Q', 
                            axis=alt.Axis(title='Size Score (%)',
                                         format='.1f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Size_Score_fmt:N', title='Size Score'),
                        alt.Tooltip('Size_Score_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de linha para Size Score (média móvel)
                line_size_ma = alt.Chart(scores_df).mark_line(color='#1E40AF', strokeWidth=3).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Size_Score_MA7:Q', 
                            axis=alt.Axis(title='Size Score (%)',
                                         format='.1f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Size_Score_fmt:N', title='Size Score'),
                        alt.Tooltip('Size_Score_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de barras para Revenue (dados originais)
                bar_revenue = alt.Chart(scores_df).mark_bar(color='#F59E0B', size=20, opacity=0.7).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Revenue:Q', 
                            axis=alt.Axis(title='Receita (R$)',
                                         format='$,.0f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Revenue_fmt:N', title='Receita'),
                        alt.Tooltip('Revenue_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de linha para Revenue (média móvel)
                line_revenue_ma = alt.Chart(scores_df).mark_line(color='#D97706', strokeWidth=3).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Revenue_MA7:Q', 
                            axis=alt.Axis(title='Receita (R$)',
                                         format='$,.0f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Revenue_fmt:N', title='Receita'),
                        alt.Tooltip('Revenue_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Combine os gráficos com escalas independentes
                timeline_chart = alt.layer(
                    bar_revenue,
                    line_revenue_ma,
                    line_size,
                    line_size_ma
                ).resolve_scale(
                    y='independent'
                ).properties(
                    width=700,
                    height=400,
                    title=alt.TitleParams(
                        text='Timeline: Receita vs Size Score',
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

                st.altair_chart(timeline_chart, use_container_width=True)

                # Adiciona legenda centralizada
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("""
                        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 12px; background-color: #F59E0B;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Receita</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 2px; background-color: #3B82F6;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Size Score</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Segundo gráfico: Receita vs Promo Label
                st.header("Timeline: Receita vs Promo Label")
                
                # Verificar se Promo Label já vem como porcentagem ou decimal
                # Se os valores são menores que 1, multiplicar por 100
                if scores_df['Promo_Label'].max() < 1:
                    scores_df['Promo_Label_Pct'] = scores_df['Promo_Label'] * 100
                else:
                    scores_df['Promo_Label_Pct'] = scores_df['Promo_Label']
                
                # Calcular média móvel de 7 dias para Promo Label
                scores_df['Promo_Label_MA7'] = scores_df['Promo_Label_Pct'].rolling(window=7, min_periods=1).mean()
                
                # Formatar os valores para o tooltip
                scores_df['Promo_Label_fmt'] = scores_df['Promo_Label_Pct'].apply(lambda x: f"{x:.2f}%")
                scores_df['Promo_Label_MA7_fmt'] = scores_df['Promo_Label_MA7'].apply(lambda x: f"{x:.2f}%")

                # Criar gráfico de linha para Promo Label (dados originais)
                line_promo = alt.Chart(scores_df).mark_line(color='#10B981', strokeWidth=1.5, opacity=0.7).encode(
                    x=alt.X('Data:T', 
                            title='Data',
                            axis=alt.Axis(format='%d/%m', labelAngle=0)),
                    y=alt.Y('Promo_Label_Pct:Q', 
                            axis=alt.Axis(title='Promo Label (%)',
                                         format='.1f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Promo_Label_fmt:N', title='Promo Label'),
                        alt.Tooltip('Promo_Label_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de linha para Promo Label (média móvel)
                line_promo_ma = alt.Chart(scores_df).mark_line(color='#047857', strokeWidth=3).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Promo_Label_MA7:Q', 
                            axis=alt.Axis(title='Promo Label (%)',
                                         format='.1f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Promo_Label_fmt:N', title='Promo Label'),
                        alt.Tooltip('Promo_Label_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de barras para Revenue (reutilizar o mesmo)
                bar_revenue_promo = alt.Chart(scores_df).mark_bar(color='#F59E0B', size=20, opacity=0.7).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Revenue:Q', 
                            axis=alt.Axis(title='Receita (R$)',
                                         format='$,.0f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Revenue_fmt:N', title='Receita'),
                        alt.Tooltip('Revenue_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Criar gráfico de linha para Revenue (média móvel) - reutilizar do primeiro gráfico
                line_revenue_promo_ma = alt.Chart(scores_df).mark_line(color='#D97706', strokeWidth=3).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Revenue_MA7:Q', 
                            axis=alt.Axis(title='Receita (R$)',
                                         format='$,.0f',
                                         titlePadding=10),
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                        alt.Tooltip('Revenue_fmt:N', title='Receita'),
                        alt.Tooltip('Revenue_MA7_fmt:N', title='Média Móvel 7d')
                    ]
                )

                # Combine os gráficos com escalas independentes
                timeline_promo_chart = alt.layer(
                    bar_revenue_promo,
                    line_revenue_promo_ma,
                    line_promo,
                    line_promo_ma
                ).resolve_scale(
                    y='independent'
                ).properties(
                    width=700,
                    height=400,
                    title=alt.TitleParams(
                        text='Timeline: Receita vs Promo Label',
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

                st.altair_chart(timeline_promo_chart, use_container_width=True)

                # Adiciona legenda centralizada
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("""
                        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 12px; background-color: #F59E0B;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Receita</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 20px; height: 2px; background-color: #10B981;"></div>
                                <span style="color: #4B5563; font-size: 14px;">Promo Label</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

    st.markdown("---")

    # Tabela de Cálculo de ROI
    # Carregar custos e dados de receita
    if st.session_state.get('tablename') == 'endogen':
        costs_df = load_costs()
        revenue_df = load_revenue_by_traffic_category()
        
        if not costs_df.empty and not revenue_df.empty:
            st.header("Análise de Custos e Receita por Categoria")
            
            # Criar sub-abas
            tab_analysis, tab_config = st.tabs(["📊 Análise", "💰 Configuração"])
            
            with tab_analysis:
                # Fazer left join com os custos respeitando o mês dos dados filtrados
                # Usar o mês dos dados de receita (que é o mês atual do dashboard)
                start_date = st.session_state.get('start_date')
                end_date = st.session_state.get('end_date')
                
                if start_date and end_date:
                    # Usar o mês do início do período como referência para custos
                    analysis_month = start_date.strftime("%Y-%m") if hasattr(start_date, 'strftime') else str(start_date)[:7]
                else:
                    # Fallback: usar mês atual
                    analysis_month = date.today().strftime("%Y-%m")
                
                # Filtrar custos do mês de análise
                month_costs = costs_df[costs_df['Mês'] == analysis_month]
                
                # Se não há custos para o mês específico, criar DataFrame vazio
                if month_costs.empty:
                    # Criar DataFrame vazio com as colunas necessárias
                    month_costs = pd.DataFrame(columns=['Categoria', 'Custo do Produto (%)', 'Custo Total', 'Imposto (%)', 'Frete Empresa (%)', 'Comissão (%)'])
                    st.info(f"ℹ️ Não há custos cadastrados para {analysis_month}. Usando 50% como custo padrão do produto e 0% para demais percentuais.")
                
                # Garantir que todas as colunas necessárias existem
                required_columns = ['Categoria', 'Custo do Produto (%)', 'Custo Total', 'Imposto (%)', 'Frete Empresa (%)', 'Comissão (%)']
                for col in required_columns:
                    if col not in month_costs.columns:
                        month_costs[col] = 0.0
                
                # Preparar dados para merge - tratar None como "🌳 Orgânico"
                month_costs_for_merge = month_costs.copy()
                month_costs_for_merge['Categoria'] = month_costs_for_merge['Categoria'].fillna("Orgânico")
                
                # Preparar dados de receita - tratar None como "🌳 Orgânico"
                revenue_df_for_merge = revenue_df.copy()
                revenue_df_for_merge['categoria_de_trafego'] = revenue_df_for_merge['categoria_de_trafego'].fillna("Orgânico")
                
                # Agrupar todas as variações de "Orgânico" em uma única categoria
                if st.session_state.get('tablename') == 'endogen':
                    # Primeiro, agrupar por soma todas as linhas que contêm variações de "Orgânico"
                    organic_variations = revenue_df_for_merge[
                        revenue_df_for_merge['categoria_de_trafego'].str.contains('Orgânico|Outros', case=False, na=False) |
                        revenue_df_for_merge['categoria_de_trafego'].str.contains('🌳|◻️', case=False, na=False)
                    ]
                    
                    # Se há dados orgânicos para agrupar
                    if not organic_variations.empty:
                        # Somar todos os valores das variações orgânicas
                        organic_grouped = organic_variations.groupby(lambda x: 'Orgânico').agg({
                            'receita_venda': 'sum',
                            'frete': 'sum', 
                            'taxas_pagamento': 'sum',
                            'cupom': 'sum',
                            'receita_com_descontos': 'sum'
                        }).reset_index()
                        organic_grouped.columns = ['categoria_de_trafego', 'receita_venda', 'frete', 'taxas_pagamento', 'cupom', 'receita_com_descontos']
                        
                        # Remover as linhas originais das variações orgânicas
                        revenue_df_for_merge = revenue_df_for_merge[
                            ~(revenue_df_for_merge['categoria_de_trafego'].str.contains('Orgânico|Outros', case=False, na=False) |
                              revenue_df_for_merge['categoria_de_trafego'].str.contains('🌳|◻️', case=False, na=False))
                        ]
                        
                        # Adicionar a linha agrupada
                        revenue_df_for_merge = pd.concat([revenue_df_for_merge, organic_grouped], ignore_index=True)
                

                
                # Fazer o merge entre receita e custos
                merged_df = pd.merge(
                    revenue_df_for_merge,
                    month_costs_for_merge[['Categoria', 'Custo do Produto (%)', 'Custo Total', 'Imposto (%)', 'Frete Empresa (%)', 'Comissão (%)']],
                    left_on='categoria_de_trafego',
                    right_on='Categoria',
                    how='left'
                )
                

                
                # Remover a coluna Categoria duplicada
                if 'Categoria' in merged_df.columns:
                    merged_df = merged_df.drop('Categoria', axis=1)
                
                # Calcular Receita Líquida (receita_venda - cupom)
                merged_df['Receita Líquida'] = merged_df['receita_venda'] - merged_df['cupom']
                
                # Usar receita_venda como Receita (receita bruta)
                merged_df['Receita'] = merged_df['receita_venda']
                
                # Preencher valores nulos com 0
                merged_df['Custo do Produto (%)'] = merged_df['Custo do Produto (%)'].fillna(50.0)  # Impor 50% como padrão
                merged_df['Custo Total'] = merged_df['Custo Total'].fillna(0)
                merged_df['Imposto (%)'] = merged_df['Imposto (%)'].fillna(0.0)  # Imposto padrão 0%
                merged_df['Frete Empresa (%)'] = merged_df['Frete Empresa (%)'].fillna(0.0)  # Frete empresa padrão 0%
                merged_df['Comissão (%)'] = merged_df['Comissão (%)'].fillna(0.0)  # Comissão padrão 0%
                
                # Renomear Custo Total para Investimento para consistência
                merged_df = merged_df.rename(columns={'Custo Total': 'Investimento'})
                
                # Calcular Custo do Produto Absoluto (sobre Receita Líquida)
                merged_df['Custo do Produto Absoluto'] = merged_df['Receita Líquida'] * (merged_df['Custo do Produto (%)'] / 100)
                
                # Calcular Imposto Absoluto (sobre Receita Líquida)
                merged_df['Imposto Absoluto'] = merged_df['Receita Líquida'] * (merged_df['Imposto (%)'] / 100)
                
                # Calcular Frete Empresa Absoluto (sobre Receita Líquida)
                merged_df['Frete Empresa Absoluto'] = merged_df['Receita Líquida'] * (merged_df['Frete Empresa (%)'] / 100)
                
                # Calcular Comissão Absoluta (sobre Receita Líquida)
                merged_df['Comissão Absoluta'] = merged_df['Receita Líquida'] * (merged_df['Comissão (%)'] / 100)
                
                # Calcular Total de Frete (Frete Empresa + Frete)
                merged_df['Total de Frete'] = merged_df['Frete Empresa Absoluto'] + merged_df['frete']
                
                # Calcular Despesas Comerciais Variáveis (Custos Variáveis + Taxas + Investimento)
                merged_df['Despesas Comerciais Variáveis'] = merged_df['Custo do Produto Absoluto'] + merged_df['Imposto Absoluto'] + merged_df['Frete Empresa Absoluto'] + merged_df['Comissão Absoluta'] + merged_df['taxas_pagamento']
                
                # Calcular Margem de Contribuição (sem custos fixos)
                merged_df['Margem de Contribuição'] = merged_df['Receita Líquida'] - merged_df['Custo do Produto Absoluto']
                
                # Calcular Margem de Contribuição Líquida (Margem de Contribuição Bruta - Imposto - Comissão - Frete Empresa - Taxas)
                merged_df['Retorno Absoluto'] = merged_df['Margem de Contribuição'] - merged_df['Imposto Absoluto'] - merged_df['Comissão Absoluta'] - merged_df['Frete Empresa Absoluto'] - merged_df['taxas_pagamento']
                
                # Calcular Lucro Bruto (Margem de Contribuição Líquida - Investimento)
                merged_df['Lucro Bruto'] = merged_df['Retorno Absoluto'] - merged_df['Investimento']
                
                # Calcular ROI considerando todos os custos
                merged_df['ROI'] = merged_df['Retorno Absoluto'] / merged_df['Despesas Comerciais Variáveis'] * 100
                
                # Calcular ROI 3 ((Lucro Bruto / Investimento) - 1) * 100
                merged_df['ROI 3'] = ((merged_df['Lucro Bruto'] / merged_df['Investimento']) - 1) * 100
                
                # Calcular Margem de Contribuição Percentual
                merged_df['Margem de Contribuição %'] = merged_df['Margem de Contribuição'] / merged_df['Receita Líquida'] * 100
                
                # Calcular ROI 1: (Receita Líquida / Investimento) - 1
                merged_df['ROI 1'] = ((merged_df['Receita Líquida'] / merged_df['Investimento']) - 1) * 100
                
                # Calcular ROI 2: (Margem de Contribuição Líquida / Investimento) - 1
                merged_df['ROI 2'] = ((merged_df['Margem de Contribuição'] / merged_df['Investimento']) - 1) * 100
                
                # Preparar DataFrame para exibição (manter valores numéricos para classificação)
                display_df = merged_df.copy()
                
                # Tratar valores infinitos e NaN nas colunas de ROI e percentuais
                display_df['ROI'] = display_df['ROI'].replace([float('inf'), -float('inf')], 0).fillna(0)
                display_df['Margem de Contribuição %'] = display_df['Margem de Contribuição %'].replace([float('inf'), -float('inf')], 0).fillna(0)
                display_df['ROI 1'] = display_df['ROI 1'].replace([float('inf'), -float('inf')], 0).fillna(0)
                display_df['ROI 2'] = display_df['ROI 2'].replace([float('inf'), -float('inf')], 0).fillna(0)
                
                # Reordenar as colunas
                display_df = display_df[[
                    'categoria_de_trafego', 
                    'Receita',
                    'frete',
                    'taxas_pagamento', 
                    'cupom',
                    'Receita Líquida',
                    'Custo do Produto (%)', 
                    'Custo do Produto Absoluto', 
                    'Imposto (%)',
                    'Imposto Absoluto',
                    'Frete Empresa (%)',
                    'Frete Empresa Absoluto',
                    'Total de Frete',
                    'Comissão (%)',
                    'Comissão Absoluta',
                    'Investimento', 
                    'Despesas Comerciais Variáveis', 
                    'Margem de Contribuição',
                    'Retorno Absoluto', 
                    'Lucro Bruto',
                    'ROI',
                    'Margem de Contribuição %',
                    'ROI 1',
                    'ROI 2',
                    'ROI 3'
                ]]
                
                # Renomear colunas para melhor visualização
                display_df = display_df.rename(columns={
                    'categoria_de_trafego': 'Categoria de Tráfego',
                    'Receita': 'Receita Bruta Produtos',
                    'frete': 'Frete',
                    'taxas_pagamento': 'Taxas',
                    'cupom': 'Cupons',
                    'Receita Líquida': 'Receita Líquida',
                    'Custo do Produto (%)': 'Custo Produto (%)',
                    'Custo do Produto Absoluto': 'Custo Produto (R$)',
                    'Imposto (%)': 'Imposto (%)',
                    'Imposto Absoluto': 'Imposto (R$)',
                    'Frete Empresa (%)': 'Frete Empresa (%)',
                    'Frete Empresa Absoluto': 'Frete Empresa (R$)',
                    'Total de Frete': 'Total de Frete (R$)',
                    'Comissão (%)': 'Comissão (%)',
                    'Comissão Absoluta': 'Comissão (R$)',
                    'Investimento': 'Investimento',
                    'Despesas Comerciais Variáveis': 'Despesas Comerciais Variáveis',
                    'Margem de Contribuição': 'Margem de Contribuição Bruta (R$)',
                    'Retorno Absoluto': 'Margem de Contribuição Líquida (R$)',
                    'Lucro Bruto': 'Lucro Bruto (R$)',
                    'ROI': 'ROI (%)',
                    'Margem de Contribuição %': 'Margem de Contribuição Líquida (%)',
                    'ROI 1': 'ROI 1',
                    'ROI 2': 'ROI 2 (%)',
                    'ROI 3': 'ROI 3 (%)'
                })
                
                # Tratar None como "🌳 Canal Orgânico" na coluna Categoria de Tráfego
                display_df['Categoria de Tráfego'] = display_df['Categoria de Tráfego'].fillna("🌳 Canal Orgânico")
                
                # Adicionar expander com explicação
                with st.expander("📊 Entenda os Indicadores", expanded=False):
                    st.markdown("""
                    ### Explicação dos Indicadores
                    
                    #### 📈 **Indicadores de Receita**
                    
                    **Receita Bruta**: Valor total das vendas antes de qualquer desconto ou dedução. Representa o faturamento bruto da empresa.
                    
                    **Frete**: Valor do frete pago pelo cliente. Este valor é adicionado à receita bruta para formar parte da receita líquida.
                    
                    **Taxas**: Taxas cobradas pelos gateways de pagamento (PIX, cartão de crédito, boleto, etc.). São deduzidas da receita.
                    
                    **Cupons**: Valor total dos cupons de desconto aplicados pelos clientes. Representa descontos diretos na receita.
                    
                    **Receita Líquida**: Receita final calculada como: Receita Bruta - Taxas - Cupons. É o valor real que entra no caixa da empresa (sem considerar o frete).
                    
                    #### 💰 **Indicadores de Custo**
                    
                    **Custo Produto (%)**: Percentual do custo do produto em relação à receita líquida. Quando não configurado, usa 50% como padrão.
                    
                    **Custo Produto (R$)**: Valor absoluto do custo do produto calculado sobre a receita líquida.
                    
                    **Imposto (%)**: Percentual de impostos (ICMS, PIS, COFINS, etc.) configurado sobre a receita líquida.
                    
                    **Imposto (R$)**: Valor absoluto dos impostos calculado sobre a receita líquida.
                    
                    **Frete Empresa (%)**: Percentual de frete pago pela empresa (frete grátis) em relação à receita líquida.
                    
                    **Frete Empresa (R$)**: Valor absoluto do frete pago pela empresa calculado sobre a receita líquida.
                    
                    **Total de Frete (R$)**: Soma do frete pago pela empresa + frete pago pelo cliente. Representa o total de custos de frete.
                    
                    **Comissão (%)**: Percentual de comissão de vendas pago a vendedores ou afiliados sobre a receita líquida.
                    
                    **Comissão (R$)**: Valor absoluto da comissão de vendas calculado sobre a receita líquida.
                    
                    **Investimento**: Custos operacionais mensais configurados por categoria (mídia paga, operação, infraestrutura, etc.).
                    
                    **Despesas Comerciais Variáveis**: Soma total de todos os custos: Custo do Produto + Investimento + Imposto + Frete Empresa + Comissão.
                    
                    #### 📊 **Indicadores de Performance**
                    
                    **Margem de Contribuição (R$)**: Margem calculada como: Receita Líquida - Custos Variáveis (Custo do Produto + Imposto + Frete Empresa + Comissão). Representa a contribuição para cobrir custos fixos e gerar lucro.
                    
                    **Margem de Contribuição Líquida (R$)**: Lucro operacional calculado como: Receita Líquida - Despesas Comerciais Variáveis (incluindo investimentos). Representa o resultado financeiro final antes do investimento.
                    
                    **Lucro Bruto (R$)**: Lucro final calculado como: Margem de Contribuição Líquida - Investimento. Representa o resultado financeiro final após deduzir todos os custos e investimentos.
                    
                    **ROI (%)**: Retorno sobre o investimento calculado como: (Retorno / Despesas Comerciais Variáveis) × 100. Mostra a eficiência do investimento em custos.
                    
                    **Margem de Contribuição (%)**: Margem de contribuição calculada como: (Margem de Contribuição / Receita Líquida) × 100. Indica a porcentagem de contribuição sobre a receita líquida.
                    
                    **ROI 1**: ROI do investimento calculado como: (Receita Líquida / Investimento) - 1. Mostra quantas vezes a receita líquida cobre o investimento.
                    
                    **ROI 2 (%)**: ROI do investimento sobre margem de contribuição calculado como: (Investimento / Margem de Contribuição) × 100. Mostra o peso do investimento no lucro.
                    
                    **ROI 3 (%)**: ROI do investimento sobre lucro bruto calculado como: ((Lucro Bruto / Investimento) - 1) × 100. Mostra o retorno do investimento considerando o lucro final após todos os custos.
                    
                    ---
                    
                    **💡 Dica**: Configure os percentuais de custo na aba "Configuração" para obter análises mais precisas por categoria de tráfego.
                    """)
                
                # Configurar formatação das colunas para manter valores numéricos mas com visualização formatada
                column_config = {
                    'Categoria de Tráfego': st.column_config.TextColumn("Categoria de Tráfego"),
                    'Receita Bruta Produtos': st.column_config.NumberColumn(
                        "Receita Bruta Produtos",
                        format="R$ %.2f"
                    ),
                    'Frete': st.column_config.NumberColumn(
                        "Frete",
                        format="R$ %.2f"
                    ),
                    'Taxas': st.column_config.NumberColumn(
                        "Taxas",
                        format="R$ %.2f"
                    ),
                    'Cupons': st.column_config.NumberColumn(
                        "Cupons",
                        format="R$ %.2f"
                    ),
                    'Receita Líquida': st.column_config.NumberColumn(
                        "Receita Líquida",
                        format="R$ %.2f"
                    ),
                    'Custo Produto (%)': st.column_config.NumberColumn(
                        "Custo Produto (%)",
                        format="%.1f%%"
                    ),
                    'Custo Produto (R$)': st.column_config.NumberColumn(
                        "Custo Produto (R$)",
                        format="R$ %.2f"
                    ),
                    'Imposto (%)': st.column_config.NumberColumn(
                        "Imposto (%)",
                        format="%.1f%%"
                    ),
                    'Imposto (R$)': st.column_config.NumberColumn(
                        "Imposto (R$)",
                        format="R$ %.2f"
                    ),
                    'Frete Empresa (%)': st.column_config.NumberColumn(
                        "Frete Empresa (%)",
                        format="%.1f%%"
                    ),
                    'Frete Empresa (R$)': st.column_config.NumberColumn(
                        "Frete Empresa (R$)",
                        format="R$ %.2f"
                    ),
                    'Total de Frete (R$)': st.column_config.NumberColumn(
                        "Total de Frete (R$)",
                        format="R$ %.2f"
                    ),
                    'Comissão (%)': st.column_config.NumberColumn(
                        "Comissão (%)",
                        format="%.1f%%"
                    ),
                    'Comissão (R$)': st.column_config.NumberColumn(
                        "Comissão (R$)",
                        format="R$ %.2f"
                    ),
                    'Investimento': st.column_config.NumberColumn(
                        "Investimento",
                        format="R$ %.2f"
                    ),
                    'Despesas Comerciais Variáveis': st.column_config.NumberColumn(
                        "Despesas Comerciais Variáveis",
                        format="R$ %.2f"
                    ),
                    'Margem de Contribuição Bruta (R$)': st.column_config.NumberColumn(
                        "Margem de Contribuição Bruta (R$)",
                        format="R$ %.2f"
                    ),
                    'Margem de Contribuição Líquida (R$)': st.column_config.NumberColumn(
                        "Margem de Contribuição Líquida (R$)",
                        format="R$ %.2f"
                    ),
                    'Lucro Bruto (R$)': st.column_config.NumberColumn(
                        "Lucro Bruto (R$)",
                        format="R$ %.2f"
                    ),
                    'ROI (%)': st.column_config.NumberColumn(
                        "ROI (%)",
                        format="%.1f%%"
                    ),
                    'Margem de Contribuição Líquida (%)': st.column_config.NumberColumn(
                        "Margem de Contribuição Líquida (%)",
                        format="%.1f%%"
                    ),
                    'ROI 1': st.column_config.NumberColumn(
                        "ROI 1",
                        format="%.1f%%"
                    ),
                    'ROI 2 (%)': st.column_config.NumberColumn(
                        "ROI 2 (%)",
                        format="%.1f%%"
                    ),
                    'ROI 3 (%)': st.column_config.NumberColumn(
                        "ROI 3 (%)",
                        format="%.1f%%"
                    )
                }
                
                st.data_editor(
                    display_df, 
                    hide_index=True, 
                    use_container_width=True, 
                    key="general_costs_enhanced",
                    column_config=column_config
                )
                
                # Calcular e exibir totais
                st.markdown("### 📊 Totais")
                
                # Calcular totais dos valores numéricos (antes da formatação)
                totals = merged_df.agg({
                    'Receita': 'sum',
                    'frete': 'sum',
                    'taxas_pagamento': 'sum',
                    'cupom': 'sum',
                    'Receita Líquida': 'sum',
                    'Custo do Produto Absoluto': 'sum',
                    'Imposto Absoluto': 'sum',
                    'Frete Empresa Absoluto': 'sum',
                    'Total de Frete': 'sum',
                    'Comissão Absoluta': 'sum',
                    'Investimento': 'sum',
                    'Despesas Comerciais Variáveis': 'sum',
                    'Margem de Contribuição': 'sum',
                    'Retorno Absoluto': 'sum',
                    'Lucro Bruto': 'sum'
                }).round(2)
                
                # Linha 1: Receita e Deduções
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    receita_bruta_total = totals['Receita'] + totals['frete']
                    st.metric("💰 Receita Bruta", f"R$ {receita_bruta_total:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col2:
                    st.metric("🚚 Frete Pago pelo Cliente", f"R$ {totals['frete']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col3:
                    st.metric("🎫 Cupons", f"R$ {totals['cupom']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col4:
                    st.metric("💵 Receita Líquida", f"R$ {totals['Receita Líquida']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                
                # Linha 2: Impostos e Custos Variáveis
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📦 Custo Produto", f"R$ {totals['Custo do Produto Absoluto']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col2:
                    st.metric("🏛️ Imposto", f"R$ {totals['Imposto Absoluto']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col3:
                    st.metric("👥 Comissão", f"R$ {totals['Comissão Absoluta']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col4:
                    st.metric("🚛 Frete Empresa", f"R$ {totals['Frete Empresa Absoluto']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                
                # Linha 3: Taxas, Comissão, Fretes e Margem de Contribuição
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💳 Taxas", f"R$ {totals['taxas_pagamento']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col2:
                    st.metric("💰 Despesas Comerciais Variáveis", f"R$ {totals['Despesas Comerciais Variáveis']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col3:
                    st.metric("💎 Margem de Contribuição Bruta (R$)", f"R$ {totals['Margem de Contribuição']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col4:
                    margem_bruta_geral = (1 - (totals['Custo do Produto Absoluto'] / totals['Receita Líquida'])) * 100 if totals['Receita Líquida'] > 0 else 0
                    st.metric("📊 Margem de Contribuição Bruta (%)", f"{margem_bruta_geral:.1f}%")
                
                # Linha 4: Frete Empresa, Total de Frete, Investimento e Despesas Comerciais
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💎 Margem de Contribuição Líquida (R$)", f"R$ {totals['Retorno Absoluto']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col2:
                    margem_liquida_geral = (totals['Retorno Absoluto'] / totals['Receita Líquida'] * 100) if totals['Receita Líquida'] > 0 else 0
                    st.metric("📊 Margem de Contribuição Líquida (%)", f"{margem_liquida_geral:.1f}%")
                with col3:
                    st.metric("🔧 Investimento", f"R$ {totals['Investimento']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                with col4:
                    st.metric("💰 Lucro Bruto (R$)", f"R$ {totals['Lucro Bruto']:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                
                # Linha 5: ROI 1, ROI 2 e ROI 3
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    roi1_geral = ((totals['Receita Líquida'] / totals['Investimento']) - 1) * 100 if totals['Investimento'] > 0 else 0
                    st.metric("📈 ROI 1 (%) - Sobre RL", f"{roi1_geral:.1f}%")
                with col2:
                    roi2_geral = ((totals['Retorno Absoluto'] / totals['Investimento']) - 1) * 100
                    st.metric("📈 ROI 2 (%) - Sobre MCL", f"{roi2_geral:.1f}%")
                with col3:
                    roi3_geral = ((totals['Lucro Bruto'] / totals['Investimento']) - 1) * 100 if totals['Investimento'] > 0 else 0
                    st.metric("📈 ROI 3 (%) - Sobre LB", f"{roi3_geral:.1f}%")
                with col4:
                    st.metric("", "")  # Espaço vazio para manter layout
                
                # Linha 6: Margem de Contribuição Líquida
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write("")
                with col2:
                    st.write("")
                    
                with col3:
                    st.metric("", "")  # Espaço vazio para manter layout
                with col4:
                    st.metric("", "")  # Espaço vazio para manter layout
            
            with tab_config:
                # Formulário para adicionar/editar custos
                with st.form("custo_form_geral"):
                    # Lista dos últimos 12 meses para seleção
                    months = []
                    for i in range(12):
                        month = (datetime.now() - pd.DateOffset(months=i)).strftime("%Y-%m")
                        months.append(month)
                    
                    # Usar o mês do filtro da aba lateral como padrão
                    start_date = st.session_state.get('start_date')
                    default_month = start_date.strftime("%Y-%m") if start_date and hasattr(start_date, 'strftime') else months[0]
                    
                    # Verificar se está editando um custo
                    editing_cost = st.session_state.get('editing_cost', None)
                    
                    selected_month = st.selectbox(
                        "Mês de Referência",
                        options=months,
                        index=months.index(editing_cost['month']) if editing_cost and editing_cost['month'] in months else months.index(default_month) if default_month in months else 0,
                        format_func=lambda x: pd.to_datetime(x).strftime("%B/%Y").capitalize(),
                        key="custo_month"
                    )
                    
                    # Obter todos os clusters disponíveis na tabela de análise
                    available_clusters = revenue_df['categoria_de_trafego'].unique().tolist()
                    
                    # Tratar None como "🌳 Orgânico"
                    available_clusters = ["Orgânico" if cluster is None else cluster for cluster in available_clusters]
                    
                    # Selecionar categoria/cluster
                    selected_category = st.selectbox(
                        "Categoria de Tráfego",
                        options=available_clusters,
                        index=available_clusters.index(editing_cost['category']) if editing_cost and editing_cost['category'] in available_clusters else 0,
                        key="custo_category"
                    )
                    
                    # Campos para custos
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        cost_of_product_percentage = st.number_input(
                            "Custo do Produto (%)",
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f",
                            value=editing_cost['cost_of_product_percentage'] if editing_cost else 0.0,
                            help="Porcentagem do custo do produto em relação à receita",
                            key="custo_percentage"
                        )
                    
                    with col2:
                        total_cost = st.number_input(
                            "Investimento (R$)",
                            min_value=0.0,
                            step=100.0,
                            format="%.2f",
                            value=editing_cost['total_cost'] if editing_cost else 0.0,
                            help="Custo total da categoria no mês",
                            key="custo_total"
                        )
                    
                    with col3:
                        tax_percentage = st.number_input(
                            "Imposto (%)",
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f",
                            value=editing_cost['tax_percentage'] if editing_cost else 0.0,
                            help="Percentual de imposto sobre a receita",
                            key="custo_tax"
                        )
                    
                    with col4:
                        shipping_percentage = st.number_input(
                            "Frete Empresa (%)",
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f",
                            value=editing_cost['shipping_percentage'] if editing_cost else 0.0,
                            help="Percentual de frete pago pela empresa",
                            key="custo_shipping"
                        )
                    
                    with col5:
                        commission_percentage = st.number_input(
                            "Comissão (%)",
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.1f",
                            value=editing_cost['commission_percentage'] if editing_cost else 0.0,
                            help="Percentual de comissão de vendas",
                            key="custo_commission"
                        )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Atualizar Custos" if editing_cost else "Salvar Custos")
                    with col2:
                        if editing_cost and st.form_submit_button("❌ Cancelar"):
                            if 'editing_cost' in st.session_state:
                                del st.session_state.editing_cost
                            st.rerun()
                    
                    if submitted:
                        # Tratar "🌳 Orgânico" como None para salvar no banco
                        category_to_save = None if selected_category == "Orgânico" else selected_category
                        
                        if save_costs(selected_month, category_to_save, cost_of_product_percentage, total_cost, tax_percentage, shipping_percentage, commission_percentage):
                            # Limpar estado de edição
                            if 'editing_cost' in st.session_state:
                                del st.session_state.editing_cost
                            st.success("Custos salvos com sucesso!" if not editing_cost else "Custos atualizados com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao salvar custos.")
                
                # Exibir custos existentes
                if not costs_df.empty:
                    st.markdown("### Custos Cadastrados")
                    
                    # Filtrar custos pelo mês selecionado
                    display_costs_df = costs_df[costs_df['Mês'] == selected_month].copy()
                    
                    # Campo de busca
                    search_term = st.text_input("Buscar custos", key="costs_search_geral")
                    
                    # Tratar None como "🌳 Orgânico" na exibição
                    display_costs_df['Categoria'] = display_costs_df['Categoria'].fillna("Orgânico")
                    
                    if search_term:
                        display_costs_df = display_costs_df[
                            display_costs_df['Categoria'].str.contains(search_term, case=False, na=False) |
                            display_costs_df['Mês'].str.contains(search_term, case=False, na=False)
                        ]
                    
                    # Formatar valores para exibição
                    display_costs_df['Custo do Produto (%)'] = display_costs_df['Custo do Produto (%)'].apply(lambda x: f"{x:.1f}%")
                    display_costs_df['Custo Total'] = display_costs_df['Custo Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
                    display_costs_df['Imposto (%)'] = display_costs_df['Imposto (%)'].apply(lambda x: f"{x:.1f}%")
                    display_costs_df['Frete Empresa (%)'] = display_costs_df['Frete Empresa (%)'].apply(lambda x: f"{x:.1f}%")
                    display_costs_df['Comissão (%)'] = display_costs_df['Comissão (%)'].apply(lambda x: f"{x:.1f}%")
                    
                    # Renomear coluna para exibição
                    display_costs_df = display_costs_df.rename(columns={'Custo Total': 'Investimento'})
                    
                    # Exibir custos em uma tabela com botões de edição
                    for index, row in display_costs_df.iterrows():
                        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([3, 1, 1, 1, 1, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{row['Categoria']}**")
                        
                        with col2:
                            st.write(row['Custo do Produto (%)'])
                        
                        with col3:
                            st.write(row['Investimento'])
                        
                        with col4:
                            st.write(row['Imposto (%)'])
                        
                        with col5:
                            st.write(row['Frete Empresa (%)'])
                        
                        with col6:
                            st.write(row['Comissão (%)'])
                        
                        with col7:
                            if st.button("✏️ Editar", key=f"edit_{index}"):
                                st.session_state.editing_cost = {
                                    'month': row['Mês'],
                                    'category': row['Categoria'],
                                    'cost_of_product_percentage': float(row['Custo do Produto (%)'].replace('%', '')),
                                    'total_cost': float(row['Investimento'].replace('R$ ', '').replace('.', '').replace(',', '.')),
                                    'tax_percentage': float(row['Imposto (%)'].replace('%', '')),
                                    'shipping_percentage': float(row['Frete Empresa (%)'].replace('%', '')),
                                    'commission_percentage': float(row['Comissão (%)'].replace('%', ''))
                                }
                                st.rerun()
                        
                        with col8:
                            if st.button("🗑️ Excluir", key=f"delete_{index}"):
                                # Tratar "🌳 Orgânico" como None para exclusão
                                category_to_delete = None if row['Categoria'] == "🌳 Orgânico" else row['Categoria']
                                
                                if delete_cost(row['Mês'], category_to_delete):
                                    st.success("Custo excluído com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao excluir custo.")
                        
                        st.markdown("---")
                else:
                    st.info("Nenhum custo cadastrado ainda.")

def display_tab_general():
    # Add attribution model selector in sidebar
    if 'tablename' in st.session_state:
        attribution_options = ['Último Clique Não Direto', 'Primeiro Clique']
        if st.session_state.tablename == 'coffeemais':
            attribution_options.append('Assinaturas')
        
        with st.sidebar:
            attribution_model = st.selectbox(
                'Modelo de Atribuição',
                options=attribution_options,
                key='attribution_model',
                help='Escolha o modelo de atribuição para análise dos dados'
            )
            
            # Store the last selected model to detect changes
            if 'last_attribution_model' not in st.session_state:
                st.session_state.last_attribution_model = attribution_model
            elif st.session_state.last_attribution_model != attribution_model:
                # Clear the cache key for basic data
                cache_key = f"basic_data_{st.session_state.tablename}_{st.session_state.start_date}_{st.session_state.end_date}_{attribution_model}"
                if 'cache_data' in st.session_state and cache_key in st.session_state.cache_data:
                    del st.session_state.cache_data[cache_key]
                if 'cache_timestamps' in st.session_state and cache_key in st.session_state.cache_timestamps:
                    del st.session_state.cache_timestamps[cache_key]
                if 'background_tasks' in st.session_state and cache_key in st.session_state.background_tasks:
                    del st.session_state.background_tasks[cache_key]
                st.session_state.last_attribution_model = attribution_model
                st.rerun()

    with st.spinner("🔄 Carregando pendências..."):
        display_pendings()
    
    with st.spinner("🔄 Carregando dados básicos..."):
        df = load_basic_data()
        df = apply_filters(df)
    
    with st.spinner("🔄 Calculando run rate..."):
        display_run_rate(df)

    with st.spinner("🔄 Calculando métricas principais..."):
        big_numbers(df)
    
    with st.spinner("🔄 Gerando gráficos e tabelas..."):
        tables(df)

    # display_performance()

    with st.spinner("🔄 Configurando cookies..."):
        def set_cookies():
            controller = CookieController()
            if "authenticated" in st.session_state:
                max_age=8*60*60
                controller.set("mm_authenticated", st.session_state.authenticated, max_age = max_age)
                controller.set("mm_username", st.session_state.username, max_age = max_age)
                controller.set("mm_tablename", st.session_state.tablename, max_age = max_age)
                controller.set("mm_admin", st.session_state.admin, max_age = max_age)

        set_cookies()