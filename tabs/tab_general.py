import streamlit as st
from helpers import components
import altair as alt
import pandas as pd
from filters import date_filters, traffic_filters
from helpers.components import send_discord_message
from datetime import datetime, date
from helpers.config import load_table_metas
import calendar

def display_tab_general(df, tx_cookies, df_ads, username, start_date, end_date, **filters):
    # Carregar as metas do usuário
    metas = load_table_metas(username)
    current_month = datetime.now().strftime("%Y-%m")
    meta_receita = float(metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0))
    
    df = traffic_filters(df, **filters)
    
    current_date = date.today()
    if current_date <= date(2025, 1, 15):
        st.markdown("""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align:center">
                <h2 style="color:#666; margin:0">🎉 Feliz 2025, {username}!</h2>
                <p style="color:#666; margin:10px 0 0 0">Que este ano seja repleto de insights valiosos e métricas positivas. Boas análises! 📊</p>
            </div>
        """.format(username=username.upper()), unsafe_allow_html=True)

    # Verifica se já mostrou os avisos para este usuário nesta sessão
    if 'showed_meta_notice' not in st.session_state:
        st.session_state.showed_meta_notice = False
    if 'showed_today_notice' not in st.session_state:
        st.session_state.showed_today_notice = False

    if not st.session_state.showed_meta_notice and meta_receita == 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            ### 🎯 Configure suas Metas de Faturamento!
            
            Agora você pode definir e acompanhar suas metas mensais de receita.
            
            Para começar:
            1. Acesse a aba "⚙️ Configurações"
            2. Defina sua meta mensal
            3. Acompanhe o progresso aqui na aba "Visão Geral"
            
            Comece agora mesmo a trackear seus objetivos! 📈
            """)
            if st.button("Entendi!", key="meta_notice", type="primary"):
                st.session_state.showed_meta_notice = True
                st.rerun()

        with col2:
            st.info("""
            ### 📊 Nova Aba de Análise do Dia!
            
            Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
            
            Recursos disponíveis:
            - Acompanhamento hora a hora
            - Comparação com dias anteriores
            - Acompanhamento de meta diária
            
            Confira agora mesmo! 🚀
            """)
            if st.button("Entendi!", key="today_notice", type="primary"):
                st.session_state.showed_today_notice = True
                st.rerun()

    elif not st.session_state.showed_today_notice:
        st.info("""
        ### 📊 Nova Aba de Análise do Dia!
        
        Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
        
        Recursos disponíveis:
        - Acompanhamento hora a hora
        - Comparação com dias anteriores
        - Principais fontes de tráfego do dia
        
        Confira agora mesmo! 🚀
        """)
        if st.button("Entendi!", key="today_notice", type="primary"):
            st.session_state.showed_today_notice = True
            st.rerun()

    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100 if df["Sessões"].sum() > 0 else 0
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (total_receita_paga / total_receita_capturada) * 100 if total_receita_capturada > 0 else 0

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

                **Como interpretar:**
                - Se o percentual for 100%, você está exatamente no ritmo para atingir a meta
                - Acima de 100% significa que está acima do ritmo necessário
                - Abaixo de 100% indica que precisa acelerar as vendas para atingir a meta

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
            hint="Valor total dos pedidos que foram efetivamente pagos"
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
