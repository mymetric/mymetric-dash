import streamlit as st
import pandas as pd
import altair as alt
import os

is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'

cache_ttl = 6 if is_dev_mode else 600

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
    yesterday = today - pd.Timedelta(days=1)
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
        if st.button("Ontem"):  # Adicionando o botão "Ontem"
            start_date = yesterday
            end_date = yesterday
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
        campaign Campanha,
        page_location `Página de Entrada`,
        COUNTIF(event_name = 'session') `Sessões`,
        COUNT(DISTINCT transaction_id) Pedidos,
        SUM(value) Receita,
        SUM(CASE WHEN status = 'paid' THEN value ELSE 0 END) `Receita Paga`
    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY ALL
    ORDER BY Pedidos DESC
    """

    # Executa a query
    rows = run_query(client, query)

    # Converte os dados em DataFrame para fácil manipulação
    df = pd.DataFrame(rows)

    # Exibe a tabela sem numeração
    st.title("Visão Geral")

    # Listar opções únicas de Origem e Mídia, com a adição de "Selecionar Todos"
    origem_options = ["Selecionar Todos"] + df['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + df['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + df['Campanha'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + df['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Filtros de Tráfego", expanded=False):
        # Multiselect para Origem e Mídia
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    # Se "Selecionar Todos" estiver selecionado, seleciona todas as opções automaticamente
    if "Selecionar Todos" in origem_selected:
        origem_selected = df['Origem'].unique().tolist()

    if "Selecionar Todos" in midia_selected:
        midia_selected = df['Mídia'].unique().tolist()

    if "Selecionar Todos" in campanha_selected:
        campanha_selected = df['Campanha'].unique().tolist()

    if "Selecionar Todos" in pagina_de_entrada_selected:
        pagina_de_entrada_selected = df['Página de Entrada'].unique().tolist()


    # Filtrar o DataFrame com base nas seleções, apenas se o usuário desmarcar algumas opções
    if origem_selected:
        df = df[df['Origem'].isin(origem_selected)]

    if midia_selected:
        df = df[df['Mídia'].isin(midia_selected)]

    if campanha_selected:
        df = df[df['Campanha'].isin(campanha_selected)]

    if pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]

    # Calcula os big numbers com base nos dados filtrados
    pedidos = df["Pedidos"].sum()
    total_receita_paga = df["Receita Paga"].sum()
    total_receita_capturada = df["Receita"].sum()

    # Exibe os valores filtrados de "Receita Paga", "Receita Capturada" e "Pedidos"
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pedidos", f"{pedidos}")

    with col2:
        st.metric("Receita Capturada", f"R$ {total_receita_capturada:,.2f}")

    with col3:
        st.metric("Receita Paga", f"R$ {total_receita_paga:,.2f}")

    # Gráfico de Sessões e Pedidos por dia filtrado
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





    # Agrega os dados por Origem e Mídia
    aggregated_df = df.groupby(['Origem', 'Mídia']).agg({'Sessões': 'sum', 'Pedidos': 'sum', 'Receita': 'sum', 'Receita Paga': 'sum'}).reset_index()
    aggregated_df = aggregated_df.sort_values(by='Pedidos', ascending=False)

    st.header("Origem e Mídia")
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    campaigns = df

    campaigns = campaigns.groupby(['Campanha']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()

    campaigns = campaigns.sort_values(by='Pedidos', ascending=False)

    st.header("Campanhas")
    st.data_editor(campaigns, hide_index=1, use_container_width=1)

    pagina_de_entrada = df

    pagina_de_entrada = pagina_de_entrada.groupby(['Página de Entrada']).agg({
        'Sessões': 'sum', 
        'Pedidos': 'sum', 
        'Receita': 'sum', 
        'Receita Paga': 'sum'
    }).reset_index()

    pagina_de_entrada = pagina_de_entrada.sort_values(by='Pedidos', ascending=False)

    st.header("Página de Entrada")
    st.data_editor(pagina_de_entrada, hide_index=1, use_container_width=1)
 