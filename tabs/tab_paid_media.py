import streamlit as st
from modules.load_data import load_paid_media, load_meta_ads
import altair as alt
from modules.components import big_number_box
from datetime import datetime
import pandas as pd
from partials.performance import analyze_meta_insights

def display_meta_ads_analysis():
    """Exibe análise detalhada do Meta Ads"""
    st.subheader("📊 Análise Meta Ads")

    st.info("""
        ℹ️ Os resultados apresentados nesta aba são baseados na atribuição do Pixel do Meta Ads.
        Isso significa que todas as métricas de conversão (vendas, receita, ROAS etc.) são contabilizadas 
        de acordo com o modelo de atribuição configurado no Facebook/Instagram Ads.
    """)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Carregar dados específicos do Meta Ads
    df_meta = load_meta_ads()
    
    if df_meta.empty:
        st.info("Não há dados do Meta Ads para o período selecionado.")
        return
    
    # Métricas principais em cards - Primeira linha
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        investimento = df_meta['spend'].sum()
        big_number_box(
            f"R$ {investimento:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Investimento",
            hint="Total investido em anúncios no Meta Ads"
        )
    
    with col2:
        receita = df_meta['purchase_value'].sum()
        big_number_box(
            f"R$ {receita:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Receita",
            hint="Receita total gerada pelos anúncios do Meta Ads"
        )
    
    with col3:
        roas = receita / investimento if investimento > 0 else 0
        big_number_box(
            f"{roas:.2f}".replace(".", ","),
            "ROAS",
            hint="Return On Ad Spend - Retorno sobre investimento"
        )
    
    with col4:
        lucro = receita - investimento
        big_number_box(
            f"R$ {lucro:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Lucro",
            hint="Receita menos investimento (Lucro bruto)"
        )

    # Segunda linha de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        impressions = df_meta['impressions'].sum()
        big_number_box(
            f"{impressions:,.0f}".replace(",", "."),
            "Impressões",
            hint="Número total de vezes que seus anúncios foram exibidos"
        )
    
    with col2:
        clicks = df_meta['clicks'].sum()
        big_number_box(
            f"{clicks:,.0f}".replace(",", "."),
            "Cliques",
            hint="Número total de cliques nos seus anúncios"
        )
    
    with col3:
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        big_number_box(
            f"{ctr:.2f}%".replace(".", ","),
            "CTR",
            hint="Click-Through Rate - Taxa de cliques por impressão"
        )
    
    with col4:
        cpc = investimento / clicks if clicks > 0 else 0
        big_number_box(
            f"R$ {cpc:.2f}".replace(".", ","),
            "CPC",
            hint="Custo Por Clique médio no Meta Ads"
        )

    # Terceira linha de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        purchases = df_meta['purchases'].sum()
        big_number_box(
            f"{purchases:,.0f}".replace(",", "."),
            "Vendas",
            hint="Número total de vendas atribuídas aos anúncios"
        )
    
    with col2:
        taxa_conv = (purchases / clicks * 100) if clicks > 0 else 0
        big_number_box(
            f"{taxa_conv:.2f}%".replace(".", ","),
            "Taxa de Conversão",
            hint="Porcentagem de cliques que resultaram em vendas"
        )
    
    with col3:
        cpv = investimento / purchases if purchases > 0 else 0
        big_number_box(
            f"R$ {cpv:.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "CPV",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda"
        )
    
    with col4:
        cpm = (investimento / impressions * 1000) if impressions > 0 else 0
        big_number_box(
            f"R$ {cpm:.2f}".replace(".", ","),
            "CPM",
            hint="Custo Por Mil Impressões no Meta Ads"
        )

    # Adicionar análise de insights após os big numbers
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    analyze_meta_insights(df_meta)

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Gráfico de tendência diária
    st.subheader("📈 Tendência Diária")
    
    df_daily = df_meta.groupby('date').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'purchase_value': 'sum',
        'purchases': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_daily['CTR'] = (df_daily['clicks'] / df_daily['impressions'] * 100).round(2)
    df_daily['CPC'] = (df_daily['spend'] / df_daily['clicks']).round(2)
    df_daily['ROAS'] = (df_daily['purchase_value'] / df_daily['spend']).round(2)
    df_daily['Taxa Conv.'] = (df_daily['purchases'] / df_daily['clicks'] * 100).round(2)
    df_daily['CPM'] = (df_daily['spend'] / df_daily['impressions'] * 1000).round(2)
    df_daily['CPV'] = (df_daily['spend'] / df_daily['purchases']).round(2)
    df_daily['Lucro'] = (df_daily['purchase_value'] - df_daily['spend']).round(2)
    
    # Renomear colunas para exibição
    df_daily = df_daily.rename(columns={
        'impressions': 'Impressões',
        'clicks': 'Cliques',
        'spend': 'Investimento',
        'purchase_value': 'Receita',
        'purchases': 'Vendas'
    })
    
    # Lista de todas as métricas disponíveis
    available_metrics = [
        'Impressões', 'Cliques', 'Vendas',  # Volume
        'CTR', 'Taxa Conv.',                # Taxas
        'Investimento', 'Receita', 'Lucro', # Financeiro
        'ROAS', 'CPC', 'CPM', 'CPV'        # Performance
    ]
    
    # Permitir escolher métricas para visualizar
    metrics = st.multiselect(
        "Escolha as métricas para visualizar:",
        available_metrics,
        default=['ROAS', 'Taxa Conv.']
    )
    
    if metrics:
        chart_data = pd.melt(
            df_daily, 
            id_vars=['date'], 
            value_vars=metrics,
            var_name='Métrica',
            value_name='Valor'
        )
        
        # Criar gráfico base
        base = alt.Chart(chart_data).encode(
            x=alt.X('date:T', title='Data'),
            color=alt.Color('Métrica:N', legend=alt.Legend(
                orient='top',
                title=None
            ))
        )
        
        # Linha principal
        line = base.mark_line(strokeWidth=2).encode(
            y=alt.Y('Valor:Q', title='Valor')
        )
        
        # Pontos
        points = base.mark_circle(size=60).encode(
            y=alt.Y('Valor:Q'),
            tooltip=[
                alt.Tooltip('date:T', title='Data', format='%d/%m/%Y'),
                alt.Tooltip('Métrica:N', title='Métrica'),
                alt.Tooltip('Valor:Q', title='Valor', format=',.2f')
            ]
        )
        
        # Combinar linha e pontos
        chart = (line + points).properties(
            height=400
        ).configure_axis(
            grid=False
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(chart, use_container_width=True)

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Campanha
    st.subheader("📑 Desempenho por Campanha")
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    campaign_options = ["Todas"] + sorted(df_meta['campaign_name'].unique().tolist())
    selected_campaign = st.selectbox("Filtrar Campanha:", campaign_options, key='campaign_filter')
    
    df_campaign = df_meta.copy()
    if selected_campaign != "Todas":
        df_campaign = df_campaign[df_campaign['campaign_name'] == selected_campaign]
    
    df_campaign = df_campaign.groupby('campaign_name').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'purchase_value': 'sum',
        'purchases': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_campaign['CTR'] = (df_campaign['clicks'] / df_campaign['impressions'] * 100).round(2)
    df_campaign['CPC'] = (df_campaign['spend'] / df_campaign['clicks']).round(2)
    df_campaign['ROAS'] = (df_campaign['purchase_value'] / df_campaign['spend']).round(2)
    df_campaign['Taxa Conv.'] = (df_campaign['purchases'] / df_campaign['clicks'] * 100).round(2)
    df_campaign['CPM'] = (df_campaign['spend'] / df_campaign['impressions'] * 1000).round(2)
    df_campaign['CPV'] = (df_campaign['spend'] / df_campaign['purchases']).round(2)
    df_campaign['Lucro'] = (df_campaign['purchase_value'] - df_campaign['spend']).round(2)
    
    df_campaign = df_campaign.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_campaign[[
            'campaign_name', 'impressions', 'clicks', 'purchases', 'CTR', 'CPC', 
            'spend', 'purchase_value', 'Lucro', 'ROAS', 'Taxa Conv.', 'CPM', 'CPV'
        ]].rename(columns={
            'campaign_name': 'Campanha',
            'impressions': 'Impressões',
            'clicks': 'Cliques',
            'purchases': 'Vendas',
            'spend': 'Investimento',
            'purchase_value': 'Receita'
        }).style.format({
            'Impressões': '{:,.0f}',
            'Cliques': '{:,.0f}',
            'Vendas': '{:,.0f}',
            'CTR': '{:.2f}%',
            'CPC': 'R$ {:.2f}',
            'CPM': 'R$ {:.2f}',
            'CPV': 'R$ {:.2f}',
            'Investimento': 'R$ {:.2f}',
            'Receita': 'R$ {:.2f}',
            'Lucro': 'R$ {:.2f}',
            'ROAS': '{:.2f}',
            'Taxa Conv.': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Grupo de Anúncios
    st.subheader("📑 Desempenho por Grupo de Anúncios")
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # Apenas um filtro para Grupos de Anúncios
    adset_options = ["Todos"] + sorted(df_meta['adset_name'].unique().tolist())
    selected_adset = st.selectbox("Filtrar Grupo de Anúncios:", adset_options, key='adset_filter')
    
    df_adset = df_meta.copy()
    if selected_adset != "Todos":
        df_adset = df_adset[df_adset['adset_name'] == selected_adset]
    
    df_adset = df_adset.groupby('adset_name').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'purchase_value': 'sum',
        'purchases': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_adset['CTR'] = (df_adset['clicks'] / df_adset['impressions'] * 100).round(2)
    df_adset['CPC'] = (df_adset['spend'] / df_adset['clicks']).round(2)
    df_adset['ROAS'] = (df_adset['purchase_value'] / df_adset['spend']).round(2)
    df_adset['Taxa Conv.'] = (df_adset['purchases'] / df_adset['clicks'] * 100).round(2)
    df_adset['CPM'] = (df_adset['spend'] / df_adset['impressions'] * 1000).round(2)
    df_adset['CPV'] = (df_adset['spend'] / df_adset['purchases']).round(2)
    df_adset['Lucro'] = (df_adset['purchase_value'] - df_adset['spend']).round(2)
    
    df_adset = df_adset.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_adset[[
            'adset_name', 'impressions', 'clicks', 'purchases', 'CTR', 'CPC',
            'spend', 'purchase_value', 'Lucro', 'ROAS', 'Taxa Conv.', 'CPM', 'CPV'
        ]].rename(columns={
            'adset_name': 'Grupo de Anúncios',
            'impressions': 'Impressões',
            'clicks': 'Cliques',
            'purchases': 'Vendas',
            'spend': 'Investimento',
            'purchase_value': 'Receita'
        }).style.format({
            'Impressões': '{:,.0f}',
            'Cliques': '{:,.0f}',
            'Vendas': '{:,.0f}',
            'CTR': '{:.2f}%',
            'CPC': 'R$ {:.2f}',
            'CPM': 'R$ {:.2f}',
            'CPV': 'R$ {:.2f}',
            'Investimento': 'R$ {:.2f}',
            'Receita': 'R$ {:.2f}',
            'Lucro': 'R$ {:.2f}',
            'ROAS': '{:.2f}',
            'Taxa Conv.': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Anúncio
    st.subheader("📑 Desempenho por Anúncio")
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # Apenas um filtro para Anúncios
    ad_options = ["Todos"] + sorted(df_meta['ad_name'].unique().tolist())
    selected_ad = st.selectbox("Filtrar Anúncio:", ad_options, key='ad_filter')
    
    df_ad = df_meta.copy()
    if selected_ad != "Todos":
        df_ad = df_ad[df_ad['ad_name'] == selected_ad]
    
    df_ad = df_ad.groupby('ad_name').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'purchase_value': 'sum',
        'purchases': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_ad['CTR'] = (df_ad['clicks'] / df_ad['impressions'] * 100).round(2)
    df_ad['CPC'] = (df_ad['spend'] / df_ad['clicks']).round(2)
    df_ad['ROAS'] = (df_ad['purchase_value'] / df_ad['spend']).round(2)
    df_ad['Taxa Conv.'] = (df_ad['purchases'] / df_ad['clicks'] * 100).round(2)
    df_ad['CPM'] = (df_ad['spend'] / df_ad['impressions'] * 1000).round(2)
    df_ad['CPV'] = (df_ad['spend'] / df_ad['purchases']).round(2)
    df_ad['Lucro'] = (df_ad['purchase_value'] - df_ad['spend']).round(2)
    
    df_ad = df_ad.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_ad[[
            'ad_name', 'impressions', 'clicks', 'purchases', 'CTR', 'CPC',
            'spend', 'purchase_value', 'Lucro', 'ROAS', 'Taxa Conv.', 'CPM', 'CPV'
        ]].rename(columns={
            'ad_name': 'Anúncio',
            'impressions': 'Impressões',
            'clicks': 'Cliques',
            'purchases': 'Vendas',
            'spend': 'Investimento',
            'purchase_value': 'Receita'
        }).style.format({
            'Impressões': '{:,.0f}',
            'Cliques': '{:,.0f}',
            'Vendas': '{:,.0f}',
            'CTR': '{:.2f}%',
            'CPC': 'R$ {:.2f}',
            'CPM': 'R$ {:.2f}',
            'CPV': 'R$ {:.2f}',
            'Investimento': 'R$ {:.2f}',
            'Receita': 'R$ {:.2f}',
            'Lucro': 'R$ {:.2f}',
            'ROAS': '{:.2f}',
            'Taxa Conv.': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )

def display_general_view(df_ads):
    """Exibe visão geral da mídia paga"""

    st.subheader("📊 Visão Geral da Mídia Paga")
    st.info("""
        ℹ️ Os resultados apresentados nesta aba são baseados na atribuição de último clique não direto, cruzando dados de Google e Meta Ads, Google Analytics e Plataforma de E-commerce.
    """)

    # Unique options for dropdown filters
    platform_options = ["All"] + sorted(df_ads['Plataforma'].dropna().unique().tolist())
    campaign_options = ["All"] + sorted(df_ads['Campanha'].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_platform = st.selectbox("Plataforma:", platform_options)

    with col2:
        campaign_filter = st.text_input("Campanha:", "")

    if selected_platform != "All":
        df_ads = df_ads[df_ads['Plataforma'] == selected_platform]

    if campaign_filter:
        df_ads = df_ads[df_ads['Campanha'].str.contains(campaign_filter, case=False, na=False)]

    df_grouped = df_ads.groupby('Data').agg({'Receita': 'sum', 'Investimento': 'sum'}).reset_index()

    # Cria o gráfico de Receita com a cor #D1B1C8 (roxo)
    line_receita = alt.Chart(df_grouped).mark_line(color='#D1B1C8', strokeWidth=3).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Receita:Q', axis=alt.Axis(title='Receita')),
        tooltip=['Data', 'Receita']
    )

    # Cria o gráfico de Investimento com a cor #C5EBC3 (verde)
    bar_investimento = alt.Chart(df_grouped).mark_bar(color='#C5EBC3', size=25).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Investimento:Q', axis=alt.Axis(title='Investimento')),
        tooltip=['Data', 'Investimento']
    )

    # Adiciona interatividade de zoom e pan
    zoom_pan = alt.selection_interval(bind='scales')

    # Combine os dois gráficos (linha e barras) com dois eixos Y e interatividade
    combined_chart = alt.layer(
        bar_investimento,
        line_receita
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    ).add_selection(
        zoom_pan  # Adiciona a interação de zoom e pan
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Investimento e Receita por Data',
            fontSize=18,
            anchor='middle'
        )
    ).configure_axis(
        grid=False,  # Adiciona grades discretas
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        strokeWidth=0  # Remove a borda ao redor do gráfico
    )

    # Exibe o gráfico no Streamlit
    st.altair_chart(combined_chart, use_container_width=True)

    # Adiciona legenda manual com HTML/CSS abaixo do gráfico
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 3px; background-color: #D1B1C8;"></div>
                <span>Receita</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 15px; background-color: #C5EBC3;"></div>
                <span>Investimento</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Métricas gerais
    total_impressoes = df_ads['Impressões'].sum()
    total_cliques = df_ads['Cliques'].sum()
    total_transacoes = df_ads['Transações'].sum()
    ctr = (total_cliques / total_impressoes * 100) if total_impressoes > 0 else 0
    taxa_conversao = (total_transacoes / total_cliques * 100) if total_cliques > 0 else 0
    cpc = df_ads['Investimento'].sum() / total_cliques if total_cliques > 0 else 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        big_number_box(
            f"R$ {df_ads['Investimento'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Investimento",
            hint="Total investido em mídia paga no período selecionado (Google Ads + Meta Ads)"
        )
    
    with col2:
        big_number_box(
            f"R$ {df_ads['Receita'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita",
            hint="Receita total gerada por mídia paga no período selecionado"
        )
    
    with col3:
        big_number_box(
            f"{df_ads['Receita'].sum()/df_ads['Investimento'].sum():,.2f}".replace(".", ","), 
            "ROAS",
            hint="Return On Ad Spend - Retorno sobre o investimento em anúncios (Receita/Investimento). Exemplo: ROAS 3 significa que para cada R$1 investido, retornou R$3 em vendas"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        big_number_box(
            f"{ctr:.2f}%".replace(".", ","),
            "CTR",
            hint="Click-Through Rate - Taxa de cliques por impressão (Cliques/Impressões). Quanto maior, melhor a relevância dos seus anúncios"
        )

    with col2:
        big_number_box(
            f"{taxa_conversao:.2f}%".replace(".", ","),
            "Taxa de Conversão",
            hint="Porcentagem de cliques que resultaram em vendas (Transações/Cliques)"
        )

    with col3:
        big_number_box(
            f"R$ {cpc:.2f}".replace(".", ","),
            "CPC",
            hint="Custo Por Clique - Valor médio pago por cada clique nos anúncios (Investimento/Cliques)"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        big_number_box(
            f"{total_impressoes:,.0f}".replace(",", "."),
            "Impressões",
            hint="Número total de vezes que seus anúncios foram exibidos"
        )

    with col2:
        big_number_box(
            f"{total_cliques:,.0f}".replace(",", "."),
            "Cliques",
            hint="Número total de cliques nos seus anúncios"
        )

    with col3:
        cpv = df_ads['Investimento'].sum() / df_ads['Transações'].sum() if df_ads['Transações'].sum() > 0 else 0
        big_number_box(
            f"R$ {cpv:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "CPV Médio",
            hint="Custo Por Venda Médio - Média do valor gasto em anúncios para conseguir uma venda"
        )

    st.markdown("---")

    # Display the aggregated data in Streamlit data editor
    df_ads_agg = df_ads.groupby(['Plataforma', 'Campanha']).agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Receita': 'sum'
    }).reset_index()

    df_ads_agg['ROAS'] = (df_ads_agg['Receita'] / df_ads_agg['Investimento'])
    df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações'].replace(0, float('nan'))).round(2)
    df_ads_agg = df_ads_agg.sort_values(by='Receita', ascending=False)
    
    st.data_editor(
        df_ads_agg,
        hide_index=True,
        use_container_width=True
    )

def display_tab_paid_media():
    st.title("💰 Mídia Paga")
    
    # Adicionar tabs para análises específicas
    tab1, tab2 = st.tabs(["Visão Geral", "Meta Ads"])
    
    with tab1:
        df_ads = load_paid_media()
        display_general_view(df_ads)
        
    with tab2:
        display_meta_ads_analysis()

    