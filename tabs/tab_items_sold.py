import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.load_data import load_purchase_items_sessions
from modules.components import big_number_box
from tabs.filters import traffic_filters_detailed, apply_filters

def display_tab_items_sold():
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <p style='color: #666; font-size: 14px; margin: 0;'>
                ℹ️ Esta página está em fase beta e utiliza dados do Google Analytics para análise de itens vendidos.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.title("Itens Vendidos")
    st.markdown("""---""")

    # Carregar dados
    df = load_purchase_items_sessions()

    if df.empty:
        st.warning("Não há dados disponíveis para o período selecionado.")
        return

    # Initialize session state for filters if not already done
    if "cluster_selected" not in st.session_state:
        st.session_state.cluster_selected = ["Selecionar Todos"]
        st.session_state.origem_selected = ["Selecionar Todos"]
        st.session_state.midia_selected = ["Selecionar Todos"]
        st.session_state.campanha_selected = ["Selecionar Todos"]
        st.session_state.conteudo_selected = ["Selecionar Todos"]
        st.session_state.pagina_de_entrada_selected = ["Selecionar Todos"]
        st.session_state.cupom_selected = ["Selecionar Todos"]
        st.session_state.categoria_produto_selected = ["Selecionar Todos"]
        st.session_state.nome_produto_selected = ["Selecionar Todos"]
        st.session_state.nome_produto_search = ""

    # Show filters in sidebar
    with st.sidebar:
        # Show advanced filters
        traffic_filters_detailed(df)

    # Apply filters to the data
    df = apply_filters(df)

    # Verificar se as colunas existem
    has_category_column = 'Categoria do Produto' in df.columns
    has_product_name_column = 'Nome do Produto' in df.columns

    # Tratar valores nulos ou vazios na categoria do produto (só se a coluna existir)
    if has_category_column:
        df['Categoria do Produto'] = df['Categoria do Produto'].fillna('Sem Categoria')
        df['Categoria do Produto'] = df['Categoria do Produto'].replace('', 'Sem Categoria')

    # Tratar valores nulos ou vazios no nome do produto (só se a coluna existir)
    if has_product_name_column:
        df['Nome do Produto'] = df['Nome do Produto'].fillna('Sem Nome')
        df['Nome do Produto'] = df['Nome do Produto'].replace('', 'Sem Nome')

    # Criar colunas para os KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"R$ {df['Receita'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
            "Receita Total",
            hint="Valor total das vendas no período"
        )
    
    with col2:
        big_number_box(
            f"{df['Quantidade'].sum():,.0f}".replace(",", "."), 
            "Total de Itens",
            hint="Quantidade total de itens vendidos"
        )
    
    with col3:
        big_number_box(
            f"{df['ID do Produto'].nunique():,.0f}".replace(",", "."), 
            "Produtos Diferentes",
            hint="Número de produtos diferentes vendidos"
        )
    
    with col4:
        big_number_box(
            f"R$ {(df['Receita'].sum() / df['Quantidade'].sum()):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
            "Ticket Médio por Item",
            hint="Valor médio por item vendido"
        )

    st.markdown("""---""")

    # Tabela de Resumo por Categoria (só se a coluna existir)
    if has_category_column:
        st.subheader("📊 Resumo por Categoria")
        
        # Criar resumo por categoria
        category_summary = df.groupby('Categoria do Produto').agg({
            'Receita': 'sum',
            'Quantidade': 'sum',
            'ID do Produto': 'nunique'
        }).reset_index().sort_values('Receita', ascending=False)
        
        # Calcular percentuais
        total_revenue = category_summary['Receita'].sum()
        total_quantity = category_summary['Quantidade'].sum()
        
        category_summary['% Receita'] = (category_summary['Receita'] / total_revenue * 100).round(1)
        category_summary['% Quantidade'] = (category_summary['Quantidade'] / total_quantity * 100).round(1)
        
        # Formatar a tabela
        category_summary['Receita'] = category_summary['Receita'].apply(lambda x: f"R$ {x:,.2f}")
        category_summary['Quantidade'] = category_summary['Quantidade'].apply(lambda x: f"{x:,.0f}")
        category_summary['ID do Produto'] = category_summary['ID do Produto'].apply(lambda x: f"{x:,.0f}")
        category_summary['% Receita'] = category_summary['% Receita'].apply(lambda x: f"{x}%")
        category_summary['% Quantidade'] = category_summary['% Quantidade'].apply(lambda x: f"{x}%")
        
        st.data_editor(
            category_summary,
            column_config={
                "Categoria do Produto": st.column_config.TextColumn("Categoria"),
                "Receita": st.column_config.TextColumn("Receita"),
                "% Receita": st.column_config.TextColumn("% Receita"),
                "Quantidade": st.column_config.TextColumn("Quantidade"),
                "% Quantidade": st.column_config.TextColumn("% Quantidade"),
                "ID do Produto": st.column_config.TextColumn("Produtos")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("""---""")

    # Top N Produtos por Receita
    st.subheader("Top Produtos por Receita")
    
    revenue_by_product = df.groupby('Nome do Produto').agg({
        'Receita': 'sum',
        'Quantidade': 'sum'
    }).reset_index().sort_values('Receita', ascending=False)

    # Formatar a tabela
    revenue_by_product['Receita'] = revenue_by_product['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    revenue_by_product['Quantidade'] = revenue_by_product['Quantidade'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        revenue_by_product,
        column_config={
            "Nome do Produto": st.column_config.TextColumn("Produto"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Cluster
    st.subheader("Análise por Cluster")
    cluster_analysis = df.groupby('Cluster').agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    # Formatar a tabela
    cluster_analysis['Receita'] = cluster_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    cluster_analysis['Quantidade'] = cluster_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    cluster_analysis['ID do Produto'] = cluster_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        cluster_analysis,
        column_config={
            "Cluster": st.column_config.TextColumn("Cluster"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Categoria do Produto (só se a coluna existir)
    if has_category_column:
        st.subheader("Análise por Categoria do Produto")
        category_analysis = df.groupby('Categoria do Produto').agg({
            'Receita': 'sum',
            'Quantidade': 'sum',
            'ID do Produto': 'nunique'
        }).reset_index().sort_values('Receita', ascending=False)

        # Salvar dados numéricos para o gráfico
        category_analysis_numeric = category_analysis.copy()

        # Formatar a tabela
        category_analysis['Receita'] = category_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
        category_analysis['Quantidade'] = category_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
        category_analysis['ID do Produto'] = category_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
        
        st.data_editor(
            category_analysis,
            column_config={
                "Categoria do Produto": st.column_config.TextColumn("Categoria"),
                "Receita": st.column_config.TextColumn("Receita"),
                "Quantidade": st.column_config.TextColumn("Quantidade"),
                "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
            },
            hide_index=True,
            use_container_width=True
        )

        # Gráfico de receita por categoria
        if not category_analysis_numeric.empty:
            fig = px.bar(
                category_analysis_numeric.head(10),  # Top 10 categorias
                x='Categoria do Produto',
                y='Receita',
                title='Receita por Categoria do Produto (Top 10)',
                color='Receita',
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                xaxis_title="Categoria do Produto",
                yaxis_title="Receita (R$)",
                showlegend=False,
                height=500
            )
            
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)

    # Análise por Origem/Mídia
    st.subheader("Análise por Origem/Mídia")
    source_medium_analysis = df.groupby(['Origem', 'Mídia']).agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    source_medium_analysis['Receita'] = source_medium_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    source_medium_analysis['Quantidade'] = source_medium_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    source_medium_analysis['ID do Produto'] = source_medium_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        source_medium_analysis,
        column_config={
            "Origem": st.column_config.TextColumn("Origem"),
            "Mídia": st.column_config.TextColumn("Mídia"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Campanha
    st.subheader("Análise por Campanha")
    campaign_analysis = df.groupby('Campanha').agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    campaign_analysis['Receita'] = campaign_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    campaign_analysis['Quantidade'] = campaign_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    campaign_analysis['ID do Produto'] = campaign_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        campaign_analysis,
        column_config={
            "Campanha": st.column_config.TextColumn("Campanha"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Conteúdo
    st.subheader("Análise por Conteúdo")
    content_analysis = df.groupby('Conteúdo').agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    content_analysis['Receita'] = content_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    content_analysis['Quantidade'] = content_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    content_analysis['ID do Produto'] = content_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        content_analysis,
        column_config={
            "Conteúdo": st.column_config.TextColumn("Conteúdo"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Termo
    st.subheader("Análise por Termo")
    term_analysis = df.groupby('Termo').agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    term_analysis['Receita'] = term_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    term_analysis['Quantidade'] = term_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    term_analysis['ID do Produto'] = term_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        term_analysis,
        column_config={
            "Termo": st.column_config.TextColumn("Termo"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    )

    # Análise por Página de Entrada
    st.subheader("Análise por Página de Entrada")
    landing_page_analysis = df.groupby('Página de Entrada').agg({
        'Receita': 'sum',
        'Quantidade': 'sum',
        'ID do Produto': 'nunique'
    }).reset_index().sort_values('Receita', ascending=False)

    landing_page_analysis['Receita'] = landing_page_analysis['Receita'].apply(lambda x: f"R$ {x:,.2f}")
    landing_page_analysis['Quantidade'] = landing_page_analysis['Quantidade'].apply(lambda x: f"{x:,.0f}")
    landing_page_analysis['ID do Produto'] = landing_page_analysis['ID do Produto'].apply(lambda x: f"{x:,.0f}")
    
    st.data_editor(
        landing_page_analysis,
        column_config={
            "Página de Entrada": st.column_config.TextColumn("Página de Entrada"),
            "Receita": st.column_config.TextColumn("Receita"),
            "Quantidade": st.column_config.TextColumn("Quantidade"),
            "ID do Produto": st.column_config.TextColumn("Produtos Diferentes")
        },
        hide_index=True,
        use_container_width=True
    ) 