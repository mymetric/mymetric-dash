import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import traceback
from modules.components import tabs_css

from tabs.filters import date_filters, traffic_filters_detailed, traffic_filters, attribution_filters
from tabs.tab_general import display_tab_general
from tabs.tab_detailed import display_tab_detailed
from tabs.tab_today import display_tab_today
from tabs.tab_funnel import display_tab_funnel
from tabs.tab_paid_media import display_tab_paid_media
from tabs.tab_config import display_tab_config
from tabs.tab_last_orders import display_tab_last_orders
from tabs.tab_leads import display_tab_leads
from tabs.tab_master import display_tab_master
from tabs.tab_rfm import display_tab_rfm

# Custom Tabs
from tabs_custom.tab_gringa_product_submitted import display_tab_gringa_product_submitted
from tabs_custom.tab_holysoup_crm import display_tab_holysoup_crm
from tabs_custom.tab_coffeemais_users import display_tab_coffeemais_users
from tabs_custom.tab_coffeemais_crm import display_tab_coffeemais_crm
from tabs_custom.tab_holysoup_social import display_tab_holysoup_social

from modules.load_data import load_paid_media, load_popup_leads, save_event_name
from modules.utilities import send_message

def load_app():
    try:
        # Inicializar o estado da página selecionada se não existir
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = "Visão Geral"
        # Atualizar o valor se for "Leads" para "Atribuição 2.0"
        elif st.session_state.selected_page == "Leads":
            st.session_state.selected_page = "Atribuição 2.0"
            
        # Carregar CSS e filtros
        tabs_css()
        
        # Carregar filtros apenas se não estiver na página de Atribuição 2.0
        if st.session_state.selected_page != "Atribuição 2.0":
            date_filters()
            traffic_filters()
            attribution_filters()
            traffic_filters_detailed()

        is_admin = st.session_state.admin

        # Load paid media data
        paid_media = load_paid_media()
        popup_leads = load_popup_leads()
        # Check if all values in 'Data do Cadastro' are None/NaN
        if popup_leads is not None and not popup_leads.empty and popup_leads['Data do Cadastro'].isna().all():
            popup_leads = None


        # Define navigation options based on data availability
        nav_options = ["Visão Geral"]
        nav_options.extend(["Visão Detalhada", "Análise do Dia", "Taxas de Conversão", "Pedidos"])    

        if popup_leads is not None and not popup_leads.empty:
            nav_options.extend(["Atribuição 2.0"])

        if paid_media is not None and not paid_media.empty:
            nav_options.extend(["Mídia Paga"])

        if st.session_state.tablename == 'oculosshop':
            nav_options.extend(["RFM"])

        if st.session_state.tablename == 'coffeemais':
            nav_options.extend(["Usuários"])
            nav_options.extend(["CRM"])

        if st.session_state.tablename == 'gringa':
            nav_options.extend(["Produtos Cadastrados"])

        if st.session_state.tablename == 'holysoup':
            nav_options.extend(["CRM"])
            nav_options.extend(["Social"])

        if is_admin:
            nav_options.extend(["Configurações"])
        
        if st.session_state.username == 'mymetric':
            nav_options.extend(["Master"])
            
        # Criar radio buttons para navegação com key para manter o estado
        selected_page = st.radio(
            "", 
            nav_options, 
            horizontal=True,
            key="page_selector",
            index=nav_options.index(st.session_state.selected_page)
        )
        
        # Atualizar o estado da página selecionada
        if st.session_state.selected_page != selected_page:
            st.session_state.selected_page = selected_page
            st.rerun()

        # Exibir conteúdo baseado na seleção
        if selected_page == "Visão Geral":
            save_event_name(event_name="tab_view", event_params={"tab": "general"})
            display_tab_general()
        
        elif selected_page == "Visão Detalhada":
            save_event_name(event_name="tab_view", event_params={"tab": "detailed"})
            display_tab_detailed()
        
        elif selected_page == "Análise do Dia":
            save_event_name(event_name="tab_view", event_params={"tab": "today"})
            display_tab_today()

        elif selected_page == "Mídia Paga" and "Mídia Paga" in nav_options:
            save_event_name(event_name="tab_view", event_params={"tab": "paid_media"})
            display_tab_paid_media()
        
        elif selected_page == "Atribuição 2.0" and "Atribuição 2.0" in nav_options:
            save_event_name(event_name="tab_view", event_params={"tab": "popup_leads"})
            display_tab_leads()
        
        elif selected_page == "Pedidos":
            save_event_name(event_name="tab_view", event_params={"tab": "last_orders"})
            display_tab_last_orders()
        
        elif selected_page == "Taxas de Conversão":
            save_event_name(event_name="tab_view", event_params={"tab": "funnel"})
            display_tab_funnel()
        
        elif selected_page == "Configurações":
            save_event_name(event_name="tab_view", event_params={"tab": "config"})
            display_tab_config()
        
        elif selected_page == "Master":
            save_event_name(event_name="tab_view", event_params={"tab": "master"})
            display_tab_master()
        
        # CUSTOM TABS
        elif selected_page == "Produtos Cadastrados" and st.session_state.tablename == 'gringa':
            save_event_name(event_name="tab_view", event_params={"tab": "gringa_product_submitted"})
            display_tab_gringa_product_submitted()
            
        elif selected_page == "Usuários" and st.session_state.tablename == 'coffeemais':
            save_event_name(event_name="tab_view", event_params={"tab": "coffeemais_users"})
            display_tab_coffeemais_users()
            
        elif selected_page == "CRM" and st.session_state.tablename in ['coffeemais', 'holysoup']:
            save_event_name(event_name="tab_view", event_params={"tab": "crm"})
            if st.session_state.tablename == 'coffeemais':
                display_tab_coffeemais_crm()
            else:
                display_tab_holysoup_crm()
                
        elif selected_page == "RFM" and st.session_state.tablename == 'oculosshop':
            save_event_name(event_name="tab_view", event_params={"tab": "rfm"})
            display_tab_rfm()
            
        elif selected_page == "Social" and st.session_state.tablename == 'holysoup':
            save_event_name(event_name="tab_view", event_params={"tab": "social"})
            display_tab_holysoup_social()

    except Exception as e:
        st.error(f"Erro ao carregar a aplicação: {str(e)}")
        st.error("Por favor, tente recarregar a página.")
        send_message(f"Erro ao carregar a página: {e}\nUsuário: {st.session_state.username}\nTabela: {st.session_state.tablename}\nPágina: {st.session_state.selected_page}")
    