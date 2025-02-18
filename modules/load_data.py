import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import json
from concurrent.futures import ThreadPoolExecutor
import time
import re
import base64
import threading
# Function to check and update session state expiration
def toast_alerts():
    # if st.session_state.username == 'mymetric':
        # return True
    # else:
        return False

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def traffic_cluster(row):
    try:
        if row['Mídia'] == 'social':
            return '🟣 Social'
        elif row['Origem'] == 'meta' and row['Mídia'] == 'cpc':
            return '🔵 Meta Ads'
        elif 'Parâmetros de URL' in row and 'fbclid' in str(row['Parâmetros de URL']):
            return '🔵 Meta Ads'
        elif row['Origem'] == 'google' and row['Mídia'] == 'cpc':
            return '🟢 Google Ads'
        elif row['Origem'] == 'google' and row['Mídia'] == 'organic':
            return '🌳 Google Orgânico'
        elif row['Origem'] == 'direct':
            return '🟡 Direto'
        elif ('whatsapp' in str(row['Origem']).lower() or 
              'whatsapp' in str(row['Mídia']).lower() or
              'zoppy' in str(row['Origem']).lower() or 
              'zoppy' in str(row['Mídia']).lower()):
            return '💬 WhatsApp'
        elif ('crm' in str(row['Origem']).lower() or
              'mautic' in str(row['Origem']).lower() or
              'email' in str(row['Origem']).lower()):
            return '✉️ E-mail'
        elif row['Origem'] == 'shopify_draft_order':
            return '🗒️ Draft'
        elif row['Origem'] == 'not captured':
            return '🍪 Perda de Cookies'
        else:
            return f"◻️ {row['Origem']} / {row['Mídia']}"
    except Exception as e:
        print(f"Erro ao atribuir cluster: {str(e)}")
        return "❓ Não classificado"

def apply_filters(df):
    """
    Aplica filtros ao DataFrame baseado nas seleções do usuário.
    Não cria elementos UI - apenas aplica a lógica de filtragem.
    """

    cluster_selected = st.session_state.cluster_selected
    origem_selected = st.session_state.origem_selected
    midia_selected = st.session_state.midia_selected
    campanha_selected = st.session_state.campanha_selected
    conteudo_selected = st.session_state.conteudo_selected
    pagina_de_entrada_selected = st.session_state.pagina_de_entrada_selected
    cupom_selected = st.session_state.cupom_selected
    
    # Aplicar filtros apenas se houver seleção e não incluir "Selecionar Todos"
    if cluster_selected and "Selecionar Todos" not in cluster_selected:
        df = df[df['Cluster'].isin(cluster_selected)]
    if origem_selected and "Selecionar Todos" not in origem_selected:
        df = df[df['Origem'].isin(origem_selected)]
    if midia_selected and "Selecionar Todos" not in midia_selected:
        df = df[df['Mídia'].isin(midia_selected)]
    if campanha_selected and "Selecionar Todos" not in campanha_selected:
        df = df[df['Campanha'].isin(campanha_selected)]
    if conteudo_selected and "Selecionar Todos" not in conteudo_selected:
        df = df[df['Conteúdo'].isin(conteudo_selected)]
    if pagina_de_entrada_selected and "Selecionar Todos" not in pagina_de_entrada_selected:
        df = df[df['Página de Entrada'].isin(pagina_de_entrada_selected)]
    if cupom_selected and "Selecionar Todos" not in cupom_selected:
        df = df[df['Cupom'].isin(cupom_selected)]
    
    return df

def check_table_exists(client, table_ref):
    try:
        client.get_table(table_ref)
        return True
    except NotFound:
        return False

def extract_table_reference_from_query(query):
    # Use regex to find the table reference in the query
    match = re.search(r'`([\w-]+\.[\w-]+\.[\w-]+)`', query)
    if match:
        return match.group(1)
    else:
        return None

@st.cache_data(ttl=3600)  # Cache de 1 hora
def execute_query(query):
    """Executa uma query, mantendo um cache de 1h."""

    try:
        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao executar query: {str(e)}")
        return pd.DataFrame()

def run_queries(queries):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_query, query) for query in queries]
        results = [future.result() for future in futures]
    return results

