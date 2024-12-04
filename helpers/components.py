import streamlit as st


def big_number_box(data, label):
        st.markdown(f"""
            <div style="background-color:#C5EBC3;padding:20px;border-radius:10px;text-align:center;margin:5px">
                <p style="color:#666;line-height:1">{label}</h3>
                <p style="color:#666;line-height:1;font-size:38px;margin:0;">{data}</p>
            </div>
        """, unsafe_allow_html=True)