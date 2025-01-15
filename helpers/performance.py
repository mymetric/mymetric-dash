import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.notices import send_discord_alert
import pandas as pd

def check_performance_alerts(username, df):
    """Verifica e retorna lista de alertas de performance."""
    alertas = []
    
    # Verificar taxas de conversão do funil
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    
    query_funnel = f"""
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
        FROM `mymetric-hub-shopify.dbt_aggregated.{username}_daily_metrics`
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
    
    df_funnel = client.query(query_funnel).to_dataframe()
    
    if not df_funnel.empty:
        etapas = [
            {
                'nome': 'Visualização -> Carrinho',
                'taxa': 'taxa_cart',
                'media': 'media_cart',
                'std': 'std_cart',
                'evento1': 'view_item',
                'evento2': 'add_to_cart'
            },
            {
                'nome': 'Carrinho -> Checkout',
                'taxa': 'taxa_checkout',
                'media': 'media_checkout',
                'std': 'std_checkout',
                'evento1': 'add_to_cart',
                'evento2': 'begin_checkout'
            },
            {
                'nome': 'Checkout -> Frete',
                'taxa': 'taxa_shipping',
                'media': 'media_shipping',
                'std': 'std_shipping',
                'evento1': 'begin_checkout',
                'evento2': 'add_shipping_info'
            },
            {
                'nome': 'Frete -> Pagamento',
                'taxa': 'taxa_payment',
                'media': 'media_payment',
                'std': 'std_payment',
                'evento1': 'add_shipping_info',
                'evento2': 'add_payment_info'
            },
            {
                'nome': 'Pagamento -> Pedido',
                'taxa': 'taxa_purchase',
                'media': 'media_purchase',
                'std': 'std_purchase',
                'evento1': 'add_payment_info',
                'evento2': 'purchase'
            }
        ]
        
        for etapa in etapas:
            try:
                taxa_atual = float(df_funnel[etapa['taxa']].iloc[0])
                media = float(df_funnel[etapa['media']].iloc[0])
                desvio = float(df_funnel[etapa['std']].iloc[0])
                
                # Verificar se os valores são válidos
                if pd.isna(taxa_atual) or pd.isna(media) or pd.isna(desvio) or desvio == 0:
                    continue
                
                # Verificar se está fora de 1.5 desvios padrões (aumentando a sensibilidade)
                if abs(taxa_atual - media) > 1.5 * desvio:
                    # Determinar severidade baseado no quanto está fora do normal
                    desvios = abs(taxa_atual - media) / desvio
                    direcao = 'acima' if taxa_atual > media else 'abaixo'
                    
                    if direcao == 'acima':
                        severidade = 'baixa'
                        mensagem = 'positivo'
                    else:
                        if desvios > 2:
                            severidade = 'alta'
                            mensagem = 'crítico'
                        elif desvios > 1.75:
                            severidade = 'media'
                            mensagem = 'moderado'
                        else:
                            severidade = 'baixa'
                            mensagem = 'baixo'
                    
                    alerta = {
                        'titulo': f'Anomalia na Taxa de Conversão ({etapa["nome"]})',
                        'descricao': f'A taxa de conversão está {direcao} do normal, em {taxa_atual:.1f}%. ' +
                                    f'A média dos últimos 30 dias é {media:.1f}% (±{desvio:.1f}%). ' +
                                    f'Isso representa um desvio {mensagem}.',
                        'acao': f'Analise o comportamento dos eventos {etapa["evento1"]} e {etapa["evento2"]} e identifique possíveis causas.',
                        'severidade': severidade,
                        'tipo': 'performance'
                    }
                    alertas.append(alerta)
                    send_discord_alert(alerta, username)
            except Exception as e:
                st.error(f"Erro ao processar etapa {etapa['nome']}: {str(e)}")
    
    return alertas 