import streamlit as st
from modules.load_data import load_detailed_data
import pandas as pd
import altair as alt

def tables_detailed(df):

    st.title("💼 Visão Detalhada")
    st.markdown("""---""")

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
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    aggregated_df['Tx Conversão'] = aggregated_df.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = aggregated_df['Receita'].sum()
    if total_receita > 0:
        aggregated_df['% Receita'] = aggregated_df.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        aggregated_df['% Receita'] = '0%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="detailed_cluster_origens")

    # tables(df)
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
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    aggregated_df['Tx Conversão'] = aggregated_df.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = aggregated_df['Receita'].sum()
    if total_receita > 0:
        aggregated_df['% Receita'] = aggregated_df.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        aggregated_df['% Receita'] = '0%'
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="detailed_origem_midia")

    # Tabela de Campanhas
    st.header("Campanhas")
    
    campaigns = df.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    campaigns['Tx Conversão'] = campaigns.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = campaigns['Receita'].sum()
    if total_receita > 0:
        campaigns['% Receita'] = campaigns.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        campaigns['% Receita'] = '0%'
    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(campaigns, hide_index=1, use_container_width=1, key="detailed_campanhas")

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
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    conteudo['Tx Conversão'] = conteudo.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = conteudo['Receita'].sum()
    if total_receita > 0:
        conteudo['% Receita'] = conteudo.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        conteudo['% Receita'] = '0%'
    conteudo = conteudo.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(conteudo, hide_index=1, use_container_width=1, key="detailed_conteudo")

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
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    pagina_de_entrada['Tx Conversão'] = pagina_de_entrada.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = pagina_de_entrada['Receita'].sum()
    if total_receita > 0:
        pagina_de_entrada['% Receita'] = pagina_de_entrada.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        pagina_de_entrada['% Receita'] = '0%'
    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1, key="detailed_pagina_entrada")

    # Tabela de Cupons
    st.header("Cupons")
    st.write("Análise dos cupons utilizados nos pedidos")
    
    cupons = df.groupby(['Cupom']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Pedidos Primeiro Clique': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    cupons['Tx Conversão'] = cupons.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula percentual de receita com tratamento para divisão por zero
    total_receita = cupons['Receita'].sum()
    if total_receita > 0:
        cupons['% Receita'] = cupons.apply(
            lambda x: f"{((x['Receita'] / total_receita) * 100):.2f}%",
            axis=1
        )
    else:
        cupons['% Receita'] = '0%'
    cupons = cupons.sort_values(by='Pedidos', ascending=False)
    
    st.data_editor(cupons, hide_index=1, use_container_width=1, key="detailed_cupons")

def display_tab_detailed():

    df = load_detailed_data()
    tables_detailed(df)