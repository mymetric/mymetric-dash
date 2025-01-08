import streamlit as st
import pandas as pd
import altair as alt
from helpers.components import section_title


def display_conversion_heatmap(df):
    section_title("Mapa de Calor de Taxa de Conversão")
    st.write("Visualize a taxa de conversão por hora do dia e dia da semana")
    
    # Adiciona filtro de mínimo de sessões
    min_sessions = st.number_input(
        "Mínimo de sessões a considerar",
        min_value=1,
        max_value=1000,
        value=50,
        help="Apenas horários com número de sessões maior ou igual a este valor serão considerados"
    )
    
    # Adiciona coluna de dia da semana
    conv_rate = df.copy()
    conv_rate['Dia da Semana'] = pd.to_datetime(conv_rate['Data']).dt.day_name()
    
    # Agrupa por dia da semana e hora
    conv_rate = conv_rate.groupby(['Dia da Semana', 'Hora']).agg({
        'Sessões': 'sum',
        'Pedidos': 'sum'
    }).reset_index()
    
    # Filtra por mínimo de sessões
    conv_rate = conv_rate[conv_rate['Sessões'] >= min_sessions]
    
    # Calcula taxa de conversão
    conv_rate['Taxa de Conversão'] = (conv_rate['Pedidos'] / conv_rate['Sessões'] * 100).round(2)
    
    # Formata a hora para exibição (00:00 - 23:00)
    conv_rate['Hora_Formatada'] = conv_rate['Hora'].apply(lambda x: f"{x:02d}:00")
    
    # Reordena os dias da semana em português
    dias_ordem = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    conv_rate['Dia da Semana'] = conv_rate['Dia da Semana'].map(dias_ordem)
    
    if not conv_rate.empty:
        # Cria o heatmap usando Altair com um design mais limpo
        heatmap = alt.Chart(conv_rate).mark_rect(
            height=18  # Aumenta a altura de cada célula
        ).encode(
            x=alt.X('Dia da Semana:N', 
                    title=None,  # Remove título do eixo X
                    sort=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']),
            y=alt.Y('Hora_Formatada:O', 
                    title='Hora do Dia',  # Adiciona título do eixo Y
                    sort=list(f"{h:02d}:00" for h in range(24)),
                    bandPosition=0.5),  # Centraliza o texto
            color=alt.Color('Taxa de Conversão:Q',
                           scale=alt.Scale(scheme='greens'),  # Usa tons de verde
                           legend=alt.Legend(
                               orient='right',
                               title='Taxa de Conversão (%)',
                               gradientLength=300
                           )),
            tooltip=[
                alt.Tooltip('Dia da Semana:N', title='Dia'),
                alt.Tooltip('Hora_Formatada:O', title='Hora'),
                alt.Tooltip('Taxa de Conversão:Q', title='Taxa de Conversão', format='.2f'),
                alt.Tooltip('Sessões:Q', title='Sessões', format=','),
                alt.Tooltip('Pedidos:Q', title='Pedidos', format=',')
            ]
        ).properties(
            width=650,
            height=600,  # Aumenta a altura total do gráfico
            title=alt.TitleParams(
                text='Taxa de Conversão por Hora do Dia e Dia da Semana',
                fontSize=16,
                anchor='middle'
            )
        ).configure_view(
            strokeWidth=0,  # Remove borda
        ).configure_axis(
            labelFontSize=11,
            grid=False,  # Remove grid
            domain=False,  # Remove linhas dos eixos
            labelPadding=8  # Aumenta o espaço entre os rótulos e as células
        ).configure_legend(
            labelFontSize=11,
            titleFontSize=12,
            padding=10
        )

        # Adiciona espaço em branco para melhor alinhamento
        st.write("")
        
        # Exibe o heatmap
        st.altair_chart(heatmap, use_container_width=True)
        
        # Adiciona explicação
        st.markdown("""
            <div style="font-size: 0.9em; color: #666; margin-top: 10px;">
                * As linhas mostram as horas do dia (00:00 até 23:00).<br>
                * As colunas representam os dias da semana.<br>
                * As células são coloridas em tons de verde de acordo com a taxa de conversão.<br>
                * Células em branco indicam horários sem dados suficientes (abaixo do mínimo de sessões).<br>
                * Os valores mostram a taxa de conversão (Pedidos/Sessões) em porcentagem.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Não há dados suficientes para exibir o mapa de calor com o mínimo de sessões selecionado.") 