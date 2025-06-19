import streamlit as st
from modules.load_data import load_paid_media, load_meta_ads, load_google_ads_keywords
import altair as alt
import plotly.express as px
from modules.components import big_number_box
from datetime import datetime
import pandas as pd
from partials.performance import analyze_meta_insights
from babel.numbers import format_currency, format_decimal, format_number

def format_currency_br(value):
    """Formata valor monetário no padrão brasileiro"""
    return format_currency(value, 'BRL', locale='pt_BR')

def format_number_br(value):
    """Formata número inteiro com separador de milhar no padrão brasileiro"""
    return format_number(value, locale='pt_BR')

def format_decimal_br(value):
    """Formata número decimal com separador de milhar no padrão brasileiro"""
    return format_decimal(value, format='#,##0.00', locale='pt_BR')

def format_currency_with_separators(x):
    return locale.currency(x, grouping=True, symbol='R$ ')

def format_number_with_separators(x):
    return locale.format_string('%.0f', x, grouping=True)

def format_decimal_with_separators(x):
    return locale.format_string('%.2f', x, grouping=True)

def create_trend_chart(df):
    """Cria gráfico de tendência com as métricas selecionadas"""
    
    # Lista de métricas disponíveis para visualização
    available_metrics = {
        'impressions': 'Impressões',
        'clicks': 'Cliques',
        'spend': 'Investimento',
        'purchase_value': 'Receita',
        'purchases': 'Vendas',
        'CTR': 'CTR (%)',
        'Taxa Conv.': 'Taxa de Conversão (%)',
        'ROAS': 'ROAS',
        'CPC': 'CPC (R$)',
        'CPV': 'CPV (R$)',
        'CPM': 'CPM (R$)'
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
            df,
            id_vars=['date'],
            value_vars=selected_metrics,
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

def display_meta_ads_analysis():
    """Exibe análise detalhada do Meta Ads"""
    
    # Carregar dados
    df_meta = load_meta_ads()
    
    if df_meta.empty:
        st.error("Não há dados do Meta Ads para exibir.")
        return
    
    # Calcular métricas totais
    investimento = df_meta['spend'].sum()
    impressions = df_meta['impressions'].sum()
    clicks = df_meta['clicks'].sum()
    purchases = df_meta['purchases'].sum()
    last_session_transactions = df_meta['last_session_transactions'].sum()
    last_session_revenue = df_meta['last_session_revenue'].sum()
    
    # Primeira linha - Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            format_currency_br(investimento),
            "Investimento",
            hint="Valor total investido em anúncios"
        )
    
    with col2:
        big_number_box(
            format_number_br(impressions),
            "Impressões",
            hint="Número total de vezes que os anúncios foram exibidos"
        )
    
    with col3:
        big_number_box(
            format_number_br(clicks),
            "Cliques",
            hint="Número total de cliques nos anúncios"
        )
    
    with col4:
        big_number_box(
            format_number_br(purchases),
            "Vendas (Pixel)",
            hint="Número total de vendas atribuídas ao Meta Ads pelo Pixel"
        )

    # Segunda linha - Métricas de receita
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            format_currency_br(last_session_revenue),
            "Receita (Última Sessão)",
            hint="Receita atribuída à última sessão antes da compra"
        )
    
    with col2:
        big_number_box(
            format_number_br(last_session_transactions),
            "Vendas (Última Sessão)",
            hint="Número de vendas atribuídas à última sessão antes da compra"
        )
    
    with col3:
        roas = (last_session_revenue / investimento) if investimento > 0 else 0
        big_number_box(
            f"{roas:.2f}".replace(".", ","),
            "ROAS (Última Sessão)",
            hint="Retorno sobre o investimento em anúncios (Receita/Investimento)"
        )
    
    with col4:
        last_session_lucro = last_session_revenue - investimento
        big_number_box(
            format_currency_br(last_session_lucro),
            "Lucro (Última Sessão)",
            hint="Receita menos investimento na última sessão (Lucro bruto)"
        )

    # Quarta linha - Métricas de custo e correspondência
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpc = (investimento / clicks) if clicks > 0 else 0
        big_number_box(
            format_currency_br(cpc),
            "CPC (Pixel)",
            hint="Custo Por Clique médio no Meta Ads"
        )
    
    with col2:
        cpv = (investimento / purchases) if purchases > 0 else 0
        big_number_box(
            format_currency_br(cpv),
            "CPV (Pixel)",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda"
        )
    
    with col3:
        cpm = (investimento / impressions * 1000) if impressions > 0 else 0
        big_number_box(
            format_currency_br(cpm),
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
            format_number_br(leads),
            "Leads",
            hint="Número total de leads gerados através dos anúncios"
        )
    
    with col2:
        cpl = (investimento / leads) if leads > 0 else 0
        big_number_box(
            format_currency_br(cpl),
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
    
    # Calcular todas as métricas com tratamento para divisão por zero
    df_daily['CTR'] = (df_daily['clicks'] / df_daily['impressions'].replace(0, float('nan')) * 100).round(2)
    df_daily['CPC'] = (df_daily['spend'] / df_daily['clicks'].replace(0, float('nan'))).round(2)
    df_daily['ROAS'] = (df_daily['purchase_value'] / df_daily['spend'].replace(0, float('nan'))).round(2)
    df_daily['Taxa Conv.'] = (df_daily['purchases'] / df_daily['clicks'].replace(0, float('nan')) * 100).round(2)
    df_daily['CPM'] = (df_daily['spend'] / df_daily['impressions'].replace(0, float('nan')) * 1000).round(2)
    df_daily['CPV'] = (df_daily['spend'] / df_daily['purchases'].replace(0, float('nan'))).round(2)
    
    # Preencher valores NaN com 0
    df_daily = df_daily.fillna(0)
    
    # Criar gráfico de tendência
    create_trend_chart(df_daily)

    # Tabela de Campanhas
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    st.subheader("Campanhas")
    
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
    
    # Calcular todas as métricas com tratamento para divisão por zero
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
    
    # Preencher valores NaN com 0
    df_campaign = df_campaign.fillna(0)
    
    # Exibir tabela de campanhas
    display_campaign_table(df_campaign)

    # Tabela de Conjuntos de Anúncios
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    st.subheader("Conjuntos de Anúncios")
    
    adset_options = ["Todos"] + sorted(df_meta['adset_name'].unique().tolist())
    selected_adset = st.selectbox("Filtrar Conjunto de Anúncios:", adset_options, key='adset_filter')
    
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
    
    # Calcular todas as métricas com tratamento para divisão por zero
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
    
    # Preencher valores NaN com 0
    df_adset = df_adset.fillna(0)
    
    # Exibir tabela de conjuntos de anúncios
    display_adset_table(df_adset)

    # Tabela de Anúncios
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    st.subheader("Anúncios")
    
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
    
    # Calcular todas as métricas com tratamento para divisão por zero
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
    
    # Preencher valores NaN com 0
    df_ad = df_ad.fillna(0)
    
    # Exibir tabela de anúncios
    display_ad_table(df_ad)

def display_general_view(df_ads):
    """Exibe visão geral da mídia paga"""

    st.subheader("📊 Visão Geral da Mídia Paga")

    # Filtros na sidebar
    with st.sidebar:
        st.subheader("Filtros")
        platform_options = ["Todas"] + sorted(df_ads['Plataforma'].dropna().unique().tolist())
        campaign_options = ["Todas"] + sorted(df_ads['Campanha'].dropna().unique().tolist())

        selected_platform = st.selectbox("Plataforma:", platform_options)
        selected_campaign = st.selectbox("Campanha:", campaign_options)
        
        st.markdown("---")
        
        # Seletor de modelo de atribuição para o funil
        modelo_funil = st.radio(
            "Modelo de Atribuição:",
            ["OriginStack™", "Last Non Direct Click"],
            help="OriginStack™: modelo proprietário que atribui a conversão seguindo uma ordem de prioridade específica. Last Non Direct Click: atribui a conversão ao último clique não direto antes da compra."
        )
        
        # Expander com explicação do OriginStack™
        with st.expander("ℹ️ Sobre o OriginStack™", expanded=False):
            st.markdown("""
                ### OriginStack™ - Modelo de Atribuição Proprietário

                O OriginStack™ é um modelo de atribuição proprietário que considera a jornada completa do usuário, atribuindo a conversão seguindo uma ordem específica de prioridade:

                1. **First Lead (Prioridade Máxima)**
                   - Atribui a conversão quando o email do usuário foi capturado em qualquer ponto do site
                   - Prioriza especialmente capturas através de popups e formulários
                   - Considera o histórico completo do usuário, mesmo em diferentes navegadores
                   - Ideal para entender o impacto inicial na jornada do cliente

                2. **First Session (Segunda Prioridade)**
                   - Atribui a conversão quando o usuário teve sua primeira sessão no mesmo navegador
                   - Considera a primeira interação do usuário com a marca
                   - Útil para entender o comportamento inicial do usuário

                3. **Last Session (Terceira Prioridade)**
                   - Atribui a conversão quando o usuário teve sua última sessão no mesmo navegador
                   - Considera a interação mais recente antes da conversão
                   - Ajuda a entender o gatilho final da conversão

                Este modelo permite uma visão mais completa da jornada do usuário, considerando tanto o impacto inicial quanto o gatilho final da conversão.
            """)

    # Aplicar filtros
    df_filtered = df_ads.copy()
    if selected_platform != "Todas":
        df_filtered = df_filtered[df_filtered['Plataforma'] == selected_platform]
    if selected_campaign != "Todas":
        df_filtered = df_filtered[df_filtered['Campanha'] == selected_campaign]

    # Funil de Conversão
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Calcular totais para o funil
    investimento = df_filtered['Investimento'].sum()
    impressoes = df_filtered['Impressões'].sum()
    cliques = df_filtered['Cliques'].sum()
    
    # Vendas e Receita - Last Non Direct Click
    vendas_last = df_filtered['Transações'].sum()
    receita_last = df_filtered['Receita'].sum()
    
    # Vendas e Receita - OriginStack™
    vendas_first = df_filtered['Transações Primeiro Lead'].sum()
    receita_first = df_filtered['Receita Primeiro Lead'].sum()

    # Primeiras Compras
    primeiras_compras_last = df_filtered['Primeiras Compras'].sum()
    primeiras_compras_first = df_filtered['Primeiras Compras Primeiro Lead'].sum()
    receita_primeiras_last = df_filtered['Receita Primeiras Compras'].sum()
    receita_primeiras_first = df_filtered['Receita Primeiras Compras Primeiro Lead'].sum()

    # Calcular métricas de custo
    cpm = (investimento / impressoes * 1000) if impressoes > 0 else 0
    cpc = (investimento / cliques) if cliques > 0 else 0
    
    # CPA para todos os modelos
    cpa_last = (investimento / vendas_last) if vendas_last > 0 else 0
    cpa_first = (investimento / vendas_first) if vendas_first > 0 else 0
    cpa_primeiras_last = (investimento / primeiras_compras_last) if primeiras_compras_last > 0 else 0
    cpa_primeiras_first = (investimento / primeiras_compras_first) if primeiras_compras_first > 0 else 0

    # Calcular ROAS
    roas_last = (receita_last / investimento) if investimento > 0 else 0
    roas_first = (receita_first / investimento) if investimento > 0 else 0
    roas_primeiras_last = (receita_primeiras_last / investimento) if investimento > 0 else 0
    roas_primeiras_first = (receita_primeiras_first / investimento) if investimento > 0 else 0

    # Selecionar valores baseado no modelo escolhido
    if modelo_funil == "Last Non Direct Click":
        vendas = vendas_last
        receita = receita_last
        primeiras_compras = primeiras_compras_last
        receita_primeiras = receita_primeiras_last
        cpa = cpa_last
        cpa_primeiras = cpa_primeiras_last
        roas = roas_last
        roas_primeiras = roas_primeiras_last
        modelo_label = "Last Click"
    else:
        vendas = vendas_first
        receita = receita_first
        primeiras_compras = primeiras_compras_first
        receita_primeiras = receita_primeiras_first
        cpa = cpa_first
        cpa_primeiras = cpa_primeiras_first
        roas = roas_first
        roas_primeiras = roas_primeiras_first
        modelo_label = "OriginStack™"

    # Calcular percentual de primeiras compras vs todas as compras
    percentual_primeiras = (primeiras_compras / vendas * 100) if vendas > 0 else 0

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
        .funnel-percentage {{
            font-size: 16px;
            font-weight: bold;
            color: #FFD700;
            margin-top: 5px;
        }}
        .step-1 {{ background: linear-gradient(135deg, #1a73e8, #0d47a1); width: 100%; }}
        .step-2 {{ background: linear-gradient(135deg, #2196f3, #1976d2); width: 90%; }}
        .step-3 {{ background: linear-gradient(135deg, #42a5f5, #2196f3); width: 80%; }}
        .step-4 {{ background: linear-gradient(135deg, #64b5f6, #42a5f5); width: 70%; }}
        .step-5 {{ background: linear-gradient(135deg, #90caf9, #64b5f6); width: 60%; }}
    </style>
    <div class="funnel-container">
        <div class="funnel-step step-1">
            <div class="funnel-main">
                <div class="funnel-value">R$ {investimento:,.2f}</div>
                <div class="funnel-label">Investimento</div>
            </div>
        </div>
        <div class="funnel-step step-2">
            <div class="funnel-main">
                <div class="funnel-value">{impressoes:,.0f}</div>
                <div class="funnel-label">Impressões</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">R$ {cpm:,.2f}</div>
                <div class="funnel-cost-label">CPM</div>
            </div>
        </div>
        <div class="funnel-step step-3">
            <div class="funnel-main">
                <div class="funnel-value">{cliques:,.0f}</div>
                <div class="funnel-label">Cliques</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">R$ {cpc:,.2f}</div>
                <div class="funnel-cost-label">CPC</div>
            </div>
        </div>
        <div class="funnel-step step-4">
            <div class="funnel-main">
                <div class="funnel-value">{vendas:,.0f}</div>
                <div class="funnel-label">Todas as Compras ({modelo_label})</div>
                <div class="funnel-divider"></div>
                <div class="funnel-value">{primeiras_compras:,.0f}</div>
                <div class="funnel-label">Primeiras Compras ({modelo_label})</div>
                <div class="funnel-percentage">{percentual_primeiras:.1f}% das compras são primeiras compras</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">R$ {cpa:,.2f}</div>
                <div class="funnel-cost-label">CPV ({modelo_label})</div>
                <div class="funnel-divider"></div>
                <div class="funnel-cost-value">R$ {cpa_primeiras:,.2f}</div>
                <div class="funnel-cost-label">CPA ({modelo_label})</div>
            </div>
        </div>
        <div class="funnel-step step-5">
            <div class="funnel-main">
                <div class="funnel-value">R$ {receita:,.2f}</div>
                <div class="funnel-label">Receita ({modelo_label})</div>
                <div class="funnel-divider"></div>
                <div class="funnel-value">R$ {receita_primeiras:,.2f}</div>
                <div class="funnel-label">Receita Primeiras Compras ({modelo_label})</div>
            </div>
            <div class="funnel-cost">
                <div class="funnel-cost-value">{roas:.2f}x</div>
                <div class="funnel-cost-label">ROAS ({modelo_label})</div>
                <div class="funnel-divider"></div>
                <div class="funnel-cost-value">{roas_primeiras:.2f}x</div>
                <div class="funnel-cost-label">ROAS Primeiras ({modelo_label})</div>
            </div>
        </div>
    </div>
    """

    st.markdown(funnel_html, unsafe_allow_html=True)

    st.markdown("---")

    # Timeline de Métricas
    st.subheader("📈 Timeline de Métricas")
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Agrupar dados por data
    df_timeline = df_filtered.groupby('Data').agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Receita': 'sum',
        'Leads': 'sum',
        'Transações Primeiro Lead': 'sum',
        'Receita Primeiro Lead': 'sum',
        'Primeiras Compras': 'sum',
        'Primeiras Compras Primeiro Lead': 'sum',
        'Receita Primeiras Compras': 'sum',
        'Receita Primeiras Compras Primeiro Lead': 'sum'
    }).reset_index()

    # Calcular métricas derivadas
    df_timeline['CTR'] = (df_timeline['Cliques'] / df_timeline['Impressões'].replace(0, float('nan')) * 100).round(2)
    df_timeline['Taxa Conv.'] = (df_timeline['Transações'] / df_timeline['Cliques'].replace(0, float('nan')) * 100).round(2)
    df_timeline['ROAS'] = (df_timeline['Receita'] / df_timeline['Investimento'].replace(0, float('nan'))).round(2)
    df_timeline['CPC'] = (df_timeline['Investimento'] / df_timeline['Cliques'].replace(0, float('nan'))).round(2)
    df_timeline['CPV'] = (df_timeline['Investimento'] / df_timeline['Transações'].replace(0, float('nan'))).round(2)
    df_timeline['CPL'] = (df_timeline['Investimento'] / df_timeline['Leads'].replace(0, float('nan'))).round(2)
    df_timeline['ROAS OriginStack™'] = (df_timeline['Receita Primeiro Lead'] / df_timeline['Investimento'].replace(0, float('nan'))).round(2)
    df_timeline['ROAS Primeiras'] = (df_timeline['Receita Primeiras Compras'] / df_timeline['Investimento'].replace(0, float('nan'))).round(2)
    df_timeline['ROAS Primeiras OriginStack™'] = (df_timeline['Receita Primeiras Compras Primeiro Lead'] / df_timeline['Investimento'].replace(0, float('nan'))).round(2)

    # Preencher valores NaN com 0
    df_timeline = df_timeline.fillna(0)

    # Lista de métricas disponíveis para visualização
    available_metrics = {
        'Investimento': 'Investimento (R$)',
        'Impressões': 'Impressões',
        'Cliques': 'Cliques',
        'Transações': 'Todas as Compras (Last Click)',
        'Transações Primeiro Lead': 'Todas as Compras (OriginStack™)',
        'Primeiras Compras': 'Primeiras Compras (Last Click)',
        'Primeiras Compras Primeiro Lead': 'Primeiras Compras (OriginStack™)',
        'Receita': 'Receita (Last Click)',
        'Receita Primeiro Lead': 'Receita (OriginStack™)',
        'Receita Primeiras Compras': 'Receita Primeiras (Last Click)',
        'Receita Primeiras Compras Primeiro Lead': 'Receita Primeiras (OriginStack™)',
        'Leads': 'Leads',
        'CTR': 'CTR (%)',
        'Taxa Conv.': 'Taxa de Conversão (%)',
        'ROAS': 'ROAS (Last Click)',
        'ROAS OriginStack™': 'ROAS (OriginStack™)',
        'ROAS Primeiras': 'ROAS Primeiras (Last Click)',
        'ROAS Primeiras OriginStack™': 'ROAS Primeiras (OriginStack™)',
        'CPC': 'CPC (R$)',
        'CPV': 'CPV (R$)',
        'CPL': 'CPL (R$)'
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

    # Dados Detalhados
    st.subheader("Dados Detalhados")
    
    # Agregar dados
    df_ads_agg = df_filtered.groupby(['Plataforma', 'Campanha']).agg({
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
    if modelo_funil == "Last Non Direct Click":
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
    else:  # OriginStack™
        df_ads_agg['ROAS'] = (df_ads_agg['Receita Primeiro Lead'] / df_ads_agg['Investimento'])
        df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações Primeiro Lead'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPA'] = (df_ads_agg['Investimento'] / df_ads_agg['Primeiras Compras Primeiro Lead'].replace(0, float('nan'))).round(2)
        df_ads_agg['CPL'] = (df_ads_agg['Investimento'] / df_ads_agg['Leads'].replace(0, float('nan'))).round(2)
        
        # Reorganizar colunas em grupos lógicos para OriginStack™
        columns_order = [
            # Identificação
            'Plataforma', 'Campanha',
            # Investimento
            'Investimento',
            # Métricas de Alcance
            'Impressões', 'Cliques',
            # Métricas de Aquisição
            'Leads', 'CPL',
            # Métricas OriginStack™
            'Transações Primeiro Lead', 'Primeiras Compras Primeiro Lead', 'CPA', 'Receita Primeiro Lead', 'ROAS', 'CPV'
        ]
    
    df_ads_agg = df_ads_agg.sort_values(by='Receita' if modelo_funil == "Last Non Direct Click" else 'Receita Primeiro Lead', ascending=False)
    
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

def display_google_ads_keywords():
    """Exibe análise detalhada das keywords do Google Ads"""
    
    # Carregar dados
    df_keywords = load_google_ads_keywords()
    
    if df_keywords.empty:
        st.error("Não há dados de keywords do Google Ads para exibir.")
        return
    
    # Calcular métricas totais
    investimento = df_keywords['cost'].sum()
    impressions = df_keywords['impressions'].sum()
    clicks = df_keywords['clicks'].sum()
    transactions = df_keywords['transactions'].sum()
    revenue = df_keywords['revenue'].sum()
    
    # Primeira linha - Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            format_currency_br(investimento),
            "Investimento",
            hint="Valor total investido em anúncios"
        )
    
    with col2:
        big_number_box(
            format_number_br(impressions),
            "Impressões",
            hint="Número total de vezes que os anúncios foram exibidos"
        )
    
    with col3:
        big_number_box(
            format_number_br(clicks),
            "Cliques",
            hint="Número total de cliques nos anúncios"
        )
    
    with col4:
        big_number_box(
            format_number_br(transactions),
            "Vendas",
            hint="Número total de vendas atribuídas ao Google Ads"
        )

    # Segunda linha - Métricas de receita
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            format_currency_br(revenue),
            "Receita",
            hint="Receita total atribuída ao Google Ads"
        )
    
    with col2:
        roas = (revenue / investimento) if investimento > 0 else 0
        big_number_box(
            f"{roas:.2f}".replace(".", ","),
            "ROAS",
            hint="Retorno sobre o investimento em anúncios (Receita/Investimento)"
        )
    
    with col3:
        lucro = revenue - investimento
        big_number_box(
            format_currency_br(lucro),
            "Lucro",
            hint="Receita menos investimento (Lucro bruto)"
        )
    
    with col4:
        taxa_conv = (transactions / clicks * 100) if clicks > 0 else 0
        big_number_box(
            f"{taxa_conv:.2f}%".replace(".", ","),
            "Taxa de Conversão",
            hint="Porcentagem de cliques que resultaram em vendas"
        )

    # Terceira linha - Métricas de custo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpc = (investimento / clicks) if clicks > 0 else 0
        big_number_box(
            format_currency_br(cpc),
            "CPC",
            hint="Custo Por Clique médio no Google Ads"
        )
    
    with col2:
        cpv = (investimento / transactions) if transactions > 0 else 0
        big_number_box(
            format_currency_br(cpv),
            "CPV",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda"
        )
    
    with col3:
        cpm = (investimento / impressions * 1000) if impressions > 0 else 0
        big_number_box(
            format_currency_br(cpm),
            "CPM",
            hint="Custo Por Mil Impressões no Google Ads"
        )
    
    with col4:
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        big_number_box(
            f"{ctr:.2f}%".replace(".", ","),
            "CTR",
            hint="Click-Through Rate - Porcentagem de impressões que resultaram em cliques"
        )

    # Tabela de Keywords
    st.subheader("📊 Análise de Keywords")
    
    # Agrupar dados por keyword
    df_keywords_grouped = df_keywords.groupby(['keyword', 'match_type']).agg({
        'cost': 'sum',
        'impressions': 'sum',
        'clicks': 'sum',
        'transactions': 'sum',
        'revenue': 'sum'
    }).reset_index()
    
    # Calcular métricas derivadas
    df_keywords_grouped['CPC'] = df_keywords_grouped['cost'] / df_keywords_grouped['clicks']
    df_keywords_grouped['CTR'] = df_keywords_grouped['clicks'] / df_keywords_grouped['impressions'] * 100
    df_keywords_grouped['Taxa Conv.'] = df_keywords_grouped['transactions'] / df_keywords_grouped['clicks'] * 100
    df_keywords_grouped['ROAS'] = df_keywords_grouped['revenue'] / df_keywords_grouped['cost']
    
    # Ordenar por investimento
    df_keywords_grouped = df_keywords_grouped.sort_values('cost', ascending=False)
    
    # Formatar valores
    df_keywords_grouped['cost'] = df_keywords_grouped['cost'].apply(format_currency_br)
    df_keywords_grouped['revenue'] = df_keywords_grouped['revenue'].apply(format_currency_br)
    df_keywords_grouped['CPC'] = df_keywords_grouped['CPC'].apply(format_currency_br)
    df_keywords_grouped['ROAS'] = df_keywords_grouped['ROAS'].apply(lambda x: f"{x:.2f}".replace(".", ","))
    df_keywords_grouped['CTR'] = df_keywords_grouped['CTR'].apply(lambda x: f"{x:.2f}%".replace(".", ","))
    df_keywords_grouped['Taxa Conv.'] = df_keywords_grouped['Taxa Conv.'].apply(lambda x: f"{x:.2f}%".replace(".", ","))
    
    # Renomear colunas
    df_keywords_grouped = df_keywords_grouped.rename(columns={
        'keyword': 'Keyword',
        'match_type': 'Tipo de Correspondência',
        'cost': 'Investimento',
        'impressions': 'Impressões',
        'clicks': 'Cliques',
        'transactions': 'Vendas',
        'revenue': 'Receita'
    })
    
    # Exibir tabela
    st.dataframe(
        df_keywords_grouped,
        use_container_width=True,
        hide_index=True
    )

def display_tab_paid_media():
    """Exibe a aba de mídia paga"""
    
    # Criar abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Meta Ads", "Google Ads Keywords"])
    
    with tab1:
        display_general_view(load_paid_media())
    
    with tab2:
        display_meta_ads_analysis()
    
    with tab3:
        display_google_ads_keywords()

def display_campaign_table(df):
    """Exibe tabela de campanhas com formatação adequada"""
    df = df.sort_values('purchase_value', ascending=False)
    
    # Lista de colunas disponíveis
    available_columns = [
        'campaign_name',  # Nome da campanha
        'impressions', 'clicks',  # Métricas de alcance
        'purchases', 'last_session_transactions', 'leads',  # Vendas e Leads
        'spend', 'purchase_value', 'last_session_revenue',  # Receita
        'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
        'CPC', 'CPM', 'CPV', 'CPL',  # Custos
        'ROAS', 'ROAS Última Sessão',  # ROAS
    ]
    
    # Filtrar apenas as colunas que existem no DataFrame
    columns_to_display = [col for col in available_columns if col in df.columns]
    
    st.data_editor(
        df[columns_to_display].rename(columns={
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
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
        }),
        hide_index=True,
        use_container_width=True
    )

def display_adset_table(df):
    """Exibe tabela de conjuntos de anúncios com formatação adequada"""
    df = df.sort_values('purchase_value', ascending=False)
    
    # Lista de colunas disponíveis
    available_columns = [
        'adset_name',  # Nome do conjunto de anúncios
        'impressions', 'clicks',  # Métricas de alcance
        'purchases', 'last_session_transactions', 'leads',  # Vendas
        'spend', 'purchase_value', 'last_session_revenue',  # Receita
        'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
        'CPC', 'CPM', 'CPV', 'CPL',  # Custos
        'ROAS', 'ROAS Última Sessão',  # ROAS
    ]
    
    # Filtrar apenas as colunas que existem no DataFrame
    columns_to_display = [col for col in available_columns if col in df.columns]
    
    st.data_editor(
        df[columns_to_display].rename(columns={
            'adset_name': 'Conjunto de Anúncios',
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
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
        }),
        hide_index=True,
        use_container_width=True
    )

def display_ad_table(df):
    """Exibe tabela de anúncios com formatação adequada"""
    df = df.sort_values('purchase_value', ascending=False)
    
    # Lista de colunas disponíveis
    available_columns = [
        'ad_name',  # Nome do anúncio
        'impressions', 'clicks',  # Métricas de alcance
        'purchases', 'last_session_transactions', 'leads',  # Vendas
        'spend', 'purchase_value', 'last_session_revenue',  # Receita
        'CTR', 'Taxa Conv.', 'Taxa Conv. Última Sessão',  # Taxas
        'CPC', 'CPM', 'CPV', 'CPL',  # Custos
        'ROAS', 'ROAS Última Sessão',  # ROAS
    ]
    
    # Filtrar apenas as colunas que existem no DataFrame
    columns_to_display = [col for col in available_columns if col in df.columns]
    
    st.data_editor(
        df[columns_to_display].rename(columns={
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
            'ROAS (Pixel)': '{:.2f}',
            'ROAS (Última Sessão)': '{:.2f}',
            'Taxa Conv. (Pixel)': '{:.2f}%',
            'Taxa Conv. (Última Sessão)': '{:.2f}%',
        }),
        hide_index=True,
        use_container_width=True
    )

    