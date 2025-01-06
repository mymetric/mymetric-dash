import streamlit as st
from datetime import date
import json
import os

def load_closed_notices(username):
    """Carrega os avisos fechados do arquivo JSON do usuário."""
    notices_path = f'configs/notices/{username}.json'
    
    try:
        with open(notices_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_closed_notices(username, notices):
    """Salva os avisos fechados no arquivo JSON do usuário."""
    # Garante que o diretório existe
    os.makedirs('configs/notices', exist_ok=True)
    
    notices_path = f'configs/notices/{username}.json'
    with open(notices_path, 'w') as f:
        json.dump(notices, f, indent=2)

def show_new_year_notice(username):
    """Exibe a mensagem de ano novo com botão de fechar estilizado."""
    closed_notices = load_closed_notices(username)
    
    if not closed_notices.get('new_year_2025', False):
        st.info(f"""
        ### 🎉 Feliz 2025, {username.upper()}!
        
        Que este ano seja repleto de insights valiosos e métricas positivas. Boas análises! 📊
        """)
        if st.button("Obrigado, vamos juntos!", key="close_new_year", type="primary"):
            closed_notices['new_year_2025'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

def show_feature_notices(username, meta_receita=0):
    """Exibe os avisos de novas features com opção de não mostrar novamente."""
    closed_notices = load_closed_notices(username)
    
    # Aviso de metas
    if not closed_notices.get('meta_notice', False) and meta_receita == 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            ### 🎯 Configure suas Metas de Faturamento!
            
            Agora você pode definir e acompanhar suas metas mensais de receita.
            
            Para começar:
            1. Acesse a aba "⚙️ Configurações"
            2. Defina sua meta mensal
            3. Acompanhe o progresso aqui na aba "Visão Geral"
            
            Comece agora mesmo a trackear seus objetivos! 📈
            """)
            if st.button("Não mostrar novamente", key="meta_notice", type="primary"):
                closed_notices['meta_notice'] = True
                save_closed_notices(username, closed_notices)
                st.rerun()

        with col2:
            st.info("""
            ### 📊 Nova Aba de Análise do Dia!
            
            Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
            
            Recursos disponíveis:
            - Acompanhamento hora a hora
            - Comparação com dias anteriores
            - Acompanhamento de meta diária
            
            Confira agora mesmo! 🚀
            """)
            if st.button("Não mostrar novamente", key="today_notice", type="primary"):
                closed_notices['today_notice'] = True
                save_closed_notices(username, closed_notices)
                st.rerun()

    # Aviso da aba de análise do dia
    elif not closed_notices.get('today_notice', False):
        st.info("""
        ### 📊 Nova Aba de Análise do Dia!
        
        Agora você pode acompanhar suas métricas em tempo real na aba "Análise do Dia".
        
        Recursos disponíveis:
        - Acompanhamento hora a hora
        - Comparação com dias anteriores
        - Principais fontes de tráfego do dia
        
        Confira agora mesmo! 🚀
        """)
        if st.button("Não mostrar novamente", key="today_notice", type="primary"):
            closed_notices['today_notice'] = True
            save_closed_notices(username, closed_notices)
            st.rerun()

def initialize_notices():
    """Inicializa o estado dos avisos se não existir."""
    if 'closed_notices' not in st.session_state:
        st.session_state.closed_notices = {} 