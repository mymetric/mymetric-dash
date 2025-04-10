import sys
import os
from datetime import datetime
import pandas as pd
import json
import argparse
import streamlit as st
import calendar

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.load_data import load_goals, load_current_month_revenue

def check_monthly_goal(tablename):
    """Verifica o status da meta do mês atual."""
    try:
        # Configurar o tablename na sessão do Streamlit
        if not hasattr(st.session_state, 'tablename'):
            st.session_state.tablename = tablename

        # Carregar metas
        df_goals = load_goals()
        if df_goals.empty or 'goals' not in df_goals.columns or df_goals['goals'].isna().all():
            print("❌ Meta do mês não cadastrada")
            return

        # Extrair meta do mês atual
        goals_json = df_goals['goals'].iloc[0]
        if not goals_json:
            print("❌ Meta do mês não cadastrada")
            return

        metas = json.loads(goals_json)
        current_month = datetime.now().strftime("%Y-%m")
        meta_receita = metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)

        if meta_receita == 0:
            print("❌ Meta do mês não cadastrada")
            return

        # Carregar receita atual do mês
        df_revenue = load_current_month_revenue()
        total_receita_mes = float(df_revenue['total_mes'].iloc[0])

        # Calcular projeção para o final do mês
        hoje = datetime.now()
        dia_atual = hoje.day
        _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
        
        # Calcular média diária até agora
        media_diaria = total_receita_mes / dia_atual if dia_atual > 0 else 0
        
        # Calcular dias restantes
        dias_restantes = ultimo_dia - dia_atual
        
        # Calcular projeção
        projecao_final = total_receita_mes + (media_diaria * dias_restantes)

        # Calcular percentual atingido e projetado
        percentual_atingido = (total_receita_mes / meta_receita * 100) if meta_receita > 0 else 0
        percentual_projetado = (projecao_final / meta_receita * 100) if meta_receita > 0 else 0

        print(f"✅ Meta do mês: R$ {meta_receita:,.2f}")
        print(f"💰 Receita atual: R$ {total_receita_mes:,.2f}")
        print(f"📊 Percentual atingido: {percentual_atingido:.1f}%")
        print(f"📈 Média diária: R$ {media_diaria:,.2f}")
        print(f"📅 Dias restantes: {dias_restantes}")
        print(f"🎯 Projeção final: R$ {projecao_final:,.2f}")
        print(f"📊 Percentual projetado: {percentual_projetado:.1f}%")

    except Exception as e:
        print(f"❌ Erro ao verificar meta: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verifica a meta do mês para uma tabela específica.')
    parser.add_argument('tablename', help='Nome da tabela para verificar a meta')
    args = parser.parse_args()
    
    check_monthly_goal(args.tablename)
