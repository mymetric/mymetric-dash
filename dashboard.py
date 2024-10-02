import streamlit as st
import pandas as pd
import altair as alt

# Função para executar a query
@st.cache_data(ttl=600)
def run_query(_client, query):
    query_job = _client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return rows

def show_dashboard(client):
    # Configuração inicial de datas
    today = pd.to_datetime("today").date()
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)

    # Variáveis para definir os valores das datas
    start_date = seven_days_ago
    end_date = today

    with st.sidebar:
        st.markdown(f"## {st.session_state.username.upper()}")

    # Filtro de datas interativo
    with st.sidebar.expander("Seleção de Datas", expanded=True):
        # Botões de datas predefinidas
        if st.button("Hoje"):
            start_date = today
            end_date = today
        if st.button("Últimos 7 Dias"):
            start_date = seven_days_ago
            end_date = today
        if st.button("Últimos 30 Dias"):
            start_date = thirty_days_ago
            end_date = today

        # Date pickers para selecionar manualmente as datas
        start_date = st.date_input("Data Inicial", start_date)
        end_date = st.date_input("Data Final", end_date)

    # Converte as datas para string no formato 'YYYY-MM-DD' para a query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Defina a tabela baseada no nome do usuário autenticado
    table = st.session_state.username

    # Query para buscar os dados com filtro de datas
    query = f"""
    SELECT
        event_date AS Data,
        source Origem,
        medium `Mídia`, 
        COUNTIF(event_name = 'session') `Sessões`,
        COUNT(DISTINCT transaction_id) Pedidos,
        SUM(value) Receita,
        SUM(CASE WHEN status = 'paid' THEN value ELSE 0 END) `Receita Paga`
    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY Data, source, medium
    ORDER BY Pedidos DESC
    """

    # Executa a query
    rows = run_query(client, query)

    # Converte os dados em DataFrame para fácil manipulação
    df = pd.DataFrame(rows)

    # Exibe a tabela sem numeração
    st.title("Visão Geral")

    # Filtros interativos de Origem e Mídia
    origem_options = df['Origem'].unique().tolist()
    midia_options = df['Mídia'].unique().tolist()

    # Multiselect para Origem e Mídia (comportamento semelhante a dropdown)
    with st.sidebar.expander("Filtros de Origem", expanded=False):
        origem_selected = st.multiselect('Selecionar Origem', origem_options, default=origem_options)

    with st.sidebar.expander("Filtros de Mídia", expanded=False):
        midia_selected = st.multiselect('Selecionar Mídia', midia_options, default=midia_options)

    # Aplica os filtros ao dataframe
    df_filtered = df[(df['Origem'].isin(origem_selected)) & (df['Mídia'].isin(midia_selected))]

    # Calcula os big numbers com base nos dados filtrados
    pedidos = df_filtered["Pedidos"].sum()
    total_receita_paga = df_filtered["Receita Paga"].sum()
    total_receita_capturada = df_filtered["Receita"].sum()

    # Exibe os valores filtrados de "Receita Paga", "Receita Capturada" e "Pedidos"
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pedidos", f"{pedidos}")

    with col2:
        st.metric("Receita Capturada", f"R$ {total_receita_capturada:,.2f}")

    with col3:
        st.metric("Receita Paga", f"R$ {total_receita_paga:,.2f}")

    # Gráfico de Sessões e Pedidos por dia filtrado
    df_filtered['Data'] = pd.to_datetime(df_filtered['Data']).dt.date  # Converte para apenas a data (sem horas)
    df_grouped = df_filtered.groupby('Data').agg({'Sessões': 'sum', 'Pedidos': 'sum'}).reset_index()

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

    # Agrega os dados por Origem e Mídia
    aggregated_df = df_filtered.groupby(['Origem', 'Mídia']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df = aggregated_df.sort_values(by='Sessões', ascending=False)

    # Exibe a tabela de dados com os filtros aplicados
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

