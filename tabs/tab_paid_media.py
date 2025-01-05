import streamlit as st
import pandas as pd
from helpers.components import send_discord_message, run_query, big_number_box
from helpers.config import load_table_metas
from datetime import datetime

def execute_query(client, query):
    return run_query(client, query)

import altair as alt

def display_tab_paid_media(client, table, df_ads, username):

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


    col1, col2, col3, col4 = st.columns(4)
        
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

    with col4:
        big_number_box(
            f"R$ {df_ads_agg['CPV'].sum():,.2f}".replace(",", "*").replace(".", ",").replace("*", "."), 
            "CPV",
            hint="Custo Por Venda - Valor médio gasto em anúncios para conseguir uma venda (Investimento/Transações)"
        )

    st.markdown("---")

    # Display the aggregated data in Streamlit data editor
    st.data_editor(df_ads_agg, hide_index=1, use_container_width=1)

    qa = f"""
        select

            sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`

        from `mymetric-hub-shopify.dbt_join.{table}_sessions_gclids`

        where

        event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
        and page_params like "%fbclid%"
    """

    qa = execute_query(client, qa)
    lost = qa['Cobertura'].sum()*100
    if lost < 80:
        st.warning(f"Atenção: A taxa de tagueamento de Meta Ads é de {lost:.2f}%, o que está abaixo do limite aceitável que é de 80%. [Saiba como implementar corretamente](https://mymetric.notion.site/Parametriza-o-de-Meta-Ads-a32df743c4e046ccade33720f0faec3a).", icon="⚠️")
        send_discord_message(f"Usuário **{username}** com taxa de tagueamento de Meta Ads abaixo do esperado: {lost:.2f}%.")
    else:
        st.write(f"A taxa de tagueamento de Meta Ads é de {lost:.2f}%, o que está dentro do limite aceitável.")

    with st.expander("Ver mais detalhes"):
        qa = f"""
            select

                source `Origem`,
                medium `Mídia`,
                campaign `Campanha`,
                count(*) `Sessões`

            from `mymetric-hub-shopify.dbt_join.{table}_sessions_gclids`

            where

            event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
            and page_params like "%fbclid%"
            and page_params not like "%mm_ads%"

            group by all

            order by `Sessões` desc

        """
        qa = execute_query(client, qa)
        st.write("As sessões a seguir vem de Meta Ads, porém, não estão no padrão de tagueamento.")
        st.data_editor(qa, hide_index=1, use_container_width=1)

    # Carregar as metas do usuário
    metas = load_table_metas(username)
    current_month = datetime.now().strftime("%Y-%m")
    meta_receita = float(metas.get('metas_mensais', {}).get(current_month, {}).get('meta_receita_paga', 0))
