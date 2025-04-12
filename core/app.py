import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import traceback
import time
from modules.components import tabs_css

from tabs.filters import date_filters, traffic_filters_detailed, traffic_filters
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
from tabs_custom.tab_kaisan_erp import display_tab_kaisan_erp

from modules.load_data import load_paid_media, load_popup_leads, save_event_name, load_basic_data, load_detailed_data
from modules.utilities import send_message

def load_app():
    try:
        with st.spinner("🔄 Inicializando aplicação..."):
            # Inicializar datas se não existirem
            if 'start_date' not in st.session_state:
                st.session_state.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if 'end_date' not in st.session_state:
                st.session_state.end_date = datetime.now().strftime('%Y-%m-%d')

            # Inicializar a página selecionada se não existir
            if 'selected_page' not in st.session_state:
                st.session_state.selected_page = "Visão Geral"
            # Atualizar o valor se for "Leads" para "Atribuição 2.0"
            elif st.session_state.selected_page == "Leads":
                st.session_state.selected_page = "Atribuição 2.0"

            # Carregar CSS e filtros
            tabs_css()
            
            # Definir is_admin
            is_admin = st.session_state.get('admin', False)

            # Definir quais filtros devem ser carregados para cada aba
            pages_without_filters = ["Atribuição 2.0", "Master", "Configurações", "Análise do Dia", "Usuários", "ERP"]
            pages_with_only_date = ["Mídia Paga", "Taxas de Conversão"]
            pages_with_basic_filters = ["Visão Geral", "Visão Detalhada", "Pedidos"]
            pages_with_detailed_filters = ["Visão Detalhada", "Pedidos"]

        with st.spinner("🔄 Carregando dados básicos..."):
            # Load paid media data
            start_time = time.time()
            paid_media = load_basic_data()
            paid_media = paid_media['Investimento'].sum()
            if paid_media > 0:
                paid_media = pd.DataFrame([{'value': paid_media}])
            else:
                paid_media = pd.DataFrame()
        
        # with st.spinner("🔄 Carregando dados de leads..."):
        #     # Load popup leads data
        #     popup_leads = load_popup_leads()
        
        # # Check if all values in 'Data do Cadastro' are None/NaN
        # if popup_leads is not None and not popup_leads.empty and popup_leads['Data do Cadastro'].isna().all():
        #     popup_leads = None

        with st.spinner("🔄 Configurando navegação..."):
            # Define navigation options based on data availability
            nav_options = ["Visão Geral"]
            nav_options.extend(["Visão Detalhada", "Análise do Dia", "Taxas de Conversão", "Pedidos"])    

            # if popup_leads is not None and not popup_leads.empty:
            #     nav_options.extend(["Atribuição 2.0"])

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

            if st.session_state.tablename == 'kaisan':
                nav_options.extend(["ERP"])

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

        # Carregar filtros baseado na aba selecionada
        if selected_page not in pages_without_filters:
            with st.spinner("🔄 Carregando filtros de data..."):
                # Carregar filtro de data para todas as abas que não estão em pages_without_filters
                date_filters()
            
            # Carregar filtros básicos e de atribuição para abas específicas
            if selected_page in pages_with_basic_filters:
                
                df_basic = load_basic_data()
                
                with st.spinner("🔄 Aplicando filtros de tráfego..."):
                    traffic_filters(df_basic)
            
            # Carregar filtros detalhados para abas específicas
            if selected_page in pages_with_detailed_filters:
                with st.spinner("🔄 Carregando dados detalhados..."):
                    start_time = time.time()
                    df_detailed = load_detailed_data()
                
                with st.spinner("🔄 Aplicando filtros detalhados..."):
                    traffic_filters_detailed(df_detailed)

        # Exibir conteúdo baseado na seleção
        with st.spinner(f"🔄 Exibindo {selected_page}..."):
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
                
            elif selected_page == "Social" and st.session_state.tablename == 'holysoup':
                save_event_name(event_name="tab_view", event_params={"tab": "social"})
                display_tab_holysoup_social()
                
            elif selected_page == "ERP" and st.session_state.tablename == 'kaisan':
                save_event_name(event_name="tab_view", event_params={"tab": "erp"})
                display_tab_kaisan_erp()

    except Exception as e:
        st.error(f"Erro ao carregar a aplicação: {str(e)}")
        st.error(traceback.format_exc())
        send_message(f"Erro ao carregar a aplicação: {str(e)}")
    