import altair as alt
import pandas as pd
import streamlit as st

def display_charts(df):
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

# Exemplo de chamada da função com um DataFrame
# df = pd.read_csv('caminho/para/seus_dados.csv')
# display_charts(df)
