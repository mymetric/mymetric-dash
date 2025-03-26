import streamlit as st
from modules.load_data import load_paid_media, load_meta_ads
import altair as alt
from modules.components import big_number_box
from datetime import datetime
import pandas as pd
from partials.performance import analyze_meta_insights

def display_meta_ads_analysis():
    """Exibe análise detalhada do Meta Ads"""
    st.subheader("Análise Meta Ads")
    
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
            "Investimento (Pixel)",
            hint="Total investido em anúncios no Meta Ads"
        )
    
    with col2:
        impressions = df_meta['impressions'].sum()
        big_number_box(
            f"{impressions:,.0f}".replace(",", "."),
            "Impressões (Pixel)",
            hint="Número total de vezes que seus anúncios foram exibidos"
        )
    
    with col3:
        clicks = df_meta['clicks'].sum()
        big_number_box(
            f"{clicks:,.0f}".replace(",", "."),
            "Cliques (Pixel)",
            hint="Número total de cliques nos seus anúncios"
        )
    
    with col4:
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        big_number_box(
            f"{ctr:.2f}%".replace(".", ","),
            "CTR (Pixel)",
            hint="Click-Through Rate - Taxa de cliques por impressão"
        )

    # Segunda linha - Métricas totais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        purchases = df_meta['purchases'].sum()
        big_number_box(
            f"{purchases:,.0f}".replace(",", "."),
            "Vendas (Pixel)",
            hint="Número total de vendas atribuídas aos anúncios"
        )
    
    with col2:
        receita = df_meta['purchase_value'].sum()
        big_number_box(
            f"R$ {receita:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Receita (Pixel)",
            hint="Receita total gerada pelos anúncios do Meta Ads"
        )
    
    with col3:
        roas = receita / investimento if investimento > 0 else 0
        big_number_box(
            f"{roas:.2f}".replace(".", ","),
            "ROAS (Pixel)",
            hint="Return On Ad Spend - Retorno sobre investimento"
        )
    
    with col4:
        lucro = receita - investimento
        big_number_box(
            f"R$ {lucro:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Lucro (Pixel)",
            hint="Receita menos investimento (Lucro bruto)"
        )

    # Terceira linha - Métricas última sessão
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        last_session_transactions = df_meta['last_session_transactions'].sum()
        big_number_box(
            f"{last_session_transactions:,.0f}".replace(",", "."),
            "Vendas (Última Sessão)",
            hint="Número total de vendas atribuídas aos anúncios na última sessão"
        )
    
    with col2:
        last_session_revenue = df_meta['last_session_revenue'].sum()
        big_number_box(
            f"R$ {last_session_revenue:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Receita (Última Sessão)",
            hint="Receita total gerada pelos anúncios na última sessão"
        )
    
    with col3:
        last_session_roas = last_session_revenue / investimento if investimento > 0 else 0
        big_number_box(
            f"{last_session_roas:.2f}".replace(".", ","),
            "ROAS (Última Sessão)",
            hint="Return On Ad Spend na última sessão"
        )
    
    with col4:
        last_session_lucro = last_session_revenue - investimento
        big_number_box(
            f"R$ {last_session_lucro:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Lucro (Última Sessão)",
            hint="Receita menos investimento na última sessão (Lucro bruto)"
        )

    # Quarta linha - Métricas de custo e correspondência
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpc = investimento / clicks if clicks > 0 else 0
        big_number_box(
            f"R$ {cpc:.2f}".replace(".", ","),
            "CPC (Pixel)",
            hint="Custo Por Clique médio no Meta Ads"
        )
    
    with col2:
        cpv = investimento / purchases if purchases > 0 else 0
        big_number_box(
            f"R$ {cpv:.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "CPV (Pixel)",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda"
        )
    
    with col3:
        cpm = (investimento / impressions * 1000) if impressions > 0 else 0
        big_number_box(
            f"R$ {cpm:.2f}".replace(".", ","),
            "CPM (Pixel)",
            hint="Custo Por Mil Impressões no Meta Ads"
        )
    
    with col4:
        taxa_conv = (purchases / clicks * 100) if clicks > 0 else 0
        match_rate = (last_session_transactions / purchases * 100) if purchases > 0 else 0
        big_number_box(
            f"{match_rate:.2f}%".replace(".", ","),
            "Taxa de Correspondência",
            hint="Porcentagem de vendas da Última Sessão em relação às vendas do Pixel"
        )

    # Adicionar análise de insights após os big numbers
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    analyze_meta_insights(df_meta)

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Gráfico de tendência diária
    st.subheader("Tendência Diária")
    
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
            x=alt.X('date:T', 
                   title='Data',
                   axis=alt.Axis(format='%d/%m', labelAngle=0)),
            color=alt.Color('Métrica:N', 
                          legend=alt.Legend(
                              orient='top',
                              title=None,
                              labelFont='DM Sans',
                              labelFontSize=12
                          ))
        )
        
        # Linha principal
        line = base.mark_line(strokeWidth=2).encode(
            y=alt.Y('Valor:Q', 
                   title='Valor',
                   axis=alt.Axis(format=',.2f',
                                titlePadding=10))
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
            height=400,
            title=alt.TitleParams(
                text='Evolução de Métricas',
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
        
        st.altair_chart(chart, use_container_width=True)

    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Campanha
    st.subheader("Desempenho por Campanha")
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
        'purchases': 'sum',
        'last_session_transactions': 'sum',
        'last_session_revenue': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_campaign['CTR'] = (df_campaign['clicks'] / df_campaign['impressions'] * 100).round(2)
    df_campaign['CPC'] = (df_campaign['spend'] / df_campaign['clicks']).round(2)
    df_campaign['ROAS'] = (df_campaign['purchase_value'] / df_campaign['spend']).round(2)
    df_campaign['Taxa Conv.'] = (df_campaign['purchases'] / df_campaign['clicks'] * 100).round(2)
    df_campaign['CPM'] = (df_campaign['spend'] / df_campaign['impressions'] * 1000).round(2)
    df_campaign['CPV'] = (df_campaign['spend'] / df_campaign['purchases']).round(2)
    df_campaign['Lucro'] = (df_campaign['purchase_value'] - df_campaign['spend']).round(2)
    df_campaign['ROAS Última Sessão'] = (df_campaign['last_session_revenue'] / df_campaign['spend']).round(2)
    df_campaign['Taxa Conv. Última Sessão'] = (df_campaign['last_session_transactions'] / df_campaign['clicks'] * 100).round(2)
    df_campaign['Lucro Última Sessão'] = (df_campaign['last_session_revenue'] - df_campaign['spend']).round(2)
    df_campaign['Taxa de Correspondência'] = (df_campaign['last_session_transactions'] / df_campaign['purchases'] * 100).round(2)
    
    df_campaign = df_campaign.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_campaign[[
            'campaign_name',  # Nome da campanha
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions',  # Vendas
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência'  # Taxa de correspondência
        ]].rename(columns={
            'campaign_name': 'Campanha',
            'impressions': 'Impressões (Pixel)',
            'clicks': 'Cliques (Pixel)',
            'purchases': 'Vendas (Pixel)',
            'last_session_transactions': 'Vendas (Última Sessão)',
            'spend': 'Investimento (Pixel)',
            'purchase_value': 'Receita (Pixel)',
            'last_session_revenue': 'Receita (Última Sessão)',
            'CTR': 'CTR (Pixel)',
            'Taxa Conv.': 'Taxa Conv. (Pixel)',
            'Taxa Conv. Última Sessão': 'Taxa Conv. (Última Sessão)',
            'CPC': 'CPC (Pixel)',
            'CPM': 'CPM (Pixel)',
            'CPV': 'CPV (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência'
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Grupo de Anúncios
    st.subheader("Desempenho por Grupo de Anúncios")
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
        'purchases': 'sum',
        'last_session_transactions': 'sum',
        'last_session_revenue': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_adset['CTR'] = (df_adset['clicks'] / df_adset['impressions'] * 100).round(2)
    df_adset['CPC'] = (df_adset['spend'] / df_adset['clicks']).round(2)
    df_adset['ROAS'] = (df_adset['purchase_value'] / df_adset['spend']).round(2)
    df_adset['Taxa Conv.'] = (df_adset['purchases'] / df_adset['clicks'] * 100).round(2)
    df_adset['CPM'] = (df_adset['spend'] / df_adset['impressions'] * 1000).round(2)
    df_adset['CPV'] = (df_adset['spend'] / df_adset['purchases']).round(2)
    df_adset['Lucro'] = (df_adset['purchase_value'] - df_adset['spend']).round(2)
    df_adset['ROAS Última Sessão'] = (df_adset['last_session_revenue'] / df_adset['spend']).round(2)
    df_adset['Taxa Conv. Última Sessão'] = (df_adset['last_session_transactions'] / df_adset['clicks'] * 100).round(2)
    df_adset['Lucro Última Sessão'] = (df_adset['last_session_revenue'] - df_adset['spend']).round(2)
    df_adset['Taxa de Correspondência'] = (df_adset['last_session_transactions'] / df_adset['purchases'] * 100).round(2)
    
    df_adset = df_adset.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_adset[[
            'adset_name',  # Nome do grupo de anúncios
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions',  # Vendas
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência'  # Taxa de correspondência
        ]].rename(columns={
            'adset_name': 'Grupo de Anúncios',
            'impressions': 'Impressões (Pixel)',
            'clicks': 'Cliques (Pixel)',
            'purchases': 'Vendas (Pixel)',
            'last_session_transactions': 'Vendas (Última Sessão)',
            'spend': 'Investimento (Pixel)',
            'purchase_value': 'Receita (Pixel)',
            'last_session_revenue': 'Receita (Última Sessão)',
            'CTR': 'CTR (Pixel)',
            'Taxa Conv.': 'Taxa Conv. (Pixel)',
            'Taxa Conv. Última Sessão': 'Taxa Conv. (Última Sessão)',
            'CPC': 'CPC (Pixel)',
            'CPM': 'CPM (Pixel)',
            'CPV': 'CPV (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência'
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)

    # Análise por Anúncio
    st.subheader("Desempenho por Anúncio")
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
        'purchases': 'sum',
        'last_session_transactions': 'sum',
        'last_session_revenue': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_ad['CTR'] = (df_ad['clicks'] / df_ad['impressions'] * 100).round(2)
    df_ad['CPC'] = (df_ad['spend'] / df_ad['clicks']).round(2)
    df_ad['ROAS'] = (df_ad['purchase_value'] / df_ad['spend']).round(2)
    df_ad['Taxa Conv.'] = (df_ad['purchases'] / df_ad['clicks'] * 100).round(2)
    df_ad['CPM'] = (df_ad['spend'] / df_ad['impressions'] * 1000).round(2)
    df_ad['CPV'] = (df_ad['spend'] / df_ad['purchases']).round(2)
    df_ad['Lucro'] = (df_ad['purchase_value'] - df_ad['spend']).round(2)
    df_ad['ROAS Última Sessão'] = (df_ad['last_session_revenue'] / df_ad['spend']).round(2)
    df_ad['Taxa Conv. Última Sessão'] = (df_ad['last_session_transactions'] / df_ad['clicks'] * 100).round(2)
    df_ad['Lucro Última Sessão'] = (df_ad['last_session_revenue'] - df_ad['spend']).round(2)
    df_ad['Taxa de Correspondência'] = (df_ad['last_session_transactions'] / df_ad['purchases'] * 100).round(2)
    
    df_ad = df_ad.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_ad[[
            'ad_name',  # Nome do anúncio
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions',  # Vendas
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência'  # Taxa de correspondência
        ]].rename(columns={
            'ad_name': 'Anúncio',
            'impressions': 'Impressões (Pixel)',
            'clicks': 'Cliques (Pixel)',
            'purchases': 'Vendas (Pixel)',
            'last_session_transactions': 'Vendas (Última Sessão)',
            'spend': 'Investimento (Pixel)',
            'purchase_value': 'Receita (Pixel)',
            'last_session_revenue': 'Receita (Última Sessão)',
            'CTR': 'CTR (Pixel)',
            'Taxa Conv.': 'Taxa Conv. (Pixel)',
            'Taxa Conv. Última Sessão': 'Taxa Conv. (Última Sessão)',
            'CPC': 'CPC (Pixel)',
            'CPM': 'CPM (Pixel)',
            'CPV': 'CPV (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência'
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%'
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

    # Formata os valores para o tooltip
    df_grouped['Receita_fmt'] = df_grouped['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_grouped['Investimento_fmt'] = df_grouped['Investimento'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Cria o gráfico de Receita com a cor #3B82F6 (azul)
    line_receita = alt.Chart(df_grouped).mark_line(color='#3B82F6', strokeWidth=2.5).encode(
        x=alt.X('Data:T', 
                title='Data',
                axis=alt.Axis(format='%d/%m', labelAngle=0)),
        y=alt.Y('Receita:Q', 
                axis=alt.Axis(title='Receita',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('Receita_fmt:N', title='Receita')
        ]
    )

    # Cria o gráfico de Investimento com barras estilosas
    bar_investimento = alt.Chart(df_grouped).mark_bar(color='#E5E7EB', size=20).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Investimento:Q', 
                axis=alt.Axis(title='Investimento',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
            alt.Tooltip('Investimento_fmt:N', title='Investimento')
        ]
    )

    # Combine os dois gráficos com melhorias visuais
    combined_chart = alt.layer(
        bar_investimento,
        line_receita
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Evolução de Investimento e Receita',
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
                <span style="color: #4B5563; font-size: 14px;">Receita</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                <span style="color: #4B5563; font-size: 14px;">Investimento</span>
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
    st.title("Mídia Paga")
    
    # Adicionar tabs para análises específicas
    tab1, tab2 = st.tabs(["Visão Geral", "Meta Ads"])
    
    with tab1:
        df_ads = load_paid_media()
        display_general_view(df_ads)
        
    with tab2:
        display_meta_ads_analysis()

    