import streamlit as st
import pandas as pd
import altair as alt

from modules.load_data import load_detailed_data

def display_tab_holysoup_social():
    st.title("Social")

    df = load_detailed_data()
    df = df[df['Cluster'] == '🟣 Social']

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

    # tables(df)
    # Tabela de Origem e Mídia
    st.header("Origem e Mídia")
    
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({
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
    
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1, key="detailed_origem_midia")

    # Tabela de Campanhas
    st.header("Campanhas")
    
    campaigns = df.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
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
    

