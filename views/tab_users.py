import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

def load_users():
    """Load users from JSON file"""
    if os.path.exists('data/users.json'):
        with open('data/users.json', 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    """Save users to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

def display_tab_users():
    st.title("👥 Gerenciamento de Usuários")
    
    # Initialize session state for user management
    if 'users' not in st.session_state:
        st.session_state.users = load_users()
    
    # Create tabs for different user management sections
    tab1, tab2 = st.tabs(["📝 Cadastrar Usuário", "📋 Lista de Usuários"])
    
    with tab1:
        st.subheader("Cadastrar Novo Usuário")
        
        # User registration form
        with st.form("user_registration", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome completo")
                email = st.text_input("E-mail")
                account = st.text_input("Conta (ex: loja1, loja2)")
                
            with col2:
                role = st.selectbox("Função", ["Administrador", "Usuário", "Visualizador"])
                password = st.text_input("Senha", type="password")
                password_confirm = st.text_input("Confirmar senha", type="password")
            
            submitted = st.form_submit_button("Cadastrar")
            
            if submitted:
                # Validate form
                if not all([name, email, role, password, password_confirm, account]):
                    st.error("Por favor, preencha todos os campos.")
                elif password != password_confirm:
                    st.error("As senhas não coincidem.")
                elif any(user['email'] == email and user['account'] == account for user in st.session_state.users):
                    st.error("Este e-mail já está cadastrado para esta conta.")
                else:
                    # Add new user
                    new_user = {
                        'id': len(st.session_state.users) + 1,
                        'name': name,
                        'email': email,
                        'account': account,
                        'role': role,
                        'password': password,  # In a real app, this should be hashed
                        'created_at': datetime.now().isoformat(),
                        'active': True
                    }
                    st.session_state.users.append(new_user)
                    save_users(st.session_state.users)
                    st.success("Usuário cadastrado com sucesso!")
    
    with tab2:
        st.subheader("Usuários Cadastrados")
        
        # Filter by account
        accounts = sorted(list(set(user['account'] for user in st.session_state.users)))
        if accounts:
            selected_account = st.selectbox("Filtrar por conta:", ["Todas"] + accounts)
        
        if not st.session_state.users:
            st.info("Nenhum usuário cadastrado.")
        else:
            # Filter users by selected account
            filtered_users = st.session_state.users
            if selected_account != "Todas":
                filtered_users = [user for user in st.session_state.users if user['account'] == selected_account]
            
            # Convert users to DataFrame for better display
            users_df = pd.DataFrame([
                {
                    'ID': user['id'],
                    'Nome': user['name'],
                    'E-mail': user['email'],
                    'Conta': user['account'],
                    'Função': user['role'],
                    'Status': 'Ativo' if user.get('active', True) else 'Inativo',
                    'Data de Cadastro': datetime.fromisoformat(user['created_at']).strftime('%d/%m/%Y %H:%M')
                }
                for user in filtered_users
            ])
            
            # Display users table
            st.dataframe(
                users_df,
                column_config={
                    'ID': st.column_config.NumberColumn('ID', format='%d'),
                    'Data de Cadastro': st.column_config.DateColumn('Data de Cadastro'),
                    'Status': st.column_config.TextColumn('Status', help='Status do usuário')
                },
                hide_index=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export option
                if st.button("Exportar para Excel"):
                    users_df.to_excel("usuarios_cadastrados.xlsx", index=False)
                    st.success("Dados exportados com sucesso!")
            
            with col2:
                # Delete user option
                if st.button("Limpar todos os registros"):
                    if st.session_state.users:
                        if st.session_state.users:
                            st.session_state.users = []
                            save_users([])
                            st.success("Todos os registros foram removidos!")
                            st.rerun()
            
            # User management section
            st.subheader("Gerenciar Usuário")
            user_email = st.selectbox("Selecione o usuário:", 
                                    options=[f"{user['name']} ({user['email']}) - {user['account']}" for user in filtered_users])
            
            if user_email:
                selected_user = next((user for user in filtered_users 
                                    if f"{user['name']} ({user['email']}) - {user['account']}" == user_email), None)
                
                if selected_user:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Toggle user status
                        current_status = selected_user.get('active', True)
                        if st.button("Desativar Usuário" if current_status else "Ativar Usuário"):
                            for user in st.session_state.users:
                                if user['id'] == selected_user['id']:
                                    user['active'] = not current_status
                                    save_users(st.session_state.users)
                                    st.success(f"Usuário {'ativado' if not current_status else 'desativado'} com sucesso!")
                                    st.rerun()
                    
                    with col2:
                        # Delete single user
                        if st.button("Excluir Usuário"):
                            st.session_state.users = [user for user in st.session_state.users if user['id'] != selected_user['id']]
                            save_users(st.session_state.users)
                            st.success("Usuário excluído com sucesso!")
                            st.rerun() 