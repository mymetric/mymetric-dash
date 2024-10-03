import altair as alt
import pandas as pd
import streamlit as st

def display_charts(df):
    df['Data'] = pd.to_datetime(df['Data']).dt.date  # Converte para apenas a data (sem horas)
    df_grouped = df.groupby('Data').agg({'Sessões': 'sum', 'Receita Paga': 'sum'}).reset_index()

    # Cria o gráfico de Sessões e Pedidos com eixo Y secundário usando Altair
    line_sessions = alt.Chart(df_grouped).mark_line(color='#56E39F', point=alt.OverlayMarkDef(color="#56E39F")).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Sessões:Q', axis=alt.Axis(title='Sessões', titleColor='#56E39F')),
        tooltip=['Data', 'Sessões']
    ).properties(
        width=600,
        title='Sessões e Pedidos por Dia' 
    )

    line_pedidos = alt.Chart(df_grouped).mark_line(color='#5BC0EB', point=alt.OverlayMarkDef(color="#5BC0EB")).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Receita Paga:Q', axis=alt.Axis(title='Receita Paga', titleColor='#5BC0EB')),
        tooltip=['Data', 'Receita Paga']
    )

    # Adiciona interatividade de zoom e pan
    zoom_pan = alt.selection_interval(bind='scales')

    # Combine as duas linhas com dois eixos Y e interatividade
    combined_chart = alt.layer(
        line_sessions,
        line_pedidos
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    ).add_selection(
        zoom_pan  # Adiciona a interação de zoom e pan
    ).properties(
        title=alt.TitleParams(
            text='Sessões e Pedidos por Dia',
            fontSize=16,
            anchor='middle'
        )
    )

    # Exibe o gráfico no Streamlit
    st.altair_chart(combined_chart, use_container_width=True)

# Exemplo de chamada da função com um DataFrame
# df = pd.read_csv('caminho/para/seus_dados.csv')
# display_charts(df)