def load_basic_data():
    if toast_alerts():
        st.toast("Carregando dados básicos...")

    tablename = st.session_state.tablename

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    attribution_model = st.session_state.get('attribution_model', 'Último Clique Não Direto')

    if attribution_model == 'Último Clique Não Direto':
        attribution_model = 'purchase'
    elif attribution_model == 'Primeiro Clique':
        attribution_model = 'fs_purchase'
    
    query = f"""
        SELECT
            event_date AS Data,
            source Origem,
            medium `Mídia`, 
            # campaign Campanha,
            # page_location `Página de Entrada`,
            # content `Conteúdo`,
            # page_params `Parâmetros de URL`,
            # coalesce(discount_code, 'Sem Cupom') `Cupom`,

            COUNTIF(event_name = 'session') `Sessões`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' then transaction_id end) `Pedidos`,
            SUM(CASE WHEN event_name = '{attribution_model}' then value - total_discounts + shipping_value end) `Receita`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' and status = 'paid' THEN transaction_id END) `Pedidos Pagos`,
            SUM(CASE WHEN event_name = '{attribution_model}' and status = 'paid' THEN value - total_discounts + shipping_value ELSE 0 END) `Receita Paga`,

        FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
        WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        GROUP BY ALL
        ORDER BY Pedidos DESC
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)
    df = apply_filters(df)

    return df

def load_detailed_data():
    
    if st.session_state.get('selected_page') not in ["💼 Visão Detalhada", "🎯 Funil de Conversão"]:
        return pd.DataFrame()  # Return empty DataFrame if not on detailed tab
    
    current_time = time.time()
    if toast_alerts():
        st.toast("Carregando dados detalhados...")

    tablename = st.session_state.tablename

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    attribution_model = st.session_state.get('attribution_model', 'Último Clique Não Direto')

    if attribution_model == 'Último Clique Não Direto':
        attribution_model = 'purchase'
    elif attribution_model == 'Primeiro Clique':
        attribution_model = 'fs_purchase'
    
    query = f"""
        SELECT
            event_date AS Data,
            extract(hour from created_at) as Hora,
            source Origem,
            medium `Mídia`, 
            campaign Campanha,
            page_location `Página de Entrada`,
            content `Conteúdo`,
            # page_params `Parâmetros de URL`,
            coalesce(discount_code, 'Sem Cupom') `Cupom`,

            COUNTIF(event_name = 'session') `Sessões`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' then transaction_id end) `Pedidos`,
            SUM(CASE WHEN event_name = '{attribution_model}' then value - total_discounts + shipping_value end) `Receita`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' and status = 'paid' THEN transaction_id END) `Pedidos Pagos`,
            SUM(CASE WHEN event_name = '{attribution_model}' and status = 'paid' THEN value - total_discounts + shipping_value ELSE 0 END) `Receita Paga`,

        FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
        WHERE event_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        GROUP BY ALL
        ORDER BY Pedidos DESC
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)
    df = apply_filters(df)
    
    if toast_alerts():
        st.toast(f"Carregando dados detalhados... {time.time() - current_time:.2f}s")

    return df

def load_goals():
    if toast_alerts():
        st.toast("Carregando metas...")

    tablename = st.session_state.tablename

    query = f"""
        SELECT goals
        FROM `mymetric-hub-shopify.dbt_config.user_goals`
        WHERE username = '{tablename}'
        LIMIT 1
    """

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def load_check_zero_metrics():
    if toast_alerts():
        st.toast("Carregando métricas zeradas...")

    tablename = st.session_state.tablename

    query = f"""
    SELECT 
        event_date,
        COALESCE(view_item, 0) as view_item,
        COALESCE(add_to_cart, 0) as add_to_cart,
        COALESCE(begin_checkout, 0) as begin_checkout,
        COALESCE(add_shipping_info, 0) as add_shipping_info,
        COALESCE(add_payment_info, 0) as add_payment_info,
        COALESCE(purchase, 0) as purchase
    FROM `mymetric-hub-shopify.dbt_aggregated.{tablename}_daily_metrics`
    WHERE event_date >= DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 1 DAY)
    ORDER BY event_date DESC
    """

    df = run_queries([query])[0]
    return df

