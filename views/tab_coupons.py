import streamlit as st
from modules.load_data import save_coupons, load_coupons, delete_coupon
import pandas as pd


def display_tab_coupons():
    st.title("Gerenciamento de Cupons")
    
    # Form para adicionar novo cupom
    with st.expander("➕ Adicionar Novo Cupom", expanded=False):
        with st.form("novo_cupom"):
            coupon_code = st.text_input("Código do Cupom")
            coupon_category = st.text_input("Categoria do Cupom")
            
            submitted = st.form_submit_button("Salvar Cupom")
            if submitted and coupon_code and coupon_category:
                save_coupons(coupon_code, coupon_category)
                st.success(f"Cupom {coupon_code} salvo com sucesso!")
                st.rerun()
    
    st.divider()
    
    # Exibir lista de cupons existentes
    coupons = load_coupons()
    
    if not coupons.empty:
        # Adicionar campos de busca
        search_code = st.text_input("🔍 Buscar por código", placeholder="Digite o código do cupom...")
        search_category = st.text_input("🔍 Buscar por categoria", placeholder="Digite a categoria...")
        
        # Filtrar cupons baseado na busca
        if search_code or search_category:
            filtered_coupons = coupons[
                (coupons['Cupom'].str.contains(search_code, case=False, na=False)) &
                (coupons['Categoria'].str.contains(search_category, case=False, na=False))
            ]
        else:
            filtered_coupons = coupons
        
        # Mostrar estatísticas
        total_coupons = len(filtered_coupons)
        st.caption(f"Total de cupons encontrados: {total_coupons}")
        
        # Estilo CSS para os cards
        st.markdown("""
        <style>
        .coupon-card {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .coupon-info {
            display: flex;
            align-items: center;
        }
        .coupon-code {
            color: #0066cc;
            font-family: monospace;
            font-size: 1.1em;
            padding: 0.2rem 0.4rem;
            background-color: #e9ecef;
            border-radius: 0.3rem;
        }
        .coupon-category {
            color: #666;
            margin-left: 1rem;
        }
        .delete-button {
            visibility: hidden;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Exibir cupons em cards
        for index, row in filtered_coupons.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div class="coupon-card">
                    <div class="coupon-info">
                        <span class="coupon-code">{row['Cupom']}</span>
                        <span class="coupon-category">📁 {row['Categoria']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_{row['Cupom']}", help="Deletar cupom", type="secondary"):
                    if delete_coupon(row['Cupom']):
                        st.success(f"Cupom {row['Cupom']} deletado com sucesso!")
                        coupons = load_coupons()
                        st.rerun()
                    else:
                        st.error(f"Erro ao deletar o cupom {row['Cupom']}")
    else:
        st.info("Nenhum cupom cadastrado.")