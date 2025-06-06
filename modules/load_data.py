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
from functools import wraps
from datetime import datetime, timedelta

def get_project_name(tablename):
    """
    Returns the appropriate project name based on the tablename.
    
    Args:
        tablename (str): The name of the table
        
    Returns:
        str: The project name to use ('bq-mktbr' for havaianas, 'mymetric-hub-shopify' for others)
    """
    return 'bq-mktbr' if tablename == 'havaianas' else 'mymetric-hub-shopify'

# Function to check and update session state expiration
def toast_alerts():
        return False

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def initialize_cache():
    """Inicializa o cache no session_state se não existir."""
    if 'cache_data' not in st.session_state:
        st.session_state.cache_data = {}
    if 'cache_timestamps' not in st.session_state:
        st.session_state.cache_timestamps = {}
    if 'background_tasks' not in st.session_state:
        st.session_state.background_tasks = {}

def background_cache(ttl_hours=1):
    """
    Decorator que implementa cache com atualização em background.
    
    Args:
        ttl_hours (int): Tempo em horas antes de iniciar atualização em background
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Inicializar cache se necessário
            initialize_cache()
            
            # Obter tablename e datas da sessão
            tablename = st.session_state.get('tablename')
            start_date = st.session_state.get('start_date')
            end_date = st.session_state.get('end_date')
            
            if not tablename:
                raise ValueError("tablename não está definido na sessão")
            
            # Criar chave única para o cache incluindo tablename e datas
            cache_key = f"{tablename}:{start_date}:{end_date}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Verificar se existe cache
            if cache_key in st.session_state.cache_data:
                last_update = st.session_state.cache_timestamps.get(cache_key)
                if last_update:
                    # Converter string de timestamp para datetime
                    last_update = datetime.fromisoformat(last_update)
                    
                    # Calcular idade do cache
                    age = datetime.now() - last_update
                    
                    # Se o cache ainda é válido (menos de 1 dia)
                    if age < timedelta(days=1):
                        # Se passou 1 hora, iniciar atualização em background
                        if age > timedelta(hours=ttl_hours):
                            _start_background_update(func, cache_key, args, kwargs)
                        return st.session_state.cache_data[cache_key]
            
            # Se não há cache ou está expirado, executar função normalmente
            result = func(*args, **kwargs)
            if result is not None and (isinstance(result, pd.DataFrame) and not result.empty):
                st.session_state.cache_data[cache_key] = result
                st.session_state.cache_timestamps[cache_key] = datetime.now().isoformat()
            return result
            
        return wrapper
    return decorator

def _start_background_update(func, cache_key, args, kwargs):
    """
    Inicia uma atualização em background do cache.
    """
    if cache_key in st.session_state.background_tasks:
        return  # Já existe uma tarefa rodando para esta chave
    
    def update_cache():
        try:
            # Executar função para obter novos dados
            new_result = func(*args, **kwargs)
            
            # Atualizar cache apenas se a função retornou dados válidos
            if new_result is not None and (isinstance(new_result, pd.DataFrame) and not new_result.empty):
                st.session_state.cache_data[cache_key] = new_result
                st.session_state.cache_timestamps[cache_key] = datetime.now().isoformat()
        except Exception as e:
            print(f"Erro ao atualizar cache em background: {str(e)}")
        finally:
            # Remover tarefa da lista de tarefas ativas
            if cache_key in st.session_state.background_tasks:
                del st.session_state.background_tasks[cache_key]
    
    # Marcar a tarefa como em execução
    st.session_state.background_tasks[cache_key] = datetime.now().isoformat()
    
    # Executar a atualização
    update_cache()

def clear_expired_cache():
    """Remove entradas de cache expiradas."""
    initialize_cache()
    
    current_time = datetime.now()
    expired_keys = []
    
    for cache_key, timestamp in st.session_state.cache_timestamps.items():
        last_update = datetime.fromisoformat(timestamp)
        age = current_time - last_update
        
        if age > timedelta(days=1):  # 1 dia é o máximo
            expired_keys.append(cache_key)
    
    for key in expired_keys:
        if key in st.session_state.cache_data:
            del st.session_state.cache_data[key]
        if key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[key]
        if key in st.session_state.background_tasks:
            del st.session_state.background_tasks[key]

# Limpar cache expirado ao iniciar
clear_expired_cache()

def traffic_cluster(row):
    try:
        if row['Mídia'] == 'social':
            return '🟣 Social'
        elif row['Origem'] == 'Insta':
            return '🟣 Social'
        elif row['Origem'] == 'meta':
            return '🔵 Meta Ads'
        elif 'Parâmetros de URL' in row and 'fbclid' in str(row['Parâmetros de URL']):
            return '🔵 Meta Ads'
        elif 'Origem' in row and 'Instagram_' in str(row['Origem']):
            return '🔵 Meta Ads'
        elif 'Origem' in row and 'Facebook_' in str(row['Origem']):
            return '🔵 Meta Ads'
        elif 'Origem' in row and '{{placement}}' in str(row['Origem']):
            return '🔵 Meta Ads'
        elif row['Origem'] == 'google' and row['Mídia'] == 'cpc':
            return '🟢 Google Ads'
        elif row['Origem'] == 'google' and row['Mídia'] == 'organic':
            return '🌳 Google Orgânico'
        elif row['Origem'] == 'direct':
            return '🟡 Direto'
        elif row['Origem'] == 'bio':
            return '🔵 Bio Instagram'
        elif ('grupo' in str(row['Mídia']).lower()):
            return '💬 WhatsApp - Grupos'
        elif ('whatsapp' in str(row['Origem']).lower() or 
              'whatsapp' in str(row['Mídia']).lower() or
              'zoppy' in str(row['Origem']).lower() or 
              'zoppy' in str(row['Mídia']).lower()):
            return '💬 WhatsApp - Direto'
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
    # Verificar se o DataFrame está vazio
    if df.empty:
        return df
        
    # Criar uma cópia do DataFrame para não modificar o original
    df_filtered = df.copy()

    # Lista de filtros para aplicar
    filters = [
        ('cluster_selected', 'Cluster'),
        ('origem_selected', 'Origem'),
        ('midia_selected', 'Mídia'),
        ('campanha_selected', 'Campanha'),
        ('conteudo_selected', 'Conteúdo'),
        ('pagina_de_entrada_selected', 'Página de Entrada'),
        ('cupom_selected', 'Cupom')
    ]

    # Aplicar cada filtro
    for state_key, column in filters:
        selected_values = st.session_state.get(state_key, [])
        if selected_values and "Selecionar Todos" not in selected_values:
            # Garantir que a coluna existe antes de filtrar
            if column in df_filtered.columns:
                # Converter valores para string para evitar problemas de tipo
                df_filtered[column] = df_filtered[column].astype(str)
                selected_values = [str(val) for val in selected_values]
                df_filtered = df_filtered[df_filtered[column].isin(selected_values)]
    
    return df_filtered

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

@background_cache(ttl_hours=1)
def load_basic_data():
    if toast_alerts():
        st.toast("Carregando dados básicos...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    date_condition = f"event_date = '{start_date_str}'" if start_date_str == end_date_str else f"event_date between '{start_date_str}' and '{end_date_str}'"

    # Usa o modelo de atribuição da sessão, com fallback para o padrão
    attribution_model = st.session_state.get('attribution_model', 'Último Clique Não Direto')
    
    # Adiciona o modelo de atribuição ao cache key para forçar recarregamento quando mudar
    cache_key = f"basic_data_{tablename}_{start_date_str}_{end_date_str}_{attribution_model}"

    # Limpa o cache se o modelo de atribuição mudou
    if 'last_attribution_model' in st.session_state and st.session_state.last_attribution_model != attribution_model:
        if cache_key in st.session_state.cache_data:
            del st.session_state.cache_data[cache_key]
        if cache_key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[cache_key]
        if cache_key in st.session_state.background_tasks:
            del st.session_state.background_tasks[cache_key]

    if attribution_model == 'Último Clique Não Direto':
        attribution_model = 'purchase'
    elif attribution_model == 'Primeiro Clique':
        attribution_model = 'fs_purchase'
    
    # Use get_project_name only for non-dbt_config datasets
    project_name = get_project_name(tablename)
    
    query = f"""
        SELECT
            event_date AS Data,
            traffic_category `Cluster`,
            SUM(CASE WHEN event_name = 'paid_media' then value else 0 end) `Investimento`,
            SUM(CASE WHEN event_name = 'paid_media' then clicks else 0 end) `Cliques`,
            COUNTIF(event_name = 'session') `Sessões`,
            COUNTIF(event_name = 'add_to_cart') `Adições ao Carrinho`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' then transaction_id end) `Pedidos`,
            SUM(CASE WHEN event_name = '{attribution_model}' then value - coalesce(total_discounts, 0) + coalesce(shipping_value, 0) end) `Receita`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') THEN transaction_id END) `Pedidos Pagos`,
            SUM(CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') THEN value - coalesce(total_discounts, 0) + coalesce(shipping_value, 0) ELSE 0 END) `Receita Paga`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') and transaction_no = 1 THEN transaction_id END) `Novos Clientes`,
            SUM(CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') and transaction_no = 1 THEN value - coalesce(total_discounts, 0) + coalesce(shipping_value, 0) ELSE 0 END) `Receita Novos Clientes`

        FROM `{project_name}.dbt_join.{tablename}_events_long`
        WHERE {date_condition}
        GROUP BY ALL
        ORDER BY Pedidos DESC
    """

    df = run_queries([query])[0]
    
    # Aplicar filtros
    df = apply_filters(df)

    return df

@background_cache(ttl_hours=1)
def load_detailed_data():
    """
    Carrega dados detalhados com todos os filtros aplicados.
    """
    if toast_alerts():
        st.toast("Carregando dados detalhados...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    date_condition = f"event_date = '{start_date_str}'" if start_date_str == end_date_str else f"event_date between '{start_date_str}' and '{end_date_str}'"

    attribution_model = st.session_state.get('attribution_model', 'Último Clique Não Direto')
    attribution_model = 'purchase' if attribution_model == 'Último Clique Não Direto' else 'fs_purchase'
    
    project_name = get_project_name(tablename)

    query = f"""
        SELECT
            event_date AS Data,
            extract(hour from created_at) as Hora,
            source Origem,
            medium `Mídia`, 
            campaign Campanha,
            page_location `Página de Entrada`,
            content `Conteúdo`,
            coalesce(discount_code, 'Sem Cupom') `Cupom`,
            traffic_category `Cluster`,

            COUNTIF(event_name = 'session') `Sessões`,
            COUNTIF(event_name = 'add_to_cart') `Adições ao Carrinho`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' then transaction_id end) `Pedidos`,
            SUM(CASE WHEN event_name = '{attribution_model}' then value - total_discounts + shipping_value end) `Receita`,
            COUNT(DISTINCT CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') THEN transaction_id END) `Pedidos Pagos`,
            SUM(CASE WHEN event_name = '{attribution_model}' and status in ('paid', 'authorized') THEN value - total_discounts + shipping_value ELSE 0 END) `Receita Paga`

        FROM `{project_name}.dbt_join.{tablename}_events_long`
        WHERE {date_condition}
        GROUP BY ALL
        ORDER BY Pedidos DESC
    """

    # Carregar dados
    df = run_queries([query])[0]
    
    # Verificar se o DataFrame está vazio
    if df.empty:
        return pd.DataFrame()
    
    # Ensure required columns exist
    required_columns = ['Origem', 'Mídia', 'Cluster']
    if not all(col in df.columns for col in required_columns):
        print(f"Missing columns: {[col for col in required_columns if col not in df.columns]}")
        # If Cluster is missing, create it
        if 'Cluster' not in df.columns:
            df['Cluster'] = df.apply(lambda row: traffic_cluster(row), axis=1)
    
    # Carregar categorias de tráfego
    categories_df = load_traffic_categories()
    
    # Aplicar categorias de tráfego
    if not categories_df.empty:
        print("Aplicando categorias de tráfego...")
        for _, category in categories_df.iterrows():
            rules = category['Regras'].get('rules', {})
            if not rules:
                continue
                
            # Criar máscara para cada regra
            mask = pd.Series(True, index=df.index)
            for field, pattern in rules.items():
                if pattern:
                    # Mapear nomes de campos
                    field_mapping = {
                        'origem': 'Origem',
                        'midia': 'Mídia',
                        'campanha': 'Campanha',
                        'conteudo': 'Conteúdo',
                        'pagina_de_entrada': 'Página de Entrada'
                    }
                    
                    mapped_field = field_mapping.get(field)
                    if mapped_field and mapped_field in df.columns:
                        try:
                            field_mask = df[mapped_field].astype(str).str.contains(pattern, regex=True, na=False)
                            mask &= field_mask
                        except Exception as e:
                            print(f"Erro ao aplicar regra {pattern} para campo {mapped_field}: {str(e)}")
            
            # Aplicar categoria onde a máscara é True
            df.loc[mask, 'Cluster'] = category['Nome']
            print(f"Categoria {category['Nome']} aplicada em {mask.sum()} linhas")
    
    # Aplicar filtros
    df = apply_filters(df)
    
    return df

@background_cache(ttl_hours=1)
def load_goals():
    if toast_alerts():
        st.toast("Carregando metas...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

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

@background_cache(ttl_hours=1)
def load_check_zero_metrics():
    if toast_alerts():
        st.toast("Carregando métricas zeradas...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

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

@background_cache(ttl_hours=1)
def load_fbclid_coverage():
    if toast_alerts():
        st.toast("Carregando cobertura de fbclid...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    query = f"""
        SELECT
            sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`
        FROM `mymetric-hub-shopify.dbt_join.{tablename}_sessions_gclids`
        WHERE
            event_date >= date_sub(current_date("America/Sao_Paulo"), interval 3 day)
            and page_params like "%fbclid%"
            and medium not like "%social%"
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_meta_ads():
    if toast_alerts():
        st.toast("Carregando dados do Meta Ads...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

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
            leads,
            purchases purchases,
            purchase_revenue purchase_value,
            last_session_transactions,
            last_session_revenue
        from `mymetric-hub-shopify.dbt_granular.{tablename}_meta_ads_campaigns`
        where date(date_start) between "{start_date}" and "{end_date}"
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_popup_leads():
    if toast_alerts():
        st.toast("Carregando leads via popup...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    query = f"""

        select
        *
        from `mymetric-hub-shopify.dbt_join.{tablename}_leads_orders`
                
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_rfm_segments():
    """
    Carrega dados de segmentação RFM do BigQuery.
    """
    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")
        
    query = f"""
    SELECT
        customer_id `ID`,
        first_name `Nome`,
        last_name `Sobrenome`,
        email `E-mail`,
        phone `Telefone`,
        recency_days `Recência`,
        frequency `Frequência`,
        monetary `Monetário`,
        segment_name AS Categoria
    FROM `mymetric-hub-shopify.dbt_aggregated.{tablename}_rfm`
    """

    df = run_queries([query])[0]
    
    # Converter recência para meses após carregar os dados
    df['Recência'] = df['Recência'] / 30
    df = df.rename(columns={'Recência': 'Recência (Meses)'})
    
    return df

@background_cache(ttl_hours=1)
def load_current_month_revenue():
    if toast_alerts():
        st.toast("Carregando receita do mês...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    hoje = pd.Timestamp.now(tz='America/Sao_Paulo')
    primeiro_dia = hoje.replace(day=1).strftime('%Y-%m-%d')
    ultimo_dia = hoje.strftime('%Y-%m-%d')
    
    query = f"""
    SELECT SUM(CASE WHEN event_name = 'purchase' and status in ('paid', 'authorized') THEN value ELSE 0 END) as total_mes
    FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
    WHERE event_date BETWEEN '{primeiro_dia}' AND '{ultimo_dia}'
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_today_data():
    if toast_alerts():
        st.toast("Carregando dados do dia...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

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
            COUNT(DISTINCT CASE WHEN event_name = 'purchase' and status in ('paid', 'authorized') THEN transaction_id END) `Pedidos Pagos`,
            SUM(CASE WHEN event_name = 'purchase' and status in ('paid', 'authorized') THEN value - total_discounts + shipping_value ELSE 0 END) `Receita Paga`,
            COUNT(DISTINCT CASE WHEN event_name = 'fs_purchase' then transaction_id end) `Pedidos Primeiro Clique`
        FROM `mymetric-hub-shopify.dbt_join.{tablename}_events_long`
        WHERE event_date = '{today_str}'
        GROUP BY ALL
        ORDER BY Hora ASC
    """

    df = run_queries([query])[0]
    df['Cluster'] = df.apply(traffic_cluster, axis=1)
    return df
    
@background_cache(ttl_hours=1)
def load_leads_popup():
    if toast_alerts():
        st.toast("Carregando leads via popup...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        SELECT
            date `Data do Cadastro`,
            emails `E-mails`
        FROM `mymetric-hub-shopify.dbt_aggregated.{tablename}_daily_leads`
        where
        date between "{start_date}" and "{end_date}"
        
        order by 1 desc
    """

    df = run_queries([query])[0]
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

# @st.cache_data(ttl=300)
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
            purchases `Pedidos`,
            purchase_revenue `Receita`,
            last_click_purchases `Pedidos Último Clique`,
            last_click_revenue `Receita Último Clique`
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

def load_funnel_data():
    if toast_alerts():
        st.toast("Carregando funnel...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    # Otimização para quando as datas são iguais
    date_condition = f"event_date = '{start_date_str}'" if start_date_str == end_date_str else f"event_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
    
    project_name = get_project_name(tablename)

    query = f"""
    SELECT 
        event_date `Data`,
        view_item `Visualização de Item`,
        add_to_cart `Adicionar ao Carrinho`,
        begin_checkout `Iniciar Checkout`,
        add_shipping_info `Adicionar Informação de Frete`,
        add_payment_info `Adicionar Informação de Pagamento`,
        purchase `Pedido`
    FROM `{project_name}.dbt_aggregated.{tablename}_daily_metrics`
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

@background_cache(ttl_hours=1)
def load_enhanced_ecommerce_funnel():
    if toast_alerts():
        st.toast("Carregando funnel...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")
    
    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    project_name = get_project_name(tablename)

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

        from `{project_name}.dbt_aggregated.{tablename}_enhanced_ecommerce_funnel`

        where event_date between '{start_date_str}' and '{end_date_str}'
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_paid_media():
    if toast_alerts():
        st.toast("Carregando mídias pagas...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    project_name = get_project_name(tablename)

    query = f"""
        SELECT
            platform `Plataforma`,
            campaign_name `Campanha`,
            date `Data`,
            sum(cost) `Investimento`,
            sum(impressions) `Impressões`,
            sum(clicks) `Cliques`,
            sum(transactions) `Transações`,
            sum(fsm_transactions) `Transações Primeiro Lead`,
            sum(first_transaction) `Primeiras Compras`,
            sum(first_revenue) `Receita Primeiras Compras`,
            sum(fsm_first_transaction) `Primeiras Compras Primeiro Lead`,
            sum(fsm_first_revenue) `Receita Primeiras Compras Primeiro Lead`,
            sum(revenue) `Receita`,
            sum(fsm_revenue) `Receita Primeiro Lead`,
            sum(leads) `Leads`
        FROM
            `{project_name}.dbt_join.{tablename}_ads_campaigns_results`
        WHERE
            date BETWEEN '{start_date_str}' AND '{end_date_str}'
        GROUP BY ALL
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_performance_alerts():
    if toast_alerts():
        st.toast("Carregando alertas de performance...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    project_name = get_project_name(tablename)

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
        FROM `{project_name}.dbt_aggregated.{tablename}_daily_metrics`
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

@background_cache(ttl_hours=1)
def load_last_orders():
    if toast_alerts():
        st.toast("Carregando últimos pedidos...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    project_name = get_project_name(tablename)
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
        FROM `{project_name}.dbt_join.{tablename}_orders_sessions`
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

def load_coffeemais_users():
    
    query = f"""
        select
            updated_at,
            email,
            name,
            phone,
            first_lead_source,
            first_lead_medium,
            first_lead_campaign,
            first_lead_content,
            first_lead_term,
            first_lead_page_location,

            last_purchase_date,
            last_purchase_revenue,
            last_purchase_cluster,
            first_purchase_date,
            first_purchase_revenue,
            first_purchase_cluster,
            total_revenue,
            purchase_quantity,

            pagbrasil_recurrence_id,
            pagbrasil_recurrence_number,
            pagbrasil_subscription_link,
            pagbrasil_payment_date,
            pagbrasil_subscription_status,
            pagbrasil_order_status
        from `coffee-mais-mkt-data-lake.df_summary.users`
        order by updated_at desc
    """

    df = run_queries([query])[0]
    return df
        

def load_internal_events():

    query = f"""
        SELECT

        created_at,
        tablename,
        user,
        event_name,
        json_extract_scalar(event_params, "$.tab") tab

        FROM `mymetric-hub-shopify.dbt_config.events`
    """

    df = run_queries([query])[0]
    return df


def load_coffeemais_crm():

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        select

        channel,
        datetime(min(timestamp)) date_first_sent,
        datetime(max(timestamp)) date_last_sent,
        date_diff(datetime(max(timestamp)), datetime(min(timestamp)), DAY) days_between,
        nome_notificacao name,
        count(*) sent,
        sum(case when type in("delivered","read") then 1 else 0 end) delivered,
        sum(case when type in("failed") then 1 else 0 end) failed,
        sum(case when type in("read") then 1 else 0 end) read,
        count(distinct order_id) orders,
        sum(revenue) revenue

        from `coffee-mais-mkt-data-lake.dbt_dito.dito_message_sent_results`

        where

        date(timestamp) between "{start_date}" and "{end_date}"

        group by all

        order by sent desc
        
    """

    df = run_queries([query])[0]
    return df

def load_coffeemais_crm_detailed():

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    query = f"""
        select

        channel,
        id_notificacao,
        id_disparo,
        email,
        datetime(min(timestamp)) date_first_sent,
        datetime(max(timestamp)) date_last_sent,
        date_diff(datetime(max(timestamp)), datetime(min(timestamp)), DAY) days_between,
        nome_notificacao name,
        count(*) sent,
        sum(case when type in("delivered","read") then 1 else 0 end) delivered,
        sum(case when type in("failed") then 1 else 0 end) failed,
        sum(case when type in("read") then 1 else 0 end) read,
        order_id,
        hours_between,
        count(distinct order_id) orders,
        sum(revenue) revenue

        from `coffee-mais-mkt-data-lake.dbt_dito.dito_message_sent_results`

        where

        
        date(timestamp) between "{start_date}" and "{end_date}"

        group by all

        order by sent desc
        
    """

    df = run_queries([query])[0]
    return df

def save_traffic_categories(category_name, description, rules):
    """
    Salva uma nova categoria de tráfego no BigQuery.
    """
    if toast_alerts():
        st.toast("Salvando categoria de tráfego...")

    tablename = st.session_state.tablename
    print(f"Salvando categoria para tablename: {tablename}")

    try:
        # Verificar se a categoria já existe usando parâmetros
        check_query = """
            SELECT COUNT(*) as count
            FROM `mymetric-hub-shopify.dbt_config.traffic_categories`
            WHERE tablename = @tablename
            AND category_name = @category_name
        """
        
        check_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("category_name", "STRING", category_name),
            ]
        )
        
        check_result = client.query(check_query, job_config=check_config).result()
        count = next(check_result).count

        if count > 0:
            st.error("Esta categoria já existe!")
            return False

        # Converter regras para JSON
        rules_json = json.dumps(rules)

        # Inserir nova categoria usando parâmetros
        insert_query = """
            INSERT INTO `mymetric-hub-shopify.dbt_config.traffic_categories`
            (tablename, category_name, description, rules, created_at)
            VALUES
            (@tablename, @category_name, @description, @rules, CURRENT_TIMESTAMP())
        """
        
        insert_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("category_name", "STRING", category_name),
                bigquery.ScalarQueryParameter("description", "STRING", description),
                bigquery.ScalarQueryParameter("rules", "STRING", rules_json),
            ]
        )

        client.query(insert_query, job_config=insert_config).result()
        print(f"Categoria {category_name} salva com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao salvar categoria: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def load_traffic_categories():
    """
    Carrega as categorias de tráfego do BigQuery.
    """
    if toast_alerts():
        st.toast("Carregando categorias de tráfego...")

    # Debug: Imprimir todo o estado da sessão
    print("Estado completo da sessão:")
    for key, value in st.session_state.items():
        print(f"{key}: {value}")

    tablename = st.session_state.get('tablename')
    print(f"Tablename obtido da sessão: {tablename}")

    if not tablename:
        print("Erro: tablename não está definido na sessão")
        return pd.DataFrame()

    try:
        # Usar parâmetros de consulta para evitar problemas com caracteres especiais
        query = """
            SELECT 
                category_name as Nome,
                description as Descricao,
                rules as Regras
            FROM `mymetric-hub-shopify.dbt_config.traffic_categories`
            WHERE tablename = @tablename
            ORDER BY category_name
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
            ]
        )
        
        print(f"Executando query com tablename: {tablename}")
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        df = pd.DataFrame([dict(row) for row in rows])
        
        print(f"DataFrame criado com {len(df)} linhas")
        print(f"Colunas do DataFrame: {df.columns.tolist()}")
        
        # Converter regras de JSON para dicionário
        if not df.empty and 'Regras' in df.columns:
            print("Convertendo regras de JSON para dicionário...")
            df['Regras'] = df['Regras'].apply(lambda x: json.loads(x) if x else {})
            
            # Debug: Imprimir informações sobre as categorias carregadas
            print(f"Carregadas {len(df)} categorias:")
            for _, row in df.iterrows():
                print(f"- {row['Nome']}")
                print(f"  Regras: {row['Regras']}")
        else:
            print("DataFrame vazio ou coluna 'Regras' não encontrada")
        
        # Renomear a coluna de volta para 'Descrição'
        if 'Descricao' in df.columns:
            df = df.rename(columns={'Descricao': 'Descrição'})
        
        return df
    except Exception as e:
        print(f"Erro ao carregar categorias: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return pd.DataFrame()

def delete_traffic_category(category_name):
    """
    Deleta uma categoria de tráfego do BigQuery.
    """
    if toast_alerts():
        st.toast("Deletando categoria de tráfego...")

    tablename = st.session_state.tablename
    print(f"Deletando categoria {category_name} para tablename: {tablename}")

    try:
        # Deletar categoria usando parâmetros
        delete_query = """
            DELETE FROM `mymetric-hub-shopify.dbt_config.traffic_categories`
            WHERE tablename = @tablename
            AND category_name = @category_name
        """
        
        delete_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("category_name", "STRING", category_name),
            ]
        )

        client.query(delete_query, job_config=delete_config).result()
        print(f"Categoria {category_name} deletada com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao deletar categoria: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

def save_event_name(event_name, event_params=None):
    """
    Salva um evento no BigQuery.
    
    Args:
        event_name (str): Nome do evento
        event_params (dict, optional): Parâmetros adicionais do evento
        
    Returns:
        bool: True se o evento foi salvo com sucesso, False caso contrário
    """
    try:
        # Obter informações da sessão
        tablename = st.session_state.get('tablename')
        username = st.session_state.get('username')
        
        if not tablename or not username:
            return False
            
        # Converter parâmetros para JSON se existirem
        event_params_json = json.dumps(event_params) if event_params else None
        
        # Query para inserir o evento
        query = """
            INSERT INTO `mymetric-hub-shopify.dbt_config.events`
            (tablename, user, event_name, event_params, created_at)
            VALUES
            (@tablename, @user, @event_name, @event_params, CURRENT_TIMESTAMP())
        """
        
        # Configurar parâmetros da query
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("user", "STRING", username),
                bigquery.ScalarQueryParameter("event_name", "STRING", event_name),
                bigquery.ScalarQueryParameter("event_params", "STRING", event_params_json),
            ]
        )
        
        # Executar query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Aguardar conclusão
        
        # Verificar se houve erros
        if query_job.errors:
            return False
            
        # Verificar se o evento foi realmente inserido
        verify_query = """
            SELECT COUNT(*) as count
            FROM `mymetric-hub-shopify.dbt_config.events`
            WHERE tablename = @tablename
            AND user = @user
            AND event_name = @event_name
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 MINUTE)
        """
        
        verify_job = client.query(verify_query, job_config=job_config)
        verify_result = verify_job.result()
        count = next(verify_result).count
        
        return count > 0
        
    except Exception as e:
        return False

def save_client(tablename, configs):
    """
    Salva os dados de um cliente no BigQuery.
    
    Args:
        tablename (str): Nome da tabela do cliente
        configs (str): JSON string com as configurações do cliente
        
    Returns:
        bool: True se o cliente foi salvo com sucesso, False caso contrário
    """
    try:
        # Query para inserir ou atualizar o cliente
        query = """
            MERGE `mymetric-hub-shopify.dbt_config.customers` AS target
            USING (SELECT @tablename as tablename, @configs as configs) AS source
            ON target.tablename = source.tablename
            WHEN MATCHED THEN
                UPDATE SET 
                    configs = source.configs,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (tablename, configs, created_at, updated_at)
                VALUES (source.tablename, source.configs, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """
        
        # Configurar parâmetros da query
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("configs", "STRING", configs),
            ]
        )
        
        # Executar query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Aguardar conclusão
        
        return True
        
    except Exception as e:
        print(f"Erro ao salvar cliente: {str(e)}")
        return False

def load_clients():
    """
    Carrega todos os clientes cadastrados do BigQuery.
    
    Returns:
        pd.DataFrame: DataFrame com os dados dos clientes
    """
    try:
        print("Iniciando carregamento de clientes...")
        
        query = """
            SELECT 
                tablename,
                configs,
                created_at,
                updated_at
            FROM `mymetric-hub-shopify.dbt_config.customers`
            ORDER BY tablename
        """
        
        print("Executando query...")
        query_job = client.query(query)
        
        print("Aguardando resultado da query...")
        rows = query_job.result()
        
        print("Convertendo resultados para DataFrame...")
        df = pd.DataFrame([dict(row) for row in rows])
        
        print(f"DataFrame criado com {len(df)} linhas")
        
        # Converter configs de JSON para dicionário
        if not df.empty and 'configs' in df.columns:
            print("Convertendo configs de JSON para dicionário...")
            df['configs'] = df['configs'].apply(lambda x: json.loads(x) if x else {})
            print("Conversão concluída")
        else:
            print("DataFrame vazio ou coluna 'configs' não encontrada")
        
        return df
        
    except Exception as e:
        print(f"Erro ao carregar clientes: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return pd.DataFrame()

def load_costs():
    """
    Carrega os custos do BigQuery.
    """
    if toast_alerts():
        st.toast("Carregando custos...")

    tablename = st.session_state.get('tablename')
    print(f"Tablename obtido da sessão: {tablename}")

    if not tablename:
        print("Erro: tablename não está definido na sessão")
        return pd.DataFrame()

    try:
        # Usar parâmetros de consulta para evitar problemas com caracteres especiais
        query = """
            SELECT 
                configs as Configs
            FROM `mymetric-hub-shopify.dbt_config.costs`
            WHERE tablename = @tablename
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
            ]
        )
        
        print(f"Executando query com tablename: {tablename}")
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        
        # Inicializar lista de registros
        records = []
        
        # Processar cada linha do resultado
        for row in rows:
            if row.Configs:
                try:
                    # Converter configs de JSON para dicionário
                    configs = json.loads(row.Configs)
                    print(f"Configs carregadas: {configs}")
                    
                    # Criar registros para cada mês e categoria
                    for month, month_data in configs.items():
                        for category, category_data in month_data.items():
                            records.append({
                                'Mês': month,
                                'Categoria': category,
                                'Custo do Produto (%)': category_data.get('cost_of_product_percentage', 0),
                                'Custo Total': category_data.get('total_cost', 0)
                            })
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                    continue
        
        # Criar DataFrame com os registros
        if records:
            df = pd.DataFrame(records)
            print(f"DataFrame criado com {len(df)} registros")
            return df
        else:
            print("Nenhum registro encontrado")
            return pd.DataFrame()
        
    except Exception as e:
        print(f"Erro ao carregar custos: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return pd.DataFrame()

def save_costs(month, category, cost_of_product_percentage, total_cost):
    """
    Salva os custos no BigQuery.
    """
    if toast_alerts():
        st.toast("Salvando custos...")

    tablename = st.session_state.tablename
    print(f"Salvando custos para tablename: {tablename}")
    print(f"Dados recebidos: month={month}, category={category}, cost_of_product_percentage={cost_of_product_percentage}, total_cost={total_cost}")

    try:
        # Verificar se a tabela existe
        check_table_query = """
            SELECT COUNT(*) as count
            FROM `mymetric-hub-shopify.dbt_config.__TABLES__`
            WHERE table_id = 'costs'
        """
        table_exists = client.query(check_table_query).result()
        if not table_exists:
            print("Tabela costs não existe. Criando...")
            create_table_query = """
                CREATE TABLE IF NOT EXISTS `mymetric-hub-shopify.dbt_config.costs`
                (
                    tablename STRING,
                    configs STRING,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """
            client.query(create_table_query).result()
            print("Tabela costs criada com sucesso")

        # Carregar configurações existentes
        query = """
            SELECT configs
            FROM `mymetric-hub-shopify.dbt_config.costs`
            WHERE tablename = @tablename
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        
        # Inicializar ou carregar configs existentes
        configs = {}
        for row in rows:
            if row.configs:
                try:
                    configs = json.loads(row.configs)
                    print(f"Configs carregadas: {configs}")
                    break
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON existente: {e}")
                    configs = {}
                    break
        
        # Garantir que o mês existe
        if month not in configs:
            configs[month] = {}
            print(f"Novo mês adicionado: {month}")
        
        # Atualizar ou criar categoria
        configs[month][category] = {
            "cost_of_product_percentage": float(cost_of_product_percentage),
            "total_cost": float(total_cost)
        }
        print(f"Configs atualizadas: {configs}")
        
        # Converter configs para JSON
        configs_json = json.dumps(configs)
        print(f"JSON gerado: {configs_json}")
        
        # Inserir ou atualizar usando MERGE
        merge_query = """
            MERGE `mymetric-hub-shopify.dbt_config.costs` AS target
            USING (SELECT @tablename as tablename, @configs as configs) AS source
            ON target.tablename = source.tablename
            WHEN MATCHED THEN
                UPDATE SET 
                    configs = source.configs,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (tablename, configs, created_at, updated_at)
                VALUES (source.tablename, source.configs, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """
        
        merge_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("tablename", "STRING", tablename),
                bigquery.ScalarQueryParameter("configs", "STRING", configs_json),
            ]
        )
        
        merge_job = client.query(merge_query, job_config=merge_config)
        merge_job.result()  # Aguardar conclusão
        
        # Verificar se houve erros
        if merge_job.errors:
            print(f"Erros na query MERGE: {merge_job.errors}")
            return False
            
        print(f"Custos salvos com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao salvar custos: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False



def load_kaisan_erp_orders():

    query = """
SELECT

  date(event_timestamp) date,
  order_status status,
  carrier_name transportadora,
  marketplace_store marketplace,
  address_state estado,
  address_city cidade,
  payment_description metodo_pagamento,

  sum(case when item_no = 1 then total_value end) receita,
  sum(case when item_no = 1 then total_discount end) descontos,
  sum(case when item_no = 1 then 1 end) pedidos,
  sum(qty) itens_vendidos,
  sum(qty*costValue) custo,

FROM `gtm-nc5rvpcz-y2e0m.erp.orders_dedup`

group by all


    """

    df = run_queries([query])[0]

    return df

def load_coffeemais_gupshup_errors():

    query = """

        SELECT
  
        datetime(timestamp_millis(timestamp), "America/Sao_Paulo") datetime,
        message_id,
        fail_reason,
        fail_destination phone_destination

        FROM `gtm-ppnx52h-ytkzm.gupshup.structured`

        where

        source = "gupshup_fail"    
        and datetime(timestamp_millis(timestamp), "America/Sao_Paulo") >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    """

    df = run_queries([query])[0]

    return df

@background_cache(ttl_hours=0.1666)
def load_purchase_items():
    if toast_alerts():
        st.toast("Carregando itens de compra...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    project_name = get_project_name(tablename)

    query = f"""
        SELECT
            event_timestamp,
            concat(ga_session_id, user_pseudo_id) session_id,
            transaction_id,
            item_category,
            item_name,
            quantity,
            item_revenue,
            source,
            medium,
            campaign,
            content,
            term,
            page_location
        FROM
            `{project_name}.dbt_join.{tablename}_purchases_items_sessions_realtime`
    """

    df = run_queries([query])[0]
    return df

@background_cache(ttl_hours=1)
def load_purchase_items_sessions():
    if toast_alerts():
        st.toast("Carregando itens de compra por sessão...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    start_date_str = st.session_state.start_date
    end_date_str = st.session_state.end_date

    # Otimização para quando as datas são iguais
    date_condition = f"event_date = '{start_date_str}'" if start_date_str == end_date_str else f"event_date BETWEEN '{start_date_str}' AND '{end_date_str}'"

    project_name = get_project_name(tablename)
    query = f"""
        SELECT
            event_date `Data`,
            item.item_id `ID do Produto`,
            item.item_name `Nome do Produto`,
            item.item_revenue `Receita`,
            item.quantity `Quantidade`,
            traffic_category `Cluster`,
            source `Origem`,
            medium `Mídia`,
            campaign `Campanha`,
            content `Conteúdo`,
            term `Termo`,
            landing_page `Página de Entrada`
        FROM `{project_name}.dbt_join.{tablename}_enhanced_ecommerce_sessions`, 
        UNNEST(items) as item
        WHERE event_name = "purchase"
        AND {date_condition}
        ORDER BY event_date DESC
    """

    try:
        query_job = client.query(query)
        rows = query_job.result()
        df = pd.DataFrame([dict(row) for row in rows])
        return df
    except Exception as e:
        print(f"Erro ao carregar itens de compra: {str(e)}")
        return pd.DataFrame()

@background_cache(ttl_hours=1)
def load_intraday_ecommerce_funnel():
    """
    Carrega dados de funil de ecommerce para o dia atual e o anterior.
    Retorna um DataFrame com eventos agrupados por hora.
    """
    if toast_alerts():
        st.toast("Carregando funil intraday...")

    tablename = st.session_state.tablename
    if not tablename:
        raise ValueError("tablename não está definido na sessão")

    project_name = get_project_name(tablename)

    query = f"""
        select
            event_date,
            extract(hour from datetime(timestamp_micros(event_timestamp), "America/Sao_Paulo")) hour,
            event_name,
            count(*) events
        from `{project_name}.dbt_granular.{tablename}_enhanced_ecommerce_only_intraday`
        where
            event_name in("add_payment_info","add_shipping_info","add_to_cart","begin_checkout","purchase","view_item")
            and event_date >= date_sub(current_date("America/Sao_Paulo"), interval 1 day)
        group by all
        order by hour desc
    """

    df = run_queries([query])[0]
    return df