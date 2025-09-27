import streamlit as st
import pandas as pd
from agent import process_query
import plotly.express as px

st.set_page_config(page_title="Agente CSV", layout="wide")
st.title("🧠 Assistente de Análise de Dados CSV")

if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("📂 Faça upload do seu arquivo CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Visualização dos dados")
    st.dataframe(df)

    query = st.text_input("💬 Pergunte algo sobre os dados:")
    if query:
        response = process_query(query, df)
        st.session_state.history.append((query, response))

    st.subheader("📜 Histórico")
    for q, r in st.session_state.history[::-1]:
        st.markdown(f"**Você:** {q}")
        st.markdown(r)
