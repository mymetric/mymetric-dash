import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from modules.load_data import load_check_zero_metrics, load_basic_data, load_paid_media, load_fbclid_coverage
from partials.run_rate import load_table_metas
from datetime import datetime

def safe_float_conversion(value):
    return float(value) if value is not None else 0.0

def check_zero_metrics():
    
    df = load_check_zero_metrics()
    
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

def check_pending_items():
    """Verifica e retorna lista de pendências com base nos dados."""
    pendencias = []
    
    meta_receita = load_table_metas()
    current_month = datetime.now().strftime("%Y-%m")
    if meta_receita:
        meta_receita = meta_receita.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
    else:
        meta_receita = 0

    zero_metrics = check_zero_metrics()


    df = load_basic_data()
    # Calculate cookie loss rate for today and yesterday
    df['Data'] = pd.to_datetime(df['Data'])
    today = pd.Timestamp.now().date()
    yesterday = today - pd.Timedelta(days=1)

    # Filter for last 2 days
    df_recent = df[df['Data'].dt.date.isin([today, yesterday])]
    
    # Calculate percentage of not captured sessions
    pedidos = df_recent['Pedidos'].sum()
    not_captured = df_recent[df_recent['Cluster'] == '🍪 Perda de Cookies']['Pedidos'].sum()
    tx_cookies = (not_captured / pedidos * 100) if pedidos > 10 else 0


    
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
            # send_discord_alert(pendencia, username)
    
    # Verificar meta do mês
    if meta_receita == 0:
        pendencia = {
            'titulo': 'Cadastrar Meta do Mês',
            'descricao': 'A meta de receita do mês não está cadastrada. Isso é importante para acompanhar seu desempenho.',
            'acao': 'Acesse a aba Configurações para cadastrar sua meta mensal.',
            'severidade': 'alta'
        }
        pendencias.append(pendencia)
    
    # Verificar taxa de perda de cookies
    if tx_cookies > 10:
        pendencia = {
            'titulo': 'Ajustar Taxa de Perda de Cookies',
            'descricao': f'A taxa de perda de cookies está em {tx_cookies:.1f}%. O ideal é manter abaixo de 10%.',
            'acao': 'Verifique a implementação do código de rastreamento e possíveis bloqueadores.',
            'severidade': 'alta'
        }
        pendencias.append(pendencia)
    
    # Verificar tagueamento do Meta Ads
    df = load_basic_data()

    if not df.empty:
        
        # Verificar connect rate do Google Ads
        df_google_ads = df[df['Cluster'] == "🟢 Google Ads"]
        if not df_google_ads.empty and df_google_ads['Cliques'].sum() > 0:
            google_sessions = df[df['Cluster'] == "🟢 Google Ads"]["Sessões"].sum()
            google_clicks = df_google_ads['Cliques'].sum()
            google_connect_rate = (google_sessions / google_clicks * 100)
            
            if google_connect_rate < 50:
                severidade = 'alta'
                mensagem = 'crítico'
            elif google_connect_rate < 70:
                severidade = 'media'
                mensagem = 'moderado'
            elif google_connect_rate < 80:
                severidade = 'baixa'
                mensagem = 'baixo'
            
            if google_connect_rate < 80:
                pendencia = {
                    'titulo': 'Connect Rate Baixo no Google Ads',
                    'descricao': f'O connect rate está em {google_connect_rate:.1f}%, o que representa um problema {mensagem}. ' +
                                f'Cliques: {google_clicks:,.0f}, Sessões: {google_sessions:,.0f}\n\n' +
                                'ℹ️ Esta pendência não afeta seu MyMetric Score.',
                    'acao': 'Verifique problemas de rastreamento do GA4, bloqueadores de anúncios ou configuração incorreta do GTM.',
                    'severidade': severidade
                }
                pendencias.append(pendencia)
                
            elif google_connect_rate > 100:
                pendencia = {
                    'titulo': 'Connect Rate Alto no Google Ads',
                    'descricao': f'O número de sessões está {google_connect_rate:.1f}% acima dos cliques no Google Ads. ' +
                                f'Cliques: {google_clicks:,.0f}, Sessões: {google_sessions:,.0f}\n\n' +
                                'ℹ️ Esta pendência não afeta seu MyMetric Score.',
                    'acao': 'Verifique se há dupla contagem de sessões ou problemas no rastreamento da plataforma.',
                    'severidade': 'alta'
                }
                pendencias.append(pendencia)
        
        # Verificar connect rate do Meta Ads
        df_meta_ads = df[df['Cluster'] == "🔵 Meta Ads"]
        if not df_meta_ads.empty and df_meta_ads['Cliques'].sum() > 0:
            meta_sessions = df[df['Cluster'] == "🔵 Meta Ads"]["Sessões"].sum()
            meta_clicks = df_meta_ads['Cliques'].sum()
            meta_connect_rate = (meta_sessions / meta_clicks * 100)
            
            if meta_connect_rate < 50:
                severidade = 'alta'
                mensagem = 'crítico'
            elif meta_connect_rate < 70:
                severidade = 'media'
                mensagem = 'moderado'
            elif meta_connect_rate < 80:
                severidade = 'baixa'
                mensagem = 'baixo'
            
            if meta_connect_rate < 80:
                pendencia = {
                    'titulo': 'Connect Rate Baixo no Meta Ads',
                    'descricao': f'O connect rate está em {meta_connect_rate:.1f}%, o que representa um problema {mensagem}. ' +
                                f'Cliques: {meta_clicks:,.0f}, Sessões: {meta_sessions:,.0f}\n\n' +
                                'ℹ️ Esta pendência não afeta seu MyMetric Score.',
                    'acao': 'Verifique problemas de rastreamento do GA4, bloqueadores de anúncios ou configuração incorreta do GTM.',
                    'severidade': severidade
                }
                pendencias.append(pendencia)

            elif meta_connect_rate > 100:
                pendencia = {
                    'titulo': 'Connect Rate Alto no Meta Ads',
                    'descricao': f'O número de sessões está {meta_connect_rate:.1f}% acima dos cliques no Meta Ads. ' +
                                f'Cliques: {meta_clicks:,.0f}, Sessões: {meta_sessions:,.0f}\n\n' +
                                'ℹ️ Esta pendência não afeta seu MyMetric Score.',
                    'acao': 'Verifique se há dupla contagem de sessões ou problemas no rastreamento da plataforma.',
                    'severidade': 'alta'
                }
                pendencias.append(pendencia)

        df_qa = load_fbclid_coverage()
        
        if not df_qa.empty and 'Cobertura' in df_qa.columns and df_qa['Cobertura'].iloc[0] is not None:
            cobertura = float(df_qa['Cobertura'].iloc[0] * 100)
            
            if cobertura < 50:
                severidade = 'alta'
                mensagem = 'crítico'
            elif cobertura < 70:
                severidade = 'media'
                mensagem = 'moderado'
            elif cobertura < 90:
                severidade = 'baixa'
                mensagem = 'baixo'
            
            if cobertura < 90:
                pendencia = {
                    'titulo': 'Tagueamento do Meta Ads',
                    'descricao': f'A cobertura do tagueamento está em {cobertura:.1f}%, o que representa um problema {mensagem}.',
                    'acao': 'Verifique se o parâmetro mm_ads está sendo adicionado corretamente nas URLs. ' +
                           'Acesse nosso <a href="https://mymetric.notion.site/UTMs-para-Meta-Ads-a32df743c4e046ccade33720f0faec3a" target="_blank">tutorial de implementação</a> para mais detalhes.',
                    'severidade': severidade
                }
                pendencias.append(pendencia)
    
    return pendencias

