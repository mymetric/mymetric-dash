import streamlit as st
import pandas as pd
from modules.load_data import load_current_month_revenue
from datetime import datetime
import calendar
import altair as alt
from modules.load_data import load_today_data
from views.partials.run_rate import load_table_metas
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

def create_progress_bar(current, target, color="#C5EBC3"):
    """Cria uma barra de progresso estilizada."""
    progress = min(100, (current / target * 100)) if target > 0 else 0
    return f"""
        <div style="margin: 10px 0;">
            <div style="
                width: 100%;
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 3px;
            ">
                <div style="
                    width: {progress}%;
                    height: 24px;
                    background-color: {color};
                    border-radius: 8px;
                    transition: width 500ms;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #31333F;
                    font-weight: bold;
                ">
                    {progress:.1f}%
                </div>
            </div>
            <div style="
                display: flex;
                justify-content: space-between;
                margin-top: 5px;
                color: #31333F;
                font-size: 14px;
            ">
                <span>Meta Diária: {format_currency(target)}</span>
                <span>Faturado Hoje: {format_currency(current)}</span>
            </div>
        </div>
    """

def display_tab_today():
    st.title("📊 Análise do Dia")
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

    # Calcula a meta diária e informações relacionadas
    meta_diaria, valor_faltante, dias_restantes = calculate_daily_goal(meta_receita, total_receita_mes)
    
    # Exibe informações sobre a meta no topo
    if meta_receita > 0:
        st.markdown(f"""
        <div style='background-color: #F0F2F6; padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='margin-top: 0; color: #31333F;'>🎯 Meta Diária</h3>
            <p style='margin: 5px 0; color: #31333F;'>
                Para bater a meta do mês de {format_currency(meta_receita)}, você precisa faturar {format_currency(meta_diaria)} por dia nos próximos {dias_restantes} dias
            </p>
            {create_progress_bar(total_receita_dia, meta_diaria)}
        </div>
        """, unsafe_allow_html=True)
    
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
    bar_hora = alt.Chart(df_hora).mark_bar(color='#C5EBC3').encode(
        x=alt.X('Hora:O', title='Hora do Dia'),
        y=alt.Y('Receita Paga:Q', title='Receita'),
        tooltip=['Hora', 'Receita Paga', 'Pedidos', 'Sessões']
    )
    
    # Criar linha para receita acumulada
    line_acumulado = alt.Chart(df_hora).mark_line(color='#D1B1C8', strokeWidth=3).encode(
        x=alt.X('Hora:O'),
        y=alt.Y('Receita Acumulada:Q', title='Receita Acumulada'),
        tooltip=['Hora', 'Receita Acumulada']
    )
    
    # Combinar os gráficos
    combined_hora = alt.layer(
        bar_hora, line_acumulado
    ).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Receita por Hora vs Receita Acumulada',
            fontSize=18,
            anchor='middle'
        )
    )
    
    # Exibir o gráfico
    st.altair_chart(combined_hora, use_container_width=True)
    
    # Adicionar legenda
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 15px; background-color: #C5EBC3;"></div>
                <span>Receita por Hora</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 3px; background-color: #D1B1C8;"></div>
                <span>Receita Acumulada</span>
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