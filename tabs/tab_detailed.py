import streamlit as st
from modules.load_data import load_detailed_data
import pandas as pd
import altair as alt

def tables_detailed(df):

    st.title("Visão Detalhada")
    st.markdown("""---""")

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
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    aggregated_df['Tx Conversão'] = aggregated_df.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    aggregated_df['RPS'] = aggregated_df.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = aggregated_df['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        aggregated_df['Tx Adições ao Carrinho'] = aggregated_df.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        aggregated_df['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = aggregated_df.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Cluster', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_cluster_origens")

    # Tabela de Origem e Mídia
    st.header("Origem e Mídia")
    
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    aggregated_df['Tx Conversão'] = aggregated_df.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    aggregated_df['RPS'] = aggregated_df.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = aggregated_df['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        aggregated_df['Tx Adições ao Carrinho'] = aggregated_df.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        aggregated_df['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = aggregated_df.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Origem', 'Mídia', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_origem_midia")

    # Tabela de Campanhas
    st.header("Campanhas")
    
    campaigns = df.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    campaigns['Tx Conversão'] = campaigns.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    campaigns['RPS'] = campaigns.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = campaigns['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        campaigns['Tx Adições ao Carrinho'] = campaigns.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        campaigns['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = campaigns.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Campanha', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_campanhas")

    # Tabela de Conteúdo
    st.header("Conteúdo")
    st.write("Valor do utm_content.")
    
    conteudo = df.groupby(['Conteúdo']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    conteudo['Tx Conversão'] = conteudo.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    conteudo['RPS'] = conteudo.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = conteudo['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        conteudo['Tx Adições ao Carrinho'] = conteudo.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        conteudo['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = conteudo.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Conteúdo', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_conteudo")

    # Tabela de Página de Entrada
    st.header("Página de Entrada")
    st.write("Página por onde o usuário iniciou a sessão")
    
    pagina_de_entrada = df.groupby(['Página de Entrada']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    pagina_de_entrada['Tx Conversão'] = pagina_de_entrada.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    pagina_de_entrada['RPS'] = pagina_de_entrada.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = pagina_de_entrada['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        pagina_de_entrada['Tx Adições ao Carrinho'] = pagina_de_entrada.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        pagina_de_entrada['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = pagina_de_entrada.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Página de Entrada', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_pagina_entrada")

    # Tabela de Cupons
    st.header("Cupons")
    st.write("Análise dos cupons utilizados nos pedidos")
    
    cupons = df.groupby(['Cupom']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum',
        'Adições ao Carrinho': 'sum'
    }).reset_index()
    
    # Adiciona coluna de taxa de conversão com tratamento para divisão por zero
    cupons['Tx Conversão'] = cupons.apply(
        lambda x: f"{(x['Pedidos'] / x['Sessões'] * 100):.2f}%" if x['Sessões'] > 0 else "0%",
        axis=1
    )
    
    # Calcula RPS (Receita por Sessão) com tratamento para divisão por zero
    cupons['RPS'] = cupons.apply(
        lambda x: f"R$ {(x['Receita Paga'] / x['Sessões']):.2f}".replace(".", ",") if x['Sessões'] > 0 else "R$ 0,00",
        axis=1
    )
    
    # Calcula percentual de adições ao carrinho com tratamento para divisão por zero
    total_adicoes = cupons['Adições ao Carrinho'].sum()
    if total_adicoes > 0:
        cupons['Tx Adições ao Carrinho'] = cupons.apply(
            lambda x: f"{((x['Adições ao Carrinho'] / total_adicoes) * 100):.2f}%",
            axis=1
        )
    else:
        cupons['Tx Adições ao Carrinho'] = '0%'
    
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
    
    # Formatar os números antes de exibir
    display_df = cupons.copy()
    display_df['Sessões'] = display_df['Sessões'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Adições ao Carrinho'] = display_df['Adições ao Carrinho'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos'] = display_df['Pedidos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Pedidos Pagos'] = display_df['Pedidos Pagos'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    display_df['Receita'] = display_df['Receita'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    display_df['Receita Paga'] = display_df['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    
    # Reordenar as colunas
    display_df = display_df[['Cupom', 'Sessões', 'Adições ao Carrinho', 'Tx Adições ao Carrinho', 'Pedidos', 'Tx Conversão', 'Pedidos Pagos', 'Receita', 'Receita Paga', 'RPS', '% Receita']]
    
    st.data_editor(display_df, hide_index=1, use_container_width=1, key="detailed_cupons")

def display_tab_detailed():

    df = load_detailed_data()
    tables_detailed(df)