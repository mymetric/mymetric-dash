import streamlit as st

def tabs_css():
    st.markdown("""
        <style>
            label[data-baseweb="radio"] {
                border: 1px solid #ccc !important;
                padding: 10px !important;
                margin: 0 5px 3px 0;
            }
            label[data-baseweb="radio"] .st-as {
                display: none !important;
            }
                label[data-baseweb="radio"] {
                transition: all 0.2s ease;
            }
            label[data-baseweb="radio"]:has(input:checked) {
                background-color: rgb(255, 75, 75) !important;
            }
            label[data-baseweb="radio"]:has(input:checked) p {
                color: white !important;
            }
            .stSidebar label[data-baseweb="radio"] {
                padding: 3px 10px !important;
                width: 100% !important;
            }
            .stSidebar label[data-baseweb="radio"] div {
                width: 100% !important;
            }
            .stSidebar label[data-baseweb="radio"] div p {
                width: 100% !important;
                text-align: center !important;
            }  
        </style>
    """, unsafe_allow_html=True)

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