def load_funnel_data():
    if toast_alerts():
        st.toast("Carregando funnel...")

    tablename = st.session_state.tablename

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    # Otimização para quando as datas são iguais
    date_condition = f"event_date = '{start_date_str}'" if start_date_str == end_date_str else f"event_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
    
    query = f"""
    SELECT 
        event_date `Data`,
        view_item `Visualização de Item`,
        add_to_cart `Adicionar ao Carrinho`,
        begin_checkout `Iniciar Checkout`,
        add_shipping_info `Adicionar Informação de Frete`,
        add_payment_info `Adicionar Informação de Pagamento`,
        purchase `Pedido`
    FROM `mymetric-hub-shopify.dbt_aggregated.{tablename}_daily_metrics`
    WHERE {date_condition}
    ORDER BY event_date
    """

    df = run_queries([query])[0]

    # Garantir que o DataFrame não está vazio e tem todas as colunas necessárias
    if df.empty:
        # Criar DataFrame vazio com as colunas necessárias
        df = pd.DataFrame(columns=[
            'Data',
            'Visualização de Item',
            'Adicionar ao Carrinho',
            'Iniciar Checkout',
            'Adicionar Informação de Frete',
            'Adicionar Informação de Pagamento',
            'Pedido'
        ])
    
    return df

def load_enhanced_ecommerce_funnel():
    if toast_alerts():
        st.toast("Carregando funnel...")

    tablename = st.session_state.tablename
    
    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    query = f"""
        select

            event_date `Data`,
            item_id `ID do Produto`,
            item_name `Nome do Produto`,
            view_item `Visualização de Item`,
            add_to_cart `Adicionar ao Carrinho`,
            begin_checkout `Iniciar Checkout`,
            add_payment_info `Adicionar Informação de Pagamento`,
            add_shipping_info `Adicionar Informação de Frete`,
            purchase `Pedido`,
            view_item_to_add_to_cart_rate `Taxa de Visualização para Adição ao Carrinho`,
            add_to_cart_to_begin_checkout_rate `Taxa de Adição ao Carrinho para Início de Checkout`,
            begin_checkout_to_add_shipping_info_rate `Taxa de Início de Checkout para Adição de Informação de Frete`,
            add_shipping_info_to_add_payment_info_rate `Taxa de Adição de Informação de Frete para Adição de Informação de Pagamento`,
            add_payment_info_to_purchase_rate `Taxa de Adição de Informação de Pagamento para Pedido`,
            view_item_to_purchase_rate `Taxa de Visualização de Item para Pedido`	

        from `mymetric-hub-shopify.dbt_aggregated.{tablename}_enhanced_ecommerce_funnel`

        where event_date between '{start_date_str}' and '{end_date_str}'
    """

    df = run_queries([query])[0]
    return df

def load_paid_media():
    
    if toast_alerts():
        st.toast("Carregando mídias pagas...")

    tablename = st.session_state.tablename
    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    query = f"""
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
            `mymetric-hub-shopify.dbt_join.{tablename}_ads_campaigns_results`
        WHERE
            date BETWEEN '{start_date_str}' AND '{end_date_str}'
        GROUP BY ALL
    """

    df = run_queries([query])[0]
    return df

def load_fbclid_coverage():
    if toast_alerts():
        st.toast("Carregando cobertura de fbclid...")

    tablename = st.session_state.tablename


    query = f"""
        SELECT
            sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`
        FROM `mymetric-hub-shopify.dbt_join.{tablename}_sessions_gclids`
        WHERE
            event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
            and page_params like "%fbclid%"
            and medium not like "%social%"
    """

    df = run_queries([query])[0]
    return df

