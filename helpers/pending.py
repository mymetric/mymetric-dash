import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

def check_pending_items(username, meta_receita, tx_cookies, df_ads):
    """Verifica e retorna lista de pendências com base nos dados."""
    pendencias = []
    
    # Verificar meta do mês
    if meta_receita == 0:
        pendencias.append({
            'titulo': 'Cadastrar Meta do Mês',
            'descricao': 'A meta de receita do mês não está cadastrada. Isso é importante para acompanhar seu desempenho.',
            'acao': 'Acesse a aba Configurações para cadastrar sua meta mensal.',
            'severidade': 'alta'
        })
    
    # Verificar taxa de perda de cookies
    if tx_cookies > 10:
        pendencias.append({
            'titulo': 'Ajustar Taxa de Perda de Cookies',
            'descricao': f'A taxa de perda de cookies está em {tx_cookies:.1f}%. O ideal é manter abaixo de 10%.',
            'acao': 'Verifique a implementação do código de rastreamento e possíveis bloqueadores.',
            'severidade': 'media' if tx_cookies <= 30 else 'alta'
        })
    
    # Verificar tagueamento do Meta Ads
    if not df_ads.empty:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        
        qa = f"""
            select
                sum(case when page_params like "%mm_ads%" then 1 else 0 end) / count(*) `Cobertura`
            from `mymetric-hub-shopify.dbt_join.{username}_sessions_gclids`
            where
                event_date >= date_sub(current_date("America/Sao_Paulo"), interval 7 day)
                and page_params like "%fbclid%"
                and medium not like "%social%"
        """
        
        df_qa = client.query(qa).to_dataframe()
        if not df_qa.empty:
            cobertura = float(df_qa['Cobertura'].iloc[0]) * 100
            if cobertura < 80:
                pendencias.append({
                    'titulo': 'Ajustar Taxa de Tagueamento Meta Ads',
                    'descricao': f'A cobertura do parâmetro mm_ads está em {cobertura:.1f}%. O ideal é manter acima de 80%.',
                    'acao': f'Verifique a implementação do parâmetro mm_ads no Meta Ads. <a href="https://mymetric.notion.site/Parametriza-o-de-Meta-Ads-a32df743c4e046ccade33720f0faec3a" target="_blank" style="color: #0366d6; text-decoration: none;">Saiba como implementar corretamente</a>',
                    'severidade': 'media'
                })
    
    return pendencias

def display_pending_items(pendencias):
    """Exibe as pendências na interface."""
    if pendencias:
        st.markdown("""
            <style>
                .pendencia-alta { border-left: 4px solid #dc3545 !important; }
                .pendencia-media { border-left: 4px solid #ffc107 !important; }
                .pendencia-baixa { border-left: 4px solid #17a2b8 !important; }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-bottom: 25px;">
                <h3 style="color: #31333F; margin-bottom: 15px;">⚠️ Pendências</h3>
        """, unsafe_allow_html=True)
        
        for p in pendencias:
            st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    border: 1px solid #eee;
                    border-left: 4px solid #dc3545;
                " class="pendencia-{p['severidade']}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #31333F;">{p['titulo']}</strong>
                        <span style="
                            background-color: {'#dc3545' if p['severidade'] == 'alta' else '#ffc107' if p['severidade'] == 'media' else '#17a2b8'};
                            color: white;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 0.8em;
                        ">
                            {p['severidade'].upper()}
                        </span>
                    </div>
                    <p style="margin: 8px 0; color: #666;">{p['descricao']}</p>
                    <p style="margin: 0; color: #31333F; font-size: 0.9em;">
                        <strong>Ação necessária:</strong> {p['acao']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) 