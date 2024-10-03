import pandas as pd
import streamlit as st

@st.cache_data(ttl=600)
def run_query(_client, query):
    query_job = _client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)
