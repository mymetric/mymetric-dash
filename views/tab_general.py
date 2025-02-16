import streamlit as st
import pandas as pd
import altair as alt

from modules.load_data import load_basic_data, apply_filters, load_paid_media, load_leads_popup
from modules.components import big_number_box
from views.partials.run_rate import display_run_rate
from views.partials.pendings import display_pendings
from views.partials.performance import display_performance
from views.partials.notices import display_notices
from streamlit_cookies_controller import CookieController


def big_numbers(df):

    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100 if df["Sessões"].sum() > 0 else 0
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (pedidos_pagos / pedidos) * 100 if total_receita_capturada > 0 else 0
    leads = load_leads_popup()

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
    
    if leads is not None and not leads.empty:
        with col4:
            big_number_box(
                f"{leads['E-mails'].sum():,.0f}".replace(",", "."), 
                "Leads",
                hint="Total de leads capturados via popup no período"
            )

    st.markdown("---")
    
    # Carrega dados de mídia paga
    df_paid = load_paid_media()

    if df_paid is not None and not df_paid.empty:
    
        total_investimento = df_paid["Investimento"].sum()
        receita = df_paid["Receita"].sum()
        investimento_google = df_paid[df_paid["Plataforma"] == "google_ads"]["Investimento"].sum()
        investimento_meta = df_paid[df_paid["Plataforma"] == "meta_ads"]["Investimento"].sum()
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

def tables(df):

    df['Data'] = pd.to_datetime(df['Data']).dt.date  # Converte para apenas a data (sem horas)
    df_grouped = df.groupby('Data').agg({'Sessões': 'sum', 'Receita Paga': 'sum'}).reset_index()

    # Cria o gráfico de Sessões com a cor #D1B1C8
    line_sessions = alt.Chart(df_grouped).mark_line(color='#D1B1C8', strokeWidth=3).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Sessões:Q', axis=alt.Axis(title='Sessões')),
        tooltip=['Data', 'Sessões']
    )

    # Cria o gráfico de Receita Paga com a cor #C5EBC3 e barras estilosas
    bar_receita = alt.Chart(df_grouped).mark_bar(color='#C5EBC3', size=25).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Receita Paga:Q', axis=alt.Axis(title='Receita Paga')),
        tooltip=['Data', 'Receita Paga']
    )
    # Combine os dois gráficos (linha e barras) com dois eixos Y e interatividade
    combined_chart = alt.layer(
        bar_receita,
        line_sessions
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Sessões e Receita por Dia',
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
                <span>Sessões</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 15px; background-color: #C5EBC3;"></div>
                <span>Receita Paga</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Tabela de Cluster de Origens
    st.header("Cluster de Origens")
    st.write("Modelo de atribuição padrão: último clique não direto.")
    
    with st.expander("ℹ️ Entenda os Clusters", expanded=False):
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
            
            🍪 **Perda de Cookies**
            - Sessões sem identificação de origem
            - Identificado por: origem=not captured
            
            ◻️ **Outros**
            - Outras combinações de origem/mídia não classificadas acima
            - Formato: origem/mídia
        """)
        
    aggregated_df = df.groupby(['Cluster']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    aggregated_df['Tx Conversão'] = (aggregated_df['Pedidos'] / aggregated_df['Sessões'] * 100).round(2).astype(str) + '%'
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="general_cluster_origens")

def display_tab_general():

    df = load_basic_data()
    df = apply_filters(df)
    
    display_pendings()
    display_performance()
    display_run_rate(df)

    big_numbers(df)
    tables(df)

    def set_cookies():
        controller = CookieController()
        if "authenticated" in st.session_state:
            max_age=8*60*60
            controller.set("mm_authenticated", st.session_state.authenticated, max_age = max_age)
            controller.set("mm_username", st.session_state.username, max_age = max_age)
            controller.set("mm_tablename", st.session_state.tablename, max_age = max_age)
            controller.set("mm_admin", st.session_state.admin, max_age = max_age)

    set_cookies()