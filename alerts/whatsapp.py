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
        
        query = f"""
        SELECT 
            SUM(CASE 
                WHEN status = 'paid' 
                AND created_at BETWEEN '{primeiro_dia}' AND '{ontem}'
                THEN value 
                    - COALESCE(total_discounts, 0) 
                    + COALESCE(shipping_value, 0)
                ELSE 0 
            END) as total_mes
        FROM `mymetric-hub-shopify.dbt_granular.{tablename}_orders_dedup`
        """

        query_job = client.query(query)
        rows_raw = query_job.result()
        rows = [dict(row) for row in rows_raw]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Erro ao carregar receita: {str(e)}")
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

def send_goal_alert(tablename, phone):
    """
    Envia um alerta com o status da meta do mês via WhatsApp.
    
    Args:
        tablename (str): Nome da tabela para verificar a meta
        phone (str): Número do telefone ou ID do grupo
    """
    try:
        print(f"\nVerificando meta para {tablename}...")
        
        # Carregar metas
        df_goals = load_goals(tablename)
        print(f"DataFrame de metas: {df_goals}")
        
        if df_goals.empty:
            print(f"❌ DataFrame de metas vazio para {tablename}")
            send_whatsapp_message(f"❌ Meta do mês não cadastrada para {tablename}\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas", phone)
            return
            
        if 'goals' not in df_goals.columns:
            print(f"❌ Coluna 'goals' não encontrada para {tablename}")
            send_whatsapp_message(f"❌ Meta do mês não cadastrada para {tablename}\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas", phone)
            return
            
        if df_goals['goals'].isna().all():
            print(f"❌ Todas as metas estão vazias para {tablename}")
            send_whatsapp_message(f"❌ Meta do mês não cadastrada para {tablename}\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas", phone)
            return

        # Extrair meta do mês atual
        goals_json = df_goals['goals'].iloc[0]
        print(f"JSON de metas: {goals_json}")
        
        if not goals_json:
            print(f"❌ JSON de metas vazio para {tablename}")
            send_whatsapp_message(f"❌ Meta do mês não cadastrada para {tablename}\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas", phone)
            return

        metas = json.loads(goals_json)
        print(f"Metas carregadas: {metas}")
        
        current_month = datetime.now().strftime("%Y-%m")
        print(f"Mês atual: {current_month}")
        
        meta_receita = metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
        print(f"Meta de receita: {meta_receita}")

        if meta_receita == 0:
            print(f"❌ Meta de receita é zero para {tablename}")
            send_whatsapp_message(f"❌ Meta do mês não cadastrada para {tablename}\n\n📝 Cadastre sua meta no MyMetric Hub em Configurações > Metas", phone)
            return

        # Carregar receita atual do mês
        df_revenue = load_current_month_revenue(tablename)
        total_receita_mes = float(df_revenue['total_mes'].iloc[0])
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
📊 *Status da Meta - {tablename}*

✅ Meta do mês: R$ {meta_receita:,.2f}
💰 Receita atual: R$ {total_receita_mes:,.2f}
📊 Percentual atingido: {percentual_atingido:.1f}%
📈 Média diária (até ontem): R$ {media_diaria:,.2f}
📅 Dias passados: {dias_passados} de {ultimo_dia}
🎯 Projeção final: R$ {projecao_final:,.2f}
📊 Percentual projetado: {percentual_projetado:.1f}%
"""

        # Enviar mensagem
        send_whatsapp_message(message, phone)

    except Exception as e:
        print(f"❌ Erro ao verificar meta para {tablename}: {str(e)}")
        send_whatsapp_message(f"❌ Erro ao verificar meta: {str(e)}", phone)

def send_alerts_to_all_groups():
    """
    Envia alertas de meta para todos os grupos de WhatsApp cadastrados.
    """
    try:
        # Carregar usuários
        users = load_users()
        
        # Enviar alerta para cada usuário que tem grupo de WhatsApp
        for user in users:
            if user.get('wpp_group'):
                print(f"Enviando alerta para {user.get('slug')} - Grupo: {user.get('wpp_group')}")
                send_goal_alert(user.get('slug'), user.get('wpp_group'))
                
    except Exception as e:
        print(f"❌ Erro ao enviar alertas: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        send_alerts_to_all_groups()
    elif len(sys.argv) > 2:
        send_goal_alert(sys.argv[1], sys.argv[2])
    else:
        print("❌ Uso incorreto do script")
        print("Para enviar para um grupo específico: python3 alerts/whatsapp.py [slug] [wpp_group]")
        print("Para enviar para todos os grupos: python3 alerts/whatsapp.py all") 