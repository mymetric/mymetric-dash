import streamlit as st
from modules.load_data import load_goals
from datetime import datetime, date
import calendar
import pandas as pd
import json    

def load_table_metas():
    
    try:
        df = load_goals()
        df = json.loads(df['goals'][0])
        return df
    
    except Exception as e:
        return 0
    
    # Se não encontrou ou deu erro, retorna valores padrão
    default_metas = {
        "metas_mensais": {
            datetime.now().strftime("%Y-%m"): {
                "meta_receita_paga": 0
            }
        }
    }
    return default_metas

def display_run_rate(df):


    
    df_run_rate = df.copy()

    current_date = date.today()
    first_day_current_month = current_date.replace(day=1)
    yesterday = current_date - pd.Timedelta(days=1)
    
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    meta_receita = load_table_metas()

    if meta_receita != 0:

        current_month = datetime.now().strftime("%Y-%m")
        meta_receita = meta_receita.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)

        is_current_month = (start_date == first_day_current_month and end_date == current_date)    

        if meta_receita > 0 and is_current_month:
            dias_passados = yesterday.day
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            meta_proporcional = meta_receita * (dias_passados / last_day)
            
            # Usar df_run_rate para cálculos do Run Rate (sem filtros)
            total_receita_paga_run_rate = df_run_rate["Receita Paga"].sum()
            percentual_meta = (total_receita_paga_run_rate / meta_proporcional) * 100 if meta_proporcional > 0 else 0
            
            st.header("Run Rate")

            # Calcula a projeção de fechamento do mês
            receita_projetada = total_receita_paga_run_rate * (last_day / dias_passados) if dias_passados > 0 else 0
            
            # Calcula a probabilidade de atingir a meta
            media_diaria = total_receita_paga_run_rate / dias_passados if dias_passados > 0 else 0
            dias_restantes = last_day - dias_passados
            valor_faltante = meta_receita - total_receita_paga_run_rate
            valor_necessario_por_dia = valor_faltante / dias_restantes if dias_restantes > 0 else float('inf')
            
            # Calcula a probabilidade baseada na diferença entre a média diária atual e a necessária
            if valor_faltante <= 0:
                probabilidade = 100  # Já atingiu a meta
                mensagem_probabilidade = "🎉 Meta atingida! Continue o ótimo trabalho!"
                cor_probabilidade = "#28a745"
            elif dias_restantes == 0:
                if valor_faltante > 0:
                    probabilidade = 0
                    mensagem_probabilidade = "⚠️ Tempo esgotado para este mês"
                    cor_probabilidade = "#dc3545"
                else:
                    probabilidade = 100
                    mensagem_probabilidade = "🎉 Meta atingida! Continue o ótimo trabalho!"
                    cor_probabilidade = "#28a745"
            else:
                # Quanto maior a média diária em relação ao necessário, maior a probabilidade
                razao = media_diaria / valor_necessario_por_dia if valor_necessario_por_dia > 0 else 0
                probabilidade = min(100, razao * 100)
                
                # Define a mensagem baseada na faixa de probabilidade
                if probabilidade >= 80:
                    mensagem_probabilidade = "🚀 Excelente ritmo! Você está muito próximo de atingir a meta!"
                    cor_probabilidade = "#28a745"
                elif probabilidade >= 60:
                    mensagem_probabilidade = "💪 Bom progresso! Continue focado que a meta está ao seu alcance!"
                    cor_probabilidade = "#17a2b8"
                elif probabilidade >= 40:
                    mensagem_probabilidade = "⚡ Momento de intensificar! Aumente as ações de marketing e vendas!"
                    cor_probabilidade = "#ffc107"
                elif probabilidade >= 20:
                    mensagem_probabilidade = "🎯 Hora de agir! Revise suas estratégias e faça ajustes!"
                    cor_probabilidade = "#fd7e14"
                else:
                    mensagem_probabilidade = "🔥 Alerta! Momento de tomar ações urgentes para reverter o cenário!"
                    cor_probabilidade = "#dc3545"

            st.markdown(f"""
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; color: #666;">
                        <p style="margin: 0;">Meta do Mês: R$ {meta_receita:,.2f}</p>
                        <p style="margin: 0;">Projeção: R$ {receita_projetada:,.2f} ({(receita_projetada/meta_receita*100):.1f}% da meta)</p>
                    </div>
                    <div style="width: 100%; background-color: #f0f2f6; border-radius: 10px;">
                        <div style="width: {min(percentual_meta, 100)}%; height: 20px; background-color: {'#28a745' if percentual_meta >= 100 else '#dc3545' if percentual_meta < 80 else '#17a2b8'}; 
                            border-radius: 10px; text-align: center; color: white; line-height: 20px;">
                            {percentual_meta:.1f}%
                        </div>
                    </div>
                    <div style="
                        margin-top: 15px;
                        padding: 15px;
                        border-radius: 10px;
                        background-color: {cor_probabilidade}15;
                        border: 1px solid {cor_probabilidade};
                    ">
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 8px;
                        ">
                            <strong style="color: {cor_probabilidade};">Probabilidade de atingir a meta</strong>
                            <span style="
                                background-color: {cor_probabilidade};
                                color: white;
                                padding: 4px 12px;
                                border-radius: 15px;
                                font-weight: bold;
                            ">{probabilidade:.1f}%</span>
                        </div>
                        <p style="
                            margin: 0;
                            color: {cor_probabilidade};
                            font-size: 0.95em;
                        ">{mensagem_probabilidade}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Adiciona explicação detalhada do Run Rate
            with st.expander("ℹ️ Como o Run Rate é calculado?"):
                st.markdown(f"""
                    ### Cálculo do Run Rate

                    O Run Rate é uma forma de avaliar se você está no caminho certo para atingir sua meta mensal, considerando o número de dias que já se passaram no mês.
                    
                    **Dados do cálculo atual:**
                    - Meta do mês: R$ {meta_receita:,.2f}
                    - Dias passados: {dias_passados} de {last_day} dias
                    - Proporção do mês: {(dias_passados/last_day*100):.1f}%
                    - Meta proporcional: R$ {meta_proporcional:,.2f}
                    - Receita realizada: R$ {total_receita_paga_run_rate:,.2f}
                    - Percentual atingido: {percentual_meta:.1f}%
                    - Probabilidade de atingir a meta: {probabilidade:.1f}%

                    **Como interpretar:**
                    - Se o percentual for 100%, você está exatamente no ritmo para atingir a meta
                    - Acima de 100% significa que está acima do ritmo necessário
                    - Abaixo de 100% indica que precisa acelerar as vendas para atingir a meta

                    **Faixas de Probabilidade:**
                    - 🟢 80-100%: Excelente chance de atingir a meta
                    - 🔵 60-79%: Boa chance, mantenha o foco
                    - 🟡 40-59%: Chance moderada, intensifique as ações
                    - 🟠 20-39%: Chance baixa, momento de revisar estratégias
                    - 🔴 0-19%: Chance muito baixa, ações urgentes necessárias

                    **Exemplo:**
                    Se sua meta é R$ 100.000 e já se passaram 15 dias de um mês com 30 dias:
                    1. Meta proporcional = R$ 100.000 × (15/30) = R$ 50.000
                    2. Se você faturou R$ 60.000, seu Run Rate é 120% (acima do necessário)
                    3. Se faturou R$ 40.000, seu Run Rate é 80% (precisa acelerar)
                """)

                # Adiciona projeção de fechamento
                receita_projetada = total_receita_paga_run_rate * (last_day / dias_passados)
                st.markdown(f"""
                    ### Projeção de Fechamento

                    Mantendo o ritmo atual de vendas:
                    - Projeção de receita: R$ {receita_projetada:,.2f}
                    - Percentual da meta: {(receita_projetada/meta_receita*100):.1f}%
                    - {'🎯 Meta será atingida!' if receita_projetada >= meta_receita else '⚠️ Meta não será atingida no ritmo atual'}
                    
                    {f'Faltam R$ {(meta_receita - receita_projetada):,.2f} para atingir a meta no ritmo atual.' if receita_projetada < meta_receita else ''}
                """)
