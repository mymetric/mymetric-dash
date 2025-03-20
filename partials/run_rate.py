import streamlit as st
from modules.load_data import load_goals
from datetime import datetime, date
import calendar
import pandas as pd
import json    

def load_table_metas():
    # Definir estrutura padrão
    default_metas = {
        "metas_mensais": {
            datetime.now().strftime("%Y-%m"): {
                "meta_receita_paga": 0
            }
        }
    }
    
    try:
        df = load_goals()
        if df.empty or 'goals' not in df.columns or df['goals'].isna().all():
            return default_metas
            
        goals_json = df['goals'].iloc[0]
        if not goals_json:
            return default_metas
            
        return json.loads(goals_json)
    
    except Exception as e:
        st.warning(f"Erro ao carregar metas: {str(e)}")
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
            
            total_receita_paga_run_rate = df_run_rate["Receita Paga"].sum()
            percentual_meta = (total_receita_paga_run_rate / meta_proporcional) * 100 if meta_proporcional > 0 else 0
            
            st.header("Run Rate")

            receita_projetada = total_receita_paga_run_rate * (last_day / dias_passados) if dias_passados > 0 else 0
            media_diaria = total_receita_paga_run_rate / dias_passados if dias_passados > 0 else 0
            dias_restantes = last_day - dias_passados
            valor_faltante = meta_receita - total_receita_paga_run_rate
            valor_necessario_por_dia = valor_faltante / dias_restantes if dias_restantes > 0 else float('inf')
            
            # Definir cores e mensagens
            if valor_faltante <= 0:
                probabilidade = 100
                mensagem_probabilidade = "Meta atingida! Continue o ótimo trabalho!"
                cor_probabilidade = "#10B981"
                gradient = "linear-gradient(135deg, #10B981, #059669)"
            elif dias_restantes == 0:
                if valor_faltante > 0:
                    probabilidade = 0
                    mensagem_probabilidade = "Tempo esgotado para este mês"
                    cor_probabilidade = "#EF4444"
                    gradient = "linear-gradient(135deg, #EF4444, #DC2626)"
                else:
                    probabilidade = 100
                    mensagem_probabilidade = "Meta atingida! Continue o ótimo trabalho!"
                    cor_probabilidade = "#10B981"
                    gradient = "linear-gradient(135deg, #10B981, #059669)"
            else:
                razao = media_diaria / valor_necessario_por_dia if valor_necessario_por_dia > 0 else 0
                probabilidade = min(100, razao * 100)
                
                if probabilidade >= 80:
                    mensagem_probabilidade = "Excelente ritmo! Você está muito próximo de atingir a meta!"
                    cor_probabilidade = "#10B981"
                    gradient = "linear-gradient(135deg, #10B981, #059669)"
                elif probabilidade >= 60:
                    mensagem_probabilidade = "Bom progresso! Continue focado que a meta está ao seu alcance!"
                    cor_probabilidade = "#3B82F6"
                    gradient = "linear-gradient(135deg, #3B82F6, #2563EB)"
                elif probabilidade >= 40:
                    mensagem_probabilidade = "Momento de intensificar! Aumente as ações de marketing e vendas!"
                    cor_probabilidade = "#F59E0B"
                    gradient = "linear-gradient(135deg, #F59E0B, #D97706)"
                elif probabilidade >= 20:
                    mensagem_probabilidade = "Hora de agir! Revise suas estratégias e faça ajustes!"
                    cor_probabilidade = "#F97316"
                    gradient = "linear-gradient(135deg, #F97316, #EA580C)"
                else:
                    mensagem_probabilidade = "Alerta! Momento de tomar ações urgentes para reverter o cenário!"
                    cor_probabilidade = "#EF4444"
                    gradient = "linear-gradient(135deg, #EF4444, #DC2626)"

            # Renderizar o card principal
            st.markdown(f"""
                <div style="background:white; border-radius:16px; padding:24px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); margin:20px 0;">
                    <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:24px; margin-bottom:24px;">
                        <div style="background:#F8FAFC; padding:16px; border-radius:12px;">
                            <div style="color:#64748B; font-size:14px; margin-bottom:8px;">Meta do Mês</div>
                            <div style="color:#0F172A; font-size:24px; font-weight:600;">R$ {meta_receita:,.2f}</div>
                        </div>
                        <div style="background:#F8FAFC; padding:16px; border-radius:12px;">
                            <div style="color:#64748B; font-size:14px; margin-bottom:8px;">Projeção</div>
                            <div style="color:#0F172A; font-size:24px; font-weight:600;">R$ {receita_projetada:,.2f}</div>
                            <div style="color:#64748B; font-size:12px; margin-top:4px;">{(receita_projetada/meta_receita*100):.1f}% da meta</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Renderizar a barra de progresso
            st.markdown(f"""
                <div style="margin-bottom:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="color:#64748B; font-size:14px;">Progresso</div>
                        <div style="color:{cor_probabilidade}; font-weight:500;">{percentual_meta:.1f}%</div>
                    </div>
                    <div style="width:100%; height:8px; background:#F1F5F9; border-radius:4px; overflow:hidden;">
                        <div style="width:{min(percentual_meta, 100)}%; height:100%; background:{gradient}; border-radius:4px; transition:width 0.3s ease;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Renderizar o card de probabilidade
            st.markdown(f"""
                <div style="background:{cor_probabilidade}10; border:1px solid {cor_probabilidade}25; padding:20px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <div style="width:8px; height:8px; border-radius:50%; background:{cor_probabilidade};"></div>
                            <span style="color:{cor_probabilidade}; font-weight:500;">Probabilidade de atingir a meta</span>
                        </div>
                        <div style="background:{cor_probabilidade}; color:white; padding:6px 16px; border-radius:20px; font-weight:500; font-size:14px;">{probabilidade:.1f}%</div>
                    </div>
                    <p style="margin:0; color:{cor_probabilidade}; font-size:14px; line-height:1.5;">{mensagem_probabilidade}</p>
                </div>
            """, unsafe_allow_html=True)

            # Renderizar as métricas adicionais
            st.markdown(f"""
                <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:24px; margin-bottom:32px;">
                    <div style="text-align:center;">
                        <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Dias Passados</div>
                        <div style="color:#0F172A; font-weight:500;">{dias_passados} de {last_day}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Média Diária</div>
                        <div style="color:#0F172A; font-weight:500;">R$ {media_diaria:,.2f}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Meta Diária</div>
                        <div style="color:#0F172A; font-weight:500;">R$ {valor_necessario_por_dia:,.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

            # Adiciona explicação detalhada do Run Rate
            with st.expander("Como o Run Rate é calculado?"):
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
                    - 80-100%: Excelente chance de atingir a meta
                    - 60-79%: Boa chance, mantenha o foco
                    - 40-59%: Chance moderada, intensifique as ações
                    - 20-39%: Chance baixa, momento de revisar estratégias
                    - 0-19%: Chance muito baixa, ações urgentes necessárias
                """)
