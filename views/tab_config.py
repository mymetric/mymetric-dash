import streamlit as st

from views.partials.run_rate import load_table_metas
from datetime import datetime
import pandas as pd
from modules.load_data import save_goals, load_users, save_users, delete_user
import random
import string
import time

def goals_config():
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
    
def display_tab_config():
    st.title("🔧 Configurações")
    st.markdown("""---""")


    st.subheader("Cadastro de Usuários")

    with st.form(key="cadastro_usuario"):
        email = st.text_input("Email do usuário", key="email")
        admin = st.checkbox("Administrador", key="admin")
        
        # Validar email
        is_valid_email = True if "@" in email and "." in email.split("@")[1] else False
        
        password = None
        if email and is_valid_email:
            # Gerar senha aleatória com 12 caracteres
            # Garantir que a senha atenda aos requisitos mínimos
            while True:
                password = ''.join(random.choices(
                    string.ascii_uppercase + 
                    string.ascii_lowercase + 
                    string.digits + 
                    string.punctuation, k=12))
                
                # Validar se atende todos os critérios
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)
                has_special = any(not c.isalnum() for c in password)
                
                if all([has_upper, has_lower, has_digit, has_special]):
                    break
            
            st.text_input("Senha gerada", value=password, type="password", key="password", disabled=True)
        
        if email and not is_valid_email:
            st.error("Por favor insira um email válido")

        submit_button = st.form_submit_button("Salvar")
        if submit_button and password:
            save_users(email, password, admin)
            st.success("Usuário salvo com sucesso!")
            time.sleep(15)
            st.rerun()

    users = load_users()
    
    if not users.empty:
        st.subheader("Usuários Cadastrados")
        
        # Formatar a tabela para exibição
        display_df = users.copy()
        display_df.columns = ['Email', 'Admin', 'Controle de Acesso']
        display_df['Admin'] = display_df['Admin'].map({True: 'Sim', False: 'Não'})
        
        # Adicionar coluna de ações
        for index, row in display_df.iterrows():
            form_key = f"delete_form_{index}_{row['Email']}"  # Chave única mais específica
            with st.form(key=form_key, clear_on_submit=True):  # Adicionado clear_on_submit
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"**Email:** {row['Email']}")
                    st.write(f"Admin: {row['Admin']} | Controle de Acesso: {row['Controle de Acesso']}")
                with col2:
                    submit = st.form_submit_button("🗑️ Deletar", type="primary", use_container_width=True)
                    if submit:
                        
                        try:
                            delete_result = delete_user(row['Email'])
                            
                            if delete_result:
                                st.toast(f"Usuário {row['Email']} deletado com sucesso!")
                                users = load_users()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Erro ao deletar usuário")
                        except Exception as e:
                            st.error(f"Erro durante a deleção: {str(e)}")
                            st.write(f"Debug: Stack trace completo:", e)
            st.divider()

    goals_config()
    
    