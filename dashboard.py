import streamlit as st
import pandas as pd
from datetime import timedelta, date, datetime
from concurrent.futures import ThreadPoolExecutor
from helpers.components import atribuir_cluster, send_discord_message, run_query, section_title
from filters import date_filters, traffic_filters
from tabs.tab_general import display_tab_general
from tabs.tab_last_orders import display_tab_last_orders
from tabs.tab_paid_media import display_tab_paid_media
from tabs.tab_settings import display_tab_settings
from custom.gringa_product_submited import display_tab_gringa_product_submited
from tabs.tab_today import display_tab_today
from tabs.tab_master import display_tab_master
from helpers.config import load_table_metas
from analytics.logger import log_event, get_location

def load_data(client, username, start_date_str, end_date_str):
    table = username

    query_general = f"""
    SELECT
        event_date AS Data,
        extract(hour from created_at) as Hora,
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

    # Query específica para dados de hoje
    today_str = date.today().strftime('%Y-%m-%d')
    query_today = f"""
    SELECT
        event_date AS Data,
        extract(hour from timestamp(created_at, "America/Sao_Paulo")) as Hora,
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
    WHERE event_date = '{today_str}'
    GROUP BY ALL
    ORDER BY Hora ASC
    """

    query_cookies = f"""
    SELECT
        round(sum(case when source = "not captured" then 1 else 0 end)/count(*),2) `Taxa Perda de Cookies Hoje`
    FROM `mymetric-hub-shopify.dbt_join.{table}_orders_sessions`
    WHERE date(created_at) = current_date("America/Sao_Paulo")
    GROUP BY ALL
    """

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
    GROUP BY ALL
    """

    query_whatsapp = f"""
    SELECT
        received_at `Data Cadastro`,
        name `Nome`,
        phone `Telefone`,
        email `E-mail`
    FROM `mymetric-hub-shopify.dbt_granular.{username}_whatsapp_widget`
    ORDER BY received_at DESC
    """

    queries = {
        "general": query_general,
        "today": query_today,
        "cookies": query_cookies,
        "ads": query_ads,
        "whatsapp": query_whatsapp
    }

    return queries

def execute_queries(client, queries):
    def execute_query(query):
        try:
            return run_query(client, query)
        except Exception as e:
            st.error(f"Erro ao executar a query: {e}")
            return pd.DataFrame()

    with ThreadPoolExecutor() as executor:
        futures = {key: executor.submit(execute_query, query) for key, query in queries.items()}
        results = {key: future.result() for key, future in futures.items()}

    return results

def process_filters(query_general):
    cluster_options = ["Selecionar Todos"] + query_general['Cluster'].unique().tolist()
    origem_options = ["Selecionar Todos"] + query_general['Origem'].unique().tolist()
    midia_options = ["Selecionar Todos"] + query_general['Mídia'].unique().tolist()
    campanha_options = ["Selecionar Todos"] + query_general['Campanha'].unique().tolist()
    conteudo_options = ["Selecionar Todos"] + query_general['Conteúdo'].unique().tolist()
    pagina_de_entrada_options = ["Selecionar Todos"] + query_general['Página de Entrada'].unique().tolist()

    with st.sidebar.expander("Fontes de Tráfego", expanded=True):
        cluster_selected = st.multiselect('Cluster', cluster_options, default=["Selecionar Todos"])
        origem_selected = st.multiselect('Origem', origem_options, default=["Selecionar Todos"])
        midia_selected = st.multiselect('Mídia', midia_options, default=["Selecionar Todos"])
        campanha_selected = st.multiselect('Campanha', campanha_options, default=["Selecionar Todos"])
        conteudo_selected = st.multiselect('Conteúdo', conteudo_options, default=["Selecionar Todos"])
        pagina_de_entrada_selected = st.multiselect('Página de Entrada', pagina_de_entrada_options, default=["Selecionar Todos"])

    return {
        "cluster_selected": cluster_selected,
        "origem_selected": origem_selected,
        "midia_selected": midia_selected,
        "campanha_selected": campanha_selected,
        "conteudo_selected": conteudo_selected,
        "pagina_de_entrada_selected": pagina_de_entrada_selected
    }

def create_tabs(username, df_ads, df_whatsapp, start_date, end_date):
    tabs = ["\U0001F441 Visão Geral", "📊 Análise do Dia"]
    
    tabs.append("\U0001F6D2 Últimos Pedidos")

    if df_ads is not None and not df_ads.empty:
        tabs.insert(len(tabs)-1, "\U0001F4B0 Mídia Paga")

    if df_whatsapp is not None and not df_whatsapp.empty:
        tabs.append("\U0001F4F1 WhatsApp Leads")

    if username == "gringa":
        tabs.append("\U0001F381 Produtos Cadastrados")

    tabs.append("\U0001F4E6 Configurações")

    if st.session_state.username == "mymetric":
        tabs.append("🎓 Mestre")

    return tabs

