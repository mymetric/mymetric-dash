import streamlit as st
import pandas as pd

from modules.load_data import load_performance_alerts

def check_performance_alerts():
    """Verifica e retorna lista de alertas de performance."""
    alertas = []
    
    df_funnel = load_performance_alerts()
    
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
            except Exception as e:
                print(f"Faltam dados na etapa {etapa['nome']}")
    
    return alertas 

def display_performance():
    """Exibe alertas e insights de performance"""
    
    with st.expander("📈 Performance", expanded=True):
        # Seção 1: Alertas de Performance do Funil
        alertas_performance = check_performance_alerts()
        
        if alertas_performance:
            st.subheader("⚠️ Alertas do Funil de Conversão")
            for alerta in alertas_performance:
                card_type = {
                    'alta': 'danger',
                    'media': 'warning',
                    'baixa': 'success' if 'positivo' in alerta.get('descricao', '').lower() else 'info'
                }.get(alerta['severidade'], 'info')
                
                render_insight_card(
                    alerta['titulo'],
                    alerta['descricao'],
                    alerta['acao'],
                    card_type
                )
        
        # Seção 2: Insights do Meta Ads
        try:
            from modules.load_data import load_meta_ads
            df_meta = load_meta_ads()
            
            if not df_meta.empty:
                st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
                analyze_meta_insights(df_meta)
                
        except Exception as e:
            st.error(f"Erro ao carregar insights do Meta Ads: {str(e)}")

def render_insight_card(title: str, content: str, suggestions: str = None, card_type: str = "success"):
    """Renderiza um card de insight com estilo padronizado"""
    colors = {
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8"
    }
    color = colors.get(card_type, "#17a2b8")
    
    card_style = f'''
        margin-bottom: 15px;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid {color};
        background-color: {color}10;
    '''
    
    title_style = f'''
        color: {color};
        font-weight: 600;
        margin-bottom: 8px;
    '''
    
    content_style = '''
        color: #666;
        margin-bottom: 8px;
    '''
    
    suggestions_style = '''
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9em;
        color: #666;
    '''
    
    html = f'''
        <div style="{card_style}">
            <div style="{title_style}">{title}</div>
            <div style="{content_style}">{content}</div>
    '''
    
    if suggestions:
        html += f'<div style="{suggestions_style}">{suggestions}</div>'
    
    html += '</div>'
    
    st.markdown(html.replace(".", ","), unsafe_allow_html=True)

def analyze_meta_insights(df_meta):
    """Analisa dados do Meta Ads para extrair insights relevantes"""
    st.subheader("🎯 Insights do Meta Ads")
    
    # 1. Análise de Campanhas Eficientes
    campaign_performance = df_meta.groupby('campaign_name').agg({
        'spend': 'sum',
        'purchase_value': 'sum',
        'purchases': 'sum',
        'clicks': 'sum',
        'impressions': 'sum'
    }).reset_index()
    
    # Calcular métricas
    campaign_performance['roas'] = (campaign_performance['purchase_value'] / campaign_performance['spend']).round(2)
    campaign_performance['cpc'] = (campaign_performance['spend'] / campaign_performance['clicks']).round(2)
    campaign_performance['conv_rate'] = (campaign_performance['purchases'] / campaign_performance['clicks'] * 100).round(2)
    
    # Campanhas eficientes
    efficient_campaigns = campaign_performance[
        (campaign_performance['roas'] > campaign_performance['roas'].mean()) &
        (campaign_performance['cpc'] < campaign_performance['cpc'].mean()) &
        (campaign_performance['spend'] > 100)
    ]
    
    if not efficient_campaigns.empty:
        roas_medio = campaign_performance['roas'].mean()
        cpc_medio = campaign_performance['cpc'].mean()
        
        content = f"""
            Encontramos {len(efficient_campaigns)} campanhas com:
            <br>• ROAS acima de {roas_medio:.2f} (média geral)
            <br>• CPC abaixo de R$ {cpc_medio:.2f} (média geral)
            <br>• Investimento mínimo de R$ 100,00
        """
        
        suggestions = f"Campanhas em destaque: {', '.join(efficient_campaigns['campaign_name'].tolist())}"
        
        render_insight_card(
            "🎯 Campanhas de Melhor Performance",
            content,
            suggestions,
            "success"
        )
    
    # Oportunidades de otimização
    optimization_opportunities = campaign_performance[
        (campaign_performance['spend'] > 100) &
        (campaign_performance['roas'] < campaign_performance['roas'].mean()) &
        (campaign_performance['conv_rate'] > campaign_performance['conv_rate'].mean())
    ]
    
    if not optimization_opportunities.empty:
        content = f"""
            Campanhas com boa taxa de conversão mas ROAS abaixo da média:
            <br>{', '.join(optimization_opportunities['campaign_name'].tolist())}
            <br><br>Estas campanhas convertem bem, mas o valor médio das vendas está baixo.
        """
        
        suggestions = """
            Sugestões:
            <br>• Revisar estratégia de preços/produtos anunciados
            <br>• Ajustar segmentação para públicos com maior poder de compra
            <br>• Analisar se o custo por clique não está muito alto
        """
        
        render_insight_card(
            "💡 Oportunidades de Otimização",
            content,
            suggestions,
            "warning"
        )
    
    # Análise de custos
    df_daily = df_meta.groupby('date').agg({
        'spend': 'sum',
        'impressions': 'sum'
    }).reset_index()
    
    df_daily['cpm'] = (df_daily['spend'] / df_daily['impressions'] * 1000).round(2)
    
    if len(df_daily) >= 7:
        recent_cpm = df_daily['cpm'].tail(7)
        cpm_trend = (recent_cpm.iloc[-1] - recent_cpm.iloc[0]).round(2)
        
        if cpm_trend > 0:
            content = f"""
                O CPM aumentou R$ {cpm_trend:.2f} nos últimos 7 dias.
                <br><br>Possíveis causas:
                <br>• Saturação do público-alvo
                <br>• Aumento da concorrência
                <br>• Necessidade de renovar criativos
            """
            
            suggestions = """
                Sugestões:
                <br>• Testar novos públicos semelhantes
                <br>• Atualizar criativos dos anúncios
                <br>• Revisar estratégia de lances
            """
            
            render_insight_card(
                "📊 Alerta de Custos",
                content,
                suggestions,
                "danger"
            )
