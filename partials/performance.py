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

def render_insight_card(title: str, content: str, suggestions: str = None, card_type: str = "success"):
    """Renderiza um card de insight com estilo padronizado"""
    colors = {
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#3B82F6",
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
    st.subheader("Insights do Meta Ads")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análise do melhor dia
        df_meta['date'] = pd.to_datetime(df_meta['date'])
        df_meta['day_of_week'] = df_meta['date'].dt.day_name()
        
        # Agregar dados por dia da semana
        daily_performance = df_meta.groupby('day_of_week').agg({
            'spend': 'sum',
            'purchase_value': 'sum',
            'purchases': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        # Calcular métricas
        daily_performance['roas'] = (daily_performance['purchase_value'] / daily_performance['spend']).round(2)
        daily_performance['conversion_rate'] = (daily_performance['purchases'] / daily_performance['clicks'] * 100).round(2)
        
        # Ordenar dias da semana
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        daily_performance['day_of_week'] = pd.Categorical(
            daily_performance['day_of_week'],
            categories=day_order,
            ordered=True
        )
        daily_performance = daily_performance.sort_values('day_of_week')
        daily_performance['day_of_week'] = daily_performance['day_of_week'].map(day_names)
        
        # Encontrar o melhor dia
        best_roas_day = daily_performance.loc[daily_performance['roas'].idxmax()]
        best_conv_day = daily_performance.loc[daily_performance['conversion_rate'].idxmax()]
        
        if not daily_performance.empty and daily_performance['spend'].sum() > 0:
            content = f"""Análise de desempenho por dia da semana:<br><br>
Melhor ROAS:
<br>• {best_roas_day['day_of_week']} (ROAS {best_roas_day['roas']:.2f})
<br>• Receita: R$ {best_roas_day['purchase_value']:,.2f}
<br>• Investimento: R$ {best_roas_day['spend']:,.2f}
<br><br>
Melhor Taxa de Conversão:
<br>• {best_conv_day['day_of_week']} ({best_conv_day['conversion_rate']:.1f}%)
<br>• Vendas: {int(best_conv_day['purchases'])}
<br>• Cliques: {int(best_conv_day['clicks'])}"""
            
            suggestions = """Sugestões:
<br>• Considere aumentar o orçamento nos dias de melhor performance
<br>• Analise as configurações de lance para cada dia da semana
<br>• Verifique se há padrões de comportamento do público que explicam essas variações"""
            
            render_insight_card(
                "📅 Análise por Dia da Semana",
                content,
                suggestions,
                "info"
            )
        
        # Oportunidades de otimização
        optimization_opportunities = daily_performance[
            (daily_performance['spend'] > 100) &
            (daily_performance['roas'] < daily_performance['roas'].mean()) &
            (daily_performance['conversion_rate'] > daily_performance['conversion_rate'].mean())
        ]
    
    with col2:
        # Campanhas eficientes
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

def display_performance():
    """Exibe alertas e insights de performance"""
    
    # Performance expander
    with st.expander("Performance", expanded=True):
        # Seção 1: Alertas de Performance do Funil
        alertas_performance = check_performance_alerts()
        
        if alertas_performance:
            st.subheader("Alertas do Funil de Conversão")
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
        
        # # Seção 2: Insights do Meta Ads
        # try:
        #     from modules.load_data import load_meta_ads
        #     df_meta = load_meta_ads()
            
        #     if not df_meta.empty:
        #         st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
        #         analyze_meta_insights(df_meta)
                
        # except Exception as e:
        #     st.error(f"Erro ao carregar insights do Meta Ads: {str(e)}")
