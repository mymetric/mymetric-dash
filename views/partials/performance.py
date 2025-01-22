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
                st.toast(f"Faltam dados na etapa {etapa['nome']}")
    
    return alertas 

def display_performance():
    
    alertas_performance = check_performance_alerts()

    # Expander para alertas de performance
    if alertas_performance:
        with st.expander("📈 Alertas de Performance", expanded=True):
            for alerta in alertas_performance:
                if alerta['severidade'] == 'alta':
                    cor = "#dc3545"  # Vermelho
                elif alerta['severidade'] == 'media':
                    cor = "#ffc107"  # Amarelo
                else:
                    cor = "#28a745" if 'positivo' in alerta.get('descricao', '').lower() else "#17a2b8"  # Verde para positivo, Azul para outros
                
                st.markdown(f"""
                    <div style="
                        margin-bottom: 15px;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid {cor};
                        background-color: {cor}10;
                    ">
                        <div style="color: {cor}; font-weight: 600; margin-bottom: 8px;">
                            {alerta['titulo']}
                        </div>
                        <div style="color: #666; margin-bottom: 8px;">
                            {alerta['descricao']}
                        </div>
                        <div style="
                            background-color: #f8f9fa;
                            padding: 8px;
                            border-radius: 4px;
                            font-size: 0.9em;
                            color: #666;
                        ">
                            {alerta['acao']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
