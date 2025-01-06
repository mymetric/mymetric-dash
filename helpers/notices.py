import streamlit as st
from datetime import date

def show_new_year_notice(username):
    """Exibe a mensagem de ano novo com botão de fechar estilizado."""
    if not st.session_state.closed_notices.get('new_year_2025', False):
        st.info(f"""
        ### 🎉 Feliz 2025, {username.upper()}!
        
        Que este ano seja repleto de insights valiosos e métricas positivas. Boas análises! 📊
        """)
        if st.button("Obrigado, vamos juntos!", key="close_new_year", type="primary"):
            st.session_state.closed_notices['new_year_2025'] = True
            st.rerun()

def show_feature_notices(username, meta_receita=0):
    """Exibe os avisos de novas features com opção de não mostrar novamente."""
    
    # Aviso de metas
    if not st.session_state.closed_notices.get(f'{username}_meta_notice', False) and meta_receita == 0:
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
                st.session_state.closed_notices[f'{username}_meta_notice'] = True
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
                st.session_state.closed_notices[f'{username}_today_notice'] = True
                st.rerun()

    # Aviso da aba de análise do dia
    elif not st.session_state.closed_notices.get(f'{username}_today_notice', False):
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
            st.session_state.closed_notices[f'{username}_today_notice'] = True
            st.rerun()

def initialize_notices():
    """Inicializa o estado dos avisos se não existir."""
    if 'closed_notices' not in st.session_state:
        st.session_state.closed_notices = {} 