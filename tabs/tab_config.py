import streamlit as st

from partials.run_rate import load_table_metas
from datetime import datetime
import pandas as pd
from modules.load_data import save_goals, load_users, save_users, delete_user, save_event_name, save_traffic_categories, load_traffic_categories, delete_traffic_category, load_costs, save_costs
import random
import string
import time
from modules.utilities import send_message
from partials.notices import display_notices

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
            send_message(f"✨ *Novo usuário cadastrado!*\n\n📧 Email: {email}\n🏢 Empresa: {tablename}")
            save_event_name("user_created", {"email": email, "admin": admin})
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
    
    # Garantir que current_metas tem a estrutura correta
    if not isinstance(current_metas, dict):
        current_metas = {
            "metas_mensais": {
                current_month: {
                    "meta_receita_paga": 0
                }
            }
        }
    
    # Garantir que metas_mensais existe
    if 'metas_mensais' not in current_metas:
        current_metas['metas_mensais'] = {}
    
    # Pegar valor atual da meta
    meta_receita = current_metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)
    
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
    current_value = current_metas.get('metas_mensais', {}).get(selected_month, {}).get('meta_receita_paga', 0)
    
    meta_receita_paga = st.number_input(
        "Meta de Receita Paga (R$)",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        help="Digite a meta de receita paga",
        value=float(current_value)
    )

    if st.button("Salvar Meta"):
        try:
            # Garantir que a estrutura existe
            if 'metas_mensais' not in current_metas:
                current_metas['metas_mensais'] = {}
            
            # Garantir que o valor é um float válido
            meta_receita_paga_float = float(meta_receita_paga)
            
            # Garantir que o mês selecionado existe na estrutura
            if selected_month not in current_metas['metas_mensais']:
                current_metas['metas_mensais'][selected_month] = {}
            
            # Atualizar a meta
            current_metas['metas_mensais'][selected_month] = {
                "meta_receita_paga": meta_receita_paga_float
            }
            
            # Tentar salvar
            save_goals(current_metas)
            st.toast(f"Salvando meta... R$ {meta_receita_paga_float:,.2f}")
            st.success("Meta salva com sucesso!")
            
        except ValueError as e:
            st.error(f"Erro ao processar o valor da meta: {str(e)}")
        except Exception as e:
            st.error(f"Erro ao salvar meta: {str(e)}")
            st.warning("Detalhes do erro para debug:")
            st.write({
                "meta_value": meta_receita_paga,
                "meta_type": type(meta_receita_paga),
                "current_metas": current_metas
            })

def traffic_categories_config():
    st.subheader("Categorização de Tráfego")
    
    # Debug: Imprimir informações sobre o estado da sessão
    print(f"Estado da sessão: {st.session_state}")
    
    # Carregar categorias existentes
    categories_df = load_traffic_categories()
    print(f"Categorias carregadas: {categories_df}")
    
    # Formulário para adicionar nova categoria
    with st.form("nova_categoria"):
        st.markdown("### Nova Categoria")
        category_name = st.text_input("Nome da Categoria")
        description = st.text_area("Descrição")
        
        # Campos para regras
        st.markdown("### Regras de Classificação")
        st.markdown("Use expressões regulares (regex) para definir as regras de classificação.")
        
        rules = {
            "type": "regex",
            "rules": {
                "origem": st.text_input("Origem (regex)"),
                "midia": st.text_input("Mídia (regex)"),
                "campanha": st.text_input("Campanha (regex)"),
                "conteudo": st.text_input("Conteúdo (regex)"),
                "pagina_de_entrada": st.text_input("Página de Entrada (regex)"),
                "termo": st.text_input("Termo (regex)"),
                "cupom": st.text_input("Cupom (regex)")
            }
        }
        
        submitted = st.form_submit_button("Adicionar Categoria")
        
        if submitted:
            if category_name:
                # Remover regras vazias
                rules["rules"] = {k: v for k, v in rules["rules"].items() if v}
                
                if save_traffic_categories(category_name, description, rules):
                    st.success("Categoria adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao adicionar categoria.")
            else:
                st.error("Por favor, preencha o nome da categoria.")
    
    # Exibir categorias existentes
    if not categories_df.empty:
        st.markdown("### Categorias Existentes")
        
        # Campo de busca
        search_term = st.text_input("Buscar categorias", key="category_search")
        
        # Filtrar categorias baseado no termo de busca
        if search_term:
            categories_df = categories_df[
                categories_df['Nome'].str.contains(search_term, case=False, na=False) |
                categories_df['Descrição'].str.contains(search_term, case=False, na=False)
            ]
        
        # Exibir categorias
        for _, row in categories_df.iterrows():
            with st.expander(f"📊 {row['Nome']}", expanded=True):
                if row['Descrição']:
                    st.markdown(f"**Descrição:** {row['Descrição']}")
                
                if row['Regras'] and 'rules' in row['Regras']:
                    st.markdown("**Regras:**")
                    for field, value in row['Regras']['rules'].items():
                        if value:
                            st.markdown(f"- {field.title()}: `{value}`")
                
                if st.button("🗑️ Deletar", key=f"delete_{row['Nome']}"):
                    if delete_traffic_category(row['Nome']):
                        st.success("Categoria deletada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao deletar categoria.")
    else:
        st.info("Nenhuma categoria cadastrada ainda.")

def costs_config():
    st.subheader("Configuração de Custos")
    
    # Carregar categorias de tráfego
    categories_df = load_traffic_categories()
    if categories_df.empty:
        st.warning("Nenhuma categoria de tráfego cadastrada. Por favor, cadastre categorias na aba 'Categorias de Tráfego' primeiro.")
        return
    
    # Carregar custos existentes
    costs_df = load_costs()
    
    # Formulário para adicionar/editar custos
    with st.form("custo_form"):
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
        
        # Selecionar categoria
        selected_category = st.selectbox(
            "Categoria de Tráfego",
            options=categories_df['Nome'].tolist()
        )
        
        # Campos para custos
        cost_of_product_percentage = st.number_input(
            "Custo do Produto (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            help="Porcentagem do custo do produto em relação à receita"
        )
        
        total_cost = st.number_input(
            "Custo Total (R$)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            help="Custo total da categoria no mês"
        )
        
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
            if save_costs(selected_month, selected_category, cost_of_product_percentage, total_cost):
                st.success("Custos salvos com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao salvar custos.")
    
    # Exibir custos existentes
    if not costs_df.empty:
        st.markdown("### Custos Cadastrados")
        
        # Campo de busca
        search_term = st.text_input("Buscar custos", key="costs_search")
        
        # Filtrar custos baseado no termo de busca
        if search_term:
            costs_df = costs_df[
                costs_df['Categoria'].str.contains(search_term, case=False, na=False) |
                costs_df['Mês'].str.contains(search_term, case=False, na=False)
            ]
        
        # Exibir custos em uma tabela
        st.data_editor(
            costs_df,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhum custo cadastrado ainda.")

def display_tab_config():
    st.title("Configurações")
    
    tab_users, tab_goals, tab_traffic, tab_costs = st.tabs([
        "👥 Usuários",
        "🎯 Metas",
        "🚦 Categorias de Tráfego",
        "💰 Custos"
    ])
    
    with tab_users:
        users_config()
    
    with tab_goals:
        goals_config()
    
    with tab_traffic:
        traffic_categories_config()
        
    with tab_costs:
        costs_config()
    
    