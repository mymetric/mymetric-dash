import streamlit as st

def tabs_css():
    st.markdown("""
        <style>
            /* Base styles for radio buttons */
            label[data-baseweb="radio"] {
                border: 2px solid #e5e7eb !important;
                background-color: white !important;
                border-radius: 8px !important;
                padding: 12px 20px !important;
                margin: 0 8px 8px 0 !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            }

            /* Hide radio button circle */
            label[data-baseweb="radio"] .st-as {
                display: none !important;
            }

            /* Hover effect */
            label[data-baseweb="radio"]:hover {
                border-color: #d1d5db !important;
                background-color: #f9fafb !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
            }

            /* Selected state */
            label[data-baseweb="radio"]:has(input:checked) {
                background-color: #4f46e5 !important;
                border-color: #4f46e5 !important;
                box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2) !important;
            }

            /* Text color for selected state */
            label[data-baseweb="radio"]:has(input:checked) p {
                color: white !important;
                font-weight: 500 !important;
            }

            /* Text styles */
            label[data-baseweb="radio"] p {
                color: #374151 !important;
                font-size: 0.95rem !important;
                transition: all 0.3s ease !important;
            }

            /* Sidebar specific styles */
            .stSidebar label[data-baseweb="radio"] {
                padding: 8px 16px !important;
                width: 100% !important;
                margin: 0 0 4px 0 !important;
            }

            .stSidebar label[data-baseweb="radio"] div {
                width: 100% !important;
            }

            .stSidebar label[data-baseweb="radio"] div p {
                width: 100% !important;
                text-align: center !important;
                font-size: 0.9rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

def big_number_box(data, label, hint=None, bg_color='#F8FAFC'):
    # Novo estilo do ícone de informação com melhor contraste
    info_icon = """
    <svg class="info-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#64748B" stroke-width="2"/>
        <path d="M12 16V12M12 8H12.01" stroke="#64748B" stroke-width="2" stroke-linecap="round"/>
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
                <div class="big-number-box">
                    {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                    <p class="label">{label}</p>
                    <p class="value">
                        <span class="currency">{currency_symbol}</span>
                        <span class="whole">{whole}</span>
                        <span class="cents">,{cents}</span>
                    </p>
                </div>
                <style>
                    .big-number-box {{
                        background-color: {bg_color};
                        padding: 24px 12px;
                        border-radius: 12px;
                        text-align: center;
                        margin: 8px 4px;
                        position: relative;
                        border: 1px solid rgba(226, 232, 240, 0.8);
                        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                        min-width: 0;
                        width: 100%;
                        box-sizing: border-box;
                    }}
                    .big-number-box:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                    }}
                    .label {{
                        color: #64748B;
                        line-height: 1.2;
                        font-size: 14px;
                        font-weight: 500;
                        margin: 0 0 12px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }}
                    .value {{
                        color: #0F172A;
                        line-height: 1;
                        margin: 0;
                        display: flex;
                        align-items: baseline;
                        justify-content: center;
                        gap: 2px;
                        white-space: nowrap;
                        overflow: hidden;
                    }}
                    .currency {{
                        font-size: 20px;
                        font-weight: 500;
                        flex-shrink: 0;
                    }}
                    .whole {{
                        font-size: 36px;
                        font-weight: 600;
                        flex-shrink: 1;
                        min-width: 0;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }}
                    .cents {{
                        font-size: 20px;
                        font-weight: 500;
                        flex-shrink: 0;
                    }}
                    .tooltip {{
                        position: absolute;
                        top: 12px;
                        right: 12px;
                        cursor: help;
                        display: inline-flex;
                        align-items: center;
                    }}
                    .info-icon {{
                        transition: transform 0.2s ease;
                        opacity: 0.6;
                    }}
                    .tooltip:hover .info-icon {{
                        transform: scale(1.1);
                        opacity: 1;
                    }}
                    .tooltip:hover:after {{
                        content: attr(data-tooltip);
                        position: absolute;
                        bottom: 100%;
                        right: 0;
                        transform: translateY(-4px);
                        background: rgba(15, 23, 42, 0.95);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 8px;
                        font-size: 13px;
                        line-height: 1.4;
                        white-space: normal;
                        z-index: 1000;
                        width: max-content;
                        max-width: 280px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                        backdrop-filter: blur(4px);
                    }}
                    .tooltip:hover:before {{
                        content: '';
                        position: absolute;
                        bottom: -4px;
                        right: 8px;
                        transform: translateY(-100%);
                        border-width: 6px;
                        border-style: solid;
                        border-color: rgba(15, 23, 42, 0.95) transparent transparent transparent;
                        z-index: 1000;
                    }}
                    
                    /* Responsive styles */
                    @media screen and (max-width: 1400px) {{
                        .big-number-box {{
                            padding: 16px 8px;
                        }}
                        .whole {{
                            font-size: 26px;
                        }}
                        .currency, .cents {{
                            font-size: 15px;
                        }}
                        .label {{
                            font-size: 12px;
                            margin: 0 0 8px;
                        }}
                    }}
                    
                    @media screen and (max-width: 1200px) {{
                        .big-number-box {{
                            padding: 14px 7px;
                        }}
                        .whole {{
                            font-size: 22px;
                        }}
                        .currency, .cents {{
                            font-size: 13px;
                        }}
                        .label {{
                            font-size: 11px;
                            margin: 0 0 6px;
                        }}
                    }}
                    
                    @media screen and (max-width: 992px) {{
                        .big-number-box {{
                            padding: 12px 6px;
                        }}
                        .whole {{
                            font-size: 18px;
                        }}
                        .currency, .cents {{
                            font-size: 12px;
                        }}
                        .label {{
                            font-size: 10px;
                            margin: 0 0 5px;
                        }}
                        .tooltip {{
                            top: 6px;
                            right: 6px;
                        }}
                        .info-icon {{
                            width: 12px;
                            height: 12px;
                        }}
                    }}

                    @media screen and (max-width: 768px) {{
                        .big-number-box {{
                            padding: 10px 5px;
                        }}
                        .whole {{
                            font-size: 16px;
                        }}
                        .currency, .cents {{
                            font-size: 11px;
                        }}
                        .label {{
                            font-size: 9px;
                            margin: 0 0 4px;
                        }}
                        .tooltip {{
                            top: 5px;
                            right: 5px;
                        }}
                        .info-icon {{
                            width: 10px;
                            height: 10px;
                        }}
                    }}

                    @media screen and (max-width: 576px) {{
                        .big-number-box {{
                            padding: 8px 4px;
                        }}
                        .whole {{
                            font-size: 14px;
                        }}
                        .currency, .cents {{
                            font-size: 10px;
                        }}
                        .label {{
                            font-size: 8px;
                            margin: 0 0 3px;
                        }}
                        .tooltip {{
                            top: 4px;
                            right: 4px;
                        }}
                        .info-icon {{
                            width: 8px;
                            height: 8px;
                        }}
                    }}
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="big-number-box">
                    {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                    <p class="label">{label}</p>
                    <p class="value">
                        <span class="currency">{currency_symbol}</span>
                        <span class="whole">{value}</span>
                    </p>
                </div>
                <style>
                    .big-number-box {{
                        background-color: {bg_color};
                        padding: 24px;
                        border-radius: 12px;
                        text-align: center;
                        margin: 8px 4px;
                        position: relative;
                        border: 1px solid rgba(226, 232, 240, 0.8);
                        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                    }}
                    .big-number-box:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                    }}
                    .label {{
                        color: #64748B;
                        line-height: 1.2;
                        font-size: 14px;
                        font-weight: 500;
                        margin: 0 0 12px;
                    }}
                    .value {{
                        color: #0F172A;
                        line-height: 1;
                        margin: 0;
                        display: flex;
                        align-items: baseline;
                        justify-content: center;
                        gap: 2px;
                    }}
                    .currency {{
                        font-size: 20px;
                        font-weight: 500;
                    }}
                    .whole {{
                        font-size: 36px;
                        font-weight: 600;
                    }}
                    .tooltip {{
                        position: absolute;
                        top: 12px;
                        right: 12px;
                        cursor: help;
                        display: inline-flex;
                        align-items: center;
                    }}
                    .info-icon {{
                        transition: transform 0.2s ease;
                        opacity: 0.6;
                    }}
                    .tooltip:hover .info-icon {{
                        transform: scale(1.1);
                        opacity: 1;
                    }}
                    .tooltip:hover:after {{
                        content: attr(data-tooltip);
                        position: absolute;
                        bottom: 100%;
                        right: 0;
                        transform: translateY(-4px);
                        background: rgba(15, 23, 42, 0.95);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 8px;
                        font-size: 13px;
                        line-height: 1.4;
                        white-space: normal;
                        z-index: 1000;
                        width: max-content;
                        max-width: 280px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                        backdrop-filter: blur(4px);
                    }}
                    .tooltip:hover:before {{
                        content: '';
                        position: absolute;
                        bottom: -4px;
                        right: 8px;
                        transform: translateY(-100%);
                        border-width: 6px;
                        border-style: solid;
                        border-color: rgba(15, 23, 42, 0.95) transparent transparent transparent;
                        z-index: 1000;
                    }}
                </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="big-number-box">
                {f'<span class="tooltip" data-tooltip="{hint}">{info_icon}</span>' if hint else ''}
                <p class="label">{label}</p>
                <p class="value">
                    <span class="whole">{data}</span>
                </p>
            </div>
            <style>
                .big-number-box {{
                    background-color: {bg_color};
                    padding: 24px;
                    border-radius: 12px;
                    text-align: center;
                    margin: 8px 4px;
                    position: relative;
                    border: 1px solid rgba(226, 232, 240, 0.8);
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                .big-number-box:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                }}
                .label {{
                    color: #64748B;
                    line-height: 1.2;
                    font-size: 14px;
                    font-weight: 500;
                    margin: 0 0 12px;
                }}
                .value {{
                    color: #0F172A;
                    line-height: 1;
                    margin: 0;
                    display: flex;
                    align-items: baseline;
                    justify-content: center;
                }}
                .whole {{
                    font-size: 36px;
                    font-weight: 600;
                }}
                .tooltip {{
                    position: absolute;
                    top: 12px;
                    right: 12px;
                    cursor: help;
                    display: inline-flex;
                    align-items: center;
                }}
                .info-icon {{
                    transition: transform 0.2s ease;
                    opacity: 0.6;
                }}
                .tooltip:hover .info-icon {{
                    transform: scale(1.1);
                    opacity: 1;
                }}
                .tooltip:hover:after {{
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 100%;
                    right: 0;
                    transform: translateY(-4px);
                    background: rgba(15, 23, 42, 0.95);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 13px;
                    line-height: 1.4;
                    white-space: normal;
                    z-index: 1000;
                    width: max-content;
                    max-width: 280px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(4px);
                }}
                .tooltip:hover:before {{
                    content: '';
                    position: absolute;
                    bottom: -4px;
                    right: 8px;
                    transform: translateY(-100%);
                    border-width: 6px;
                    border-style: solid;
                    border-color: rgba(15, 23, 42, 0.95) transparent transparent transparent;
                    z-index: 1000;
                }}
            </style>
        """, unsafe_allow_html=True)