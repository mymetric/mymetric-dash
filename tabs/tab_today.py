import streamlit as st
import pandas as pd
from modules.load_data import load_current_month_revenue
from datetime import datetime
import calendar
import altair as alt
from modules.load_data import load_today_data
from partials.run_rate import load_table_metas
from modules.components import big_number_box

def calculate_daily_goal(meta_receita, total_receita_mes):
    """Calcula a meta diária considerando apenas o valor que falta para bater a meta do mês."""
    hoje = datetime.now()
    _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
    dias_restantes = ultimo_dia - hoje.day + 1  # +1 para incluir o dia atual
    
    # Calcula quanto falta para atingir a meta
    valor_faltante = meta_receita - total_receita_mes
    if valor_faltante <= 0:
        return 0, 0, 0
        
    # Calcula a meta diária baseada apenas no valor faltante
    meta_diaria = valor_faltante / dias_restantes if dias_restantes > 0 else 0
    
    return meta_diaria, valor_faltante, dias_restantes

def format_currency(value):
    """Formata valor para o padrão de moeda BR."""
    return f"R$ {value:,.2f}".replace(",", "*").replace(".", ",").replace("*", ".")

def display_tab_today():
    st.title("Análise do Dia")
    st.markdown("""---""")

    df = load_today_data()
    
    # st.write(df)
    
    # Calcular métricas totais do dia
    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    total_receita_dia = df["Receita Paga"].sum()
    
    # Pegar hora atual em Brasília
    hora_atual = pd.Timestamp.now(tz='America/Sao_Paulo').hour
    
    df_mes = load_current_month_revenue()
    total_receita_mes = float(df_mes['total_mes'].iloc[0])
    
    meta_receita = load_table_metas()
    current_month = datetime.now().strftime("%Y-%m")
    meta_receita = meta_receita.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0)

    # Agrupa por hora
    df_hora = df.groupby('Hora').agg({
        'Sessões': 'sum',
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum',
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Garantir que todas as horas até a atual estejam presentes
    todas_horas = pd.DataFrame({'Hora': range(0, hora_atual + 1)})
    df_hora = pd.merge(todas_horas, df_hora, on='Hora', how='left')
    df_hora = df_hora.fillna(0)
    
    # Calcula métricas acumuladas
    df_hora['Receita Acumulada'] = df_hora['Receita Paga'].cumsum()
    df_hora['Pedidos Acumulados'] = df_hora['Pedidos'].cumsum()
    df_hora['Sessões Acumuladas'] = df_hora['Sessões'].cumsum()
    
    # Calcula médias por hora até agora
    media_receita_hora = df_hora[df_hora['Hora'] < hora_atual]['Receita Paga'].mean()
    media_pedidos_hora = df_hora[df_hora['Hora'] < hora_atual]['Pedidos'].mean()
    media_sessoes_hora = df_hora[df_hora['Hora'] < hora_atual]['Sessões'].mean()
    
    # Projeção para o final do dia
    horas_restantes = 24 - hora_atual
    projecao_receita = total_receita_dia + (media_receita_hora * horas_restantes)
    projecao_pedidos = pedidos + (media_pedidos_hora * horas_restantes)
    projecao_sessoes = sessoes + (media_sessoes_hora * horas_restantes)

    # Calcula a meta diária e informações relacionadas
    meta_diaria, valor_faltante, dias_restantes = calculate_daily_goal(meta_receita, total_receita_mes)
    
    # Exibe informações sobre a meta no topo
    if meta_receita > 0:
        # Definir cores e mensagens baseadas no progresso
        percentual_meta = (total_receita_dia / meta_diaria * 100) if meta_diaria > 0 else 0
        
        if percentual_meta >= 100:
            cor_probabilidade = "#10B981"
            gradient = "linear-gradient(135deg, #10B981, #059669)"
            mensagem_probabilidade = "Excelente dia! Você já atingiu a meta diária!"
        elif percentual_meta >= 80:
            cor_probabilidade = "#3B82F6"
            gradient = "linear-gradient(135deg, #3B82F6, #2563EB)"
            mensagem_probabilidade = "Bom progresso! Continue focado que a meta está ao seu alcance!"
        elif percentual_meta >= 60:
            cor_probabilidade = "#F59E0B"
            gradient = "linear-gradient(135deg, #F59E0B, #D97706)"
            mensagem_probabilidade = "Momento de intensificar! Aumente as ações de marketing e vendas!"
        elif percentual_meta >= 40:
            cor_probabilidade = "#F97316"
            gradient = "linear-gradient(135deg, #F97316, #EA580C)"
            mensagem_probabilidade = "Hora de agir! Revise suas estratégias e faça ajustes!"
        else:
            cor_probabilidade = "#EF4444"
            gradient = "linear-gradient(135deg, #EF4444, #DC2626)"
            mensagem_probabilidade = "Alerta! Momento de tomar ações urgentes para reverter o cenário!"

        # Renderizar o card principal
        st.markdown(f"""
            <div style="background:white; border-radius:16px; padding:24px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); margin:20px 0;">
                <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:24px; margin-bottom:24px;">
                    <div style="background:#F8FAFC; padding:16px; border-radius:12px;">
                        <div style="color:#64748B; font-size:14px; margin-bottom:8px;">Meta Diária</div>
                        <div style="color:#0F172A; font-size:24px; font-weight:600;">{format_currency(meta_diaria)}</div>
                    </div>
                    <div style="background:#F8FAFC; padding:16px; border-radius:12px;">
                        <div style="color:#64748B; font-size:14px; margin-bottom:8px;">Realizado Hoje</div>
                        <div style="color:#0F172A; font-size:24px; font-weight:600;">{format_currency(total_receita_dia)}</div>
                        <div style="color:#64748B; font-size:12px; margin-top:4px;">{percentual_meta:.1f}% da meta</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Renderizar a barra de progresso
        st.markdown(f"""
            <div style="margin-bottom:24px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="color:#64748B; font-size:14px;">Progresso</div>
                    <div style="color:{cor_probabilidade}; font-weight:500;">{percentual_meta:.1f}%</div>
                </div>
                <div style="width:100%; height:8px; background:#F1F5F9; border-radius:4px; overflow:hidden;">
                    <div style="width:{min(percentual_meta, 100)}%; height:100%; background:{gradient}; border-radius:4px; transition:width 0.3s ease;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Renderizar o card de probabilidade
        st.markdown(f"""
            <div style="background:{cor_probabilidade}10; border:1px solid {cor_probabilidade}25; padding:20px; border-radius:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:8px; height:8px; border-radius:50%; background:{cor_probabilidade};"></div>
                        <span style="color:{cor_probabilidade}; font-weight:500;">Status do Dia</span>
                    </div>
                    <div style="background:{cor_probabilidade}; color:white; padding:6px 16px; border-radius:20px; font-weight:500; font-size:14px;">{percentual_meta:.1f}%</div>
                </div>
                <p style="margin:0; color:{cor_probabilidade}; font-size:14px; line-height:1.5;">{mensagem_probabilidade}</p>
            </div>
        """, unsafe_allow_html=True)

        # Renderizar as métricas adicionais
        st.markdown(f"""
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:24px; margin-bottom:32px;">
                <div style="text-align:center;">
                    <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Horas Passadas</div>
                    <div style="color:#0F172A; font-weight:500;">{hora_atual} de 24</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Média por Hora</div>
                    <div style="color:#0F172A; font-weight:500;">{format_currency(media_receita_hora)}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#64748B; font-size:13px; margin-bottom:4px;">Meta por Hora</div>
                    <div style="color:#0F172A; font-weight:500;">{format_currency(meta_diaria/24)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
    
    # Big Numbers com realizado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        big_number_box(
            format_currency(total_receita_dia),
            "Receita Realizada",
            hint=f"Receita total realizada até {hora_atual:02d}:00"
        )
        
    with col2:
        big_number_box(
            f"{pedidos:,.0f}".replace(",", "."), 
            "Pedidos Realizados",
            hint=f"Total de pedidos até {hora_atual:02d}:00"
        )
        
    with col3:
        big_number_box(
            f"{sessoes:,.0f}".replace(",", "."), 
            "Sessões Realizadas",
            hint=f"Total de sessões até {hora_atual:02d}:00"
        )
    
    # Big Numbers com projeções
    col1, col2, col3 = st.columns(3)
    
    with col1:
        big_number_box(
            format_currency(projecao_receita),
            "Projeção de Receita",
            hint=f"Projeção baseada na média de {format_currency(media_receita_hora)} por hora. Faltam {horas_restantes}h para o fim do dia."
        )
        
    with col2:
        big_number_box(
            f"{projecao_pedidos:,.0f}".replace(",", "."), 
            "Projeção de Pedidos",
            hint=f"Projeção baseada na média de {media_pedidos_hora:.1f} pedidos por hora. Faltam {horas_restantes}h para o fim do dia."
        )
        
    with col3:
        big_number_box(
            f"{projecao_sessoes:,.0f}".replace(",", "."), 
            "Projeção de Sessões",
            hint=f"Projeção baseada na média de {media_sessoes_hora:.1f} sessões por hora. Faltam {horas_restantes}h para o fim do dia."
        )
    
    # Adiciona espaço entre os big numbers e o gráfico
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Criar gráfico de barras para receita por hora
    bar_hora = alt.Chart(df_hora).mark_bar(color='#E5E7EB', size=20).encode(
        x=alt.X('Hora:O', 
                title='Hora do Dia',
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Receita Paga:Q', 
                axis=alt.Axis(title='Receita',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Hora:O', title='Hora'),
            alt.Tooltip('Receita Paga:Q', title='Receita', format='$,.2f'),
            alt.Tooltip('Pedidos:Q', title='Pedidos', format=',d'),
            alt.Tooltip('Sessões:Q', title='Sessões', format=',d')
        ]
    )
    
    # Criar linha para receita acumulada
    line_acumulado = alt.Chart(df_hora).mark_line(color='#3B82F6', strokeWidth=2.5).encode(
        x=alt.X('Hora:O'),
        y=alt.Y('Receita Acumulada:Q', 
                axis=alt.Axis(title='Receita Acumulada',
                             format='$,.0f',
                             titlePadding=10)),
        tooltip=[
            alt.Tooltip('Hora:O', title='Hora'),
            alt.Tooltip('Receita Acumulada:Q', title='Receita Acumulada', format='$,.2f')
        ]
    )
    
    # Combinar os gráficos com melhorias visuais
    combined_hora = alt.layer(
        bar_hora, 
        line_acumulado
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Evolução de Receita por Hora',
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
    
    # Exibir o gráfico
    st.altair_chart(combined_hora, use_container_width=True)

    # Adiciona legenda manual com design melhorado
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 2.5px; background-color: #3B82F6;"></div>
                <span style="color: #4B5563; font-size: 14px;">Receita Acumulada</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 12px; background-color: #E5E7EB;"></div>
                <span style="color: #4B5563; font-size: 14px;">Receita por Hora</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Criar colunas para mais métricas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Métricas por Hora")
        # Adicionar tabela com dados por hora
        df_hora_display = df_hora.copy()
        for col in ['Receita Paga', 'Receita Acumulada']:
            df_hora_display[col] = df_hora_display[col].apply(format_currency)
        
        # Adicionar % do total
        df_hora_display['% do Total'] = (df_hora['Receita Paga'] / df_hora['Receita Paga'].sum() * 100).round(2).astype(str) + '%'
        
        # Ordenar e exibir
        df_hora_display = df_hora_display.sort_values('Hora', ascending=True)
        st.dataframe(df_hora_display, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Insights")
        # Melhor hora
        melhor_hora = df_hora.loc[df_hora['Receita Paga'].idxmax()]
        st.success(f"🌟 Melhor hora do dia: {int(melhor_hora['Hora'])}h com {format_currency(melhor_hora['Receita Paga'])} em receita e {int(melhor_hora['Pedidos'])} pedidos")
        
        # Média por hora
        st.info(f"📊 Média por hora até agora: {format_currency(media_receita_hora)} em receita e {media_pedidos_hora:.1f} pedidos")
        
        # Ritmo necessário
        if meta_receita > 0:
            # Calcula o ritmo necessário por hora para o resto do dia
            ritmo_hora = (meta_diaria - total_receita_dia) / horas_restantes if horas_restantes > 0 else 0
            
            st.warning(f"""
            🎯 **Metas e Ritmos:**
            - Meta diária: {format_currency(meta_diaria)}
            - Faturado hoje: {format_currency(total_receita_dia)}
            - Falta hoje: {format_currency(meta_diaria - total_receita_dia)}
            - Ritmo necessário: {format_currency(ritmo_hora)}/hora para as próximas {horas_restantes}h
            """)
        
        # Comparação com média
        if hora_atual > 0:
            ultima_hora = df_hora[df_hora['Hora'] == hora_atual - 1]['Receita Paga'].iloc[0]
            diff_media = ((ultima_hora / media_receita_hora) - 1) * 100 if media_receita_hora > 0 else 0
            status = "acima" if diff_media > 0 else "abaixo"
            st.info(f"📈 Última hora completa ({hora_atual-1}h) está {abs(diff_media):.1f}% {status} da média")
        
    # Adiciona espaço
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Análise de Origens
    st.header("Análise de Origens")
    
    # Agrupa dados por origem
    df_origem = df.groupby(['Cluster', 'Origem', 'Mídia']).agg({
        'Sessões': 'sum',
        'Pedidos': 'sum',
        'Pedidos Pagos': 'sum',
        'Receita Paga': 'sum'
    }).reset_index()
    
    # Calcula métricas adicionais
    df_origem['Tx Conversão'] = (df_origem['Pedidos'] / df_origem['Sessões'] * 100).round(2)
    df_origem['% Receita'] = (df_origem['Receita Paga'] / df_origem['Receita Paga'].sum() * 100).round(2)
    df_origem['Ticket Médio'] = (df_origem['Receita Paga'] / df_origem['Pedidos Pagos']).round(2)
    
    # Formata as colunas numéricas
    df_origem['Receita Paga'] = df_origem['Receita Paga'].apply(format_currency)
    df_origem['Ticket Médio'] = df_origem['Ticket Médio'].apply(format_currency)
    df_origem['Tx Conversão'] = df_origem['Tx Conversão'].astype(str) + '%'
    df_origem['% Receita'] = df_origem['% Receita'].astype(str) + '%'
    
    # Ordena pelo número de pedidos
    df_origem = df_origem.sort_values('Pedidos', ascending=False)
    
    # Insights sobre as origens
    melhor_origem = df_origem.iloc[0]
    st.success(f"""
    🏆 **Principal origem do dia:** {melhor_origem['Cluster']} - {melhor_origem['Origem']}/{melhor_origem['Mídia']}
    - Sessões: {melhor_origem['Sessões']}
    - Pedidos: {melhor_origem['Pedidos']} ({melhor_origem['Tx Conversão']} de conversão)
    - Receita: {melhor_origem['Receita Paga']} ({melhor_origem['% Receita']} do total)
    """)
    
    # Alerta para origens com baixa conversão
    baixa_conv = df_origem[
        (df_origem['Sessões'] >= 100) & 
        (df_origem['Tx Conversão'].str.rstrip('%').astype(float) < 0.5)
    ]
    if not baixa_conv.empty:
        st.warning(f"""
        ⚠️ **Origens com baixa conversão (>100 sessões e <0.5%):**
        """ + "\n".join([
            f"- {row['Cluster']} - {row['Origem']}/{row['Mídia']}: {row['Tx Conversão']} ({row['Sessões']} sessões)"
            for _, row in baixa_conv.iterrows()
        ]))
    
    # Adiciona espaço antes da tabela
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Exibe a tabela
    st.subheader("Detalhamento por Origem")
    st.dataframe(df_origem, hide_index=True, use_container_width=True) 