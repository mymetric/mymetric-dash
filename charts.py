import altair as alt
import pandas as pd
import streamlit as st

def display_charts(df):
    df['Data'] = pd.to_datetime(df['Data']).dt.date  # Converte para apenas a data (sem horas)
    df_grouped = df.groupby('Data').agg({'Sessões': 'sum', 'Pedidos': 'sum'}).reset_index()

    # Cria o gráfico de Sessões e Pedidos com eixo Y secundário usando Altair
    line_sessions = alt.Chart(df_grouped).mark_line(color='blue').encode(
        x='Data:T',
        y=alt.Y('Sessões:Q', axis=alt.Axis(title='Sessões', titleColor='blue')),
        tooltip=['Data', 'Sessões']
    ).properties(
        width=600,
        title='Sessões e Pedidos por Dia'
    )

    line_pedidos = alt.Chart(df_grouped).mark_line(color='green').encode(
        x='Data:T',
        y=alt.Y('Pedidos:Q', axis=alt.Axis(title='Pedidos', titleColor='green')),
        tooltip=['Data', 'Pedidos']
    )

    # Combine as duas linhas com dois eixos Y
    combined_chart = alt.layer(
        line_sessions,
        line_pedidos
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    )

    # Exibe o gráfico no Streamlit
    st.altair_chart(combined_chart, use_container_width=True)
