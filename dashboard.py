import streamlit as st
import pandas as pd
import pytz
from query_utils import run_query
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from filters import date_filters, traffic_filters
from metrics import display_metrics
from charts import display_charts
from aggregations import display_aggregations
from tab_paid_media import display_tab_paid_media
from custom.gringa_product_submited import display_tab_gringa_product_submited
from helpers.components import atribuir_cluster, send_discord_message

    
def show_dashboard(client, username):

    today = pd.to_datetime("today").date()
    yesterday = today - pd.Timedelta(days=1)
    seven_days_ago = today - pd.Timedelta(days=7)
    thirty_days_ago = today - pd.Timedelta(days=30)

    start_date, end_date = date_filters(today, yesterday, seven_days_ago, thirty_days_ago)

    # Converte as datas para string no formato 'YYYY-MM-DD' para a query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str_b = start_date.strftime('%Y%m%d')
    end_date_str_b = end_date.strftime('%Y%m%d')

    table = username

    query1 = f"""
    SELECT
        event_date AS Data,
        source Origem,
        medium `Mídia`, 
        campaign Campanha,
        page_location `Página de Entrada`,
        content `Conteúdo`,

        COUNTIF(event_name = 'session') `Sessões`,
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' then transaction_id end) `Pedidos`,
        SUM(CASE WHEN event_name = 'purchase' then value end) `Receita`,
        COUNT(DISTINCT CASE WHEN event_name = 'purchase' and status = 'paid' THEN transaction_id END) `Pedidos Pagos`,
        SUM(CASE WHEN event_name = 'purchase' and status = 'paid' THEN value ELSE 0 END) `Receita Paga`,
        COUNT(DISTINCT CASE WHEN event_name = 'fs_purchase' then transaction_id end) `Pedidos Primeiro Clique`

    FROM `mymetric-hub-shopify.dbt_join.{table}_events_long`
    WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    GROUP BY ALL
    ORDER BY Pedidos DESC
    """

    query3 = f"""
    SELECT
        round(sum(case when source = "not captured" then 1 else 0 end)/count(*),2) `Taxa Perda de Cookies Hoje`
    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
    WHERE date(created_at) = current_date("America/Sao_Paulo")
    GROUP BY ALL
    """
    
    # Adiciona a nova query responsiva ao filtro de data
    query_ads = f"""
        SELECT
            platform `Plataforma`,
            campaign_name `Campanha`,
            date `Data`,
            sum(cost) `Investimento`,
            sum(impressions) `Impressões`,
            sum(clicks) `Cliques`,
            sum(transactions) `Transações`,
            sum(revenue) `Receita`
        FROM
            `mymetric-hub-shopify.dbt_join.{table}_ads_campaigns_results`
        WHERE
            date BETWEEN '{start_date_str}' AND '{end_date_str}'
        group by all
    """

    # Função auxiliar para rodar as queries
    def execute_query(query):
        return run_query(client, query)
    
    # Função auxiliar para rodar query com tratamento de exceção
    def execute_query_safe(query):
        try:
            return run_query(client, query)
        except Exception as e:
            # Captura o erro, registra o log (opcional) e retorna um DataFrame vazio
            st.error(f"Erro ao executar a query: {e}")
            return pd.DataFrame()

    # Usar ThreadPoolExecutor para rodar as queries em paralelo
    with ThreadPoolExecutor() as executor:
        future_query1 = executor.submit(execute_query, query1)
        future_query3 = executor.submit(execute_query, query3)
        future_query_ads = executor.submit(execute_query_safe, query_ads)

        # Obter os resultados das queries
        df = future_query1.result()
        df3 = future_query3.result()
        df_ads = future_query_ads.result()
    

        df['Cluster'] = df.apply(atribuir_cluster, axis=1)

    # Processar o resultado da terceira query
    
    tx_cookies = df3["Taxa Perda de Cookies Hoje"].sum()
    tx_cookies = tx_cookies * 100

    if tx_cookies > 10:
        st.warning(f"Atenção: A taxa de perda de cookies hoje é {tx_cookies:.2f}%, o que está acima do limite aceitável, favor contatar o time MyMetric para auxiliar na resolução.", icon="⚠️")
        send_discord_message(f"Usuário **{username}** com taxa de perda de cookies elevada: {tx_cookies:.2f}%.")

    cluster_options = ["Selecionar Todos"] + df['Cluster'].unique().tolist()
    origem_options = ["Selecionar Todos"] + df['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + df['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + df['Campanha'].unique().tolist()
    conteudo_options = ["Selecionar Todos"] + df['Conteúdo'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + df['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Fontes de Tráfego", expanded=True):
        cluster_selected = st.multiselect('Cluster', cluster_options, default=["Selecionar Todos"])
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        conteudo_selected = st.multiselect('Conteúdo', conteudo_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    # Aplicar os filtros
    if "Selecionar Todos" in cluster_selected:
        cluster_selected = df['Cluster'].unique().tolist()
    if "Selecionar Todos" in origem_selected:
        origem_selected = df['Origem'].unique().tolist()
    if "Selecionar Todos" in midia_selected:
        midia_selected = df['Mídia'].unique().tolist()
    if "Selecionar Todos" in campanha_selected:
        campanha_selected = df['Campanha'].unique().tolist()
    if "Selecionar Todos" in conteudo_selected:
        conteudo_selected = df['Conteúdo'].unique().tolist()
    if "Selecionar Todos" in pagina_de_entrada_selected:
        pagina_de_entrada_selected = df['Página de Entrada'].unique().tolist()

    # Query for WhatsApp widget data
    query_whatsapp = f"""
    SELECT
        received_at `Data Cadastro`,
        name `Nome`,
        phone `Telefone`,
        email `E-mail`
    FROM `mymetric-hub-shopify.dbt_granular.{table}_whatsapp_widget`
    ORDER BY received_at DESC
    """
    df_whatsapp = execute_query(query_whatsapp)

    tabs = ["👀 Visão Geral", "🛒 Últimos Pedidos"]  # Abas padrão

    # Adiciona abas condicionalmente
    if df_ads is not None and not df_ads.empty:
        tabs.insert(1, "💰 Mídia Paga")
    if df_whatsapp is not None and not df_whatsapp.empty:
        tabs.append("📱 WhatsApp Leads")
    


    if username == "gringa":
        tabs.append("🎁 Produtos Cadastrados")



    # Cria abas no Streamlit
    tab_list = st.tabs(tabs)

    if "👀 Visão Geral" in tabs:
        with tab_list[tabs.index("👀 Visão Geral")]:

            df_filtered = traffic_filters(df, cluster_selected, origem_selected, midia_selected, campanha_selected, conteudo_selected, pagina_de_entrada_selected)
            display_metrics(df_filtered, tx_cookies, df_ads)
            display_charts(df_filtered)
            display_aggregations(df_filtered)

    if "💰 Mídia Paga" in tabs:
        with tab_list[tabs.index("💰 Mídia Paga")]:
            display_tab_paid_media(client, table, df_ads, username)

    if "🛒 Últimos Pedidos" in tabs:
        with tab_list[tabs.index("🛒 Últimos Pedidos")]:
            # Executa a query2 quando a aba "Últimos Pedidos" é aberta
            query2 = f"""
            SELECT
                created_at `Horário`,
                transaction_id `ID da Transação`,
                first_name `Primeiro Nome`,
                status `Status`,
                value `Receita`,
                source_name `Canal`,
                source `Origem`,
                medium `Mídia`,
                campaign `Campanha`,
                content `Conteúdo`,
                fs_source `Origem Primeiro Clique`,
                fs_medium `Mídia Primeiro Clique`,
                fs_campaign `Campanha Primeiro Clique`,
                page_location `Página de Entrada`,
                page_params `Parâmetros de URL`
            FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
            WHERE date(created_at) BETWEEN '{start_date_str}' AND '{end_date_str}'
            ORDER BY created_at DESC
            LIMIT 2000
            """

            # Executa a query2
            df2 = execute_query(query2)

            # Aplicar a função usando apply
            df2['Cluster'] = df2.apply(atribuir_cluster, axis=1)

            # Criar colunas para os filtros
            col1, col2, col3 = st.columns(3)

            # Adiciona o campo de entrada para filtrar pelo ID da Transação na primeira coluna
            with col1:
                id_transacao_input = st.text_input("ID da Transação")

            # Adiciona o campo de seleção para o Status na segunda coluna
            with col2:
                status_selected = st.multiselect("Status", options=df2['Status'].unique())

            # Adiciona o campo de seleção para o Canal na terceira coluna
            with col3:
                canal_selected = st.multiselect("Canal", options=df2['Canal'].unique())

            # Aplica os filtros anteriores
            df_filtered2 = traffic_filters(df2, cluster_selected, origem_selected, midia_selected, campanha_selected, conteudo_selected, pagina_de_entrada_selected)

            # Filtra pelo ID da Transação, se o valor estiver preenchido
            if id_transacao_input:
                df_filtered2 = df_filtered2[df_filtered2['ID da Transação'].astype(str).str.contains(id_transacao_input, na=False)]

            # Filtra pelo Status se algum status for selecionado
            if status_selected:
                df_filtered2 = df_filtered2[df_filtered2['Status'].isin(status_selected)]

            # Filtra pelo Canal se algum canal for selecionado
            if canal_selected:
                df_filtered2 = df_filtered2[df_filtered2['Canal'].isin(canal_selected)]

            # Exibe os dados filtrados
            st.header("Últimos Pedidos")
            st.data_editor(df_filtered2, hide_index=True, use_container_width=True)

    if "📱 WhatsApp Leads" in tabs:
        with tab_list[tabs.index("📱 WhatsApp Leads")]:
            # Display WhatsApp Leads table
            st.header("WhatsApp Leads")
            st.data_editor(df_whatsapp, hide_index=True, use_container_width=True)

            # Export button for WhatsApp data
            csv = df_whatsapp.to_csv(index=False)
            st.download_button(
                label="Exportar para CSV",
                data=csv,
                file_name='whatsapp_leads.csv',
                mime='text/csv'
            )
    
    if "🎁 Produtos Cadastrados" in tabs:
        with tab_list[tabs.index("🎁 Produtos Cadastrados")]:
            st.toast('Novo painel de Produtos Cadastrados disponível!', icon='😍')
            display_tab_gringa_product_submited(client, start_date, end_date, cluster_selected, origem_selected, midia_selected, campanha_selected, conteudo_selected, pagina_de_entrada_selected)
