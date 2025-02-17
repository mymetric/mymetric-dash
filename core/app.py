import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from modules.components import tabs_css

from tabs.filters import date_filters, traffic_filters_detailed, traffic_filters, attribution_filters
from tabs.tab_general import display_tab_general
from tabs.tab_detailed import display_tab_detailed
from tabs.tab_today import display_tab_today
from tabs.tab_funnel import display_tab_funnel
from tabs.tab_paid_media import display_tab_paid_media
from tabs.tab_config import display_tab_config
from tabs.tab_last_orders import display_tab_last_orders

# Custom Tabs
from tabs_custom.tab_gringa_product_submitted import display_tab_gringa_product_submitted
from tabs_custom.tab_holysoup_crm import display_tab_holysoup_crm

from modules.load_data import load_paid_media, save_event_name

def load_app():

    tabs_css()
    date_filters()
    traffic_filters()

    is_admin = st.session_state.admin

    # Load paid media data
    paid_media = load_paid_media()

    # Define navigation options based on data availability
    nav_options = ["👀 Visão Geral"]

    if paid_media is not None and not paid_media.empty:
        nav_options.extend(["💰 Mídia Paga"])

    nav_options.extend(["🛒 Últimos Pedidos", "🎯 Funil de Conversão", "📊 Análise do Dia", "💼 Visão Detalhada"])

    if st.session_state.tablename == 'gringa':
        nav_options.extend(["👜 Produtos Cadastrados"])

    if st.session_state.tablename == 'holysoup':
        nav_options.extend(["✉️ CRM"])

    if is_admin:
        nav_options.extend(["🔧 Configurações"])
        
    # Create radio buttons for navigation
    selected_page = st.radio("", nav_options, horizontal=True)
    st.session_state.selected_page = selected_page

    # Display content based on selection
    if selected_page == "👀 Visão Geral":
        save_event_name(event_name="tab_view", event_params={"tab": "general"})
        attribution_filters()
        display_tab_general()
        
    elif selected_page == "💰 Mídia Paga" and "💰 Mídia Paga" in nav_options:
        save_event_name(event_name="tab_view", event_params={"tab": "paid_media"})
        display_tab_paid_media()
    elif selected_page == "🛒 Últimos Pedidos":
        save_event_name(event_name="tab_view", event_params={"tab": "last_orders"})
        display_tab_last_orders()
    elif selected_page == "🎯 Funil de Conversão":
        save_event_name(event_name="tab_view", event_params={"tab": "funnel"})
        display_tab_funnel()
    elif selected_page == "📊 Análise do Dia":
        save_event_name(event_name="tab_view", event_params={"tab": "today"})
        display_tab_today()
    elif selected_page == "👜 Produtos Cadastrados" and st.session_state.tablename == 'gringa':
        save_event_name(event_name="tab_view", event_params={"tab": "gringa_product_submitted"})
        display_tab_gringa_product_submitted()
    elif selected_page == "✉️ CRM" and st.session_state.tablename == 'holysoup':
        save_event_name(event_name="tab_view", event_params={"tab": "holysoup_crm"})
        display_tab_holysoup_crm()
    elif selected_page == "💼 Visão Detalhada":
        save_event_name(event_name="tab_view", event_params={"tab": "detailed"})
        traffic_filters_detailed()
        attribution_filters()
        display_tab_detailed()
    elif selected_page == "🔧 Configurações":
        save_event_name(event_name="tab_view", event_params={"tab": "config"})
        display_tab_config()