def display_pending_items(pendencias):
    """Exibe as pendências na interface."""
    if pendencias:
        st.markdown("""
            <style>
                .pendencia-alta { 
                    border-left: 4px solid #3B82F6 !important;
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
                'alta': '#3B82F6',
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

def display_pendings():
    
    pendencias = check_pending_items()
    
    # Calcular e exibir MyMetric Score com pendências
    if pendencias:
        # Pontuação base de 10
        score = 10
        
        # Penalidades por severidade
        for p in pendencias:
            # Penalidade extra para meta não cadastrada
            if p['titulo'] == 'Cadastrar Meta do Mês':
                score -= 3  # Penalidade maior por não ter meta cadastrada
            # Penalidades padrão para outros problemas (exceto connect rate)
            elif 'Connect Rate' not in p['titulo']:  # Ignora problemas de connect rate no score
                if p['severidade'] == 'alta':
                    score -= 2  # -2 pontos para pendências críticas
                elif p['severidade'] == 'media':
                    score -= 1  # -1 ponto para pendências médias
                elif p['severidade'] == 'baixa':
                    score -= 0.5  # -0.5 pontos para pendências baixas
        
        # Garantir que o score não seja negativo
        score = max(0, score)
        
        # Definir cor e mensagem baseada no score
        if score >= 8:
            cor_score = "#10B981"  # Verde esmeralda
            status = "Excelente"
            gradient = "linear-gradient(135deg, #10B981, #059669)"
        elif score >= 6:
            cor_score = "#3B82F6"  # Azul
            status = "Bom"
            gradient = "linear-gradient(135deg, #3B82F6, #2563EB)"
        elif score >= 4:
            cor_score = "#F59E0B"  # Amarelo
            status = "Regular"
            gradient = "linear-gradient(135deg, #F59E0B, #D97706)"
        else:
            cor_score = "#EF4444"  # Vermelho
            status = "Crítico"
            gradient = "linear-gradient(135deg, #EF4444, #DC2626)"
        
        # Calcular o percentual para o círculo de progresso
        percent = (score / 10) * 100
        
        # Exibir o score com design moderno
        st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                margin: 20px 0;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 24px;
                ">
                    <div style="
                        position: relative;
                        width: 120px;
                        height: 120px;
                    ">
                        <div style="
                            position: absolute;
                            width: 100%;
                            height: 100%;
                            border-radius: 50%;
                            background: {gradient};
                            clip-path: circle({percent}% at center);
                            transition: all 0.3s ease;
                        "></div>
                        <div style="
                            position: absolute;
                            top: 10px;
                            left: 10px;
                            right: 10px;
                            bottom: 10px;
                            background: white;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            flex-direction: column;
                        ">
                            <span style="
                                font-size: 32px;
                                font-weight: 700;
                                color: {cor_score};
                                line-height: 1;
                            ">{score:.1f}</span>
                            <span style="
                                font-size: 12px;
                                color: #6B7280;
                                margin-top: 4px;
                            ">/10</span>
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 8px;
                        ">
                            <h2 style="
                                margin: 0;
                                font-size: 24px;
                                color: #111827;
                                font-weight: 600;
                            ">MyMetric Score</h2>
                            <span style="
                                background: {cor_score}15;
                                color: {cor_score};
                                padding: 4px 12px;
                                border-radius: 20px;
                                font-size: 14px;
                                font-weight: 500;
                            ">{status}</span>
                        </div>
                        <p style="
                            margin: 0;
                            color: #6B7280;
                            font-size: 14px;
                            line-height: 1.5;
                        ">
                            Avaliação da qualidade do seu rastreamento e implementação. 
                            Resolva as pendências abaixo para melhorar sua pontuação.
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Expander para pendências
        with st.expander("Melhore seu Score", expanded=False):
            display_pending_items(pendencias)