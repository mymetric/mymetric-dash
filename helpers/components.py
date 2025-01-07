import streamlit as st
import requests
import pandas as pd

def section_title(title):
    """Cria um título de seção com margem padronizada."""
    st.markdown(f"""
        <h2 style="margin-top: 40px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f2f6;">
            {title}
        </h2>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def run_query(_client, query):
    query_job = _client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

def big_number_box(data, label, hint=None, bg_color='#C5EBC3'):
    # Novo estilo do ícone de informação
    info_icon = """
    <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#666" stroke-width="2"/>
        <path d="M12 16V12M12 8H12.01" stroke="#666" stroke-width="2" stroke-linecap="round"/>
    </svg>
    """
    
    # Check if the data starts with "R$" and if so, split it into parts
    if isinstance(data, str) and data.startswith("R$"):
        currency_symbol = "R$"
        value = data[2:].strip()  # Remove "R$" and any whitespace
        
        # Split the value into whole numbers and cents if there's a decimal point
        if "," in value:
            whole, cents = value.split(",")
            st.markdown(f"""
                <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px;position:relative">
                    {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                    <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</p>
                    <p style="color:#666;line-height:1;margin:0;">
                        <span style="font-size:20px">{currency_symbol}</span>
                        <span style="font-size:33px">{whole}</span>
                        <span style="font-size:20px">,{cents}</span>
                    </p>
                </div>
                <style>
                    .tooltip {{
                        position: absolute;
                        top: 8px;
                        right: 8px;
                        cursor: help;
                        display: inline-flex;
                        align-items: center;
                    }}
                    .info-icon {{
                        transition: transform 0.2s ease;
                    }}
                    .tooltip:hover .info-icon {{
                        transform: scale(1.1);
                    }}
                    .tooltip:hover:after {{
                        content: attr(data-tooltip);
                        position: absolute;
                        bottom: 100%;
                        right: 0;
                        transform: translateY(-8px);
                        background: rgba(51, 51, 51, 0.95);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        white-space: normal;
                        z-index: 1000;
                        width: max-content;
                        max-width: 250px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        backdrop-filter: blur(2px);
                    }}
                    .tooltip:hover:before {{
                        content: '';
                        position: absolute;
                        bottom: -8px;
                        right: 8px;
                        transform: translateY(-100%);
                        border-width: 6px;
                        border-style: solid;
                        border-color: rgba(51, 51, 51, 0.95) transparent transparent transparent;
                    }}
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px;position:relative">
                    {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                    <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</p>
                    <p style="color:#666;line-height:1;margin:0;">
                        <span style="font-size:20px">{currency_symbol}</span>
                        <span style="font-size:35px">{value}</span>
                    </p>
                </div>
                <style>
                    .tooltip {{
                        position: absolute;
                        top: 8px;
                        right: 8px;
                        cursor: help;
                        display: inline-flex;
                        align-items: center;
                    }}
                    .info-icon {{
                        transition: transform 0.2s ease;
                    }}
                    .tooltip:hover .info-icon {{
                        transform: scale(1.1);
                    }}
                    .tooltip:hover:after {{
                        content: attr(data-tooltip);
                        position: absolute;
                        bottom: 100%;
                        right: 0;
                        transform: translateY(-8px);
                        background: rgba(51, 51, 51, 0.95);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        white-space: normal;
                        z-index: 1000;
                        width: max-content;
                        max-width: 250px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        backdrop-filter: blur(2px);
                    }}
                    .tooltip:hover:before {{
                        content: '';
                        position: absolute;
                        bottom: -8px;
                        right: 8px;
                        transform: translateY(-100%);
                        border-width: 6px;
                        border-style: solid;
                        border-color: rgba(51, 51, 51, 0.95) transparent transparent transparent;
                    }}
                </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background-color:{bg_color};padding:20px;border-radius:10px;text-align:center;margin:5px;position:relative">
                {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                <p style="color:#666;line-height:1;font-size:13px;margin:0 0 5px;">{label}</p>
                <p style="color:#666;line-height:1;font-size:35px;margin:0;">{data}</p>
            </div>
            <style>
                .tooltip {{
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    cursor: help;
                    display: inline-flex;
                    align-items: center;
                }}
                .info-icon {{
                    transition: transform 0.2s ease;
                }}
                .tooltip:hover .info-icon {{
                    transform: scale(1.1);
                }}
                .tooltip:hover:after {{
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 100%;
                    right: 0;
                    transform: translateY(-8px);
                    background: rgba(51, 51, 51, 0.95);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    white-space: normal;
                    z-index: 1000;
                    width: max-content;
                    max-width: 250px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    backdrop-filter: blur(2px);
                }}
                .tooltip:hover:before {{
                    content: '';
                    position: absolute;
                    bottom: -8px;
                    right: 8px;
                    transform: translateY(-100%);
                    border-width: 6px;
                    border-style: solid;
                    border-color: rgba(51, 51, 51, 0.95) transparent transparent transparent;
                }}
            </style>
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

def send_discord_message(message):
    """Envia uma mensagem para o webhook do Discord."""
    try:
        webhook_url = st.secrets["discord_webhook_url"]
        st.write(webhook_url)
        data = {
            "content": message
        }
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except Exception as e:
        st.error(f"Erro ao enviar mensagem para o Discord: {str(e)}")
        print(f"Erro ao enviar mensagem para o Discord: {str(e)}")