def load_performance_alerts():
    if toast_alerts():
        st.toast("Carregando alertas de performance...")

    tablename = st.session_state.tablename

    query = f"""
    WITH daily_rates AS (
        SELECT 
            event_date,
            view_item `Visualização de Item`,
            add_to_cart `Adicionar ao Carrinho`,
            begin_checkout `Iniciar Checkout`,
            add_shipping_info `Adicionar Informação de Frete`,
            add_payment_info `Adicionar Informação de Pagamento`,
            purchase `Pedido`,
            SAFE_DIVIDE(add_to_cart, NULLIF(view_item, 0)) * 100 as taxa_cart,
            SAFE_DIVIDE(begin_checkout, NULLIF(add_to_cart, 0)) * 100 as taxa_checkout,
            SAFE_DIVIDE(add_shipping_info, NULLIF(begin_checkout, 0)) * 100 as taxa_shipping,
            SAFE_DIVIDE(add_payment_info, NULLIF(add_shipping_info, 0)) * 100 as taxa_payment,
            SAFE_DIVIDE(purchase, NULLIF(add_payment_info, 0)) * 100 as taxa_purchase
        FROM `mymetric-hub-shopify.dbt_aggregated.{tablename}_daily_metrics`
        WHERE event_date >= DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 30 DAY)
    ),
    stats AS (
        SELECT
            AVG(CASE WHEN taxa_cart IS NOT NULL THEN taxa_cart END) as media_cart,
            STDDEV(CASE WHEN taxa_cart IS NOT NULL THEN taxa_cart END) as std_cart,
            AVG(CASE WHEN taxa_checkout IS NOT NULL THEN taxa_checkout END) as media_checkout,
            STDDEV(CASE WHEN taxa_checkout IS NOT NULL THEN taxa_checkout END) as std_checkout,
            AVG(CASE WHEN taxa_shipping IS NOT NULL THEN taxa_shipping END) as media_shipping,
            STDDEV(CASE WHEN taxa_shipping IS NOT NULL THEN taxa_shipping END) as std_shipping,
            AVG(CASE WHEN taxa_payment IS NOT NULL THEN taxa_payment END) as media_payment,
            STDDEV(CASE WHEN taxa_payment IS NOT NULL THEN taxa_payment END) as std_payment,
            AVG(CASE WHEN taxa_purchase IS NOT NULL THEN taxa_purchase END) as media_purchase,
            STDDEV(CASE WHEN taxa_purchase IS NOT NULL THEN taxa_purchase END) as std_purchase
        FROM daily_rates
        WHERE event_date < CURRENT_DATE("America/Sao_Paulo")
            AND event_date >= DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 30 DAY)
    )
    SELECT 
        r.*,
        s.*
        FROM daily_rates r
        CROSS JOIN stats s
        WHERE r.event_date >= DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 1 DAY)
        ORDER BY r.event_date DESC
        LIMIT 1
    """

    df = run_queries([query])[0]
    return df

def load_last_orders():
    if toast_alerts():
        st.toast("Carregando últimos pedidos...")

    tablename = st.session_state.tablename
    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    query = f"""
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
        FROM `mymetric-hub-shopify.dbt_join.{tablename}_orders_sessions`
        WHERE date(created_at) BETWEEN '{start_date_str}' AND '{end_date_str}'
        ORDER BY created_at DESC
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)
    df = apply_filters(df)
    
    return df

def save_goals(metas):
        """
        Salva as metas para uma tabela específica no BigQuery.
        """
        
        tablename = st.session_state.tablename
        
        # Converte o dicionário de metas para JSON
        metas_json = json.dumps(metas)
        
        # Query para inserir ou atualizar as metas
        query = f"""
        MERGE `mymetric-hub-shopify.dbt_config.user_goals` AS target
        USING (SELECT '{tablename}' as username, '{metas_json}' as goals) AS source
        ON target.username = source.username
        WHEN MATCHED THEN
            UPDATE SET goals = source.goals, updated_at = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN
            INSERT (username, goals, created_at, updated_at)
            VALUES (source.username, source.goals, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """
        
        try:
            client.query(query)
        except Exception as e:
            st.error(f"Erro ao salvar metas: {str(e)}")

def load_current_month_revenue():

    if toast_alerts():
        st.toast("Carregando receita do mês...")

    tablename = st.session_state.tablename

    hoje = pd.Timestamp.now(tz='America/Sao_Paulo')
    primeiro_dia = hoje.replace(day=1).strftime('%Y-%m-%d')
    ultimo_dia = hoje.strftime('%Y-%m-%d')
    
    query = f"""
    SELECT SUM(CASE WHEN event_name = 'purchase' and status = 'paid' THEN value ELSE 0 END) as total_mes
    FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
    WHERE event_date BETWEEN '{primeiro_dia}' AND '{ultimo_dia}'
    """

    df = run_queries([query])[0]
    return df

def load_today_data():

    if toast_alerts():
        st.toast("Carregando dados do dia...")

    tablename = st.session_state.tablename

    today_str = pd.Timestamp.now(tz='America/Sao_Paulo').strftime('%Y-%m-%d')

    query = f"""
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
            SUM(CASE WHEN event_name = 'purchase' and status = 'paid' THEN value - total_discounts + shipping_value ELSE 0 END) `Receita Paga`,
            COUNT(DISTINCT CASE WHEN event_name = 'fs_purchase' then transaction_id end) `Pedidos Primeiro Clique`

        FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
        WHERE event_date = '{today_str}'
        GROUP BY ALL
        ORDER BY Hora ASC
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)
    return df
    
