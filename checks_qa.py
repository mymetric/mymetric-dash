import streamlit as st
from partials import pendings
from datetime import datetime, timedelta
from tabs.filters import traffic_filters
from modules.utilities import send_message
from core.users import load_users
from partials.performance import check_performance_alerts
from modules.load_data import load_basic_data


def pending_checks():
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
            'alta': '🔴 Alta',
            'media': '🟡 Média', 
            'baixa': '🔵 Baixa'
        }
        
        message = f"""Cliente: *{st.session_state.tablename.upper()}*
        
*🍪 Nova Pendência Detectada!*

Severidade: {severity_emoji[p['severidade']]}

Título: {p['titulo']}

Descrição:
{p['descricao']}

Ação Necessária:
{p['acao']}"""

        send_message(message)




def performance_checks():

    alerts = check_performance_alerts()

    for alert in alerts:
        print(alert)
        message = f"""Cliente: *{st.session_state.tablename.upper()}*

*⚠️ Alerta de Performance!*

Severidade: {'🔴' if alert["severidade"] == 'alta' else '🟡' if alert["severidade"] == 'media' else '🔵'} {alert["severidade"].upper()}

Título: {alert["titulo"]}

Descrição:
{alert["descricao"]}

Ação Necessária:
{alert["acao"]}"""

        send_message(message)


# st.session_state.tablename = "gringa"

# pending_checks()
# performance_checks()


users = load_users()

for user in users:
    if (user["skip"] == "y"):
        break
    print(user['slug'])
    st.session_state.tablename = user['slug']
    pending_checks()

def check_qa():
    st.title("QA")
    
    # Carregar dados básicos para os filtros
    df_basic = load_basic_data()
    traffic_filters(df_basic)
