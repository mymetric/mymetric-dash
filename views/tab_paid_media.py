import streamlit as st
from modules.load_data import load_paid_media
import altair as alt
from modules.components import big_number_box
from datetime import datetime

def display_tab_paid_media():
    st.title("💰 Mídia Paga")
    st.markdown("""---""")


    df_ads = load_paid_media()

    # Unique options for dropdown filters
    platform_options = ["All"] + sorted(df_ads['Plataforma'].dropna().unique().tolist())
    campaign_options = ["All"] + sorted(df_ads['Campanha'].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_platform = st.selectbox("Plataforma:", platform_options)

    with col2:
        campaign_filter = st.text_input("Campanha:", "")

    if selected_platform != "All":
        df_ads = df_ads[df_ads['Plataforma'] == selected_platform]

    if campaign_filter:
        df_ads = df_ads[df_ads['Campanha'].str.contains(campaign_filter, case=False, na=False)]

    df_grouped = df_ads.groupby('Data').agg({'Receita': 'sum', 'Investimento': 'sum'}).reset_index()

    # Cria o gráfico de Receita com a cor #D1B1C8 (roxo)
    line_receita = alt.Chart(df_grouped).mark_line(color='#D1B1C8', strokeWidth=3).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Receita:Q', axis=alt.Axis(title='Receita')),
        tooltip=['Data', 'Receita']
    )

    # Cria o gráfico de Investimento com a cor #C5EBC3 (verde)
    bar_investimento = alt.Chart(df_grouped).mark_bar(color='#C5EBC3', size=25).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Investimento:Q', axis=alt.Axis(title='Investimento')),
        tooltip=['Data', 'Investimento']
    )

    # Adiciona interatividade de zoom e pan
    zoom_pan = alt.selection_interval(bind='scales')

    # Combine os dois gráficos (linha e barras) com dois eixos Y e interatividade
    combined_chart = alt.layer(
        bar_investimento,
        line_receita
    ).resolve_scale(
        y='independent'  # Escalas independentes para as duas métricas
    ).add_selection(
        zoom_pan  # Adiciona a interação de zoom e pan
    ).properties(
        width=700,
        height=400,
        title=alt.TitleParams(
            text='Investimento e Receita por Data',
            fontSize=18,
            anchor='middle'
        )
    ).configure_axis(
        grid=False,  # Adiciona grades discretas
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        strokeWidth=0  # Remove a borda ao redor do gráfico
    )

    # Exibe o gráfico no Streamlit
    st.altair_chart(combined_chart, use_container_width=True)

    # Adiciona legenda manual com HTML/CSS abaixo do gráfico
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: -20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 3px; background-color: #D1B1C8;"></div>
                <span>Receita</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 15px; background-color: #C5EBC3;"></div>
                <span>Investimento</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Group by platform and campaign, aggregating relevant metrics
    df_ads_agg = df_ads.groupby(['Plataforma', 'Campanha']).agg({
        'Investimento': 'sum',
        'Impressões': 'sum',
        'Cliques': 'sum',
        'Transações': 'sum',
        'Receita': 'sum'
    }).reset_index()

    # Calculate ROAS and CPV, adding them as new columns
    df_ads_agg['ROAS'] = (df_ads_agg['Receita'] / df_ads_agg['Investimento'])
    df_ads_agg['CPV'] = (df_ads_agg['Investimento'] / df_ads_agg['Transações'].replace(0, float('nan'))).round(2)

    # Round other numerical columns to 2 decimal places
    df_ads_agg[['Investimento', 'Impressões', 'Cliques', 'Transações', 'Receita']] = df_ads_agg[['Investimento', 'Impressões', 'Cliques', 'Transações', 'Receita']].round(2)

    # Order by revenue in descending order
    df_ads_agg = df_ads_agg.sort_values(by='Receita', ascending=False).reset_index(drop=True)

    # Calcular métricas adicionais
    total_impressoes = df_ads_agg['Impressões'].sum()
    total_cliques = df_ads_agg['Cliques'].sum()
    total_transacoes = df_ads_agg['Transações'].sum()
    ctr = (total_cliques / total_impressoes * 100) if total_impressoes > 0 else 0
    taxa_conversao = (total_transacoes / total_cliques * 100) if total_cliques > 0 else 0
    cpc = df_ads_agg['Investimento'].sum() / total_cliques if total_cliques > 0 else 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        big_number_box(
            f"R$ {df_ads_agg['Investimento'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Investimento",
            hint="Total investido em mídia paga no período selecionado (Google Ads + Meta Ads)"
        )
    
    with col2:
        big_number_box(
            f"R$ {df_ads_agg['Receita'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "Receita",
            hint="Receita total gerada por mídia paga no período selecionado"
        )
    
    with col3:
        big_number_box(
            f"{df_ads_agg['Receita'].sum()/df_ads_agg['Investimento'].sum():,.2f}".replace(".", ","), 
            "ROAS",
            hint="Return On Ad Spend - Retorno sobre o investimento em anúncios (Receita/Investimento). Exemplo: ROAS 3 significa que para cada R$1 investido, retornou R$3 em vendas"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        big_number_box(
            f"{ctr:.2f}%".replace(".", ","),
            "CTR",
            hint="Click-Through Rate - Taxa de cliques por impressão (Cliques/Impressões). Quanto maior, melhor a relevância dos seus anúncios"
        )

    with col2:
        big_number_box(
            f"{taxa_conversao:.2f}%".replace(".", ","),
            "Taxa de Conversão",
            hint="Porcentagem de cliques que resultaram em vendas (Transações/Cliques)"
        )

    with col3:
        big_number_box(
            f"R$ {cpc:.2f}".replace(".", ","),
            "CPC",
            hint="Custo Por Clique - Valor médio pago por cada clique nos anúncios (Investimento/Cliques)"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        big_number_box(
            f"{total_impressoes:,.0f}".replace(",", "."),
            "Impressões",
            hint="Número total de vezes que seus anúncios foram exibidos"
        )

    with col2:
        big_number_box(
            f"{total_cliques:,.0f}".replace(",", "."),
            "Cliques",
            hint="Número total de cliques nos seus anúncios"
        )

    with col3:
        big_number_box(
            f"R$ {df_ads_agg['CPV'].mean():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."),
            "CPV Médio",
            hint="Custo Por Venda Médio - Média do valor gasto em anúncios para conseguir uma venda"
        )

    st.markdown("---")

    # Display the aggregated data in Streamlit data editor
    st.data_editor(df_ads_agg, hide_index=1, use_container_width=1)

    