import streamlit as st
from modules.load_data import load_paid_media, load_meta_ads
import altair as alt
import plotly.express as px
from modules.components import big_number_box
from datetime import datetime
import pandas as pd
from partials.performance import analyze_meta_insights
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def format_currency(value):
    """Formata valor monetário no padrão brasileiro"""
    return f"R$ {value:,.2f}".replace(",", "*").replace(".", ",").replace("*", ".")

def format_number(value):
    """Formata número inteiro com separador de milhar no padrão brasileiro"""
    return f"{int(value):,}".replace(",", ".")

def format_decimal(value):
    """Formata número decimal com separador de milhar no padrão brasileiro"""
    return f"{value:.2f}".replace(".", ",")

def format_currency_with_separators(x):
    return locale.currency(x, grouping=True, symbol='R$ ')

def format_number_with_separators(x):
    return locale.format_string('%.0f', x, grouping=True)

def format_decimal_with_separators(x):
    return locale.format_string('%.2f', x, grouping=True)

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
            format_currency(investimento),
            "Investimento (Pixel)",
            hint="Total investido em anúncios no Meta Ads"
        )
    
    with col2:
        impressions = df_meta['impressions'].sum()
        big_number_box(
            format_number(impressions),
            "Impressões (Pixel)",
            hint="Número total de vezes que seus anúncios foram exibidos"
        )
    
    with col3:
        clicks = df_meta['clicks'].sum()
        big_number_box(
            format_number(clicks),
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
            format_number(purchases),
            "Vendas (Pixel)",
            hint="Número total de vendas atribuídas aos anúncios"
        )
    
    with col2:
        receita = df_meta['purchase_value'].sum()
        big_number_box(
            format_currency(receita),
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
            format_currency(lucro),
            "Lucro (Pixel)",
            hint="Receita menos investimento (Lucro bruto)"
        )

    # Terceira linha - Métricas última sessão
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        last_session_transactions = df_meta['last_session_transactions'].sum()
        big_number_box(
            format_number(last_session_transactions),
            "Vendas (Última Sessão)",
            hint="Número total de vendas atribuídas aos anúncios na última sessão"
        )
    
    with col2:
        last_session_revenue = df_meta['last_session_revenue'].sum()
        big_number_box(
            format_currency(last_session_revenue),
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
            format_currency(last_session_lucro),
            "Lucro (Última Sessão)",
            hint="Receita menos investimento na última sessão (Lucro bruto)"
        )

    # Quarta linha - Métricas de custo e correspondência
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpc = investimento / clicks if clicks > 0 else 0
        big_number_box(
            format_currency(cpc),
            "CPC (Pixel)",
            hint="Custo Por Clique médio no Meta Ads"
        )
    
    with col2:
        cpv = investimento / purchases if purchases > 0 else 0
        big_number_box(
            format_currency(cpv),
            "CPV (Pixel)",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda"
        )
    
    with col3:
        cpm = (investimento / impressions * 1000) if impressions > 0 else 0
        big_number_box(
            format_currency(cpm),
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

    # Quinta linha - Métricas de leads
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leads = df_meta['leads'].sum()
        big_number_box(
            format_number(leads),
            "Leads",
            hint="Número total de leads gerados através dos anúncios"
        )
    
    with col2:
        cpl = investimento / leads if leads > 0 else 0
        big_number_box(
            format_currency(cpl),
            "CPL (Pixel)",
            hint="Custo Por Lead - Valor médio gasto em anúncios para conseguir um lead"
        )
    
    with col3:
        taxa_conv_leads = (leads / clicks * 100) if clicks > 0 else 0
        big_number_box(
            f"{taxa_conv_leads:.2f}%".replace(".", ","),
            "Taxa de Conversão em Leads",
            hint="Porcentagem de cliques que resultaram em leads"
        )
    
    with col4:
        taxa_conv_leads_vendas = (purchases / leads * 100) if leads > 0 else 0
        big_number_box(
            f"{taxa_conv_leads_vendas:.2f}%".replace(".", ","),
            "Taxa de Conversão Leads/Vendas",
            hint="Porcentagem de leads que resultaram em vendas"
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
        'last_session_revenue': 'sum',
        'leads': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_campaign['CTR'] = (df_campaign['clicks'] / df_campaign['impressions'].replace(0, float('nan')) * 100).round(2)
    df_campaign['CPC'] = (df_campaign['spend'] / df_campaign['clicks'].replace(0, float('nan'))).round(2)
    df_campaign['ROAS'] = (df_campaign['purchase_value'] / df_campaign['spend'].replace(0, float('nan'))).round(2)
    df_campaign['Taxa Conv.'] = (df_campaign['purchases'] / df_campaign['clicks'].replace(0, float('nan')) * 100).round(2)
    df_campaign['CPM'] = (df_campaign['spend'] / df_campaign['impressions'].replace(0, float('nan')) * 1000).round(2)
    df_campaign['CPV'] = (df_campaign['spend'] / df_campaign['purchases'].replace(0, float('nan'))).round(2)
    df_campaign['CPL'] = (df_campaign['spend'] / df_campaign['leads'].replace(0, float('nan'))).round(2)
    df_campaign['Lucro'] = (df_campaign['purchase_value'] - df_campaign['spend']).round(2)
    df_campaign['ROAS Última Sessão'] = (df_campaign['last_session_revenue'] / df_campaign['spend'].replace(0, float('nan'))).round(2)
    df_campaign['Taxa Conv. Última Sessão'] = (df_campaign['last_session_transactions'] / df_campaign['clicks'].replace(0, float('nan')) * 100).round(2)
    df_campaign['Lucro Última Sessão'] = (df_campaign['last_session_revenue'] - df_campaign['spend']).round(2)
    df_campaign['Taxa de Correspondência'] = (df_campaign['last_session_transactions'] / df_campaign['purchases'].replace(0, float('nan')) * 100).round(2)
    df_campaign['Taxa Conv. Leads'] = (df_campaign['leads'] / df_campaign['clicks'].replace(0, float('nan')) * 100).round(2)
    df_campaign['Taxa Conv. Leads/Vendas'] = (df_campaign['purchases'] / df_campaign['leads'].replace(0, float('nan')) * 100).round(2)
    
    df_campaign = df_campaign.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_campaign[[
            'campaign_name',  # Nome da campanha
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions', 'leads',  # Vendas e Leads
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV', 'CPL',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência', 'Taxa Conv. Leads', 'Taxa Conv. Leads/Vendas',  # Taxas e Leads
        ]].rename(columns={
            'campaign_name': 'Campanha',
            'impressions': 'Impressões (Pixel)',
            'clicks': 'Cliques (Pixel)',
            'purchases': 'Vendas (Pixel)',
            'last_session_transactions': 'Vendas (Última Sessão)',
            'leads': 'Leads',
            'spend': 'Investimento (Pixel)',
            'purchase_value': 'Receita (Pixel)',
            'last_session_revenue': 'Receita (Última Sessão)',
            'CTR': 'CTR (Pixel)',
            'Taxa Conv.': 'Taxa Conv. (Pixel)',
            'Taxa Conv. Última Sessão': 'Taxa Conv. (Última Sessão)',
            'CPC': 'CPC (Pixel)',
            'CPM': 'CPM (Pixel)',
            'CPV': 'CPV (Pixel)',
            'CPL': 'CPL (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência',
            'Taxa Conv. Leads': 'Taxa Conv. Leads',
            'Taxa Conv. Leads/Vendas': 'Taxa Conv. Leads/Vendas',
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'Leads': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'CPL (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%',
            'Taxa Conv. Leads': '{:.2f}%',
            'Taxa Conv. Leads/Vendas': '{:.2f}%',
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
        'last_session_revenue': 'sum',
        'leads': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_adset['CTR'] = (df_adset['clicks'] / df_adset['impressions'].replace(0, float('nan')) * 100).round(2)
    df_adset['CPC'] = (df_adset['spend'] / df_adset['clicks'].replace(0, float('nan'))).round(2)
    df_adset['ROAS'] = (df_adset['purchase_value'] / df_adset['spend'].replace(0, float('nan'))).round(2)
    df_adset['Taxa Conv.'] = (df_adset['purchases'] / df_adset['clicks'].replace(0, float('nan')) * 100).round(2)
    df_adset['CPM'] = (df_adset['spend'] / df_adset['impressions'].replace(0, float('nan')) * 1000).round(2)
    df_adset['CPV'] = (df_adset['spend'] / df_adset['purchases'].replace(0, float('nan'))).round(2)
    df_adset['CPL'] = (df_adset['spend'] / df_adset['leads'].replace(0, float('nan'))).round(2)
    df_adset['Lucro'] = (df_adset['purchase_value'] - df_adset['spend']).round(2)
    df_adset['ROAS Última Sessão'] = (df_adset['last_session_revenue'] / df_adset['spend'].replace(0, float('nan'))).round(2)
    df_adset['Taxa Conv. Última Sessão'] = (df_adset['last_session_transactions'] / df_adset['clicks'].replace(0, float('nan')) * 100).round(2)
    df_adset['Lucro Última Sessão'] = (df_adset['last_session_revenue'] - df_adset['spend']).round(2)
    df_adset['Taxa de Correspondência'] = (df_adset['last_session_transactions'] / df_adset['purchases'].replace(0, float('nan')) * 100).round(2)
    df_adset['Taxa Conv. Leads'] = (df_adset['leads'] / df_adset['clicks'].replace(0, float('nan')) * 100).round(2)
    df_adset['Taxa Conv. Leads/Vendas'] = (df_adset['purchases'] / df_adset['leads'].replace(0, float('nan')) * 100).round(2)
    
    df_adset = df_adset.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_adset[[
            'adset_name',  # Nome do grupo de anúncios
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions', 'leads',  # Vendas
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV', 'CPL',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência', 'Taxa Conv. Leads', 'Taxa Conv. Leads/Vendas',  # Taxas e Leads
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
            'CPL': 'CPL (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência',
            'Taxa Conv. Leads': 'Taxa Conv. Leads',
            'Taxa Conv. Leads/Vendas': 'Taxa Conv. Leads/Vendas',
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'Leads': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'CPL (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%',
            'Taxa Conv. Leads': '{:.2f}%',
            'Taxa Conv. Leads/Vendas': '{:.2f}%',
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
        'last_session_revenue': 'sum',
        'leads': 'sum'
    }).reset_index()
    
    # Calcular todas as métricas
    df_ad['CTR'] = (df_ad['clicks'] / df_ad['impressions'].replace(0, float('nan')) * 100).round(2)
    df_ad['CPC'] = (df_ad['spend'] / df_ad['clicks'].replace(0, float('nan'))).round(2)
    df_ad['ROAS'] = (df_ad['purchase_value'] / df_ad['spend'].replace(0, float('nan'))).round(2)
    df_ad['Taxa Conv.'] = (df_ad['purchases'] / df_ad['clicks'].replace(0, float('nan')) * 100).round(2)
    df_ad['CPM'] = (df_ad['spend'] / df_ad['impressions'].replace(0, float('nan')) * 1000).round(2)
    df_ad['CPV'] = (df_ad['spend'] / df_ad['purchases'].replace(0, float('nan'))).round(2)
    df_ad['CPL'] = (df_ad['spend'] / df_ad['leads'].replace(0, float('nan'))).round(2)
    df_ad['Lucro'] = (df_ad['purchase_value'] - df_ad['spend']).round(2)
    df_ad['ROAS Última Sessão'] = (df_ad['last_session_revenue'] / df_ad['spend'].replace(0, float('nan'))).round(2)
    df_ad['Taxa Conv. Última Sessão'] = (df_ad['last_session_transactions'] / df_ad['clicks'].replace(0, float('nan')) * 100).round(2)
    df_ad['Lucro Última Sessão'] = (df_ad['last_session_revenue'] - df_ad['spend']).round(2)
    df_ad['Taxa de Correspondência'] = (df_ad['last_session_transactions'] / df_ad['purchases'].replace(0, float('nan')) * 100).round(2)
    df_ad['Taxa Conv. Leads'] = (df_ad['leads'] / df_ad['clicks'].replace(0, float('nan')) * 100).round(2)
    df_ad['Taxa Conv. Leads/Vendas'] = (df_ad['purchases'] / df_ad['leads'].replace(0, float('nan')) * 100).round(2)
    
    df_ad = df_ad.sort_values('purchase_value', ascending=False)
    
    st.data_editor(
        df_ad[[
            'ad_name',  # Nome do anúncio
            'impressions', 'clicks',  # Métricas de alcance
            'purchases', 'last_session_transactions', 'leads',  # Vendas
            'spend', 'purchase_value', 'last_session_revenue',  # Receita
            'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
            'CPC', 'CPM', 'CPV', 'CPL',  # Custos
            'ROAS', 'ROAS Última Sessão',  # ROAS
            'Lucro', 'Lucro Última Sessão',  # Lucro
            'Taxa de Correspondência', 'Taxa Conv. Leads', 'Taxa Conv. Leads/Vendas',  # Taxas e Leads
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
            'CPL': 'CPL (Pixel)',
            'ROAS': 'ROAS (Pixel)',
            'ROAS Última Sessão': 'ROAS (Última Sessão)',
            'Lucro': 'Lucro (Pixel)',
            'Lucro Última Sessão': 'Lucro (Última Sessão)',
            'Taxa de Correspondência': 'Taxa de Correspondência',
            'Taxa Conv. Leads': 'Taxa Conv. Leads',
            'Taxa Conv. Leads/Vendas': 'Taxa Conv. Leads/Vendas',
        }).style.format({
            'Impressões (Pixel)': '{:,.0f}',
            'Cliques (Pixel)': '{:,.0f}',
            'Vendas (Pixel)': '{:,.0f}',
            'Vendas (Última Sessão)': '{:,.0f}',
            'Leads': '{:,.0f}',
            'CTR (Pixel)': '{:.2f}%',
            'CPC (Pixel)': 'R$ {:.2f}',
            'CPM (Pixel)': 'R$ {:.2f}',
            'CPV (Pixel)': 'R$ {:.2f}',
            'CPL (Pixel)': 'R$ {:.2f}',
            'Investimento (Pixel)': 'R$ {:.2f}',
            'Receita (Pixel)': 'R$ {:.2f}',
            'Receita (Última Sessão)': 'R$ {:.2f}',
            'Lucro (Pixel)': 'R$ {:.2f}',
            'Lucro (Última Sessão)': 'R$ {:.2f}',
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
            'Taxa de Correspondência': '{:.2f}%',
            'Taxa Conv. Leads': '{:.2f}%',
            'Taxa Conv. Leads/Vendas': '{:.2f}%',
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
            format_currency(df_ads['Investimento'].sum()), 
            "Investimento",
            hint="Total investido em mídia paga no período selecionado (Google Ads + Meta Ads)"
        )
    
    with col2:
        big_number_box(
            format_currency(df_ads['Receita'].sum()), 
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
            format_currency(cpv),
            "CPV Médio",
            hint="Custo Por Venda - Média do valor gasto em anúncios para conseguir uma venda"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        primeiras_compras = df_ads['Primeiras Compras'].sum()
        big_number_box(
            f"{primeiras_compras:,.0f}".replace(",", "."),
            "Primeiras Compras",
            hint="Número total de novos clientes adquiridos através de mídia paga"
        )

    with col2:
        cpa = df_ads['Investimento'].sum() / primeiras_compras if primeiras_compras > 0 else 0
        big_number_box(
            format_currency(cpa),
            "CPA Médio",
            hint="Custo Por Aquisição - Média do valor gasto em anúncios para conseguir um novo cliente"
        )

    with col3:
        leads = df_ads['Leads'].sum()
        big_number_box(
            f"{leads:,.0f}".replace(",", "."),
            "Leads",
            hint="Número total de leads gerados através de mídia paga"
        )

    # Nova linha - Métricas de Vendas
    col1, col2, col3 = st.columns(3)

    with col1:
        vendas = df_ads['Transações'].sum()
        big_number_box(
            f"{vendas:,.0f}".replace(",", "."),
            "Vendas",
            hint="Número total de vendas atribuídas à mídia paga (modelo de último clique)"
        )

    with col2:
        receita = df_ads['Receita'].sum()
        big_number_box(
            format_currency(receita),
            "Receita",
            hint="Receita total gerada pela mídia paga (modelo de último clique)"
        )

    with col3:
        roas = receita / df_ads['Investimento'].sum() if df_ads['Investimento'].sum() > 0 else 0
        big_number_box(
            f"{roas:.2f}".replace(".", ","),
            "ROAS",
            hint="Return On Ad Spend - Retorno sobre investimento (modelo de último clique)"
        )

    # Nova linha - Métricas First Lead
    col1, col2, col3 = st.columns(3)

    with col1:
        fsm_transactions = df_ads['Transações Primeiro Lead'].sum()
        big_number_box(
            f"{fsm_transactions:,.0f}".replace(",", "."),
            "Vendas (First Lead)",
            hint="Número total de vendas atribuídas ao primeiro lead"
        )

    with col2:
        fsm_revenue = df_ads['Receita Primeiro Lead'].sum()
        big_number_box(
            format_currency(fsm_revenue),
            "Receita (First Lead)",
            hint="Receita total atribuída ao primeiro lead"
        )

    with col3:
        fsm_roas = fsm_revenue / df_ads['Investimento'].sum() if df_ads['Investimento'].sum() > 0 else 0
        big_number_box(
            f"{fsm_roas:.2f}".replace(".", ","),
            "ROAS (First Lead)",
            hint="Return On Ad Spend baseado no primeiro lead"
        )

    st.markdown("---")

    # Gráficos de distribuição por plataforma
    st.subheader("Distribuição por Plataforma")
    
    # Expander com explicações sobre os modelos de atribuição
    with st.expander("ℹ️ Entenda os Modelos de Atribuição", expanded=False):
        st.markdown("""
            ### Modelos de Atribuição Disponíveis

            #### Last Non Direct Click
            - Atribui a conversão ao último clique não direto antes da compra
            - Ignora cliques diretos (quando o usuário acessa o site digitando a URL)
            - Útil para entender qual canal foi o último a influenciar a compra
            - Métricas incluídas:
                - Transações
                - Receita
                - ROAS
                - CPV (Custo por Venda)
                - Primeiras Compras
                - CPA (Custo por Aquisição)

            #### First Lead
            - Atribui a conversão ao primeiro lead gerado
            - Considera todo o caminho de conversão desde o primeiro contato
            - Útil para entender o impacto inicial na jornada do cliente
            - Métricas incluídas:
                - Transações Primeiro Lead
                - Receita Primeiro Lead
                - ROAS First Lead
                - CPV First Lead
                - Primeiras Compras Primeiro Lead
                - CPA First Lead

            ### Por que usar diferentes modelos?
            - **Last Non Direct Click**: Melhor para otimização de campanhas e análise de performance imediata
            - **First Lead**: Melhor para entender o impacto inicial e a jornada completa do cliente
            - A comparação entre os modelos ajuda a entender o papel de cada canal na jornada de conversão
        """)
    
    # Seletor de modelo de atribuição
    modelo_atribuicao = st.radio(
        "Modelo de Atribuição:",
        ["Last Non Direct Click", "First Lead"],
        horizontal=True,
        help="Last Non Direct Click: atribui a conversão ao último clique não direto antes da compra. First Lead: atribui a conversão ao primeiro lead gerado."
    )
    
    # Agrupar dados por plataforma
    df_platform = df_ads.groupby('Plataforma').agg({
        'Investimento': 'sum',
        'Cliques': 'sum',
        'Receita': 'sum',
        'Leads': 'sum',
        'Transações Primeiro Lead': 'sum',
        'Receita Primeiro Lead': 'sum'
    }).reset_index()
    
    # Garantir que os valores sejam numéricos
    df_platform['Investimento'] = pd.to_numeric(df_platform['Investimento'], errors='coerce')
    df_platform['Cliques'] = pd.to_numeric(df_platform['Cliques'], errors='coerce')
    df_platform['Receita'] = pd.to_numeric(df_platform['Receita'], errors='coerce')
    df_platform['Leads'] = pd.to_numeric(df_platform['Leads'], errors='coerce')
    df_platform['Transações Primeiro Lead'] = pd.to_numeric(df_platform['Transações Primeiro Lead'], errors='coerce')
    df_platform['Receita Primeiro Lead'] = pd.to_numeric(df_platform['Receita Primeiro Lead'], errors='coerce')
    
    # Remover linhas com valores nulos
    df_platform = df_platform.dropna()
    
    # Criar quatro colunas para os gráficos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Investimento**")
        # Calcular percentuais
        total_investimento = df_platform['Investimento'].sum()
        df_platform['Investimento_pct'] = (df_platform['Investimento'] / total_investimento * 100).round(1)
        
        # Gráfico de pizza para Investimento
        fig = px.pie(df_platform, 
                    values='Investimento', 
                    names='Plataforma',
                    title='')
        
        fig.update_traces(textposition='inside', 
                         textinfo='percent',
                         textfont_size=14)
        
        fig.update_layout(showlegend=True,
                         legend=dict(
                             orientation="v",
                             yanchor="middle",
                             y=0.5,
                             xanchor="right",
                             x=1.2
                         ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Cliques**")
        # Calcular percentuais
        total_cliques = df_platform['Cliques'].sum()
        df_platform['Cliques_pct'] = (df_platform['Cliques'] / total_cliques * 100).round(1)
        
        # Gráfico de pizza para Cliques
        fig = px.pie(df_platform, 
                    values='Cliques', 
                    names='Plataforma',
                    title='')
        
        fig.update_traces(textposition='inside', 
                         textinfo='percent',
                         textfont_size=14)
        
        fig.update_layout(showlegend=True,
                         legend=dict(
                             orientation="v",
                             yanchor="middle",
                             y=0.5,
                             xanchor="right",
                             x=1.2
                         ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Receita**")
        # Calcular percentuais
        receita_col = 'Receita Primeiro Lead' if modelo_atribuicao == "First Lead" else 'Receita'
        total_receita = df_platform[receita_col].sum()
        df_platform['Receita_pct'] = (df_platform[receita_col] / total_receita * 100).round(1)
        
        # Gráfico de pizza para Receita
        fig = px.pie(df_platform, 
                    values=receita_col, 
                    names='Plataforma',
                    title='')
        
        fig.update_traces(textposition='inside', 
                         textinfo='percent',
                         textfont_size=14)
        
        fig.update_layout(showlegend=True,
                         legend=dict(
                             orientation="v",
                             yanchor="middle",
                             y=0.5,
                             xanchor="right",
                             x=1.2
                         ))
        
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("**Leads**")
        # Calcular percentuais
        total_leads = df_platform['Leads'].sum()
        df_platform['Leads_pct'] = (df_platform['Leads'] / total_leads * 100).round(1)
        
        # Gráfico de pizza para Leads
        fig = px.pie(df_platform, 
                    values='Leads', 
                    names='Plataforma',
                    title='')
        
        fig.update_traces(textposition='inside', 
                         textinfo='percent',
                         textfont_size=14)
        
        fig.update_layout(showlegend=True,
                         legend=dict(
                             orientation="v",
                             yanchor="middle",
                             y=0.5,
                             xanchor="right",
                             x=1.2
                         ))
        
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Timeline de Métricas
    st.subheader("📈 Timeline de Métricas")
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Agrupar dados por data
    df_timeline = df_ads.groupby('Data').agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Receita': 'sum',
        'Leads': 'sum',
        'Transações Primeiro Lead': 'sum',
        'Receita Primeiro Lead': 'sum'
    }).reset_index()

    # Calcular métricas derivadas
    df_timeline['CTR'] = (df_timeline['Cliques'] / df_timeline['Impressões'] * 100).round(2)
    df_timeline['Taxa Conv.'] = (df_timeline['Transações'] / df_timeline['Cliques'] * 100).round(2)
    df_timeline['ROAS'] = (df_timeline['Receita'] / df_timeline['Investimento']).round(2)
    df_timeline['CPC'] = (df_timeline['Investimento'] / df_timeline['Cliques']).round(2)
    df_timeline['CPV'] = (df_timeline['Investimento'] / df_timeline['Transações']).round(2)
    df_timeline['CPL'] = (df_timeline['Investimento'] / df_timeline['Leads']).round(2)
    df_timeline['ROAS First Lead'] = (df_timeline['Receita Primeiro Lead'] / df_timeline['Investimento']).round(2)

    # Lista de métricas disponíveis para visualização
    available_metrics = {
        'Investimento': 'Investimento (R$)',
        'Impressões': 'Impressões',
        'Cliques': 'Cliques',
        'Transações': 'Vendas',
        'Receita': 'Receita (R$)',
        'Leads': 'Leads',
        'CTR': 'CTR (%)',
        'Taxa Conv.': 'Taxa de Conversão (%)',
        'ROAS': 'ROAS',
        'CPC': 'CPC (R$)',
        'CPV': 'CPV (R$)',
        'CPL': 'CPL (R$)',
        'ROAS First Lead': 'ROAS First Lead'
    }

    # Seletor de métricas
    selected_metrics = st.multiselect(
        "Selecione as métricas para visualizar:",
        list(available_metrics.keys()),
        default=['ROAS', 'Taxa Conv.', 'CTR'],
        format_func=lambda x: available_metrics[x]
    )

    if selected_metrics:
        # Preparar dados para o gráfico
        chart_data = pd.melt(
            df_timeline,
            id_vars=['Data'],
            value_vars=selected_metrics,
            var_name='Métrica',
            value_name='Valor'
        )

        # Criar gráfico base
        base = alt.Chart(chart_data).encode(
            x=alt.X('Data:T',
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
                alt.Tooltip('Data:T', title='Data', format='%d/%m/%Y'),
                alt.Tooltip('Métrica:N', title='Métrica'),
                alt.Tooltip('Valor:Q', title='Valor', format=',.2f')
            ]
        )

        # Combinar linha e pontos
        chart = (line + points).properties(
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

        st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # Filtros para a tabela
    st.subheader("Dados Detalhados")
    
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

    # Display the aggregated data in Streamlit data editor
    df_ads_agg = df_ads.groupby(['Plataforma', 'Campanha']).agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Primeiras Compras': 'sum',
        'Leads': 'sum',
        'Receita': 'sum',
        'Transações Primeiro Lead': 'sum',
        'Receita Primeiro Lead': 'sum',
        'Primeiras Compras Primeiro Lead': 'sum'
    }).reset_index()

    # Calcular métricas baseado no modelo de atribuição selecionado
    if modelo_atribuicao == "Last Non Direct Click":
        df_ads_agg['ROAS'] = (df_ads_agg['Receita'] / df_ads_agg['Investimento'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPA'] = (df_ads_agg['Investimento'] / df_ads_agg['Primeiras Compras'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPL'] = (df_ads_agg['Investimento'] / df_ads_agg['Leads'].replace(0, float('nan'))).round(2)
        
        # Reorganizar colunas em grupos lógicos para Last Non Direct Click
        columns_order = [
            # Identificação
            'Plataforma', 'Campanha',
            # Investimento
            'Investimento',
            # Métricas de Alcance
            'Impressões', 'Cliques',
            # Métricas de Aquisição
            'Leads', 'CPL',
            # Métricas de Vendas (Last Non Direct Click)
            'Transações', 'Primeiras Compras', 'CPA', 'Receita', 'ROAS', 'CPV'
        ]
    else:  # First Lead
        df_ads_agg['ROAS'] = (df_ads_agg['Receita Primeiro Lead'] / df_ads_agg['Investimento'])
        df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações Primeiro Lead'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPA'] = (df_ads_agg['Investimento'] / df_ads_agg['Primeiras Compras Primeiro Lead'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPL'] = (df_ads_agg['Investimento'] / df_ads_agg['Leads'].replace(0, float('nan'))).round(2)
        
        # Reorganizar colunas em grupos lógicos para First Lead
        columns_order = [
            # Identificação
            'Plataforma', 'Campanha',
            # Investimento
            'Investimento',
            # Métricas de Alcance
            'Impressões', 'Cliques',
            # Métricas de Aquisição
            'Leads', 'CPL',
            # Métricas First Lead
            'Transações Primeiro Lead', 'Primeiras Compras Primeiro Lead', 'CPA', 'Receita Primeiro Lead', 'ROAS', 'CPV'
        ]
    
    df_ads_agg = df_ads_agg.sort_values(by='Receita' if modelo_atribuicao == "Last Non Direct Click" else 'Receita Primeiro Lead', ascending=False)
    
    # Format the columns to have at most 2 decimal places
    df_ads_agg['Investimento'] = df_ads_agg['Investimento'].round(2)
    df_ads_agg['Receita'] = df_ads_agg['Receita'].round(2)
    df_ads_agg['Receita Primeiro Lead'] = df_ads_agg['Receita Primeiro Lead'].round(2)
    df_ads_agg['ROAS'] = df_ads_agg['ROAS'].round(2)
    df_ads_agg['CPV'] = df_ads_agg['CPV'].round(2)
    df_ads_agg['CPA'] = df_ads_agg['CPA'].round(2)
    df_ads_agg['CPL'] = df_ads_agg['CPL'].round(2)
    
    # Configurar o estilo do pandas
    pd.options.display.float_format = '{:,.2f}'.format
    
    # Criar o estilo
    styled_df = df_ads_agg[columns_order].style.format({
        'Investimento': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Impressões': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Cliques': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Transações': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Primeiras Compras': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Primeiras Compras Primeiro Lead': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Leads': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Receita': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'ROAS': lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'CPV': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'CPA': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'CPL': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Transações Primeiro Lead': lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
        'Receita Primeiro Lead': lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    })
    
    # Aplicar o estilo
    st.dataframe(styled_df, use_container_width=True)

def display_tab_paid_media():
    st.title("Mídia Paga")
    
    # Adicionar tabs para análises específicas
    tab1, tab2 = st.tabs(["Visão Geral", "Meta Ads"])
    
    with tab1:
        df_ads = load_paid_media()
        display_general_view(df_ads)
        
    with tab2:
        display_meta_ads_analysis()

    