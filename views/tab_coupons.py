import streamlit as st
from modules.load_data import save_coupons, load_coupons


def display_tab_coupons():
    st.title("Gerenciamento de Cupons")
    
    # Form para adicionar novo cupom
    with st.form("novo_cupom"):
        st.subheader("Adicionar Novo Cupom")
        coupon_code = st.text_input("Código do Cupom")
        coupon_category = st.text_input("Categoria do Cupom")
        
        submitted = st.form_submit_button("Salvar Cupom")
        if submitted and coupon_code and coupon_category:
            save_coupons(coupon_code, coupon_category)
            st.success(f"Cupom {coupon_code} salvo com sucesso!")
            st.rerun()
    
    # Exibir lista de cupons existentes
    coupons = load_coupons()
    st.data_editor(coupons, use_container_width=True, hide_index=True)