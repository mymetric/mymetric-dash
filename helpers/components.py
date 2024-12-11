import streamlit as st


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
    if row['Origem'] == 'meta' and row['Mídia'] == 'cpc':
        return '🔵 Meta Ads'
    elif row['Origem'] == 'google' and row['Mídia'] == 'organic':
        return '🌳 Google Orgânico'
    elif row['Origem'] == 'direct':
        return '🟡 Direto'
    elif row['Origem'] == 'shopify_draft_order':
        return '🗒️ Draft'
    elif row['Origem'] == 'not captured':
        return '🍪 Perda de Cookies'
    else:
        return f"◻️ {row['Origem']} / {row['Mídia']}"