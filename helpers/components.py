import streamlit as st
import requests


def big_number_box(data, label):
        st.markdown(f"""
            <div style="background-color:#C5EBC3;padding:20px;border-radius:10px;text-align:center;margin:5px">
                <p style="color:#666;line-height:1">{label}</h3>
                <p style="color:#666;line-height:1;font-size:38px;margin:0;">{data}</p>
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
