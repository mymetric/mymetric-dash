import requests
import streamlit as st
import sys
import json
import calendar
from datetime import datetime
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from core.users import load_users

def load_goals(tablename):
    """
    Carrega as metas para uma tabela específica.
    """
    try:
        # Configurar credenciais do BigQuery
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)

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
    except Exception as e:
        print(f"Erro ao carregar metas: {str(e)}")
        return pd.DataFrame()

def load_current_month_revenue(tablename):
    """
    Carrega a receita do mês atual para uma tabela específica.
    """
    try:
        # Configurar credenciais do BigQuery
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)

        hoje = pd.Timestamp.now(tz='America/Sao_Paulo')
        primeiro_dia = hoje.replace(day=1).strftime('%Y-%m-%d')
        ontem = (hoje - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        # Ajusta a query baseado na tabela
        if tablename == 'wtennis':
            query = f"""
            WITH filtered_events AS (
                SELECT 
                    value,
                    total_discounts
                FROM `{project_id}.dbt_join.{tablename}_events_long`
                WHERE event_date BETWEEN '{primeiro_dia}' AND '{ontem}'
                AND event_name = 'purchase'
                AND status in ('paid', 'authorized')
            )
            SELECT SUM(value - COALESCE(total_discounts, 0)) as total_mes
            FROM filtered_events
            """
        else:
            query = f"""
            SELECT SUM(CASE 
                WHEN event_name = 'purchase' and status in ('paid', 'authorized') 
                THEN value - COALESCE(total_discounts, 0) + COALESCE(shipping_value, 0)
                ELSE 0 
            END) as total_mes
            FROM `{project_id}.dbt_join.{tablename}_events_long`
            WHERE event_date BETWEEN '{primeiro_dia}' AND '{ontem}'
            """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar receita: {str(e)}")
        return pd.DataFrame()

def load_yesterday_revenue(tablename):
    """
    Carrega a receita do dia anterior.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        # Ajusta a query baseado na tabela
        if tablename == 'wtennis':
            query = f"""
            WITH filtered_events AS (
                SELECT 
                    value,
                    total_discounts
                FROM `{project_id}.dbt_join.{tablename}_events_long`
                WHERE event_date = date_sub(current_date(), interval 1 day)
                AND event_name = 'purchase'
                AND status in ('paid', 'authorized')
            )
            SELECT COALESCE(SUM(value - COALESCE(total_discounts, 0)), 0) as total_ontem
            FROM filtered_events
            """
        else:
            query = f"""
            SELECT COALESCE(SUM(CASE 
                WHEN event_name = 'purchase' and status in ('paid', 'authorized') 
                THEN value - COALESCE(total_discounts, 0) + COALESCE(shipping_value, 0)
                ELSE 0 
            END), 0) as total_ontem
            FROM `{project_id}.dbt_join.{tablename}_events_long`
            WHERE event_date = date_sub(current_date(), interval 1 day)
            """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar receita de ontem: {str(e)}")
        return pd.DataFrame()

def load_yesterday_sessions(tablename):
    """
    Carrega o número de sessões do dia anterior, usando fallback para _sessions_intraday se necessário.
    Retorna None se a data de ontem não existir em nenhuma das tabelas.
    """
    try:
        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
        client = bigquery.Client(credentials=credentials)
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        # Descobrir a data de ontem
        from datetime import datetime, timedelta
        ontem = (datetime.now() - timedelta(days=1)).date()
        ontem_str = str(ontem)
        
        # 1. Verificar se a data de ontem existe na tabela principal
        check_main = f"""
        SELECT COUNT(*) as n FROM `{project_id}.dbt_granular.{tablename}_sessions` WHERE event_date = DATE('{ontem_str}')
        """
        res_main = list(client.query(check_main).result())
        if res_main and res_main[0].n > 0:
            # Buscar o count real
            query_main = f"""
            SELECT COUNT(*) as total_sessions
            FROM `{project_id}.dbt_granular.{tablename}_sessions`
            WHERE event_date = DATE('{ontem_str}')
            """
            rows = [dict(row) for row in client.query(query_main).result()]
            return pd.DataFrame(rows)
        # 2. Se não houver na principal, verificar na intraday
        check_intraday = f"""
        SELECT COUNT(*) as n FROM `{project_id}.dbt_granular.{tablename}_sessions_intraday` WHERE event_date = DATE('{ontem_str}')
        """
        res_intraday = list(client.query(check_intraday).result())
        if res_intraday and res_intraday[0].n > 0:
            query_intraday = f"""
            SELECT COUNT(*) as total_sessions
            FROM `{project_id}.dbt_granular.{tablename}_sessions_intraday`
            WHERE event_date = DATE('{ontem_str}')
            """
            rows2 = [dict(row) for row in client.query(query_intraday).result()]
            return pd.DataFrame(rows2)
        # 3. Se a data não existe em nenhuma, retorna None
        return None
    except Exception as e:
        print(f"Erro ao carregar sessões de ontem: {str(e)}")
        return None

def load_day_before_yesterday_revenue(tablename):
    """
    Carrega a receita de anteontem.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        # Ajusta a query baseado na tabela
        if tablename == 'wtennis':
            query = f"""
            WITH filtered_events AS (
                SELECT 
                    value,
                    total_discounts
                FROM `{project_id}.dbt_join.{tablename}_events_long`
                WHERE event_date = date_sub(current_date(), interval 2 day)
                AND event_name = 'purchase'
                AND status in ('paid', 'authorized')
            )
            SELECT COALESCE(SUM(value - COALESCE(total_discounts, 0)), 0) as total_anteontem
            FROM filtered_events
            """
        else:
            query = f"""
            SELECT COALESCE(SUM(CASE 
                WHEN event_name = 'purchase' and status in ('paid', 'authorized') 
                THEN value - COALESCE(total_discounts, 0) + COALESCE(shipping_value, 0)
                ELSE 0 
            END), 0) as total_anteontem
            FROM `{project_id}.dbt_join.{tablename}_events_long`
            WHERE event_date = date_sub(current_date(), interval 2 day)
            """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar receita de anteontem: {str(e)}")
        return pd.DataFrame()

def load_day_before_yesterday_sessions(tablename):
    """
    Carrega o número de sessões de anteontem, usando fallback para _sessions_intraday se necessário.
    Retorna None se a data de anteontem não existir em nenhuma das tabelas.
    """
    try:
        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
        client = bigquery.Client(credentials=credentials)
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        from datetime import datetime, timedelta
        anteontem = (datetime.now() - timedelta(days=2)).date()
        anteontem_str = str(anteontem)
        
        check_main = f"""
        SELECT COUNT(*) as n FROM `{project_id}.dbt_granular.{tablename}_sessions` WHERE event_date = DATE('{anteontem_str}')
        """
        res_main = list(client.query(check_main).result())
        if res_main and res_main[0].n > 0:
            query_main = f"""
            SELECT COUNT(*) as total_sessions
            FROM `{project_id}.dbt_granular.{tablename}_sessions`
            WHERE event_date = DATE('{anteontem_str}')
            """
            rows = [dict(row) for row in client.query(query_main).result()]
            return pd.DataFrame(rows)
        check_intraday = f"""
        SELECT COUNT(*) as n FROM `{project_id}.dbt_granular.{tablename}_sessions_intraday` WHERE event_date = DATE('{anteontem_str}')
        """
        res_intraday = list(client.query(check_intraday).result())
        if res_intraday and res_intraday[0].n > 0:
            query_intraday = f"""
            SELECT COUNT(*) as total_sessions
            FROM `{project_id}.dbt_granular.{tablename}_sessions_intraday`
            WHERE event_date = DATE('{anteontem_str}')
            """
            rows2 = [dict(row) for row in client.query(query_intraday).result()]
            return pd.DataFrame(rows2)
        return None
    except Exception as e:
        print(f"Erro ao carregar sessões de anteontem: {str(e)}")
        return None

def load_funnel_comparison(tablename):
    """
    Carrega as taxas de funil de ontem vs anteontem.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        query = f"""
        SELECT
            event_date,
            event_name,
            COUNT(*) as events
        FROM `{project_id}.dbt_granular.{tablename}_enhanced_ecommerce_only_intraday`
        WHERE event_name IN ('view_item', 'add_to_cart', 'begin_checkout', 'add_shipping_info', 'add_payment_info', 'purchase')
        AND event_date IN (date_sub(current_date(), interval 1 day), date_sub(current_date(), interval 2 day))
        GROUP BY event_date, event_name
        ORDER BY event_date, event_name
        """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        df = pd.DataFrame(rows)
        
        if df.empty:
            return pd.DataFrame()
        
        # Separar dados de ontem e anteontem
        ontem = (pd.Timestamp.now(tz='America/Sao_Paulo') - pd.Timedelta(days=1)).date()
        anteontem = (pd.Timestamp.now(tz='America/Sao_Paulo') - pd.Timedelta(days=2)).date()
        
        df_ontem = df[df['event_date'] == ontem]
        df_anteontem = df[df['event_date'] == anteontem]
        
        # Calcular totais por evento
        totais_ontem = df_ontem.groupby('event_name')['events'].sum()
        totais_anteontem = df_anteontem.groupby('event_name')['events'].sum()
        
        # Calcular taxas de conversão
        taxas_ontem = {
            'Visualização → Carrinho': round(totais_ontem.get('add_to_cart', 0) / totais_ontem.get('view_item', 1) * 100, 2),
            'Carrinho → Checkout': round(totais_ontem.get('begin_checkout', 0) / totais_ontem.get('add_to_cart', 1) * 100, 2),
            'Checkout → Frete': round(totais_ontem.get('add_shipping_info', 0) / totais_ontem.get('begin_checkout', 1) * 100, 2),
            'Frete → Pagamento': round(totais_ontem.get('add_payment_info', 0) / totais_ontem.get('add_shipping_info', 1) * 100, 2),
            'Pagamento → Pedido': round(totais_ontem.get('purchase', 0) / totais_ontem.get('add_payment_info', 1) * 100, 2),
            'Visualização → Pedido': round(totais_ontem.get('purchase', 0) / totais_ontem.get('view_item', 1) * 100, 2)
        }
        
        taxas_anteontem = {
            'Visualização → Carrinho': round(totais_anteontem.get('add_to_cart', 0) / totais_anteontem.get('view_item', 1) * 100, 2),
            'Carrinho → Checkout': round(totais_anteontem.get('begin_checkout', 0) / totais_anteontem.get('add_to_cart', 1) * 100, 2),
            'Checkout → Frete': round(totais_anteontem.get('add_shipping_info', 0) / totais_anteontem.get('begin_checkout', 1) * 100, 2),
            'Frete → Pagamento': round(totais_anteontem.get('add_payment_info', 0) / totais_anteontem.get('add_shipping_info', 1) * 100, 2),
            'Pagamento → Pedido': round(totais_anteontem.get('purchase', 0) / totais_anteontem.get('add_payment_info', 1) * 100, 2),
            'Visualização → Pedido': round(totais_anteontem.get('purchase', 0) / totais_anteontem.get('view_item', 1) * 100, 2)
        }
        
        # Criar DataFrame de comparação
        df_comparison = pd.DataFrame({
            'Etapa': list(taxas_ontem.keys()),
            'Ontem (%)': list(taxas_ontem.values()),
            'Anteontem (%)': list(taxas_anteontem.values())
        })
        
        # Calcular variação percentual
        df_comparison['Variação (%)'] = ((df_comparison['Ontem (%)'] - df_comparison['Anteontem (%)']) / df_comparison['Anteontem (%)'] * 100).round(2)
        
        return df_comparison
        
    except Exception as e:
        print(f"Erro ao carregar comparação de funil: {str(e)}")
        return pd.DataFrame()

def load_duplicate_sessions(tablename):
    """
    Carrega o percentual de sessões duplicadas.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        query = f"""
        with prep as (
            SELECT
                event_date,
                user_pseudo_id,
                ga_session_id,
                LAG(ga_session_id) OVER (
                    PARTITION BY user_pseudo_id
                    ORDER BY ga_session_id
                ) AS previous_ga_session_id
            FROM `{project_id}.dbt_granular.{tablename}_sessions`
        )
        select
            round(
                sum(
                    case
                        when ga_session_id - previous_ga_session_id is null then 0
                        when ga_session_id - previous_ga_session_id < 1800 then 1
                        else 0
                    end
                ) / count(*), 2) as duplicated_sessions
        from prep
        group by all
        """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar sessões duplicadas: {str(e)}")
        return pd.DataFrame()

def load_lost_cookies(tablename):
    """
    Carrega o percentual de perda de cookies.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        if tablename == "linus":
            query = f"""
            select
                1-round(count(distinct concat(user_pseudo_id, ga_session_id)) / count(*),2) lost_cookies
            from `{project_id}.dbt_granular.linus_orders_dedup`
            where
                date(created_at) = date_sub(current_date(), interval 1 day)
                and source_name = "web"
            group by all
            """

            query_job = client.query(query)
            rows_raw = query_job.result()
            rows = [dict(row) for row in rows_raw]
            return pd.DataFrame(rows)
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar perda de cookies: {str(e)}")
        return pd.DataFrame()

def load_utm_metrics(tablename):
    """
    Carrega as métricas de UTM e mm_ads para uma tabela específica.
    """
    try:
        # Configurar credenciais do BigQuery
        try:
            # Tenta usar as credenciais do Streamlit
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
        except:
            # Se falhar, tenta usar as credenciais do ambiente
            credentials = service_account.Credentials.from_service_account_file(
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "gcp-credentials.json")
            )
            
        client = bigquery.Client(credentials=credentials)
        
        # Define o project_id baseado na empresa
        project_id = "bq-mktbr" if tablename == "havaianas" else "mymetric-hub-shopify"
        
        query = f"""
        SELECT
            sum(case when page_params like "%utm%" then 1 else 0 end)/count(*) as with_utm,
            sum(case when page_params like "%mm_ads%" then 1 else 0 end)/count(*) as with_mm_ads
        FROM `{project_id}.dbt_granular.{tablename}_sessions`
        WHERE page_params like "%fbclid%"
        """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar métricas de UTM: {str(e)}")
        return pd.DataFrame()

def send_whatsapp_message(message, phone):
    """
    Envia uma mensagem via WhatsApp usando o Z-API.
    
    Args:
        message (str): Mensagem a ser enviada
        phone (str): Número do telefone ou ID do grupo
    """
    try:
        # Configurações do Z-API
        zapi_payload = {
            "phone": phone,
            "message": message
        }

        # Enviar para o Z-API
        response = requests.post(
            st.secrets["zapi"]["url"],
            json=zapi_payload,
            headers={"Client-Token": st.secrets["zapi"]["client_token"]}
        )

        if response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso para {phone}!")
        else:
            print(f"❌ Erro ao enviar mensagem para {phone}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para {phone}: {str(e)}")

def send_goal_alert(tablename, phone, testing_mode=False):
    """
    Envia um alerta com o status da meta do mês via WhatsApp.
    
    Args:
        tablename (str): Nome da tabela para verificar a meta
        phone (str): Número do telefone ou ID do grupo
        testing_mode (bool): Se True, envia mensagem de teste
    """
    try:
        if testing_mode:
            message = f"""
*{tablename.upper()}*

Mensagem de Teste

Esta é uma mensagem de teste para verificar o funcionamento do sistema de alertas.
"""
            send_whatsapp_message(message, phone)
            return

        print(f"\nVerificando meta para {tablename}...")
        
        # Carregar métricas de UTM
        print("Carregando métricas de UTM...")
        df_utm = load_utm_metrics(tablename)
        print(f"DataFrame de métricas UTM: {df_utm}")
        with_utm = float(df_utm['with_utm'].iloc[0]) if not df_utm.empty else 0
        with_mm_ads = float(df_utm['with_mm_ads'].iloc[0]) if not df_utm.empty else 0
        print(f"Tráfego com UTM: {with_utm:.1%}")
        print(f"Tráfego com mm_ads: {with_mm_ads:.1%}")
        
        # Verificar alertas de UTM e mm_ads
        aviso_utm = with_utm < 0.90  # UTM menor que 90%
        aviso_mm_ads = with_mm_ads < (with_utm * 0.95)  # mm_ads menor que 95% do UTM
        
        # Carregar sessões duplicadas (sempre)
        print("Carregando sessões duplicadas...")
        df_duplicate = load_duplicate_sessions(tablename)
        print(f"DataFrame de sessões duplicadas: {df_duplicate}")
        duplicated_sessions = float(df_duplicate['duplicated_sessions'].iloc[0]) if not df_duplicate.empty else 0
        print(f"Sessões duplicadas: {duplicated_sessions}")
        aviso_duplicadas = duplicated_sessions > 0.02

        # Carregar perda de cookies (apenas para Linus)
        print("Carregando perda de cookies...")
        df_lost_cookies = load_lost_cookies(tablename)
        print(f"DataFrame de perda de cookies: {df_lost_cookies}")
        lost_cookies = float(df_lost_cookies['lost_cookies'].iloc[0]) if not df_lost_cookies.empty else 0
        print(f"Perda de cookies: {lost_cookies}")
        aviso_cookies = lost_cookies > 0.05

        # Carregar vendas de ontem
        print("Carregando vendas de ontem...")
        df_yesterday = load_yesterday_revenue(tablename)
        print(f"DataFrame de vendas de ontem: {df_yesterday}")
        vendas_ontem = float(df_yesterday['total_ontem'].iloc[0]) if not df_yesterday.empty else 0
        print(f"Vendas de ontem: {vendas_ontem}")

        # Carregar sessões de ontem
        print("Carregando sessões de ontem...")
        df_yesterday_sessions = load_yesterday_sessions(tablename)
        print(f"DataFrame de sessões de ontem: {df_yesterday_sessions}")
        if df_yesterday_sessions is None:
            sessoes_ontem = None
        else:
            sessoes_ontem = int(df_yesterday_sessions['total_sessions'].iloc[0]) if not df_yesterday_sessions.empty else 0
        print(f"Sessões de ontem: {sessoes_ontem}")

        # Carregar vendas de anteontem
        print("Carregando vendas de anteontem...")
        df_anteontem = load_day_before_yesterday_revenue(tablename)
        print(f"DataFrame de vendas de anteontem: {df_anteontem}")
        vendas_anteontem = float(df_anteontem['total_anteontem'].iloc[0]) if not df_anteontem.empty else 0
        print(f"Vendas de anteontem: {vendas_anteontem}")

        # Carregar sessões de anteontem
        print("Carregando sessões de anteontem...")
        df_anteontem_sessions = load_day_before_yesterday_sessions(tablename)
        print(f"DataFrame de sessões de anteontem: {df_anteontem_sessions}")
        if df_anteontem_sessions is None:
            sessoes_anteontem = None
        else:
            sessoes_anteontem = int(df_anteontem_sessions['total_sessions'].iloc[0]) if not df_anteontem_sessions.empty else 0
        print(f"Sessões de anteontem: {sessoes_anteontem}")

        # Verificar alertas de vendas e sessões zeradas
        aviso_vendas_zeradas = vendas_ontem == 0
        aviso_sessoes_zeradas = (sessoes_ontem == 0) if sessoes_ontem is not None else False

        # Carregar comparação de taxas de funil
        print("Carregando comparação de taxas de funil...")
        df_funnel = load_funnel_comparison(tablename)
        print(f"DataFrame de comparação de funil: {df_funnel}")

        # Verificar métricas zeradas do funil
        aviso_funil_zerado = False
        etapas_zeradas = []
        if not df_funnel.empty:
            for _, row in df_funnel.iterrows():
                etapa = row['Etapa']
                taxa_ontem = row['Ontem (%)']
                if taxa_ontem == 0:
                    aviso_funil_zerado = True
                    etapas_zeradas.append(etapa)

        # Carregar metas
        print("Carregando metas...")
        df_goals = load_goals(tablename)
        print(f"DataFrame de metas: {df_goals}")
        
        if df_goals.empty or 'goals' not in df_goals.columns or df_goals['goals'].isna().all():
            print(f"❌ DataFrame de metas vazio ou coluna ausente para {tablename}")
            msg = f"*{tablename.upper()}*\n\n❌ *Meta do mês não cadastrada*\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas"
            
            # Adicionar alertas de vendas e sessões zeradas
            if aviso_vendas_zeradas:
                msg += f"\n\n🚨 *ALERTA: Vendas Zeradas*\n💰 Vendas de ontem: R$ 0,00"
            if sessoes_ontem is None:
                msg += f"\n\n🚨 *ALERTA: Sessões*\n📊 Sessões de ontem: Dados não disponíveis"
            elif aviso_sessoes_zeradas:
                msg += f"\n\n🚨 *ALERTA: Sessões Zeradas*\n📊 Sessões de ontem: 0"
            
            # Adicionar alerta de funil zerado
            if aviso_funil_zerado:
                msg += f"\n\n🚨 *ALERTA: Funil Zerado*"
                for etapa in etapas_zeradas:
                    msg += f"\n- {etapa}"
            
            if aviso_duplicadas:
                msg += f"\n\n🔄 *Qualidade dos Dados*\n📊 Sessões duplicadas: {duplicated_sessions:.1%}"
            if aviso_cookies:
                msg += f"\n📊 Perda de cookies: {lost_cookies:.1%}"
            if vendas_ontem > 0:
                msg += f"\n\n📊 *Vendas de Ontem*\n💰 Total: R$ {vendas_ontem:,.2f}"
            
            # Adicionar comparação de taxas de funil se disponível
            if not df_funnel.empty:
                message += "\n\n🔄 Taxas de Funil (Ontem vs Anteontem)"
                for _, row in df_funnel.iterrows():
                    etapa = row['Etapa']
                    taxa_ontem = row['Ontem (%)']
                    taxa_anteontem = row['Anteontem (%)']
                    variacao = row['Variação (%)']
                    
                    # Adicionar emoji se variação > 10%
                    emoji = ""
                    if abs(variacao) > 10:
                        if variacao > 0:
                            emoji = "🟢 "
                        else:
                            emoji = "🔴 "
                    
                    message += f"\n- {emoji}{etapa}: {taxa_ontem:.1f}% ({variacao:+.1f}%)"
            
            send_whatsapp_message(msg, phone)
            return

        # Extrair meta do mês atual
        goals_json = df_goals['goals'].iloc[0]
        print(f"JSON de metas: {goals_json}")
        
        if not goals_json:
            print(f"❌ JSON de metas vazio para {tablename}")
            msg = f"*{tablename.upper()}*\n\n❌ *Meta do mês não cadastrada*\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas"
            
            # Adicionar alertas de vendas e sessões zeradas
            if aviso_vendas_zeradas:
                msg += f"\n\n🚨 *ALERTA: Vendas Zeradas*\n💰 Vendas de ontem: R$ 0,00"
            if sessoes_ontem is None:
                msg += f"\n\n🚨 *ALERTA: Sessões*\n📊 Sessões de ontem: Dados não disponíveis"
            elif aviso_sessoes_zeradas:
                msg += f"\n\n🚨 *ALERTA: Sessões Zeradas*\n📊 Sessões de ontem: 0"
            
            # Adicionar alerta de funil zerado
            if aviso_funil_zerado:
                msg += f"\n\n🚨 *ALERTA: Funil Zerado*"
                for etapa in etapas_zeradas:
                    msg += f"\n- {etapa}"
            
            if aviso_duplicadas:
                msg += f"\n\n🔄 *Qualidade dos Dados*\n📊 Sessões duplicadas: {duplicated_sessions:.1%}"
            if aviso_cookies:
                msg += f"\n📊 Perda de cookies: {lost_cookies:.1%}"
            if vendas_ontem > 0:
                msg += f"\n\n📊 *Vendas de Ontem*\n💰 Total: R$ {vendas_ontem:,.2f}"
            
            # Adicionar comparação de taxas de funil se disponível
            if not df_funnel.empty:
                message += "\n\n🔄 Taxas de Funil (Ontem vs Anteontem)"
                for _, row in df_funnel.iterrows():
                    etapa = row['Etapa']
                    taxa_ontem = row['Ontem (%)']
                    taxa_anteontem = row['Anteontem (%)']
                    variacao = row['Variação (%)']
                    
                    # Adicionar emoji se variação > 10%
                    emoji = ""
                    if abs(variacao) > 10:
                        if variacao > 0:
                            emoji = "🟢 "
                        else:
                            emoji = "🔴 "
                    
                    message += f"\n- {emoji}{etapa}: {taxa_ontem:.1f}% ({variacao:+.1f}%)"
            
            send_whatsapp_message(msg, phone)
            return

        metas = json.loads(goals_json)
        print(f"Metas carregadas: {metas}")
        
        current_month = datetime.now().strftime("%Y-%m")
        print(f"Mês atual: {current_month}")
        
        meta_receita = metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
        print(f"Meta de receita: {meta_receita}")

        if meta_receita == 0:
            print(f"❌ Meta de receita é zero para {tablename}")
            msg = f"*{tablename.upper()}*\n\n❌ *Meta do mês não cadastrada*\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas"
            
            # Adicionar alertas de vendas e sessões zeradas
            if aviso_vendas_zeradas:
                msg += f"\n\n🚨 *ALERTA: Vendas Zeradas*\n💰 Vendas de ontem: R$ 0,00"
            if sessoes_ontem is None:
                msg += f"\n\n🚨 *ALERTA: Sessões*\n📊 Sessões de ontem: Dados não disponíveis"
            elif aviso_sessoes_zeradas:
                msg += f"\n\n🚨 *ALERTA: Sessões Zeradas*\n📊 Sessões de ontem: 0"
            
            # Adicionar alerta de funil zerado
            if aviso_funil_zerado:
                msg += f"\n\n🚨 *ALERTA: Funil Zerado*\n"
                for etapa in etapas_zeradas:
                    msg += f"\n- {etapa}"
            
            if aviso_duplicadas:
                msg += f"\n\n🔄 *Qualidade dos Dados*\n📊 Sessões duplicadas: {duplicated_sessions:.1%}"
            if aviso_cookies:
                msg += f"\n📊 Perda de cookies: {lost_cookies:.1%}"
            if vendas_ontem > 0:
                msg += f"\n\n📊 *Vendas de Ontem*\n💰 Total: R$ {vendas_ontem:,.2f}"
            
            # Adicionar comparação de taxas de funil se disponível
            if not df_funnel.empty:
                message += "\n\n🔄 Taxas de Funil (Ontem vs Anteontem)"
                for _, row in df_funnel.iterrows():
                    etapa = row['Etapa']
                    taxa_ontem = row['Ontem (%)']
                    taxa_anteontem = row['Anteontem (%)']
                    variacao = row['Variação (%)']
                    
                    # Adicionar emoji se variação > 10%
                    emoji = ""
                    if abs(variacao) > 10:
                        if variacao > 0:
                            emoji = "🟢 "
                        else:
                            emoji = "🔴 "
                    
                    message += f"\n- {emoji}{etapa}: {taxa_ontem:.1f}% ({variacao:+.1f}%)"
            
            send_whatsapp_message(msg, phone)
            return

        # Carregar receita atual do mês
        print("Carregando receita atual do mês...")
        df_revenue = load_current_month_revenue(tablename)
        print(f"DataFrame de receita: {df_revenue}")
        total_receita_mes = float(df_revenue['total_mes'].iloc[0]) if not df_revenue.empty else 0
        print(f"Receita atual: {total_receita_mes}")

        # Calcular projeção para o final do mês
        hoje = datetime.now()
        dia_atual = hoje.day
        _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
        
        # Calcular média diária até ontem
        dias_passados = dia_atual - 1  # Considera até ontem
        media_diaria = total_receita_mes / dias_passados if dias_passados > 0 else 0
        
        # Calcular projeção considerando o mês inteiro
        projecao_final = (total_receita_mes / dias_passados) * ultimo_dia if dias_passados > 0 else 0

        # Calcular percentual atingido e projetado
        percentual_atingido = (total_receita_mes / meta_receita * 100) if meta_receita > 0 else 0
        percentual_projetado = (projecao_final / meta_receita * 100) if meta_receita > 0 else 0

        # Criar mensagem
        message = f"""
*{tablename.upper()}*

📊 Status da Meta

- Meta do mês: R$ {meta_receita:,.2f}
- Receita atual: R$ {total_receita_mes:,.2f}
- Percentual atingido: {percentual_atingido:.1f}%
- Média diária (até ontem): R$ {media_diaria:,.2f}
- Dias passados: {dias_passados} de {ultimo_dia}
- Projeção final: R$ {projecao_final:,.2f}
- Percentual projetado: {percentual_projetado:.1f}%
"""
        
        # Adicionar alertas de vendas e sessões zeradas
        if aviso_vendas_zeradas:
            message += f"\n\n🚨 *ALERTA: Vendas Zeradas*\n💰 Vendas de ontem: R$ 0,00"
        if sessoes_ontem is None:
            message += f"\n\n🚨 *ALERTA: Sessões*\n📊 Sessões de ontem: Dados não disponíveis"
        elif aviso_sessoes_zeradas:
            message += f"\n\n🚨 *ALERTA: Sessões Zeradas*\n📊 Sessões de ontem: 0"
        
        # Adicionar alerta de funil zerado
        if aviso_funil_zerado:
            message += f"\n\n🚨 *ALERTA: Funil Zerado*\n"
            for etapa in etapas_zeradas:
                message += f"\n- {etapa}"
        
        if vendas_ontem > 0:
            # Calcular variação de vendas
            variacao_vendas = ((vendas_ontem - vendas_anteontem) / vendas_anteontem * 100) if vendas_anteontem > 0 else 0
            emoji_vendas = ""
            if abs(variacao_vendas) > 10:
                if variacao_vendas > 0:
                    emoji_vendas = " 🟢"
                else:
                    emoji_vendas = " 🔴"
            
            message += f"\n\n💰 *Vendas de Ontem*\n- Total: R$ {vendas_ontem:,.2f}"
            if vendas_anteontem > 0:
                message += f"\n- Variação vs anteontem: {variacao_vendas:+.1f}%{emoji_vendas}"
            else:
                message += f"\n- Anteontem: Sem dados disponíveis"
        
        if sessoes_ontem is not None and sessoes_ontem > 0:
            # Calcular variação de sessões
            if sessoes_anteontem is not None and sessoes_anteontem > 0:
                variacao_sessoes = ((sessoes_ontem - sessoes_anteontem) / sessoes_anteontem * 100)
                emoji_sessoes = ""
                if abs(variacao_sessoes) > 10:
                    if variacao_sessoes > 0:
                        emoji_sessoes = " 🟢"
                    else:
                        emoji_sessoes = " 🔴"
                message += f"\n\n📊 Sessões de Ontem\n- Total: {sessoes_ontem:,}"
                message += f"\n- Variação vs anteontem: {variacao_sessoes:+.1f}%{emoji_sessoes}"
            else:
                message += f"\n\n📊 Sessões de Ontem\n- Total: {sessoes_ontem:,}"
                message += f"\n- Anteontem: Dados não disponíveis"
        elif sessoes_ontem is not None and sessoes_ontem == 0:
            message += f"\n\n📊 Sessões de Ontem\n- Total: 0"
            if sessoes_anteontem is not None and sessoes_anteontem > 0:
                message += f"\n- Variação vs anteontem: -100% 🔴"
            elif sessoes_anteontem is None:
                message += f"\n- Anteontem: Dados não disponíveis"

        # Adicionar comparação de taxas de funil se disponível
        if not df_funnel.empty:
            message += "\n\n🔄 Taxas de Funil (Ontem vs Anteontem)"
            for _, row in df_funnel.iterrows():
                etapa = row['Etapa']
                taxa_ontem = row['Ontem (%)']
                taxa_anteontem = row['Anteontem (%)']
                variacao = row['Variação (%)']
                
                # Adicionar emoji se variação > 10%
                emoji = ""
                if abs(variacao) > 10:
                    if variacao > 0:
                        emoji = " 🟢"
                    else:
                        emoji = " 🔴"
                
                message += f"\n- {etapa}: {taxa_ontem:.1f}% ({variacao:+.1f}%){emoji}"

        if aviso_duplicadas or aviso_cookies:
            message += "\n\n🔄 Qualidade dos Dados"
            if aviso_duplicadas:
                message += f"\n- Sessões duplicadas: {duplicated_sessions:.1%}"
            if aviso_cookies:
                message += f"\n- Perda de cookies: {lost_cookies:.1%}"
                
        # Adicionar métricas de UTM apenas se houver alertas
        if aviso_utm or aviso_mm_ads:
            message += "\n\n🎯 Parâmetros UTM de Meta"
            if aviso_utm:
                message += f"\n- Tráfego com UTM: {with_utm:.1%}\n(abaixo de 90%)"
            if aviso_mm_ads:
                message += f"\n- Tráfego com mm_ads: {with_mm_ads:.1%}\n(menor que 95% do UTM)\n- Instruções: https://abrir.link/kAnOz"

        # Enviar mensagem
        send_whatsapp_message(message, phone)

    except Exception as e:
        print(f"❌ Erro ao verificar meta para {tablename}: {str(e)}")
        # Mesmo em caso de erro, tenta enviar o aviso de sessões duplicadas e cookies
        try:
            msg = f"*{tablename.upper()}*\n\n❌ *Erro ao verificar meta*\n{str(e)}"
            
            # Adicionar alertas de vendas e sessões zeradas
            if aviso_vendas_zeradas:
                msg += f"\n\n🚨 *ALERTA: Vendas Zeradas*\n💰 Vendas de ontem: R$ 0,00"
            if sessoes_ontem is None:
                msg += f"\n\n🚨 *ALERTA: Sessões*\n📊 Sessões de ontem: Dados não disponíveis"
            elif aviso_sessoes_zeradas:
                msg += f"\n\n🚨 *ALERTA: Sessões Zeradas*\n📊 Sessões de ontem: 0"
            
            if vendas_ontem > 0:
                msg += f"\n\n📊 *Vendas de Ontem*\n💰 Total: R$ {vendas_ontem:,.2f}"
            if aviso_duplicadas or aviso_cookies:
                msg += "\n\n🔄 *Qualidade dos Dados*"
                if aviso_duplicadas:
                    msg += f"\n📊 Sessões duplicadas: {duplicated_sessions:.1%}"
                if aviso_cookies:
                    msg += f"\n📊 Perda de cookies: {lost_cookies:.1%}"
            
            # Adicionar comparação de taxas de funil se disponível
            if not df_funnel.empty:
                msg += "\n\n🔄 *Taxas de Funil (Ontem vs Anteontem)*"
                for _, row in df_funnel.iterrows():
                    etapa = row['Etapa']
                    taxa_ontem = row['Ontem (%)']
                    taxa_anteontem = row['Anteontem (%)']
                    variacao = row['Variação (%)']
                    
                    # Adicionar emoji se variação > 10%
                    emoji = ""
                    if abs(variacao) > 10:
                        if variacao > 0:
                            emoji = "🟢 "
                        else:
                            emoji = "🔴 "
                    
                    message += f"\n- {emoji}{etapa}: {taxa_ontem:.1f}% ({variacao:+.1f}%)"
            
            send_whatsapp_message(msg, phone)
        except:
            send_whatsapp_message(f"*{tablename.upper()}*\n\n❌ *Erro ao verificar meta*\n{str(e)}", phone)

def send_alerts_to_all_groups(test_mode=False):
    """
    Envia alertas de meta para todos os grupos de WhatsApp cadastrados.
    
    Args:
        test_mode (bool): Se True, envia para o grupo de teste
    """
    try:
        # Carregar usuários
        users = load_users()
        
        # Grupo de teste para modo teste
        test_group = "120363322379870288-group"
        
        # Enviar alerta para cada usuário que tem grupo de WhatsApp
        for user in users:
            if user.get('slug'):
                print(f"\nEnviando alerta para {user.get('slug')}...")
                if test_mode:
                    send_goal_alert(user.get('slug'), test_group)
                elif user.get('wpp_group'):
                    send_goal_alert(user.get('slug'), user.get('wpp_group'))
                
    except Exception as e:
        print(f"❌ Erro ao enviar alertas: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        if len(sys.argv) > 2 and sys.argv[2] == "test":
            send_alerts_to_all_groups(test_mode=True)
        else:
            send_alerts_to_all_groups(test_mode=False)
    elif len(sys.argv) > 2:
        company = sys.argv[1]
        is_test = sys.argv[2] == "test"
        
        if is_test:
            # Send test message to the specified group
            test_group = "120363322379870288-group"
            send_goal_alert(company, test_group)
        else:
            # Get the client's WhatsApp group from configuration
            users = load_users()
            client_group = None
            
            # Find the WhatsApp group for the specified client
            for user in users:
                if user.get('slug') == company and user.get('wpp_group'):
                    client_group = user.get('wpp_group')
                    break
            
            if client_group:
                send_goal_alert(company, client_group)
            else:
                print(f"❌ Grupo de WhatsApp não encontrado para o cliente {company}")
    else:
        print("❌ Uso incorreto do script")
        print("Para enviar para um cliente específico: python3 alerts/whatsapp.py [slug] [test]")
        print("Para enviar para todos os grupos: python3 alerts/whatsapp.py all")
        print("Para enviar para todos os clientes em modo teste: python3 alerts/whatsapp.py all test") 
