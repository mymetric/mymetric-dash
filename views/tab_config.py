import streamlit as st

from views.partials.run_rate import load_table_metas
from datetime import datetime
import pandas as pd
from modules.load_data import save_goals, load_users, save_users, delete_user, save_coupons, load_coupons, delete_coupon
import random
import string
import time
from modules.utilities import send_discord_message

def users_config():
    st.subheader("Cadastro de Usuários")

    with st.form(key="cadastro_usuario"):
        email = st.text_input("Email do usuário", key="new_user_email")
        admin = st.checkbox("Administrador", key="new_user_admin")
        
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
            tablename = st.session_state.tablename
            send_discord_message(f"Usuário {email} cadastrado em {tablename}!")
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
            with st.form(key=form_key):  # Cria um formulário que limpa após envio
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"**Email:** {row['Email']}")
                    st.write(f"Admin: {row['Admin']} | Controle de Acesso: {row['Controle de Acesso']}")
                with col2:
                    submit = st.form_submit_button("🗑️ Deletar", use_container_width=True)
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

def goals_config():
    st.subheader("Meta de Receita Paga")
    
    # Carregar configurações existentes usando table
    current_metas = load_table_metas()
    current_month = datetime.now().strftime("%Y-%m")
    if current_metas:
        meta_receita = current_metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
    else:
        meta_receita = 0
    
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
        st.success("Meta salva com sucesso!")

def coupons_config():
    st.subheader("Gerenciamento de Cupons")
    
    # Form para adicionar novo cupom
    with st.form("novo_cupom"):
        coupon_code = st.text_input("Código do Cupom")
        coupon_category = st.text_input("Categoria do Cupom")
        
        submitted = st.form_submit_button("Salvar Cupom")
        if submitted and coupon_code and coupon_category:
            save_coupons(coupon_code, coupon_category)
            st.success(f"Cupom {coupon_code} salvo com sucesso!")
            st.rerun()
    
    st.divider()
    
    # Exibir lista de cupons existentes
    coupons = load_coupons()
    
    if not coupons.empty:
        # Adicionar campos de busca
        search_code = st.text_input("🔍 Buscar por código", placeholder="Digite o código do cupom...")
        search_category = st.text_input("🔍 Buscar por categoria", placeholder="Digite a categoria...")
        
        # Filtrar cupons baseado na busca
        if search_code or search_category:
            filtered_coupons = coupons[
                (coupons['Cupom'].str.contains(search_code, case=False, na=False)) &
                (coupons['Categoria'].str.contains(search_category, case=False, na=False))
            ]
        else:
            filtered_coupons = coupons
        
        # Mostrar estatísticas
        total_coupons = len(filtered_coupons)
        st.caption(f"Total de cupons encontrados: {total_coupons}")
        
        # Estilo CSS para os cards
        st.markdown("""
        <style>
        .coupon-card {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .coupon-info {
            display: flex;
            align-items: center;
        }
        .coupon-code {
            color: #0066cc;
            font-family: monospace;
            font-size: 1.1em;
            padding: 0.2rem 0.4rem;
            background-color: #e9ecef;
            border-radius: 0.3rem;
        }
        .coupon-category {
            color: #666;
            margin-left: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Exibir cupons em cards
        for index, row in filtered_coupons.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div class="coupon-card">
                    <div class="coupon-info">
                        <span class="coupon-code">{row['Cupom']}</span>
                        <span class="coupon-category">📁 {row['Categoria']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_{row['Cupom']}", help="Deletar cupom", type="secondary"):
                    if delete_coupon(row['Cupom']):
                        st.success(f"Cupom {row['Cupom']} deletado com sucesso!")
                        coupons = load_coupons()
                        st.rerun()
                    else:
                        st.error(f"Erro ao deletar o cupom {row['Cupom']}")
    else:
        st.info("Nenhum cupom cadastrado.")

def display_tab_config():
    st.title("🔧 Configurações")
    st.markdown("""---""")

    # Criar tabs para cada seção
    tab_users, tab_goals, tab_coupons = st.tabs([
        "👥 Usuários",
        "💰 Metas",
        "🎫 Cupons"
    ])
    
    # Conteúdo da tab de usuários
    with tab_users:
        users_config()
    
    # Conteúdo da tab de metas
    with tab_goals:
        goals_config()
    
    # Conteúdo da tab de cupons
    with tab_coupons:
        coupons_config()
    
    