def load_gringa_product_submited():
    if toast_alerts():
        st.toast("Carregando cadastros de produtos...")

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        with

        prep as (

        select

        a.*,
        b.product_submited

        from `mymetric-hub-shopify.dbt_join.gringa_sessions_gclids` a

        left join `mymetric-hub-shopify.dbt_granular.gringa_product_submited` b on a.user_pseudo_id = b.user_pseudo_id and a.ga_session_id = b.ga_session_id

        where
            a.event_date BETWEEN '{start_date}' AND '{end_date}'

        )

        select

        event_date `Data`,
        source `Origem`,
        medium `Mídia`,
        campaign `Campanha`,
        content `Conteúdo`,
        page_location `Página de Entrada`,
        count(*) `Sessões`,
        sum(product_submited) `Cadastros`

        from prep

        group by all

        order by Cadastros desc
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)

    return df

def load_holysoup_mautic_segments():
    if toast_alerts():
        st.toast("Carregando segmentos do Mautic...")

    query = """
        SELECT 
            list_name
        FROM `holy-soup.mautic.export_segment`
        group by all
    """

    df = run_queries([query])[0]
    return df

@st.cache_data(ttl=300)
def load_holysoup_mautic_contacts(list_name):
    if toast_alerts():
        st.toast("Carregando contatos do Mautic...")

    query = f"""
        SELECT 
            *
        FROM `holy-soup.mautic.export_segment`
        WHERE list_name = '{list_name}'
    """

    st.toast(f"Carregando contatos do Mautic... {list_name}")

    
    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def load_holysoup_email_stats():
    if toast_alerts():
        st.toast("Carregando estatísticas de e-mails...")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    # Otimização para quando as datas são iguais
    date_condition = f"date(email_date) = '{start_date_str}'" if start_date_str == end_date_str else f"date(email_date) BETWEEN '{start_date_str}' AND '{end_date_str}'"

    query = f"""
        SELECT 
            email_id `ID`,
            email_name `Nome`,
            email_date `Data`,
            email_sent `Enviado`,
            email_cost `Custo`,
            email_opened `Abertos`,
            email_clicks `Cliques`,
            purchase_revenue `Receita`
        FROM `holy-soup.email_stats.email_stats`
        WHERE {date_condition}
    """

    df = run_queries([query])[0]
    return df

def load_holysoup_crm_optout():
    if toast_alerts():
        st.toast("Carregando optouts do CRM...")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    # Otimização para quando as datas são iguais
    date_condition = f"data = '{start_date_str}'" if start_date_str == end_date_str else f"data between '{start_date_str}' and '{end_date_str}'"

    query = f"""
        SELECT
            data,
            enviado,
            descadastro,
            rejeicao,
            marcou_como_spam
        FROM `holy-soup.email_stats.optout`
        WHERE {date_condition}
    """

    df = run_queries([query])[0]
    return df

def load_all_users():
    
    query = f"""
        SELECT
            email,
            admin,
            access_control,
            tablename,
            password
        FROM `mymetric-hub-shopify.dbt_config.users`
    """

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def load_users():
    
    tablename = st.session_state.tablename

    query = f"""
        SELECT
            email,
            admin,
            access_control,
        FROM `mymetric-hub-shopify.dbt_config.users`
        WHERE tablename = '{tablename}'
    """

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def save_users(email, password, admin):
    tablename = st.session_state.tablename
    # Encode password using base64
    st.info(f"Guarde a senha gerada em um local seguro (desaparecerá em 15 segundos): {password}")
    encoded_password = base64.b64encode(password.encode()).decode()

    query = f"""
        MERGE `mymetric-hub-shopify.dbt_config.users` AS target
        USING (SELECT '{tablename}' as tablename, '{email}' as email, '{encoded_password}' as password) AS source
        ON target.tablename = source.tablename AND target.email = source.email
        WHEN MATCHED THEN
            UPDATE SET email = source.email, password = source.password, admin = {admin}
        WHEN NOT MATCHED THEN
            INSERT (tablename, email, password, admin, access_control)
            VALUES ('{tablename}', '{email}', '{encoded_password}', {admin}, '[]')
    """

    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao salvar usuário: {str(e)}")

