import streamlit as st
from helpers.components import atribuir_cluster, run_query
from filters import date_filters, traffic_filters


def display_tab_gringa_product_submited(client, start_date, end_date, cluster_selected=None, origem_selected=None, midia_selected=None, campanha_selected=None, conteudo_selected=None, pagina_de_entrada_selected=None, cupom_selected=None):

    def execute_query(query):
        return run_query(client, query)

    st.header("Cadastro de Produtos")
    st.write("Cadastros realizados no site para venda de produtos.")

    query = f"""
        with

        prep as (

        select

        a.*,
        b.product_submited

        from `mymetric-hub-shopify.dbt_join.gringa_sessions_gclids` a

        left join `mymetric-hub-shopify.dbt_granular.gringa_product_submited` b on a.user_pseudo_id = b.user_pseudo_id and a.ga_session_id = b.ga_session_id

        where
            a.event_date BETWEEN '{start_date}' AND '{end_date}'

        )

        select

        event_date `Data`,
        source `Origem`,
        medium `Mídia`,
        campaign `Campanha`,
        content `Conteúdo`,
        page_location `Página de Entrada`,
        count(*) `Sessões`,
        sum(product_submited) `Cadastros`

        from prep

        group by all

        order by Cadastros desc

    """

    df = execute_query(query)
    
    df['Cluster'] = df.apply(atribuir_cluster, axis=1)
    df = traffic_filters(df, cluster_selected, origem_selected, midia_selected, campanha_selected, conteudo_selected, pagina_de_entrada_selected)

    aggregated_df = df.groupby(['Data']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.line_chart(aggregated_df, x = "Data", y = "Cadastros")

    st.header("Cluster")

    aggregated_df = df.groupby(['Cluster']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)

    st.header("Campanha")

    aggregated_df = df.groupby(['Campanha']).agg({'Sessões': 'sum', 'Cadastros': 'sum'}).reset_index().sort_values(by='Cadastros', ascending=False)
    st.data_editor(aggregated_df, hide_index=1, use_container_width=1)
