import altair as alt
import pandas as pd
import streamlit as st

def create_session_orders_chart(df):
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df_grouped = df.groupby('Data').agg({'Sessões': 'sum', 'Pedidos': 'sum'}).reset_index()

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

    combined_chart = alt.layer(
        line_sessions, line_pedidos
    ).resolve_scale(
        y='independent'
    )

    st.altair_chart(combined_chart, use_container_width=True)