def show_dashboard(client, username):
    try:
        today = pd.to_datetime("today").date()
        yesterday = today - pd.Timedelta(days=1)
        seven_days_ago = today - pd.Timedelta(days=7)
        thirty_days_ago = today - pd.Timedelta(days=30)

        start_date, end_date = date_filters(today, yesterday, seven_days_ago, thirty_days_ago)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        queries = load_data(client, username, start_date_str, end_date_str)
        results = execute_queries(client, queries)

        if not results["general"].empty:
            query_general = results["general"]
            query_general['Cluster'] = query_general.apply(atribuir_cluster, axis=1)

            filters = process_filters(query_general)
            tabs = create_tabs(username, results["ads"], results["whatsapp"], start_date, end_date)

            # Carrega as metas do usuário para usar em várias abas
            metas = load_table_metas(username)
            current_month = datetime.now().strftime("%Y-%m")
            meta_receita = float(metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0))

            # Cria as abas
            tab_list = st.tabs(tabs)

            # Exemplo de uso das abas
            if "\U0001F441 Visão Geral" in tabs:
                with tab_list[tabs.index("\U0001F441 Visão Geral")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'visao_geral'})
                    tx_cookies = results["cookies"]["Taxa Perda de Cookies Hoje"].sum()*100
                    display_tab_general(query_general, tx_cookies, results["ads"], username, start_date=start_date, end_date=end_date, **filters)

                    if tx_cookies > 10:
                        send_discord_message(f"""
⚠️ **Alerta de Perda de Cookies** ⚠️

**Cliente:** `{username}`
**Taxa de Perda:** `{tx_cookies:.2f}%`
**Limite Recomendado:** `30%`

*Este alerta é gerado quando a taxa de perda de cookies está acima do normal.*
""")

            # Aba de Análise do Dia
            if "📊 Análise do Dia" in tabs:
                with tab_list[tabs.index("📊 Análise do Dia")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'analise_dia'})
                    df_today = results["today"]
                    df_today['Cluster'] = df_today.apply(atribuir_cluster, axis=1)
                    display_tab_today(df_today, results["ads"], username, meta_receita)

            if "\U0001F4B0 Mídia Paga" in tabs:
                with tab_list[tabs.index("\U0001F4B0 Mídia Paga")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'midia_paga'})
                    display_tab_paid_media(client, username, results["ads"], username)

            if "\U0001F6D2 Últimos Pedidos" in tabs:
                with tab_list[tabs.index("\U0001F6D2 Últimos Pedidos")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'ultimos_pedidos'})
                    query_last_orders = f"""
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
                    FROM `mymetric-hub-shopify.dbt_join.{username}_orders_sessions`
                    WHERE date(created_at) BETWEEN '{start_date_str}' AND '{end_date_str}'
                    ORDER BY created_at DESC
                    LIMIT 2000
                    """
                    df_last_orders = run_query(client, query_last_orders)
                    display_tab_last_orders(df_last_orders, **filters)

            if "\U0001F4F1 WhatsApp Leads" in tabs:
                with tab_list[tabs.index("\U0001F4F1 WhatsApp Leads")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'whatsapp_leads'})
                    df_whatsapp = results["whatsapp"]
                    section_title("WhatsApp Leads")
                    st.data_editor(df_whatsapp, hide_index=True, use_container_width=True)
                    csv = df_whatsapp.to_csv(index=False)
                    st.download_button(
                        label="Exportar para CSV",
                        data=csv,
                        file_name='whatsapp_leads.csv',
                        mime='text/csv'
                    )

            if "\U0001F381 Produtos Cadastrados" in tabs:
                with tab_list[tabs.index("\U0001F381 Produtos Cadastrados")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'produtos_cadastrados'})
                    display_tab_gringa_product_submited(client, start_date, end_date, **filters)

            if "🎓 Mestre" in tabs:
                with tab_list[tabs.index("🎓 Mestre")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'mestre'})
                    display_tab_master(client)

            if "\U0001F4E6 Configurações" in tabs:
                with tab_list[tabs.index("\U0001F4E6 Configurações")]:
                    log_event(st.session_state.username, 'tab_view', {'tab': 'configuracoes'})
                    display_tab_settings(username)

        else:
            error_msg = f"""
❌ **Erro de Carregamento de Dados** ❌

**Cliente:** `{username}`
**Problema:** Não foi possível carregar os dados do dashboard.

*Por favor, verifique se há problemas com as queries ou com o acesso ao banco de dados.*
"""
            st.error(error_msg)
            send_discord_message(error_msg)
            
    except Exception as e:
        error_msg = f"""
🚨 **Erro Crítico no Dashboard** 🚨

**Cliente:** `{username}`
**Erro:** `{str(e)}`

*Este é um erro crítico que impede o funcionamento do dashboard. Necessita atenção imediata.*
"""
        st.error(error_msg)
        send_discord_message(error_msg)
        st.stop()