def delete_user(email):
    """
    Delete a user from the database
    
    Args:
        email (str): Email of the user to delete
        tablename (str): Current table name from session state
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        tablename = st.session_state.tablename
        
        query = f"""
            DELETE FROM `mymetric-hub-shopify.dbt_config.users` 
            WHERE tablename = '{tablename}'
            AND email = '{email}'
        """
        client.query(query)
        return True
    except Exception as e:
        st.toast(f"Error deleting user: {str(e)}")
        return False

def save_coupons(coupon_code, coupon_category):
    
    tablename = st.session_state.tablename
    user = st.session_state.username

    query = f"""
        MERGE `mymetric-hub-shopify.dbt_config.coupons` AS target
        USING (SELECT '{tablename}' as tablename, '{coupon_code}' as coupon_code) AS source
        ON target.tablename = source.tablename AND target.coupon_code = source.coupon_code
        WHEN MATCHED THEN
            UPDATE SET coupon_category = coupon_category, user = user
        WHEN NOT MATCHED THEN
            INSERT (created_at, tablename, user, coupon_code, coupon_category)
            VALUES (CURRENT_TIMESTAMP(), '{tablename}', '{user}', '{coupon_code}', '{coupon_category}')
    """

    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao salvar usuário: {str(e)}")

def load_coupons():

    if toast_alerts():
        st.toast("Carregando cupons...")

    tablename = st.session_state.tablename
    query = f"""
        SELECT
            coupon_code `Cupom`,
            coupon_category `Categoria`
        FROM `mymetric-hub-shopify.dbt_config.coupons`
        WHERE tablename = '{tablename}'
    """

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def delete_coupon(coupon_code):
    tablename = st.session_state.tablename
    query = f"""
        DELETE FROM `mymetric-hub-shopify.dbt_config.coupons`
        WHERE tablename = '{tablename}' AND coupon_code = '{coupon_code}'
    """
    try:
        client.query(query)
        return True
    except Exception as e:
        st.toast(f"Error deleting user: {str(e)}")
        return False

def load_leads_popup():

    if toast_alerts():
        st.toast("Carregando leads via popup...")

    tablename = st.session_state.tablename
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        SELECT
        
        date_received_at `Data`,
        count(distinct email) `E-mails`

        FROM `mymetric-hub-shopify.dbt_granular.popup_subscribe`
        where event_name like "%{tablename}%"
        and date(date_received_at) between "{start_date}" and "{end_date}"

        group by all

        order by 1 desc
    """

    df = run_queries([query])[0]
    return df

def load_meta_ads():
    
    if toast_alerts():
        st.toast("Carregando dados do Meta Ads...")

    tablename = st.session_state.tablename
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        select

            date_start date,
            campaign_name,
            adset_name,
            ad_name,
            spend,
            impressions,
            clicks,
            purchases purchases,
            purchase_revenue purchase_value

        from `mymetric-hub-shopify.dbt_granular.{tablename}_meta_ads_campaigns`
        where date(date_start) between "{start_date}" and "{end_date}"

        """

    # st.markdown(f"```sql{query}")

    df = run_queries([query])[0]
    return df

def save_event_name(event_name, event_params):

    tablename = st.session_state.tablename
    user = st.session_state.username
    event_params = json.dumps(event_params)

    query = f"""
        INSERT INTO `mymetric-hub-shopify.dbt_config.events` (
            created_at,
            tablename,
            user,
            event_name,
            event_params
        )
        VALUES (
            CURRENT_TIMESTAMP(),
            '{tablename}',
            '{user}',
            '{event_name}',
            '{event_params}'
        )
    """

    try:
        client.query(query)
    except Exception as e:
        st.error(f"Erro ao salvar evento: {str(e)}")


def load_popup_leads():

    tablename = st.session_state.tablename

    query = f"""

        with

        leads as (

        select

        datetime(received_at, "America/Sao_Paulo") subscribe_timestamp,
        name,
        phone,
        email

        from `mymetric-hub-shopify.dbt_granular.popup_subscribe`

        where

        event_name like "%{tablename}%"

        order by received_at desc

        ),

        orders as (

        select

        max(created_at) purchase_timestamp,
        email

        from `mymetric-hub-shopify.dbt_granular.{tablename}_orders_dedup`

        group by all

        )

        select

        a.subscribe_timestamp `Data do Cadastro`,
        a.name `Nome`,
        a.phone `Telefone`,
        a.email `E-mail`,
        b.purchase_timestamp `Data da Compra`

        from leads a

        left join orders b on a.email = b.email

        order by subscribe_timestamp desc

    """

    df = run_queries([query])[0]
    return df