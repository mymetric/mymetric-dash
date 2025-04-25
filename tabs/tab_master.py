import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from modules.load_data import load_internal_events, save_client, load_clients
from modules.components import big_number_box

def display_client_registration():
    st.header("👥 Cadastro de Clientes")
    
    # Adicionar botões para links externos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <a href="https://docs.google.com/spreadsheets/d/1VFkY-N3zIvUK7qQmuqvhuiFz9HhoG687itpSxnS3L-M/edit?gid=754044428#gid=754044428" 
            target="_blank">
                <button style="background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                    📝 Atualizar Planilha após Edições
                </button>
            </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <a href="https://docs.google.com/spreadsheets/d/e/2PACX-1vS30dOYdoH1XYmakElzEAdCTBZdA1SGS0SnJeHTFMIaXykD6EaUZJ3iZk4oMvIBQ_L4vc4GDWUw7nE0/pub?gid=754044428&single=true&output=csv" 
            target="_blank">
                <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                    📥 CSV para APIs Front-end
                </button>
            </a>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Carregar clientes existentes
    try:
        clients_df = load_clients()
        
        if clients_df.empty:
            st.warning("Nenhum cliente encontrado no banco de dados.")
        else:
            st.subheader("Clientes Cadastrados")
            
            # Preparar dados para exibição
            display_df = clients_df.copy()
            
            # Converter timestamps
            if 'created_at' in display_df.columns:
                display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.tz_convert('America/Sao_Paulo')
            if 'updated_at' in display_df.columns:
                display_df['updated_at'] = pd.to_datetime(display_df['updated_at']).dt.tz_convert('America/Sao_Paulo')
            
            # Extrair informações relevantes do JSON de configs
            if 'configs' in display_df.columns:
                display_df['Nome'] = display_df['configs'].apply(lambda x: x.get('name', 'N/A') if isinstance(x, dict) else 'N/A')
                display_df['E-commerce'] = display_df['configs'].apply(lambda x: x.get('ecommerce', 'N/A') if isinstance(x, dict) else 'N/A')
            
            # Criar cabeçalho da tabela
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
            with col1:
                st.markdown("**📁 Tabela**")
            with col2:
                st.markdown("**👤 Nome**")
            with col3:
                st.markdown("**🛍️ E-commerce**")
            with col4:
                st.markdown("**📅 Data de Criação**")
            with col5:
                st.markdown("**🔄 Última Atualização**")
            with col6:
                st.markdown("**⚙️ Ações**")
            
            # Adicionar linha divisória
            st.markdown("---")
            
            # Exibir cada cliente em uma linha
            for idx, row in display_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                
                with col1:
                    st.write(row['tablename'])
                with col2:
                    st.write(row['Nome'])
                with col3:
                    st.write(row['E-commerce'])
                with col4:
                    st.write(row['created_at'].strftime("%d/%m/%y %H:%M") if 'created_at' in row else 'N/A')
                with col5:
                    st.write(row['updated_at'].strftime("%d/%m/%y %H:%M") if 'updated_at' in row else 'N/A')
                with col6:
                    if st.button("✏️", key=f"edit_{row['tablename']}"):
                        st.session_state['editing_client'] = row['tablename']
                        st.session_state['client_data'] = clients_df[clients_df['tablename'] == row['tablename']].iloc[0]['configs']
                        st.rerun()
            
            # Adicionar linha divisória
            st.markdown("---")
            
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {str(e)}")
        print(f"Erro detalhado: {str(e)}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    # Formulário de cadastro/edição
    with st.form("client_registration_form"):
        col1, col2 = st.columns(2)
        
        # Verificar se está editando um cliente existente
        editing_client = st.session_state.get('editing_client')
        client_data = st.session_state.get('client_data', {})
        
        with col1:
            tablename = st.text_input("Nome da Tabela (tablename)", 
                                    value=editing_client if editing_client else "")
            name = st.text_input("Nome do Cliente", 
                                value=client_data.get('name', ''),
                                key="name")
            password = st.text_input("Senha", 
                                   type="password", 
                                   value=client_data.get('password', ''),
                                   key="password")
            skip = st.selectbox("Skip", 
                              ["n", "y"], 
                              index=0 if client_data.get('skip') == 'n' else 1,
                              key="skip")
            ecommerce = st.selectbox("E-commerce", 
                                   ["ga", "shopify"], 
                                   index=0 if client_data.get('ecommerce') == 'ga' else 1,
                                   key="ecommerce")
            
        with col2:
            ga4_dataset_id = st.text_input("GA4 Dataset ID", 
                                         value=client_data.get('ga4_dataset_id', ''),
                                         key="ga4_dataset_id")
            meta_account_id = st.text_input("Meta Account ID", 
                                          value=client_data.get('meta_account_id', ''),
                                          key="meta_account_id")
            gads_dataset = st.text_input("GADS Dataset", 
                                       value=client_data.get('gads_dataset', ''),
                                       key="gads_dataset")
            gads_account = st.text_input("GADS Account", 
                                       value=client_data.get('gads_account', ''),
                                       key="gads_account")
            gsc = st.text_input("GSC", 
                              value=client_data.get('gsc', ''),
                              key="gsc")
            wpp_group = st.text_input("WPP Group", 
                                    value=client_data.get('wpp_group', ''),
                                    key="wpp_group")
            meta_pixel_id = st.text_input("Meta Pixel ID", 
                                        value=client_data.get('meta_pixel_id', ''),
                                        key="meta_pixel_id")
            ga_data_stream = st.text_input("GA Data Stream", 
                                         value=client_data.get('ga_data_stream', ''),
                                         key="ga_data_stream")
        
        submitted = st.form_submit_button("Cadastrar Cliente" if not editing_client else "Atualizar Cliente")
        
        if submitted:
            try:
                # Criar dicionário com os dados do cliente
                client_data = {
                    "name": name,
                    "password": password,
                    "skip": skip,
                    "ecommerce": ecommerce,
                    "ga4_dataset_id": ga4_dataset_id,
                    "meta_account_id": meta_account_id,
                    "gads_dataset": gads_dataset,
                    "gads_account": gads_account,
                    "gsc": gsc,
                    "wpp_group": wpp_group,
                    "meta_pixel_id": meta_pixel_id,
                    "ga_data_stream": ga_data_stream
                }
                
                # Converter para JSON
                configs = json.dumps(client_data)
                
                # Salvar no BigQuery
                if save_client(tablename, configs):
                    st.success("Cliente cadastrado com sucesso!" if not editing_client else "Cliente atualizado com sucesso!")
                    
                    # Limpar o formulário e estado de edição
                    for key in ["tablename", "name", "password", "skip", "ecommerce", 
                               "ga4_dataset_id", "meta_account_id", "gads_dataset", 
                               "gads_account", "gsc", "wpp_group", "meta_pixel_id", 
                               "ga_data_stream"]:
                        st.session_state[key] = ""
                    if 'editing_client' in st.session_state:
                        del st.session_state['editing_client']
                    if 'client_data' in st.session_state:
                        del st.session_state['client_data']
                    st.rerun()
                else:
                    st.error("Erro ao cadastrar cliente. Por favor, tente novamente.")
            except Exception as e:
                st.error(f"Erro ao processar formulário: {str(e)}")
                print(f"Erro detalhado: {str(e)}")
                import traceback
                print(f"Stack trace: {traceback.format_exc()}")

def display_tab_master():
    st.title("Master")
    
    # Criar tabs
    tab_analytics, tab_clients = st.tabs(["📊 Analytics", "👥 Clientes"])
    
    with tab_analytics:
        # Carregar eventos internos
        df = load_internal_events()
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('America/Sao_Paulo')
        
        # Filtrar apenas eventos de login
        df_logins = df[df['event_name'] == 'login']
        
        # Calcular MAU/WAU/DAU
        now = pd.Timestamp.now(tz='America/Sao_Paulo')
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)
        one_day_ago = now - timedelta(days=1)
        
        st.subheader("Métricas por Empresa")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mau = df_logins[df_logins['created_at'] >= thirty_days_ago]['tablename'].nunique()
            big_number_box(mau, "MAU", hint="Empresas únicas que fizeram login nos últimos 30 dias")
        
        with col2:
            wau = df_logins[df_logins['created_at'] >= seven_days_ago]['tablename'].nunique()
            big_number_box(wau, "WAU", hint="Empresas únicas que fizeram login nos últimos 7 dias")
        
        with col3:
            dau = df_logins[df_logins['created_at'] >= one_day_ago]['tablename'].nunique()
            big_number_box(dau, "DAU", hint="Empresas únicas que fizeram login nas últimas 24 horas")

        st.divider()
        
        # Segunda linha de métricas baseada em load_internal_events
        st.subheader("Métricas por Usuário")
        
        # Filtrar usuários específicos para análise
        df_filtered = df[~df['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mau_events = df_filtered[df_filtered['created_at'] >= thirty_days_ago]['user'].nunique()
            big_number_box(mau_events, "MAU", hint="Usuários únicos que realizaram eventos nos últimos 30 dias")
        
        with col2:
            wau_events = df_filtered[df_filtered['created_at'] >= seven_days_ago]['user'].nunique()
            big_number_box(wau_events, "WAU", hint="Usuários únicos que realizaram eventos nos últimos 7 dias")
        
        with col3:
            dau_events = df_filtered[df_filtered['created_at'] >= one_day_ago]['user'].nunique()
            big_number_box(dau_events, "DAU", hint="Usuários únicos que realizaram eventos nas últimas 24 horas")
        
        st.divider()
        
        # Insights
        st.subheader("Insights")
        st.markdown("---")
        
        # Empresa mais ativa (mais eventos nos últimos 30 dias)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Empresa Mais Ativa**")
            empresa_mais_ativa = (df[df['created_at'] >= thirty_days_ago]
                                .groupby('tablename')
                                .size()
                                .sort_values(ascending=False)
                                .head(1))
            
            if not empresa_mais_ativa.empty:
                empresa = empresa_mais_ativa.index[0]
                eventos = empresa_mais_ativa.values[0]
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: #1f77b4;">{empresa}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">{eventos:,} eventos nos últimos 30 dias</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Sem dados suficientes para determinar a empresa mais ativa")
        
        with col2:
            st.markdown("**👥 Empresa com Mais Usuários Ativos**")
            empresa_mais_usuarios = (df[df['created_at'] >= thirty_days_ago]
                                   .groupby('tablename')['user']
                                   .nunique()
                                   .sort_values(ascending=False)
                                   .head(1))
            
            if not empresa_mais_usuarios.empty:
                empresa = empresa_mais_usuarios.index[0]
                usuarios = empresa_mais_usuarios.values[0]
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: #1f77b4;">{empresa}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">{usuarios:,} usuários únicos nos últimos 30 dias</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Sem dados suficientes para determinar a empresa com mais usuários ativos")
        
        st.markdown("---")
        
        # Top 5 empresas por atividade
        st.markdown("**📊 Top 5 Empresas por Atividade**")
        st.markdown("")
        top_empresas = (df[df['created_at'] >= thirty_days_ago]
                       .groupby('tablename')
                       .size()
                       .sort_values(ascending=False)
                       .head(5))
        
        if not top_empresas.empty:
            st.dataframe(
                pd.DataFrame({
                    'Empresa': top_empresas.index,
                    'Eventos': top_empresas.values
                }),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Sem dados suficientes para mostrar o ranking de empresas")
        
        st.markdown("---")
        st.divider()
        
        # Análise por Tabela
        st.header("📊 Análise de Uso das Tabelas")
        
        # Filtrar usuários específicos para análise de tabelas
        df_tables = df[~df['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
        df_logins_tables = df_logins[~df_logins['user'].isin(['mymetric', 'buildgrowth', 'alvisi'])]
        
        # Agrupar por tablename e calcular métricas
        table_analysis = (df_tables.groupby('tablename')
                         .agg({
                             'created_at': 'max',  # última atividade
                             'tab': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 abas mais acessadas
                             'event_name': 'count'  # total de eventos
                         })
                         .reset_index()
                         .rename(columns={'created_at': 'ultima_atividade'}))
        
        # Adicionar contagem de logins
        login_counts = df_logins_tables.groupby('tablename').size().reset_index(name='logins')
        table_analysis = table_analysis.merge(login_counts, on='tablename', how='left')
        table_analysis['logins'] = table_analysis['logins'].fillna(0).astype(int)
        
        # Ordenar por número de logins
        table_analysis = table_analysis.sort_values('logins', ascending=False)
        
        st.dataframe(
            table_analysis,
            column_config={
                "tablename": st.column_config.Column("📁 Nome da Tabela"),
                "logins": st.column_config.NumberColumn("🔑 Número de Logins", format="%d"),
                "event_name": st.column_config.NumberColumn("📊 Total de Eventos", format="%d"),
                "ultima_atividade": st.column_config.DatetimeColumn("⏰ Última Atividade", format="DD/MM/YY HH:mm"),
                "tab": st.column_config.Column("📑 Top 2 Abas")
            },
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        # Análise por Usuário
        st.header("👤 Análise de Uso por Usuário")
        
        # Agrupar por usuário e calcular métricas
        user_analysis = (df.groupby('user')
                        .agg({
                            'created_at': 'max',  # última atividade
                            'tablename': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 tabelas mais acessadas
                            'tab': lambda x: ' → '.join(x.value_counts().nlargest(2).index.tolist()) if len(x.value_counts()) > 0 else 'N/A',  # 2 abas mais acessadas
                            'event_name': 'count'  # total de eventos
                        })
                        .reset_index()
                        .rename(columns={'created_at': 'ultima_atividade'}))
        
        # Adicionar contagem de logins
        user_login_counts = df_logins.groupby('user').size().reset_index(name='logins')
        user_analysis = user_analysis.merge(user_login_counts, on='user', how='left')
        user_analysis['logins'] = user_analysis['logins'].fillna(0).astype(int)
        
        # Ordenar por número de logins
        user_analysis = user_analysis.sort_values('logins', ascending=False)
        
        st.dataframe(
            user_analysis,
            column_config={
                "user": st.column_config.Column("👤 Usuário"),
                "logins": st.column_config.NumberColumn("🔑 Número de Logins", format="%d"),
                "event_name": st.column_config.NumberColumn("📊 Total de Eventos", format="%d"),
                "ultima_atividade": st.column_config.DatetimeColumn("⏰ Última Atividade", format="DD/MM/YY HH:mm"),
                "tablename": st.column_config.Column("📁 Top 2 Tabelas"),
                "tab": st.column_config.Column("📑 Top 2 Abas")
            },
            hide_index=True,
            use_container_width=True
        )

        st.divider()
        
        # Análise de Tabelas por Aba
        st.header("📑 Tabelas por Aba")
        
        # Contar tablenames distintos por aba
        tab_analysis = (df
                       .groupby('tab')
                       .agg({
                           'tablename': 'nunique',  # conta tablenames distintos
                           'event_name': 'count'    # total de eventos
                       })
                       .reset_index()
                       .rename(columns={
                           'tablename': 'tabelas_distintas',
                           'event_name': 'total_eventos'
                       })
                       .sort_values('tabelas_distintas', ascending=False))
        
        st.dataframe(
            tab_analysis,
            column_config={
                "tab": st.column_config.Column("📑 Aba"),
                "tabelas_distintas": st.column_config.NumberColumn("📁 Tabelas Distintas", format="%d"),
                "total_eventos": st.column_config.NumberColumn("📊 Total de Eventos", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab_clients:
        display_client_registration()

    