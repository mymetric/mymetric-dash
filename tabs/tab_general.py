import streamlit as st
import pandas as pd
import altair as alt

from modules.load_data import load_basic_data, apply_filters, load_paid_media, load_leads_popup, load_costs
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

    # Tabela de Cálculo de ROI
    # Carregar custos
    costs_df = load_costs()
    
    if not costs_df.empty:
        st.header("Cálculo de ROI")
        
        # Fazer left join com os custos
        # Primeiro, vamos pegar o mês mais recente dos custos
        latest_month = costs_df['Mês'].max()
        
        # Filtrar custos apenas do mês mais recente
        latest_costs = costs_df[costs_df['Mês'] == latest_month]
        
        # Fazer o left join
        merged_df = pd.merge(
            aggregated_df[['Cluster', 'Receita']],
            latest_costs[['Categoria', 'Custo do Produto (%)', 'Custo Total']],
            left_on='Cluster',
            right_on='Categoria',
            how='left'
        )
        
        # Remover a coluna Categoria duplicada
        if 'Categoria' in merged_df.columns:
            merged_df = merged_df.drop('Categoria', axis=1)
        
        # Preencher valores nulos com 0
        merged_df['Custo do Produto (%)'] = merged_df['Custo do Produto (%)'].fillna(0)
        merged_df['Custo Total'] = merged_df['Custo Total'].fillna(0)
        
        # Calcular Custo do Produto Absoluto
        merged_df['Custo do Produto Absoluto'] = merged_df['Receita'] * (merged_df['Custo do Produto (%)'] / 100)
        
        # Calcular Custo Geral
        merged_df['Custo Geral'] = merged_df['Custo Total'] + merged_df['Custo do Produto Absoluto']
        
        # Calcular Retorno Absoluto
        merged_df['Retorno Absoluto'] = merged_df['Receita'] - merged_df['Custo Total'] - merged_df['Custo do Produto Absoluto']
        
        # Calcular ROI considerando Custo Total e Custo do Produto Absoluto
        merged_df['ROI'] = ((merged_df['Receita'] - merged_df['Custo Total'] - merged_df['Custo do Produto Absoluto']) / (merged_df['Custo Total'] + merged_df['Custo do Produto Absoluto']) * 100).fillna(0)
        
        # Formatar os números antes de exibir
        display_df = merged_df.copy()
        display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        display_df['Custo Total'] = display_df['Custo Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        display_df['Custo do Produto Absoluto'] = display_df['Custo do Produto Absoluto'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        display_df['Custo Geral'] = display_df['Custo Geral'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        display_df['Retorno Absoluto'] = display_df['Retorno Absoluto'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        display_df['Custo do Produto (%)'] = display_df['Custo do Produto (%)'].apply(lambda x: f"{x:.1f}%")
        
        # Formatar ROI substituindo inf% por "-" ou "0"
        display_df['ROI'] = display_df['ROI'].apply(lambda x: "-" if pd.isna(x) or x == float('inf') else f"{x:.1f}%")
        
        # Reordenar as colunas
        display_df = display_df[['Cluster', 'Receita', 'Custo do Produto (%)', 'Custo do Produto Absoluto', 'Custo Total', 'Custo Geral', 'Retorno Absoluto', 'ROI']]
        
        st.data_editor(display_df, hide_index=1, use_container_width=True, key="general_costs")

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