import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from modules.components import tabs_css

from views.filters import date_filters, traffic_filters_detailed, traffic_filters
from views.tab_general import display_tab_general
from views.tab_detailed import display_tab_detailed
from views.tab_today import display_tab_today
from views.tab_funnel import display_tab_funnel
from views.tab_paid_media import display_tab_paid_media
from views.tab_config import display_tab_config
from views.tab_last_orders import display_tab_last_orders

# Custom Tabs
from views.custom.tab_gringa_product_submitted import display_tab_gringa_product_submitted
from views.custom.tab_holysoup_crm import display_tab_holysoup_crm

from modules.load_data import load_paid_media

def load_app():

    tabs_css()
    date_filters()
    traffic_filters()

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

    if st.session_state.admin is not None and st.session_state.admin is not False:
        nav_options.extend(["🔧 Configurações"])

    # Create radio buttons for navigation
    selected_page = st.radio("", nav_options, horizontal=True)
    st.session_state.selected_page = selected_page

    # Display content based on selection
    if selected_page == "👀 Visão Geral":
        display_tab_general()
    elif selected_page == "💰 Mídia Paga" and "💰 Mídia Paga" in nav_options:
        display_tab_paid_media()
    elif selected_page == "🛒 Últimos Pedidos":
        display_tab_last_orders()
    elif selected_page == "🎯 Funil de Conversão":
        display_tab_funnel()
    elif selected_page == "📊 Análise do Dia":
        display_tab_today()
    elif selected_page == "👜 Produtos Cadastrados" and st.session_state.tablename == 'gringa':
        display_tab_gringa_product_submitted()
    elif selected_page == "✉️ CRM" and st.session_state.tablename == 'holysoup':
        display_tab_holysoup_crm()
    elif selected_page == "💼 Visão Detalhada":
        traffic_filters_detailed()
        display_tab_detailed()
    elif selected_page == "🔧 Configurações":
        display_tab_config()
