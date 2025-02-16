import streamlit as st
import pandas as pd
from datetime import timedelta
from streamlit_cookies_controller import CookieController

def display_notices():
    
    with st.expander("🔔 Novidades", expanded=True):
        controller = CookieController()

        def display_notice(title, date, message, expiry_date):
            # Sempre exibe o card
            st.markdown(f"""
                <div style="
                    padding: 1.2rem;
                    border-radius: 0.8rem;
                    background-color: #fefefe;
                    margin-bottom: 1.2rem;
                    border: 1px solid #e9ecef;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <h3 style="color: #4a90e2; margin-bottom: 0.2rem; font-weight: 500; font-size: 1.3em;">{title}</h3>
                    <p style="color: #8c8c8c; font-size: 0.85em; margin-bottom: 0.7rem; font-style: italic;">{date}</p>
                    <p style="color: #4d4d4d; line-height: 1.5;">{message}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Verifica se deve exibir toast (novidade com menos de 7 dias)
            notice_date = pd.Timestamp(expiry_date).date()
            today = pd.Timestamp.now().date()
            
            if (today <= notice_date + timedelta(days=7)):
                # Cria um ID único para o toast
                toast_id = f"notice_{expiry_date}_{title.lower().replace(' ', '_')}"
                
                # Verifica se o toast já foi exibido
                if not controller.get(toast_id):
                    st.toast(f"🔔 Nova funcionalidade: {title}", icon="✨")
                    # Salva cookie para não mostrar novamente
                    controller.set(toast_id, "shown", max_age=30*24*60*60)  # 30 dias

        display_notice(
            "Atribuição de Pedidos",
            "16 de fevereiro de 2025",
            "Agora é possível escolher entre 'Último Clique Não Direto' e 'Primeiro Clique' como modelo de atribuição de pedidos. Isso é muito útil para quando você está usando o MyMetricHUB várias vezes ao dia sem precisar ficar logando.",
            "2025-02-16"
        )
        
        display_notice(
            "Análise de Meta Ads",
            "13 de fevereiro de 2025",
            "Agora é possível analisar os dados do Meta Ads na aba de Análise de Mídia Paga.",
            "2025-02-13"
        )
        
        display_notice(
            "Cadastro de Cupons",
            "6 de fevereiro de 2025",
            "Agora é possível organizar cupons por áreas como CRM, cupons de Mídia Paga, Influenciadores ou o que você desejar. Você encontra essa funcionalidade na aba de Configurações.",
            "2025-02-06"
        )

        display_notice(
            "Gerenciamento de Usuários", 
            "1 de fevereiro de 2025",
            "Agora é possível criar usuários e gerenciar suas permissões. Verifique a aba de Configurações.",
            "2025-02-01"
        )

        display_notice(
            "Login Persistente",
            "2 de fevereiro de 2025", 
            "Agora o login dura até 8 horas. Isso é muito útil para quando você está usando o MyMetricHUB várias vezes ao dia sem precisar ficar logando.",
            "2025-02-02"
        )