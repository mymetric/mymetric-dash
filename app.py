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

    # Define tabs based on data availability
    tabs = ["👀 Visão Geral"]

    if paid_media is not None and not paid_media.empty:
        tabs.extend(["💰 Mídia Paga"])

    tabs.extend(["🛒 Últimos Pedidos", "🎯 Funil de Conversão", "📊 Análise do Dia"])

    if st.session_state.tablename == 'gringa':
        tabs.extend(["👜 Produtos Cadastrados"])

    if st.session_state.tablename == 'holysoup':
        tabs.extend(["✉️ CRM"])

    tabs.extend(["💼 Visão Detalhada", "🔧 Configurações"])


    # Create tabs
    tab_objects = st.tabs(tabs)

    # Display content in tabs
    with tab_objects[0]:
        display_tab_general()

    if "💰 Mídia Paga" in tabs:
        with tab_objects[1]:
            display_tab_paid_media()

    with tab_objects[tabs.index("🛒 Últimos Pedidos")]:
        display_tab_last_orders()

    with tab_objects[tabs.index("🎯 Funil de Conversão")]:
        display_tab_funnel()

    with tab_objects[tabs.index("📊 Análise do Dia")]:
        display_tab_today()



    if st.session_state.tablename == 'gringa':
        with tab_objects[tabs.index("👜 Produtos Cadastrados")]:
            display_tab_gringa_product_submitted()

    if st.session_state.tablename == 'holysoup':
        with tab_objects[tabs.index("✉️ CRM")]:
            display_tab_holysoup_crm()


    with tab_objects[tabs.index("💼 Visão Detalhada")]:
        traffic_filters_detailed()
        display_tab_detailed()

    with tab_objects[tabs.index("🔧 Configurações")]:
        display_tab_config()