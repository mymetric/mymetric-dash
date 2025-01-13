import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from .components import run_query

def execute_queries(client, queries):
    def execute_query(query):
        try:
            return run_query(client, query)
        except Exception as e:
            st.error(f"Erro ao executar a query: {e}")
            return pd.DataFrame()

    with ThreadPoolExecutor() as executor:
        futures = {key: executor.submit(execute_query, query) for key, query in queries.items()}
        results = {key: future.result() for key, future in futures.items()}

    return results 