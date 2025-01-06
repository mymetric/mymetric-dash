import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from helpers.components import big_number_box
import calendar

def display_tab_today(df, df_ads, username, meta_receita):
    st.header("Análise do Dia")
    
    # Calcular métricas totais
    sessoes = df["Sessões"].sum()
    pedidos = df["Pedidos"].sum()
    pedidos_pagos = df["Pedidos Pagos"].sum()
    total_receita_paga = df["Receita Paga"].sum()
    
    # Pegar hora atual
    hora_atual = datetime.now().hour
    
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
    projecao_receita = total_receita_paga + (media_receita_hora * horas_restantes)
    projecao_pedidos = pedidos + (media_pedidos_hora * horas_restantes)
    projecao_sessoes = sessoes + (media_sessoes_hora * horas_restantes)
    
    # Big Numbers com projeções
    col1, col2, col3 = st.columns(3)
    
    with col1:
        big_number_box(
            f"R$ {projecao_receita:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Projeção de Receita",
            hint=f"Projeção baseada na média de R$ {media_receita_hora:,.2f} por hora. Faltam {horas_restantes}h para o fim do dia."
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
            df_hora_display[col] = df_hora_display[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
        
        # Adicionar % do total
        df_hora_display['% do Total'] = (df_hora['Receita Paga'] / df_hora['Receita Paga'].sum() * 100).round(2).astype(str) + '%'
        
        # Ordenar e exibir
        df_hora_display = df_hora_display.sort_values('Hora', ascending=True)
        st.dataframe(df_hora_display, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Insights")
        # Melhor hora
        melhor_hora = df_hora.loc[df_hora['Receita Paga'].idxmax()]
        st.success(f"🌟 Melhor hora do dia: {int(melhor_hora['Hora'])}h com R$ {melhor_hora['Receita Paga']:,.2f} em receita e {int(melhor_hora['Pedidos'])} pedidos")
        
        # Média por hora
        st.info(f"📊 Média por hora até agora: R$ {media_receita_hora:,.2f} em receita e {media_pedidos_hora:.1f} pedidos")
        
        # Ritmo necessário
        if meta_receita > 0:
            # Pega o último dia do mês atual
            _, ultimo_dia = calendar.monthrange(datetime.now().year, datetime.now().month)
            # Calcula a meta diária
            meta_diaria = meta_receita / ultimo_dia
            # Calcula o ritmo necessário por hora para o resto do dia
            ritmo_hora = (meta_diaria - total_receita_paga) / horas_restantes if horas_restantes > 0 else 0
            
            st.warning(f"""
            🎯 **Metas e Ritmos:**
            - Meta diária: R$ {meta_diaria:,.2f}
            - Faturado hoje: R$ {total_receita_paga:,.2f}
            - Falta hoje: R$ {(meta_diaria - total_receita_paga):,.2f}
            - Ritmo necessário: R$ {ritmo_hora:,.2f}/hora para as próximas {horas_restantes}h
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
    df_origem['Receita Paga'] = df_origem['Receita Paga'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
    df_origem['Ticket Médio'] = df_origem['Ticket Médio'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "*").replace(".", ",").replace("*", "."))
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