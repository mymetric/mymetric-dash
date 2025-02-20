import streamlit as st
import plotly.express as px
from modules.load_data import load_rfm_segments
import pandas as pd
from io import BytesIO

def export_to_csv(df):
    """Converte o DataFrame para CSV e retorna os bytes"""
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def display_tab_rfm():
    st.title("👥 RFM")
    st.markdown("""---""")
    
    # Carregar dados
    df = load_rfm_segments()
    
    if not df.empty:
        with st.expander("ℹ️ Sobre a Segmentação RFM", expanded=False):
            st.markdown("""
                ### O que é Segmentação RFM?
                
                RFM é uma técnica de segmentação de clientes baseada em três métricas:
                
                1. **Recency (R)** - Quantos meses desde a última compra do cliente
                2. **Frequency (F)** - Com que frequência o cliente compra
                3. **Monetary (M)** - Quanto dinheiro o cliente gasta
                
                ### Segmentos Principais:
                
                - **Champions**: Clientes mais valiosos e recentes
                - **Loyal**: Clientes fiéis com bom valor
                - **Lost**: Clientes que não compram há muito tempo
                - **New**: Novos clientes com potencial
                - **At Risk**: Clientes em risco de abandono
                
                💡 **Dica**: Use esta segmentação para:
                - Personalizar campanhas de marketing
                - Identificar clientes para retenção
                - Otimizar investimentos em marketing
            """)

        # Agrupar dados por categoria
        df_grouped = df.groupby('Categoria').size().reset_index(name='Clientes')
        total_clientes = df_grouped['Clientes'].sum()
        
        # Preparar dados para o treemap
        df_grouped['Percentual'] = (df_grouped['Clientes'] / total_clientes * 100).round(2)
        df_grouped['Label'] = df_grouped.apply(
            lambda x: f"{x['Categoria']}<br>{x['Clientes']:,.0f} clientes<br>{x['Percentual']:.1f}%",
            axis=1
        )
        
        # Criar treemap
        fig = px.treemap(
            df_grouped,
            values='Clientes',
            path=['Categoria'],
            custom_data=['Label'],
            title='Distribuição dos Segmentos',
            color='Categoria',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Atualizar layout
        fig.update_traces(
            textinfo="label+percent parent",
            textfont=dict(size=14),
            hovertemplate="%{customdata[0]}<extra></extra>"
        )
        fig.update_layout(
            height=500,
            margin=dict(t=30, l=10, r=10, b=10),
            title_font_size=18,
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Criar filtro de categoria
        st.markdown("### Detalhamento")
        categorias = ['Todos'] + sorted(df['Categoria'].unique().tolist())
        categoria_selecionada = st.selectbox(
            "Filtrar por Categoria",
            options=categorias,
            help="Selecione uma categoria RFM específica ou visualize todas"
        )
        
        # Filtrar dados se uma categoria específica for selecionada
        if categoria_selecionada != 'Todos':
            df_display = df[df['Categoria'] == categoria_selecionada].copy()
        else:
            df_display = df.copy()
        
        # Formatar valores monetários e números
        df_display['Monetário'] = df_display['Monetário'].map('R$ {:,.2f}'.format)
        
        # Garantir que a coluna existe antes de formatar
        if 'Recência (Meses)' in df_display.columns:
            df_display['Recência (Meses)'] = df_display['Recência (Meses)'].map(lambda x: f"{x:.1f}")
        
        # Exibir tabela
        st.dataframe(
            df_display,
            hide_index=True,
            use_container_width=True
        )
        
        # Mostrar total e botão de exportação na mesma linha
        total_filtrado = len(df_display)
        st.markdown(
            f"""
            **Total de Clientes:** {total_filtrado:,.0f} 
            <span style='float: right;'>
            """, 
            unsafe_allow_html=True
        )
        
        # Botão de exportação
        csv = export_to_csv(df_display)
        st.download_button(
            label="📥 Exportar Dados",
            data=csv,
            file_name=f"rfm_segmentos_{st.session_state.tablename}.csv",
            mime="text/csv",
            help="Baixar tabela em formato CSV"
        )
    else:
        st.warning("Não foram encontrados dados de segmentação RFM para este período.") 