import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.notices import send_discord_alert

def check_zero_metrics(client, username):
    """Verifica métricas zeradas nos últimos dois dias."""
    query = f"""
    SELECT 
        event_date,
        COALESCE(view_item, 0) as view_item,
        COALESCE(add_to_cart, 0) as add_to_cart,
        COALESCE(begin_checkout, 0) as begin_checkout,
        COALESCE(add_shipping_info, 0) as add_shipping_info,
        COALESCE(add_payment_info, 0) as add_payment_info,
        COALESCE(purchase, 0) as purchase
    FROM `mymetric-hub-shopify.dbt_aggregated.{username}_daily_metrics`
    WHERE event_date >= DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 1 DAY)
    ORDER BY event_date DESC
    """
    
    df = client.query(query).to_dataframe()
    zero_metrics = []
    
    if not df.empty:
        metrics = {
            'Visualização de Item': 'view_item',
            'Adicionar ao Carrinho': 'add_to_cart',
            'Iniciar Checkout': 'begin_checkout',
            'Adicionar Informação de Frete': 'add_shipping_info',
            'Adicionar Informação de Pagamento': 'add_payment_info',
            'Pedidos': 'purchase'
        }
        
        for date in df['event_date'].unique():
            day_data = df[df['event_date'] == date]
            for metric_name, metric_col in metrics.items():
                if day_data[metric_col].iloc[0] <= 0:
                    zero_metrics.append({
                        'data': date,
                        'metrica': metric_name
                    })
    
    return zero_metrics

def check_pending_items(username, meta_receita, tx_cookies, df_ads):
    """Verifica e retorna lista de pendências com base nos dados."""
    pendencias = []
    
    # Verificar métricas zeradas
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    zero_metrics = check_zero_metrics(client, username)
    
    if zero_metrics:
        all_metrics = []
        for zm in zero_metrics:
            metric = zm['metrica']
            if metric not in all_metrics:
                all_metrics.append(metric)
        
        if all_metrics:
            pendencia = {
                'titulo': 'Métricas Zeradas nas Últimas 48h',
                'descricao': 'As seguintes métricas estão zeradas:' + '\n• ' + '\n• '.join(all_metrics),
                'acao': 'Verifique a implementação do rastreamento e se há problemas técnicos.',
                'severidade': 'alta'
            }
            pendencias.append(pendencia)
            send_discord_alert(pendencia, username)
    
    # Verificar meta do mês
    if meta_receita == 0:
        pendencia = {
            'titulo': 'Cadastrar Meta do Mês',
            'descricao': 'A meta de receita do mês não está cadastrada. Isso é importante para acompanhar seu desempenho.',
            'acao': 'Acesse a aba Configurações para cadastrar sua meta mensal.',
            'severidade': 'alta'
        }
        pendencias.append(pendencia)
        send_discord_alert(pendencia, username)
    
    # Verificar taxa de perda de cookies
    if tx_cookies > 10:
        pendencia = {
            'titulo': 'Ajustar Taxa de Perda de Cookies',
            'descricao': f'A taxa de perda de cookies está em {tx_cookies:.1f}%. O ideal é manter abaixo de 10%.',
            'acao': 'Verifique a implementação do código de rastreamento e possíveis bloqueadores.',
            'severidade': 'alta'
        }
        pendencias.append(pendencia)
        send_discord_alert(pendencia, username)
    
    # Verificar tagueamento do Meta Ads
    if not df_ads.empty:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        
        qa = f"""
            select
                sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`
            from `mymetric-hub-shopify.dbt_join.{username}_sessions_gclids`
            where
                event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
                and page_params like "%fbclid%"
                and medium not like "%social%"
        """
        
        df_qa = client.query(qa).to_dataframe()
        if not df_qa.empty:
            cobertura = float(df_qa['Cobertura'].iloc[0]) * 100
            if cobertura < 80:
                pendencia = {
                    'titulo': 'Ajustar Taxa de Tagueamento Meta Ads',
                    'descricao': f'A cobertura do parâmetro mm_ads está em {cobertura:.1f}%. O ideal é manter acima de 80%.',
                    'acao': f'Verifique a implementação do parâmetro mm_ads no Meta Ads. <a href="https://mymetric.notion.site/Parametriza-o-de-Meta-Ads-a32df743c4e046ccade33720f0faec3a" target="_blank" style="color: #0366d6; text-decoration: none;">Saiba como implementar corretamente</a>',
                    'severidade': 'media'
                }
                pendencias.append(pendencia)
                send_discord_alert(pendencia, username)
    
    return pendencias

def display_pending_items(pendencias):
    """Exibe as pendências na interface."""
    if pendencias:
        st.markdown("""
            <style>
                .pendencia-alta { 
                    border-left: 4px solid #dc3545 !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .pendencia-media { 
                    border-left: 4px solid #ffc107 !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .pendencia-baixa { 
                    border-left: 4px solid #17a2b8 !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .pendencia-card {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border: 1px solid #eee;
                    transition: transform 0.2s ease-in-out;
                }
                .pendencia-card:hover {
                    transform: translateY(-2px);
                }
                .pendencia-title {
                    font-size: 1.1em;
                    font-weight: 600;
                    margin-bottom: 12px;
                }
                .pendencia-badge {
                    padding: 4px 12px;
                    border-radius: 15px;
                    font-size: 0.8em;
                    font-weight: 500;
                }
                .pendencia-description {
                    color: #666;
                    margin: 12px 0;
                    line-height: 1.5;
                }
                .pendencia-action {
                    background-color: #f8f9fa;
                    padding: 12px;
                    border-radius: 6px;
                    margin-top: 12px;
                    font-size: 0.9em;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-bottom: 30px;">
                <h3 style="color: #31333F; margin-bottom: 20px; display: flex; align-items: center; gap: 8px;">
                    <span>⚠️</span>
                    <span>Pendências</span>
                </h3>
        """, unsafe_allow_html=True)
        
        for p in pendencias:
            severity_colors = {
                'alta': '#dc3545',
                'media': '#ffc107',
                'baixa': '#17a2b8'
            }
            
            st.markdown(f"""
                <div class="pendencia-card pendencia-{p['severidade']}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="pendencia-title">{p['titulo']}</div>
                        <span class="pendencia-badge" style="
                            background-color: {severity_colors[p['severidade']]};
                            color: {'#fff' if p['severidade'] != 'media' else '#000'};
                        ">
                            {p['severidade'].upper()}
                        </span>
                    </div>
                    <div class="pendencia-description">{p['descricao']}</div>
                    <div class="pendencia-action">
                        <strong>🎯 Ação necessária:</strong> {p['acao']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) 