import streamlit as st

from views.partials.run_rate import load_table_metas
from datetime import datetime
import pandas as pd
from modules.load_data import save_goals

def display_tab_config():
    st.title("🔧 Configurações")
    st.markdown("""---""")

    
    # Carregar configurações existentes usando table
    current_metas = load_table_metas()
    current_month = datetime.now().strftime("%Y-%m")
    meta_receita = current_metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
    
    # Criar campo para seleção do mês
    st.subheader("Meta de Receita Paga")
    
    
    # Lista dos últimos 12 meses para seleção
    months = []
    for i in range(12):
        month = (datetime.now() - pd.DateOffset(months=i)).strftime("%Y-%m")
        months.append(month)
    
    selected_month = st.selectbox(
        "Mês de Referência",
        options=months,
        format_func=lambda x: pd.to_datetime(x).strftime("%B/%Y").capitalize()
    )
    
    # Pegar o valor atual da meta para o mês selecionado
    current_value = meta_receita
    
    meta_receita_paga = st.number_input(
        "Meta de Receita Paga (R$)",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        help="Digite a meta de receita paga",
        value=float(current_value)
    )

    if st.button("Salvar Meta"):
        
        # Garantir que a estrutura existe
        if 'metas_mensais' not in current_metas:
            current_metas['metas_mensais'] = {}
            
        # Atualizar ou criar a meta para o mês selecionado
        current_metas['metas_mensais'][selected_month] = {
            "meta_receita_paga": meta_receita_paga
        }

        save_goals(current_metas)

        st.toast(f"Salvando meta... {meta_receita_paga}")
        
        # save_table_metas(current_metas)
        st.success("Meta salva com sucesso!")

        
        # st.rerun()