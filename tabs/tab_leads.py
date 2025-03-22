import streamlit as st
from modules.load_data import load_popup_leads
import pandas as pd
from modules.components import big_number_box

def display_tab_leads():

    st.title("Atribuição 2.0")
    st.write("Os leads coletados a partir do popup de cadastro ajudam a entender como as origens de tráfego estão performando para além dos cookies e do comportamento cross-browser.")

    popup_leads = load_popup_leads()
    
    # Botão para resetar filtros (movido para o início)
    if st.button("🔄 Resetar Filtros", key="reset_filters"):
        st.session_state.clear()
        st.rerun()
    
    # Inicializar session_state se não existir
    if 'checkbox_sem_compra' not in st.session_state:
        st.session_state['checkbox_sem_compra'] = True
    if 'checkbox_compras_sem_lead' not in st.session_state:
        st.session_state['checkbox_compras_sem_lead'] = False
    if 'selected_date_cadastro' not in st.session_state:
        st.session_state['selected_date_cadastro'] = (popup_leads['Data do Cadastro'].min().date(), popup_leads['Data do Cadastro'].max().date())
    if 'selected_date_compra' not in st.session_state:
        st.session_state['selected_date_compra'] = (popup_leads['Data da Compra'].min().date(), popup_leads['Data da Compra'].max().date())
    if 'selected_origem_cadastro' not in st.session_state:
        st.session_state['selected_origem_cadastro'] = "Todos"
    if 'selected_origem_compra' not in st.session_state:
        st.session_state['selected_origem_compra'] = "Todos"
    if 'selected_midia_cadastro' not in st.session_state:
        st.session_state['selected_midia_cadastro'] = "Todos"
    if 'selected_midia_compra' not in st.session_state:
        st.session_state['selected_midia_compra'] = "Todos"
    if 'selected_campanha_cadastro' not in st.session_state:
        st.session_state['selected_campanha_cadastro'] = "Todos"
    if 'selected_campanha_compra' not in st.session_state:
        st.session_state['selected_campanha_compra'] = "Todos"
    if 'selected_dias' not in st.session_state:
        st.session_state['selected_dias'] = (float(popup_leads['Dias entre Cadastro e Compra'].min()), float(popup_leads['Dias entre Cadastro e Compra'].max()))
    if 'selected_minutos' not in st.session_state:
        st.session_state['selected_minutos'] = (float(popup_leads['Minutos entre Cadastro e Compra'].min()), float(popup_leads['Minutos entre Cadastro e Compra'].max()))
    
    # Filtros em expander
    with st.expander("🔍 Filtros", expanded=False):
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            # Filtro de data do cadastro
            min_date_cadastro = popup_leads['Data do Cadastro'].min().date()
            max_date_cadastro = popup_leads['Data do Cadastro'].max().date()
            selected_date_cadastro = st.date_input(
                'Filtrar por Data do Cadastro:',
                value=st.session_state.get('selected_date_cadastro', (min_date_cadastro, max_date_cadastro)),
                min_value=min_date_cadastro,
                max_value=max_date_cadastro,
                key='selected_date_cadastro'
            )
            
            # Filtro de origem do cadastro
            origem_cadastro_options = ["Todos"] + sorted(popup_leads['Origem do Cadastro'].dropna().unique().tolist())
            selected_origem_cadastro = st.selectbox(
                "Origem do Cadastro:", 
                origem_cadastro_options,
                key='selected_origem_cadastro'
            )
            
            # Filtro de mídia do cadastro
            midia_cadastro_options = ["Todos"] + sorted(popup_leads['Mídia do Cadastro'].dropna().unique().tolist())
            selected_midia_cadastro = st.selectbox(
                "Mídia do Cadastro:", 
                midia_cadastro_options,
                key='selected_midia_cadastro'
            )
            
            # Filtro de campanha do cadastro
            campanha_cadastro_options = ["Todos"] + sorted(popup_leads['Campanha do Cadastro'].dropna().unique().tolist())
            selected_campanha_cadastro = st.selectbox(
                "Campanha do Cadastro:", 
                campanha_cadastro_options,
                key='selected_campanha_cadastro'
            )
            
            # Filtro de dias entre cadastro e compra
            min_dias = popup_leads['Dias entre Cadastro e Compra'].min()
            max_dias = popup_leads['Dias entre Cadastro e Compra'].max()
            selected_dias = st.slider(
                'Dias entre Cadastro e Compra:',
                min_value=float(min_dias),
                max_value=float(max_dias),
                value=st.session_state.get('selected_dias', (float(min_dias), float(max_dias))),
                key='selected_dias'
            )
            
            # Checkboxes lado a lado
            col_checkbox1, col_checkbox2 = st.columns(2)
            with col_checkbox1:
                incluir_sem_compra = st.checkbox(
                    "Incluir leads sem compra", 
                    value=st.session_state.get('checkbox_sem_compra', True),
                    key="checkbox_sem_compra"
                )
            with col_checkbox2:
                incluir_compras_sem_lead = st.checkbox(
                    "Incluir compras sem lead", 
                    value=st.session_state.get('checkbox_compras_sem_lead', False),
                    key="checkbox_compras_sem_lead"
                )
        
        with col2:
            # Filtro de data da compra
            min_date_compra = popup_leads['Data da Compra'].min().date()
            max_date_compra = popup_leads['Data da Compra'].max().date()
            selected_date_compra = st.date_input(
                'Filtrar por Data da Compra:',
                value=st.session_state.get('selected_date_compra', (min_date_compra, max_date_compra)),
                min_value=min_date_compra,
                max_value=max_date_compra,
                key='selected_date_compra'
            )
            
            # Filtro de origem da compra
            origem_compra_options = ["Todos", "Sem Compra"] + sorted(popup_leads['Origem da Compra'].dropna().unique().tolist())
            selected_origem_compra = st.selectbox(
                "Origem da Compra:", 
                origem_compra_options,
                key='selected_origem_compra'
            )
            
            # Filtro de mídia da compra
            midia_compra_options = ["Todos", "Sem Compra"] + sorted(popup_leads['Mídia da Compra'].dropna().unique().tolist())
            selected_midia_compra = st.selectbox(
                "Mídia da Compra:", 
                midia_compra_options,
                key='selected_midia_compra'
            )
            
            # Filtro de campanha da compra
            campanha_compra_options = ["Todos", "Sem Compra"] + sorted(popup_leads['Campanha da Compra'].dropna().unique().tolist())
            selected_campanha_compra = st.selectbox(
                "Campanha da Compra:", 
                campanha_compra_options,
                key='selected_campanha_compra'
            )
            
            # Filtro de minutos entre cadastro e compra
            min_minutos = popup_leads['Minutos entre Cadastro e Compra'].min()
            max_minutos = popup_leads['Minutos entre Cadastro e Compra'].max()
            selected_minutos = st.slider(
                'Minutos entre Cadastro e Compra:',
                min_value=float(min_minutos),
                max_value=float(max_minutos),
                value=st.session_state.get('selected_minutos', (float(min_minutos), float(max_minutos))),
                key='selected_minutos'
            )
    
    # Aplicar filtros
    filtered_df = popup_leads.copy()
    
    # Filtro de compras sem lead (movido para o início e ajustado)
    if not incluir_compras_sem_lead:
        filtered_df = filtered_df[filtered_df['E-mail'].notna()]
    
    # Filtro de data do cadastro (ajustado para incluir compras sem lead)
    if len(selected_date_cadastro) == 2:
        start_date_cadastro, end_date_cadastro = selected_date_cadastro
        # Ajustar end_date para incluir todo o dia
        end_date_cadastro = pd.Timestamp(end_date_cadastro).replace(hour=23, minute=59, second=59)
        filtered_df = filtered_df[
            (filtered_df['Data do Cadastro'].isna()) |  # Incluir compras sem lead
            ((filtered_df['Data do Cadastro'] >= pd.Timestamp(start_date_cadastro)) & 
            (filtered_df['Data do Cadastro'] <= end_date_cadastro))
        ]
    
    # Filtro de data da compra (ajustado para incluir leads sem compra)
    if len(selected_date_compra) == 2:
        start_date_compra, end_date_compra = selected_date_compra
        # Ajustar end_date para incluir todo o dia
        end_date_compra = pd.Timestamp(end_date_compra).replace(hour=23, minute=59, second=59)
        filtered_df = filtered_df[
            (filtered_df['Data da Compra'].isna()) |  # Incluir leads sem compra
            ((filtered_df['Data da Compra'] >= pd.Timestamp(start_date_compra)) & 
            (filtered_df['Data da Compra'] <= end_date_compra))
        ]
    
    # Filtro de origem do cadastro (ajustado para incluir compras sem lead)
    if selected_origem_cadastro != "Todos":
        filtered_df = filtered_df[
            (filtered_df['Origem do Cadastro'].isna()) |  # Incluir compras sem lead
            (filtered_df['Origem do Cadastro'] == selected_origem_cadastro)
        ]
    
    # Filtro de origem da compra (ajustado para incluir leads sem compra)
    if selected_origem_compra == "Sem Compra":
        filtered_df = filtered_df[filtered_df['Origem da Compra'].isna()]
    elif selected_origem_compra != "Todos":
        filtered_df = filtered_df[filtered_df['Origem da Compra'] == selected_origem_compra]
        
    # Filtro de mídia do cadastro (ajustado para incluir compras sem lead)
    if selected_midia_cadastro != "Todos":
        filtered_df = filtered_df[
            (filtered_df['Mídia do Cadastro'].isna()) |  # Incluir compras sem lead
            (filtered_df['Mídia do Cadastro'] == selected_midia_cadastro)
        ]
        
    # Filtro de mídia da compra (ajustado para incluir leads sem compra)
    if selected_midia_compra == "Sem Compra":
        filtered_df = filtered_df[filtered_df['Mídia da Compra'].isna()]
    elif selected_midia_compra != "Todos":
        filtered_df = filtered_df[filtered_df['Mídia da Compra'] == selected_midia_compra]
        
    # Filtro de campanha do cadastro (ajustado para incluir compras sem lead)
    if selected_campanha_cadastro != "Todos":
        filtered_df = filtered_df[
            (filtered_df['Campanha do Cadastro'].isna()) |  # Incluir compras sem lead
            (filtered_df['Campanha do Cadastro'] == selected_campanha_cadastro)
        ]
        
    # Filtro de campanha da compra (ajustado para incluir leads sem compra)
    if selected_campanha_compra == "Sem Compra":
        filtered_df = filtered_df[filtered_df['Campanha da Compra'].isna()]
    elif selected_campanha_compra != "Todos":
        filtered_df = filtered_df[filtered_df['Campanha da Compra'] == selected_campanha_compra]
        
    # Filtro de dias entre cadastro e compra (ajustado para incluir leads sem compra)
    if incluir_sem_compra:
        filtered_df = filtered_df[
            (filtered_df['Dias entre Cadastro e Compra'].isna()) |  # Incluir leads sem compra
            ((filtered_df['Dias entre Cadastro e Compra'] >= selected_dias[0]) & 
            (filtered_df['Dias entre Cadastro e Compra'] <= selected_dias[1]))
        ]
    else:
        filtered_df = filtered_df[
            (filtered_df['Dias entre Cadastro e Compra'] >= selected_dias[0]) & 
            (filtered_df['Dias entre Cadastro e Compra'] <= selected_dias[1])
        ]
    
    # Filtro de minutos entre cadastro e compra (ajustado para incluir leads sem compra)
    if incluir_sem_compra:
        filtered_df = filtered_df[
            (filtered_df['Minutos entre Cadastro e Compra'].isna()) |  # Incluir leads sem compra
            ((filtered_df['Minutos entre Cadastro e Compra'] >= selected_minutos[0]) & 
            (filtered_df['Minutos entre Cadastro e Compra'] <= selected_minutos[1]))
        ]
    else:
        filtered_df = filtered_df[
            (filtered_df['Minutos entre Cadastro e Compra'] >= selected_minutos[0]) & 
            (filtered_df['Minutos entre Cadastro e Compra'] <= selected_minutos[1])
        ]
    
    # Big Numbers
    st.header("Big Numbers")
    
    # Calcular métricas com dados filtrados
    total_leads = len(filtered_df)
    leads_com_compra = filtered_df['ID da Compra'].notna().sum()
    tx_conversao = (leads_com_compra / total_leads * 100) if total_leads > 0 else 0
    
    # Calcular receita total sem duplicar vendas
    receita_total = filtered_df[filtered_df['ID da Compra'].notna()].drop_duplicates(subset=['ID da Compra'])['Valor da Compra'].sum()
    
    # Calcular valor médio por lead (primeira compra)
    valor_medio_compra = filtered_df[filtered_df['ID da Compra'].notna()].groupby('E-mail')['Valor da Compra'].first().mean() if leads_com_compra > 0 else 0
    
    # Calcular tempo médio até primeira compra
    tempo_medio_conversao = filtered_df[filtered_df['ID da Compra'].notna()].groupby('E-mail')['Dias entre Cadastro e Compra'].first().mean() if leads_com_compra > 0 else 0
    
    # Exibir métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"{total_leads:,.0f}".replace(",", "."),
            "Total de Leads",
            hint="Número total de leads capturados via popup"
        )
    
    with col2:
        big_number_box(
            f"{leads_com_compra:,.0f}".replace(",", "."),
            "Compras",
            hint="Número de leads que realizaram pelo menos uma compra"
        )
    
    with col3:
        big_number_box(
            f"{tx_conversao:.1f}%",
            "Taxa de Conversão",
            hint="Percentual de leads que realizaram compras"
        )
    
    with col4:
        big_number_box(
            f"R$ {receita_total:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Receita Total",
            hint="Valor total das compras realizadas por leads (sem duplicar vendas)"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        big_number_box(
            f"R$ {valor_medio_compra:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "Ticket Médio",
            hint="Valor médio da primeira compra por lead"
        )
    
    with col2:
        big_number_box(
            f"{tempo_medio_conversao:.1f}",
            "Dias para Conversão",
            hint="Tempo médio entre o cadastro e a primeira compra"
        )
    
    with col3:
        leads_hoje = len(filtered_df[filtered_df['Data do Cadastro'].dt.date == pd.Timestamp.now().date()])
        big_number_box(
            f"{leads_hoje:,.0f}".replace(",", "."),
            "Leads Hoje",
            hint="Leads capturados hoje"
        )
    
    with col4:
        leads_sem_compra = total_leads - leads_com_compra
        big_number_box(
            f"{leads_sem_compra:,.0f}".replace(",", "."),
            "Leads sem Compra",
            hint="Leads que ainda não realizaram compras"
        )
    
    st.markdown("---")
    
    # Tabelas lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Desempenho por Origem e Mídia de Cadastro")
        
        # Criar tabela agrupada por origem e mídia de cadastro
        grouped_df_cadastro = filtered_df.groupby([
            'Origem do Cadastro',
            'Mídia do Cadastro'
        ]).agg({
            'E-mail': 'count',  # Total de leads
            'ID da Compra': lambda x: x.notna().sum()  # Total de compras
        }).reset_index()
        
        # Renomear colunas
        grouped_df_cadastro.columns = [
            'Origem do Cadastro',
            'Mídia do Cadastro',
            'Total de Leads',
            'Total de Compras'
        ]
        
        # Calcular taxa de conversão
        grouped_df_cadastro['Taxa de Conversão'] = (grouped_df_cadastro['Total de Compras'] / grouped_df_cadastro['Total de Leads'] * 100).round(2)
        
        # Ordenar por total de leads (decrescente)
        grouped_df_cadastro = grouped_df_cadastro.sort_values('Total de Leads', ascending=False)
        
        # Exibir tabela agrupada
        st.data_editor(
            grouped_df_cadastro,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Taxa de Conversão': st.column_config.NumberColumn(
                    'Taxa de Conversão',
                    format="%.2f%%"
                )
            }
        )
    
    with col2:
        st.subheader("Desempenho por Origem e Mídia de Compra")
        
        # Criar tabela agrupada por origem e mídia de compra
        grouped_df_compra = filtered_df.groupby([
            'Origem da Compra',
            'Mídia da Compra'
        ]).agg({
            'ID da Compra': lambda x: x.notna().sum()  # Total de compras
        }).reset_index()
        
        # Renomear colunas
        grouped_df_compra.columns = [
            'Origem da Compra',
            'Mídia da Compra',
            'Total de Compras'
        ]
        
        # Ordenar por total de compras (decrescente)
        grouped_df_compra = grouped_df_compra.sort_values('Total de Compras', ascending=False)
        
        # Exibir tabela agrupada
        st.data_editor(
            grouped_df_compra,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    st.subheader("Leads Individuais")
    
    # Botão de exportação
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name="leads.csv",
        mime="text/csv"
    )
    
    # Exibir dados filtrados
    st.data_editor(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data do Cadastro": st.column_config.DatetimeColumn(
                "Data do Cadastro",
                format="DD/MM/YYYY HH:mm:ss"
            ),
            "Data da Compra": st.column_config.DatetimeColumn(
                "Data da Compra", 
                format="DD/MM/YYYY HH:mm:ss"
            )
        }
    )