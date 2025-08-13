import streamlit as st
import pandas as pd
import altair as alt
from modules.load_data import load_purchase_items
from modules.components import big_number_box

# Nota: Este módulo utiliza o fuso horário de São Paulo (America/Sao_Paulo) para todos os cálculos de tempo

def format_currency(value):
    """Formata valor para o padrão de moeda BR."""
    return f"R$ {value:,.2f}".replace(",", "*").replace(".", ",").replace("*", ".")

def format_number(value):
    """Formata número com separador de milhar."""
    return f"{value:,.0f}".replace(",", ".")

def display_tab_today():
    st.title("Tempo Real")
    st.markdown("""---""")

    # Adicionar texto de atualização
    st.markdown("""
    <div style='text-align: right; color: #666; font-size: 0.9em;'>
        Atualizado a cada 10 minutos
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""---""")

    # Carregar dados
    with st.spinner("Carregando dados de vendas..."):
        df = load_purchase_items()
    
    if df.empty:
        st.warning("Não há dados disponíveis para análise.")
        return
    
    # Tratar valores None antes de qualquer operação
    df = df.fillna({
        'item_name': 'Sem Nome',
        'source': 'Sem Origem',
        'medium': 'Sem Mídia',
        'campaign': 'Sem Campanha',
        'content': 'Sem Conteúdo',
        'term': 'Sem Termo',
        'page_location': 'Sem Página',
        'item_revenue': 0.0,
        'quantity': 0,
        'item_category': 'Sem Categoria'
    })
    
    # Arredondar quantidade para 0 dígitos decimais
    df['quantity'] = df['quantity'].round(0).astype(int)
    
    # Filtros na barra lateral
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro de Categorias
        categorias = sorted(df['item_category'].unique())
        categoria_selecionada = st.selectbox(
            "Selecione uma Categoria",
            ["Todas"] + categorias
        )
        
        # Filtro de Produtos
        produtos = sorted(df['item_name'].unique())
        produto_selecionado = st.selectbox(
            "Selecione um Produto",
            ["Todos"] + produtos
        )
        
        # Filtro de Origens
        origens = sorted(df['source'].unique())
        origem_selecionada = st.selectbox(
            "Selecione uma Origem",
            ["Todas"] + origens
        )
        
        # Filtro de Mídias
        midias = sorted(df['medium'].unique())
        midia_selecionada = st.selectbox(
            "Selecione uma Mídia",
            ["Todas"] + midias
        )
        
        # Filtro de Campanhas
        campanhas = sorted(df['campaign'].unique())
        campanha_selecionada = st.selectbox(
            "Selecione uma Campanha",
            ["Todas"] + campanhas
        )
        
        # Filtro de Conteúdo
        conteudos = sorted(df['content'].unique())
        conteudo_selecionado = st.selectbox(
            "Selecione um Conteúdo",
            ["Todos"] + conteudos
        )
        
        # Filtro de Termos
        termos = sorted(df['term'].unique())
        termo_selecionado = st.selectbox(
            "Selecione um Termo",
            ["Todos"] + termos
        )
        
        # Filtro de Páginas
        paginas = sorted(df['page_location'].unique())
        pagina_selecionada = st.selectbox(
            "Selecione uma Página",
            ["Todas"] + paginas
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if categoria_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['item_category'] == categoria_selecionada]
    
    if produto_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['item_name'] == produto_selecionado]
        
    if origem_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['source'] == origem_selecionada]
        
    if midia_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['medium'] == midia_selecionada]
        
    if campanha_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['campaign'] == campanha_selecionada]
        
    if conteudo_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['content'] == conteudo_selecionado]
        
    if termo_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['term'] == termo_selecionado]
        
    if pagina_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['page_location'] == pagina_selecionada]
    
    # Métricas Principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"R$ {df_filtrado['item_revenue'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita",
            hint="Valor total das vendas"
        )
    
    with col2:
        big_number_box(
            f"{df_filtrado['quantity'].sum():,.0f}".replace(",", "."), 
            "Itens Vendidos",
            hint="Quantidade total de itens vendidos"
        )
    
    with col3:
        big_number_box(
            f"{df_filtrado['transaction_id'].nunique():,.0f}".replace(",", "."), 
            "Pedidos",
            hint="Número total de pedidos"
        )
    
    with col4:
        big_number_box(
            f"{df_filtrado['session_id'].nunique():,.0f}".replace(",", "."), 
            "Sessões",
            hint="Número total de sessões"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"{df_filtrado['transaction_id'].nunique() / df_filtrado['session_id'].nunique() * 100:.2f}%", 
            "Taxa de Conversão",
            hint="Percentual de sessões que resultaram em pedidos"
        )
    
    with col2:
        big_number_box(
            f"R$ {df_filtrado['item_revenue'].sum() / df_filtrado['transaction_id'].nunique():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Ticket Médio",
            hint="Valor médio por pedido"
        )
    
    with col3:
        big_number_box(
            f"R$ {df_filtrado['item_revenue'].sum() / df_filtrado['session_id'].nunique():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "RPS",
            hint="Receita por Sessão"
        )
    
    st.markdown("""---""")
    
    # Projeção do Dia
    st.header("Projeção do Dia")
    
    # Calcular progresso do dia (usando horário de São Paulo)
    hora_atual = pd.Timestamp.now(tz='America/Sao_Paulo').hour
    progresso_dia = hora_atual / 24
    
    # Calcular projeções
    receita_atual = df_filtrado['item_revenue'].sum()
    itens_atual = df_filtrado['quantity'].sum()
    pedidos_atual = df_filtrado['transaction_id'].nunique()
    sessoes_atual = df_filtrado['session_id'].nunique()
    
    # Projetar valores finais
    receita_projetada = receita_atual / progresso_dia if progresso_dia > 0 else 0
    itens_projetados = itens_atual / progresso_dia if progresso_dia > 0 else 0
    pedidos_projetados = pedidos_atual / progresso_dia if progresso_dia > 0 else 0
    sessoes_projetadas = sessoes_atual / progresso_dia if progresso_dia > 0 else 0
    
    # Calcular métricas projetadas
    taxa_conversao_projetada = (pedidos_projetados / sessoes_projetadas * 100) if sessoes_projetadas > 0 else 0
    ticket_medio_projetado = receita_projetada / pedidos_projetados if pedidos_projetados > 0 else 0
    rps_projetado = receita_projetada / sessoes_projetadas if sessoes_projetadas > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"R$ {receita_projetada:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita Projetada",
            hint="Projeção de receita para o final do dia"
        )
    
    with col2:
        big_number_box(
            f"{itens_projetados:,.0f}".replace(",", "."), 
            "Itens Projetados",
            hint="Projeção de itens vendidos para o final do dia"
        )
    
    with col3:
        big_number_box(
            f"{pedidos_projetados:,.0f}".replace(",", "."), 
            "Pedidos Projetados",
            hint="Projeção de pedidos para o final do dia"
        )
    
    with col4:
        big_number_box(
            f"{sessoes_projetadas:,.0f}".replace(",", "."), 
            "Sessões Projetadas",
            hint="Projeção de sessões para o final do dia"
        )
    
    # Adicionar texto explicativo
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 20px;'>
        Projeção baseada no progresso atual do dia ({hora_atual}h - Horário de São Paulo) - {progresso_dia*100:.1f}% do dia
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""---""")
    
    # Seção 2: Análise por Hora
    st.header("Análise por Hora")
    
    # Converter event_timestamp para datetime e ajustar para São Paulo
    # event_timestamp é um timestamp em microssegundos UTC (mesmo formato usado no BigQuery)
    df_filtrado['datetime_sp'] = pd.to_datetime(df_filtrado['event_timestamp'], unit='us', utc=True).dt.tz_convert('America/Sao_Paulo')
    df_filtrado['hora'] = df_filtrado['datetime_sp'].dt.hour
    df_filtrado['data_sp'] = df_filtrado['datetime_sp'].dt.date
    
    # Filtrar apenas dados do dia atual em São Paulo
    data_atual_sp = pd.Timestamp.now(tz='America/Sao_Paulo').date()
    df_filtrado = df_filtrado[df_filtrado['data_sp'] == data_atual_sp]
    
    # Filtrar horas válidas (0-23) para remover valores negativos
    df_filtrado = df_filtrado[df_filtrado['hora'].between(0, 23)]
    

    
    # Agrupar por hora
    df_hora = df_filtrado.groupby('hora').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_hora = df_hora.rename(columns={
        'hora': 'Hora',
        'quantity': 'Quantidade',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por hora
    df_hora['Ticket Médio'] = df_hora['Receita'] / df_hora['Pedidos']
    df_hora['Taxa de Conversão'] = (df_hora['Pedidos'] / df_hora['Sessões'] * 100).round(2)
    
    # Gráfico de barras para receita por hora
    chart_hora = alt.Chart(df_hora).transform_filter(alt.datum.Hora >= 0).mark_bar(color='#3B82F6', size=20).encode(
        x=alt.X('Hora:Q', 
                title='Hora do Dia',
                scale=alt.Scale(domain=[0, 23]),
                axis=alt.Axis(format='d', labelAngle=0)),
        y=alt.Y('Receita:Q', 
                title='Receita',
                axis=alt.Axis(format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Hora:Q', title='Hora'),
            alt.Tooltip('Receita:Q', title='Receita', format='$,.2f'),
            alt.Tooltip('Quantidade:Q', title='Quantidade'),
            alt.Tooltip('Pedidos:Q', title='Pedidos'),
            alt.Tooltip('Sessões:Q', title='Sessões'),
            alt.Tooltip('Taxa de Conversão:Q', title='Taxa de Conversão', format='.2f'),
            alt.Tooltip('Ticket Médio:Q', title='Ticket Médio', format='$,.2f')
        ]
    ).properties(
        height=400,
        title=alt.TitleParams(
            text='Receita por Hora do Dia (Horário de São Paulo)',
            fontSize=16,
            font='DM Sans',
            anchor='start',
            dy=-10
        )
    ).configure_axis(
        grid=True,
        gridOpacity=0.1,
        labelFontSize=12,
        titleFontSize=13,
        labelFont='DM Sans',
        titleFont='DM Sans'
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart_hora, use_container_width=True)
    
    # Gráfico de linha para sessões e taxa de conversão
    base = alt.Chart(df_hora).transform_filter(alt.datum.Hora >= 0).encode(
        x=alt.X('Hora:Q', 
                title='Hora do Dia',
                scale=alt.Scale(domain=[0, 23]),
                axis=alt.Axis(format='d', labelAngle=0))
    )
    
    line_sessoes = base.mark_line(color='#3B82F6', strokeWidth=2.5).encode(
        y=alt.Y('Sessões:Q', 
                title='Sessões',
                axis=alt.Axis(titleColor='#3B82F6',
                             format=',.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Hora:Q', title='Hora'),
            alt.Tooltip('Sessões:Q', title='Sessões')
        ]
    )
    
    bar_taxa = base.mark_bar(color='#E5E7EB', size=20).encode(
        y=alt.Y('Taxa de Conversão:Q', 
                title='Taxa de Conversão (%)',
                axis=alt.Axis(titleColor='#E5E7EB',
                             format='.2f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Hora:Q', title='Hora'),
            alt.Tooltip('Taxa de Conversão:Q', title='Taxa de Conversão', format='.2f')
        ]
    )
    
    chart_sessoes = (bar_taxa + line_sessoes).resolve_scale(
        y='independent'
    ).properties(
        height=400,
        title=alt.TitleParams(
            text='Sessões e Taxa de Conversão por Hora do Dia',
            fontSize=16,
            font='DM Sans',
            anchor='start',
            dy=-10
        )
    ).configure_axis(
        grid=True,
        gridOpacity=0.1,
        labelFontSize=12,
        titleFontSize=13,
        labelFont='DM Sans',
        titleFont='DM Sans'
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart_sessoes, use_container_width=True)
    
    # Adiciona legenda manual com design melhorado
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                <span style="color: #4B5563; font-size: 14px;">Sessões</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                <span style="color: #4B5563; font-size: 14px;">Taxa de Conversão</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""---""")
    
    # Seção 4: Análise por Origem e Mídia
    st.header("Origem e Mídia")
    
    # Agrupar por origem
    df_origem = df_filtrado.groupby(['source', 'medium']).agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_origem = df_origem.rename(columns={
        'source': 'Origem',
        'medium': 'Mídia',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por origem
    df_origem['Ticket Médio'] = df_origem['Receita'] / df_origem['Pedidos']
    df_origem['Taxa de Conversão'] = (df_origem['Pedidos'] / df_origem['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_origem = df_origem.sort_values('Receita', ascending=False)
    
    # Exibir tabela de origens
    st.dataframe(
        df_origem.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 5: Análise por Campanha
    st.header("Campanha")
    
    # Análise por Campanha
    df_campanha = df_filtrado.groupby('campaign').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_campanha = df_campanha.rename(columns={
        'campaign': 'Campanha',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por campanha
    df_campanha['Ticket Médio'] = df_campanha['Receita'] / df_campanha['Pedidos']
    df_campanha['Taxa de Conversão'] = (df_campanha['Pedidos'] / df_campanha['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_campanha = df_campanha.sort_values('Receita', ascending=False)
    
    # Exibir tabela de campanhas
    st.dataframe(
        df_campanha.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 6: Análise por Conteúdo
    st.header("Conteúdo")
    
    # Análise por Conteúdo
    df_conteudo = df_filtrado.groupby('content').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_conteudo = df_conteudo.rename(columns={
        'content': 'Conteúdo',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por conteúdo
    df_conteudo['Ticket Médio'] = df_conteudo['Receita'] / df_conteudo['Pedidos']
    df_conteudo['Taxa de Conversão'] = (df_conteudo['Pedidos'] / df_conteudo['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_conteudo = df_conteudo.sort_values('Receita', ascending=False)
    
    # Exibir tabela de conteúdo
    st.dataframe(
        df_conteudo.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 11: Análise por Termo
    st.header("Termo")
    
    # Análise por Termo
    df_termo = df_filtrado.groupby('term').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_termo = df_termo.rename(columns={
        'term': 'Termo',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por termo
    df_termo['Ticket Médio'] = df_termo['Receita'] / df_termo['Pedidos']
    df_termo['Taxa de Conversão'] = (df_termo['Pedidos'] / df_termo['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_termo = df_termo.sort_values('Receita', ascending=False)
    
    # Exibir tabela de termos
    st.dataframe(
        df_termo.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 8: Análise por Página
    st.header("Página")
    
    # Análise por Página
    df_pagina = df_filtrado.groupby('page_location').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_pagina = df_pagina.rename(columns={
        'page_location': 'Página',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por página
    df_pagina['Ticket Médio'] = df_pagina['Receita'] / df_pagina['Pedidos']
    df_pagina['Taxa de Conversão'] = (df_pagina['Pedidos'] / df_pagina['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_pagina = df_pagina.sort_values('Receita', ascending=False)
    
    # Exibir tabela de páginas
    st.dataframe(
        df_pagina.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 9: Análise por Categoria
    st.header("Categoria")
    
    # Análise por Categoria
    df_categoria = df_filtrado.groupby('item_category').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_categoria = df_categoria.rename(columns={
        'item_category': 'Categoria',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por categoria
    df_categoria['Ticket Médio'] = df_categoria['Receita'] / df_categoria['Pedidos']
    df_categoria['Taxa de Conversão'] = (df_categoria['Pedidos'] / df_categoria['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_categoria = df_categoria.sort_values('Receita', ascending=False)
    
    # Exibir tabela de categorias
    st.dataframe(
        df_categoria.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""---""")
    
    # Seção 10: Análise por Produto
    st.header("Produto")
    
    # Análise por Produto
    df_produto = df_filtrado.groupby('item_name').agg({
        'quantity': 'sum',
        'item_revenue': 'sum',
        'transaction_id': 'nunique',
        'session_id': 'nunique'
    }).reset_index()
    
    df_produto = df_produto.rename(columns={
        'item_name': 'Produto',
        'quantity': 'Itens Vendidos',
        'item_revenue': 'Receita',
        'transaction_id': 'Pedidos',
        'session_id': 'Sessões'
    })
    
    # Calcular ticket médio e taxa de conversão por produto
    df_produto['Ticket Médio'] = df_produto['Receita'] / df_produto['Pedidos']
    df_produto['Taxa de Conversão'] = (df_produto['Pedidos'] / df_produto['Sessões'] * 100).round(2)
    
    # Ordenar por receita
    df_produto = df_produto.sort_values('Receita', ascending=False)
    
    # Exibir tabela de produtos
    st.dataframe(
        df_produto.style.format({
            'Receita': lambda x: format_currency(x),
            'Ticket Médio': lambda x: format_currency(x),
            'Taxa de Conversão': lambda x: f"{x:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    
