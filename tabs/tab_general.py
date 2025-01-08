import streamlit as st
from helpers import components
import altair as alt
import pandas as pd
from filters import date_filters, traffic_filters
from datetime import datetime, date
from helpers.config import load_table_metas
from helpers.notices import initialize_notices, show_new_year_notice, show_feature_notices
import calendar
from tabs.tab_today import calculate_daily_goal, format_currency, create_progress_bar
from google.cloud import bigquery
from google.oauth2 import service_account

def display_tab_general(df, tx_cookies, df_ads, username, start_date, end_date, **filters):
    # Carregar as metas do usuário
    metas = load_table_metas(username)
    current_month = datetime.now().strftime("%Y-%m")
    meta_receita = float(metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0))
    
    df = traffic_filters(df, **filters)
    
    # Inicializa e mostra os notices
    initialize_notices()
    current_date = date.today()
    
    if current_date <= date(2025, 1, 15):
        show_new_year_notice(username)
    
    show_feature_notices(username, meta_receita)

    # Calcular métricas gerais
    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100 if df["Sessões"].sum() > 0 else 0
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (total_receita_paga / total_receita_capturada) * 100 if total_receita_capturada > 0 else 0

    # Verificar pendências
    pendencias = []
    
    # Verificar meta do mês
    if meta_receita == 0:
        pendencias.append({
            'titulo': 'Cadastrar Meta do Mês',
            'descricao': 'A meta de receita do mês não está cadastrada. Isso é importante para acompanhar seu desempenho.',
            'acao': 'Acesse a aba Configurações para cadastrar sua meta mensal.',
            'severidade': 'alta'
        })
    
    # Verificar taxa de perda de cookies
    if tx_cookies > 10:
        pendencias.append({
            'titulo': 'Ajustar Taxa de Perda de Cookies',
            'descricao': f'A taxa de perda de cookies está em {tx_cookies:.1f}%. O ideal é manter abaixo de 10%.',
            'acao': 'Verifique a implementação do código de rastreamento e possíveis bloqueadores.',
            'severidade': 'media' if tx_cookies <= 30 else 'alta'
        })
    
    # Verificar tagueamento do Meta Ads
    if not df_ads.empty:
        #Query para verificar cobertura do mm_ads
        qa = f"""
            select
                sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`
            from `mymetric-hub-shopify.dbt_join.{username}_sessions_gclids`
            where
                event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
                and page_params like "%fbclid%"
        """
        
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        
        df_qa = client.query(qa).to_dataframe()
        if not df_qa.empty:
            cobertura = float(df_qa['Cobertura'].iloc[0]) * 100
            if cobertura < 80:
                pendencias.append({
                    'titulo': 'Ajustar Taxa de Tagueamento Meta Ads',
                    'descricao': f'A cobertura do parâmetro mm_ads está em {cobertura:.1f}%. O ideal é manter acima de 80%.',
                    'acao': f'Verifique a implementação do parâmetro mm_ads no Meta Ads. <a href="https://mymetric.notion.site/Parametriza-o-de-Meta-Ads-a32df743c4e046ccade33720f0faec3a" target="_blank" style="color: #0366d6; text-decoration: none;">Saiba como implementar corretamente</a>',
                    'severidade': 'media'
                })
    
    # Exibir pendências se houver
    if pendencias:
        st.markdown("""
            <style>
                .pendencia-alta { border-left: 4px solid #dc3545 !important; }
                .pendencia-media { border-left: 4px solid #ffc107 !important; }
                .pendencia-baixa { border-left: 4px solid #17a2b8 !important; }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-bottom: 25px;">
                <h3 style="color: #31333F; margin-bottom: 15px;">⚠️ Pendências</h3>
        """, unsafe_allow_html=True)
        
        for p in pendencias:
            st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    border: 1px solid #eee;
                    border-left: 4px solid #dc3545;
                " class="pendencia-{p['severidade']}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #31333F;">{p['titulo']}</strong>
                        <span style="
                            background-color: {'#dc3545' if p['severidade'] == 'alta' else '#ffc107' if p['severidade'] == 'media' else '#17a2b8'};
                            color: white;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 0.8em;
                        ">
                            {p['severidade'].upper()}
                        </span>
                    </div>
                    <p style="margin: 8px 0; color: #666;">{p['descricao']}</p>
                    <p style="margin: 0; color: #31333F; font-size: 0.9em;">
                        <strong>Ação necessária:</strong> {p['acao']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Add progress bar for meta only if we're looking at the current month
    first_day_current_month = current_date.replace(day=1)
    
    # Check if the selected date range matches current month
    is_current_month = (start_date == first_day_current_month and end_date == current_date)
    
    if meta_receita > 0 and is_current_month:
        dias_passados = current_date.day
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        meta_proporcional = meta_receita * (dias_passados / last_day)
        percentual_meta = (total_receita_paga / meta_proporcional) * 100 if meta_proporcional > 0 else 0
        
        st.header("Run Rate")

        # Calcula a projeção de fechamento do mês
        receita_projetada = total_receita_paga * (last_day / dias_passados) if dias_passados > 0 else 0
        
        # Calcula a probabilidade de atingir a meta
        media_diaria = total_receita_paga / dias_passados if dias_passados > 0 else 0
        dias_restantes = last_day - dias_passados
        valor_faltante = meta_receita - total_receita_paga
        valor_necessario_por_dia = valor_faltante / dias_restantes if dias_restantes > 0 else float('inf')
        
        # Calcula a probabilidade baseada na diferença entre a média diária atual e a necessária
        if valor_faltante <= 0:
            probabilidade = 100  # Já atingiu a meta
            mensagem_probabilidade = "🎉 Meta atingida! Continue o ótimo trabalho!"
            cor_probabilidade = "#28a745"
        elif dias_restantes == 0:
            if valor_faltante > 0:
                probabilidade = 0
                mensagem_probabilidade = "⚠️ Tempo esgotado para este mês"
                cor_probabilidade = "#dc3545"
            else:
                probabilidade = 100
                mensagem_probabilidade = "🎉 Meta atingida! Continue o ótimo trabalho!"
                cor_probabilidade = "#28a745"
        else:
            # Quanto maior a média diária em relação ao necessário, maior a probabilidade
            razao = media_diaria / valor_necessario_por_dia if valor_necessario_por_dia > 0 else 0
            probabilidade = min(100, razao * 100)
            
            # Define a mensagem baseada na faixa de probabilidade
            if probabilidade >= 80:
                mensagem_probabilidade = "🚀 Excelente ritmo! Você está muito próximo de atingir a meta!"
                cor_probabilidade = "#28a745"
            elif probabilidade >= 60:
                mensagem_probabilidade = "💪 Bom progresso! Continue focado que a meta está ao seu alcance!"
                cor_probabilidade = "#17a2b8"
            elif probabilidade >= 40:
                mensagem_probabilidade = "⚡ Momento de intensificar! Aumente as ações de marketing e vendas!"
                cor_probabilidade = "#ffc107"
            elif probabilidade >= 20:
                mensagem_probabilidade = "🎯 Hora de agir! Revise suas estratégias e faça ajustes!"
                cor_probabilidade = "#fd7e14"
            else:
                mensagem_probabilidade = "🔥 Alerta! Momento de tomar ações urgentes para reverter o cenário!"
                cor_probabilidade = "#dc3545"

        st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; color: #666;">
                    <p style="margin: 0;">Meta do Mês: R$ {meta_receita:,.2f}</p>
                    <p style="margin: 0;">Projeção: R$ {receita_projetada:,.2f} ({(receita_projetada/meta_receita*100):.1f}% da meta)</p>
                </div>
                <div style="width: 100%; background-color: #f0f2f6; border-radius: 10px;">
                    <div style="width: {min(percentual_meta, 100)}%; height: 20px; background-color: {'#28a745' if percentual_meta >= 100 else '#dc3545' if percentual_meta < 80 else '#17a2b8'}; 
                         border-radius: 10px; text-align: center; color: white; line-height: 20px;">
                        {percentual_meta:.1f}%
                    </div>
                </div>
                <div style="
                    margin-top: 15px;
                    padding: 15px;
                    border-radius: 10px;
                    background-color: {cor_probabilidade}15;
                    border: 1px solid {cor_probabilidade};
                ">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 8px;
                    ">
                        <strong style="color: {cor_probabilidade};">Probabilidade de atingir a meta</strong>
                        <span style="
                            background-color: {cor_probabilidade};
                            color: white;
                            padding: 4px 12px;
                            border-radius: 15px;
                            font-weight: bold;
                        ">{probabilidade:.1f}%</span>
                    </div>
                    <p style="
                        margin: 0;
                        color: {cor_probabilidade};
                        font-size: 0.95em;
                    ">{mensagem_probabilidade}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Adiciona explicação detalhada do Run Rate
        with st.expander("ℹ️ Como o Run Rate é calculado?"):
            st.markdown(f"""
                ### Cálculo do Run Rate

                O Run Rate é uma forma de avaliar se você está no caminho certo para atingir sua meta mensal, considerando o número de dias que já se passaram no mês.
                
                **Dados do cálculo atual:**
                - Meta do mês: R$ {meta_receita:,.2f}
                - Dias passados: {dias_passados} de {last_day} dias
                - Proporção do mês: {(dias_passados/last_day*100):.1f}%
                - Meta proporcional: R$ {meta_proporcional:,.2f}
                - Receita realizada: R$ {total_receita_paga:,.2f}
                - Percentual atingido: {percentual_meta:.1f}%
                - Probabilidade de atingir a meta: {probabilidade:.1f}%

                **Como interpretar:**
                - Se o percentual for 100%, você está exatamente no ritmo para atingir a meta
                - Acima de 100% significa que está acima do ritmo necessário
                - Abaixo de 100% indica que precisa acelerar as vendas para atingir a meta

                **Faixas de Probabilidade:**
                - 🟢 80-100%: Excelente chance de atingir a meta
                - 🔵 60-79%: Boa chance, mantenha o foco
                - 🟡 40-59%: Chance moderada, intensifique as ações
                - 🟠 20-39%: Chance baixa, momento de revisar estratégias
                - 🔴 0-19%: Chance muito baixa, ações urgentes necessárias

                **Exemplo:**
                Se sua meta é R$ 100.000 e já se passaram 15 dias de um mês com 30 dias:
                1. Meta proporcional = R$ 100.000 × (15/30) = R$ 50.000
                2. Se você faturou R$ 60.000, seu Run Rate é 120% (acima do necessário)
                3. Se faturou R$ 40.000, seu Run Rate é 80% (precisa acelerar)
            """)

            # Adiciona projeção de fechamento
            receita_projetada = total_receita_paga * (last_day / dias_passados)
            st.markdown(f"""
                ### Projeção de Fechamento

                Mantendo o ritmo atual de vendas:
                - Projeção de receita: R$ {receita_projetada:,.2f}
                - Percentual da meta: {(receita_projetada/meta_receita*100):.1f}%
                - {'🎯 Meta será atingida!' if receita_projetada >= meta_receita else '⚠️ Meta não será atingida no ritmo atual'}
                
                {f'Faltam R$ {(meta_receita - receita_projetada):,.2f} para atingir a meta no ritmo atual.' if receita_projetada < meta_receita else ''}
            """)

    st.header("Big Numbers")
    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        components.big_number_box(
            f"{pedidos:,.0f}".replace(",", "."), 
            "Pedidos Capturados",
            hint="Total de pedidos registrados no período, incluindo pagos e não pagos"
        )
    
    with col2:
        components.big_number_box(
            f"{pedidos_pagos:,.0f}".replace(",", "."), 
            "Pedidos Pagos",
            hint="Total de pedidos que foram efetivamente pagos no período"
        )

    with col3:
        components.big_number_box(
            f"R$ {total_receita_capturada:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita Capturada",
            hint="Valor total dos pedidos capturados, incluindo pagos e não pagos"
        )

    with col4:
        components.big_number_box(
            f"R$ {total_receita_paga:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita Paga",
            hint="Valor total dos pedidos que foram efetivamente pagos. Fórmula: Valor Total com Status Pago - Descontos + Frete"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        components.big_number_box(
            f"{sessoes:,.0f}".replace(",", "."), 
            "Sessões",
            hint="Número total de visitas ao site no período selecionado"
        )

    with col2:
        components.big_number_box(
            f"{tx_conv:.2f}".replace(".", ",") + "%", 
            "Tx Conversão",
            hint="Percentual de sessões que resultaram em pedidos (Pedidos/Sessões)"
        )

    with col3:
        components.big_number_box(
            f"{tx_cookies:.2f}".replace(".", ",") + "%", 
            "Tx Perda de Cookies Hoje",
            hint="Percentual de sessões sem identificação de origem devido à perda de cookies. Ideal manter abaixo de 10%"
        )

    with col4:
        components.big_number_box(
            f"{percentual_pago:.1f}%", 
            "% Receita Paga/Capturada",
            hint="Percentual da receita total capturada que foi efetivamente paga"
        )
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(
                f"R$ {round(df_ads['Investimento'].sum(),2):,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
                "Investimento Total em Ads",
                hint="Soma do investimento em todas as plataformas de mídia paga (Google Ads + Meta Ads)"
            )
    with col2:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(
                f"{(df_ads['Investimento'].sum() / total_receita_paga) * 100:.2f}".replace(".", ",") + "%", 
                "TACoS",
                hint="Total Advertising Cost of Sales - Percentual do faturamento gasto em publicidade"
            )

    # Filtra os dados para a plataforma google_ads
    if not df_ads.empty:
        df_google_ads = df_ads[df_ads['Plataforma'] == 'google_ads']
        df_meta_ads = df_ads[df_ads['Plataforma'] == 'meta_ads']

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_google_ads.empty and df_google_ads['Investimento'].sum() > 0:
            with col3:
                gads_connect_rate = df[df['Cluster'] == "🟢 Google Ads"]["Sessões"].sum()/df_ads[df_ads['Plataforma'] =="google_ads"]["Cliques"].sum()*100
                components.big_number_box(
                    f"{gads_connect_rate:.1f}%", 
                    "Connect Rate Google Ads",
                    hint="Percentual de cliques do Google Ads que foram corretamente atribuídos como sessões. Ideal manter acima de 80%"
                )

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_meta_ads.empty and df_meta_ads['Investimento'].sum() > 0:
            with col4:
                # Calcula o connect rate do Meta Ads
                meta_ads_sessions = df[df['Cluster'] == "🔵 Meta Ads"]["Sessões"].sum()
                meta_ads_clicks = df_ads[df_ads['Plataforma'] == "meta_ads"]["Cliques"].sum()
                mads_connect_rate = (meta_ads_sessions / meta_ads_clicks * 100) if meta_ads_clicks > 0 else 0

                # Formata e exibe o investimento em Meta Ads
                meta_ads_investment = round(df_meta_ads['Investimento'].sum(), 2)
                components.big_number_box(
                    f"{mads_connect_rate:.1f}%", 
                    "Connect Rate Meta Ads",
                    hint="Percentual de cliques do Meta Ads que foram corretamente atribuídos como sessões. Ideal manter acima de 80%"
                )

    st.markdown("---")

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

    # Adiciona interatividade de zoom e pan
    zoom_pan = alt.selection_interval(bind='scales')

    # Combine os dois gráficos (linha e barras) com dois eixos Y e interatividade
    combined_chart = alt.layer(
        bar_receita,
        line_sessions
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    ).add_selection(
        zoom_pan  # Adiciona a interação de zoom e pan
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
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    # Tabela de Origem e Mídia
    st.header("Origem e Mídia")
    
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({
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
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    # Tabela de Campanhas
    st.header("Campanhas")
    
    campaigns = df.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    campaigns['Tx Conversão'] = (campaigns['Pedidos'] / campaigns['Sessões'] * 100).round(2).astype(str) + '%'
    campaigns['% Receita'] = ((campaigns['Receita'] / campaigns['Receita'].sum()) * 100).round(2).astype(str) + '%'
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

    # Tabela de Conteúdo
    st.header("Conteúdo")
    st.write("Valor do utm_content.")
    
    conteudo = df.groupby(['Conteúdo']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    conteudo['Tx Conversão'] = (conteudo['Pedidos'] / conteudo['Sessões'] * 100).round(2).astype(str) + '%'
    conteudo['% Receita'] = ((conteudo['Receita'] / conteudo['Receita'].sum()) * 100).round(2).astype(str) + '%'
    conteudo = conteudo.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(conteudo, hide_index=1, use_container_width=1)

    # Tabela de Página de Entrada
    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão
    pagina_de_entrada['Tx Conversão'] = (pagina_de_entrada['Pedidos'] / pagina_de_entrada['Sessões'] * 100).round(2).astype(str) + '%'
    pagina_de_entrada['% Receita'] = ((pagina_de_entrada['Receita'] / pagina_de_entrada['Receita'].sum()) * 100).round(2).astype(str) + '%'
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)

    
    conv_rate = df
    # Adiciona coluna de dia da semana
    conv_rate['Dia da Semana'] = pd.to_datetime(conv_rate['Data']).dt.day_name()
    
    # Agrupa por dia da semana e hora
    conv_rate = conv_rate.groupby(['Dia da Semana', 'Hora']).agg({
        'Sessões': 'sum',
        'Pedidos': 'sum'
    }).reset_index()
    
    # Calcula taxa de conversão
    conv_rate['Taxa de Conversão'] = (conv_rate['Pedidos'] / conv_rate['Sessões'] * 100).round(2)
    # Pivota a tabela para criar a matriz
    conv_rate_matrix = conv_rate.pivot(
        index='Hora',
        columns='Dia da Semana',
        values='Taxa de Conversão'
    )
    
    # Reordena os dias da semana emportuguês
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
    
    # Cria o heatmap usando Altair com um design mais limpo
    heatmap = alt.Chart(conv_rate).mark_rect().encode(
        x=alt.X('Dia da Semana:N', 
                title=None,  # Remove título do eixo X
                sort=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']),
        y=alt.Y('Hora:O', 
                title=None,  # Remove título do eixo Y
                sort=list(range(24))),
        color=alt.Color('Taxa de Conversão:Q',
                       scale=alt.Scale(scheme='greens'),  # Usa tons de verde
                       legend=alt.Legend(
                           orient='right',
                           title='Taxa de Conversão (%)',
                           gradientLength=300
                       )),
        tooltip=[
            alt.Tooltip('Dia da Semana:N', title='Dia'),
            alt.Tooltip('Hora:O', title='Hora'),
            alt.Tooltip('Taxa de Conversão:Q', title='Taxa de Conversão', format='.2f'),
            alt.Tooltip('Sessões:Q', title='Sessões', format=','),
            alt.Tooltip('Pedidos:Q', title='Pedidos', format=',')
        ]
    ).properties(
        width=650,
        height=500
    ).configure_view(
        strokeWidth=0,  # Remove borda
    ).configure_axis(
        labelFontSize=11,
        grid=False,  # Remove grid
        domain=False  # Remove linhas dos eixos
    ).configure_legend(
        labelFontSize=11,
        titleFontSize=12,
        padding=10
    )

    # Adiciona espaço em branco para melhor alinhamento
    st.write("")
    
    # Exibe o heatmap
    st.altair_chart(heatmap, use_container_width=True)