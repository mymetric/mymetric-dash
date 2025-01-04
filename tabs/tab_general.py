import streamlit as st
from helpers import components
import altair as alt
import pandas as pd
from filters import date_filters, traffic_filters
from helpers.components import send_discord_message
from datetime import datetime, date

def display_tab_general(df, tx_cookies, df_ads, username,**filters):


    df = traffic_filters(df, **filters)

    
    current_date = date.today()
    if current_date <= date(2025, 1, 15):
        st.markdown("""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px; text-align:center">
                <h2 style="color:#666; margin:0">🎉 Feliz 2025, {username}!</h2>
                <p style="color:#666; margin:10px 0 0 0">Que este ano seja repleto de insights valiosos e métricas positivas. Boas análises! 📊</p>
            </div>
        """.format(username=username.upper()), unsafe_allow_html=True)

    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    tx_conv = (df["Pedidos"].sum()/df["Sessões"].sum())*100
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()
    percentual_pago = (total_receita_paga / total_receita_capturada) * 100

    st.header("Big Numbers")

    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        components.big_number_box(f"{pedidos:,.0f}".replace(",", "."), "Pedidos Capturados")
    
    with col2:
        components.big_number_box(f"{pedidos_pagos:,.0f}".replace(",", "."), "Pedidos Pagos")

    with col3:
        components.big_number_box(f"R$ {total_receita_capturada:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), "Receita Capturada")

    with col4:
        components.big_number_box(f"R$ {total_receita_paga:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), "Receita Paga")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        components.big_number_box(f"{sessoes:,.0f}".replace(",", "."), "Sessões")

    with col2:
        components.big_number_box(f"{tx_conv:.2f}".replace(".", ",") + "%", "Tx Conversão")

    with col3:
        components.big_number_box(f"{tx_cookies:.2f}".replace(".", ",") + "%", "Tx Perda de Cookies Hoje")

    with col4:
        components.big_number_box(f"{percentual_pago:.2f}".replace(".", ",") + "%", "% Pago")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(f"R$ {round(df_ads['Investimento'].sum(),2):,.2f}".replace(",", "."), "Investimento Total em Ads")
    with col2:
        # Exibe os dados da query_ads se houver resultado
        if not df_ads.empty and df_ads['Investimento'].sum() > 0:
            components.big_number_box(f"{(df_ads['Investimento'].sum() / total_receita_paga) * 100:.2f}".replace(".", ",") + "%", "TACoS")

    # Filtra os dados para a plataforma google_ads
    if not df_ads.empty:
        df_google_ads = df_ads[df_ads['Plataforma'] == 'google_ads']
        df_meta_ads = df_ads[df_ads['Plataforma'] == 'meta_ads']

        # Exibe o investimento total em Ads apenas se houver dados para google_ads
        if not df_google_ads.empty and df_google_ads['Investimento'].sum() > 0:
            with col3:
                gads_connect_rate = df[df['Cluster'] == "🟢 Google Ads"]["Sessões"].sum()/df_ads[df_ads['Plataforma'] =="google_ads"]["Cliques"].sum()*100
                components.big_number_box(
                    f"R$ {round(df_google_ads['Investimento'].sum(), 2):,}".replace(",", "."), 
                    "Investimento em Google Ads"
                )

                components.big_number_box(f"{gads_connect_rate:.1f}%", "Connect Rate Google Ads")

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
                    f"R$ {meta_ads_investment:,.2f}".replace(",", "."),
                    "Investimento em Meta Ads"
                )

                
                if mads_connect_rate < 80:
                    send_discord_message(f"Usuário **{username}** com Connect Rate do Meta Ads abaixo do esperado: {mads_connect_rate:.2f}%.")
                components.big_number_box(f"{mads_connect_rate:.1f}%", "Connect Rate Meta Ads")


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
        line_sessions,
        bar_receita
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






    aggregated_df = df.groupby(['Cluster']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Pedidos Pagos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Cluster de Origens")
    st.write("Modelo de atribuição padrão: último clique não direto.")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)


    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Pedidos Pagos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df['% Receita'] = ((aggregated_df['Receita'] / aggregated_df['Receita'].sum()) * 100).round(2).astype(str) + '%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Origem e Mídia")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    # Agrega os dados por Campanha
    campaigns = df.groupby(['Campanha']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    campaigns['% Receita'] = ((campaigns['Receita'] / campaigns['Receita'].sum()) * 100).round(2).astype(str) + '%'
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)

    st.header("Campanhas")
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

    # Agrega os dados por Conteúdo
    conteudo = df.groupby(['Conteúdo']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    conteudo['% Receita'] = ((conteudo['Receita'] / conteudo['Receita'].sum()) * 100).round(2).astype(str) + '%'
    conteudo = conteudo.sort_values(by='Pedidos', ascending=False)

    st.header("Conteúdo")
    st.write("Valor do utm_content.")
    st.data_editor(conteudo, hide_index=1, use_container_width=1)


    # Agrega os dados por Página de Entrada
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Pedidos Primeiro Clique': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    pagina_de_entrada['% Receita'] = ((pagina_de_entrada['Receita'] / pagina_de_entrada['Receita'].sum()) * 100).round(2).astype(str) + '%'
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)

    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)
