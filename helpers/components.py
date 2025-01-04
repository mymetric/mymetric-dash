import streamlit as st
import requests
import pandas as pd

@st.cache_data(ttl=600)
def run_query(_client, query):
    query_job = _client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def big_number_box(data, label, bg_color='#C5EBC3'):
    # Check if the data starts with "R$" and if so, split it into parts
    if isinstance(data, str) and data.startswith("R$"):
        currency_symbol = "R$"
        value = data[2:].strip()  # Remove "R$" and any whitespace
        
        # Split the value into whole numbers and cents if there's a decimal point
        if "," in value:
            whole, cents = value.split(",")
            st.markdown(f"""
                <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px">
                    <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</h3>
                    <p style="color:#666;line-height:1;margin:0;">
                        <span style="font-size:20px">{currency_symbol}</span>
                        <span style="font-size:33px">{whole}</span>
                        <span style="font-size:20px">,{cents}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px">
                    <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</h3>
                    <p style="color:#666;line-height:1;margin:0;">
                        <span style="font-size:20px">{currency_symbol}</span>
                        <span style="font-size:35px">{value}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px">
                <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</h3>
                <p style="color:#666;line-height:1;font-size:35px;margin:0;">{data}</p>
            </div>
        """, unsafe_allow_html=True)

def atribuir_cluster(row):
    if row['Origem'] == 'google' and row['Mídia'] == 'cpc':
        return '🟢 Google Ads'
    elif row['Origem'] == 'meta' and row['Mídia'] == 'cpc':
        return '🔵 Meta Ads'
    elif row['Origem'] == 'google' and row['Mídia'] == 'organic':
        return '🌳 Google Orgânico'
    elif row['Origem'] == 'direct':
        return '🟡 Direto'
    elif row['Origem'] == 'crm':
        return '✉️ CRM'
    elif row['Origem'] == 'shopify_draft_order':
        return '🗒️ Draft'
    elif row['Origem'] == 'not captured':
        return '🍪 Perda de Cookies'
    else:
        return f"◻️ {row['Origem']} / {row['Mídia']}"

# URL do webhook do Discord (substitua pela URL do seu webhook)

def send_discord_message(message):

    discord_webhook_url = "https://discord.com/api/webhooks/1296840635776766003/FwqBXh2mKVhqS2jnQmmP15RweElgco4v_eFp3kq4inxIrOYRPzNgRddcUjz2y_pwi2ep"

    message = {
        "content": message
    }
    # Faz a requisição POST para enviar a mensagem
    requests.post(discord_webhook_url, json=message)
