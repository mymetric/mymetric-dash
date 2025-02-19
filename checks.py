import streamlit as st
from partials import pendings
from datetime import datetime, timedelta
from tabs.filters import traffic_filters
from modules.utilities import send_message
from core.users import load_users

def make_checks():
    current_date = datetime.now()
    st.session_state.start_date = current_date.strftime("%Y-%m-01")
    st.session_state.end_date = (current_date.replace(day=1).replace(month=current_date.month+1 if current_date.month < 12 else 1, 
                year=current_date.year if current_date.month < 12 else current_date.year + 1) - 
                timedelta(days=1)).strftime("%Y-%m-%d")

    traffic_filters()

    pending = pendings.check_pending_items()

    print(pending)

    # Send message for each pending item
    for p in pending:
        severity_emoji = {
            'alta': '🔴',
            'media': '🟡', 
            'baixa': '🔵'
        }
        
        message = f"""{severity_emoji[p['severidade']]} Nova Pendência Detectada!

    Cliente: {st.session_state.tablename.upper()}
        
    Título: {p['titulo']}
    Severidade: {p['severidade'].upper()}

    Descrição:
    {p['descricao']}

    Ação Necessária:
    {p['acao']}"""

        send_message(message)



users = load_users()

for user in users:
    if (user["skip"] == "y"):
        break
    print(user['slug'])
    st.session_state.tablename = user['slug']
    make_checks()

# st.session_state.tablename = "gringa"

# make_checks()