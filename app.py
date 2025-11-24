import streamlit as st
import pandas as pd
#from agent import process_query, generate_structured_response
from agent import orquestrador, generate_structured_response
import plotly.express as px
from fpdf import FPDF
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#####################
# Campo para o usuário inserir a API Key
gemini_api_key = st.text_input("🔑 Insira sua Gemini API Key", type="password")

# Se o usuário forneceu a chave, armazenamos na sessão
if gemini_api_key:
    st.session_state["gemini_api_key"] = gemini_api_key
####################

def analise_inicial(df):
    resultados = []

    # 1. Descrição dos Dados
    tipos = df.dtypes.astype(str).to_dict()
    resultados.append({
        "query": "Descrição dos tipos de dados",
        "result": tipos,
        "explanation": "Identifiquei os tipos de dados de cada coluna do dataset."
    })

    desc = df.describe(include="all").transpose()
    resultados.append({
        "query": "Estatísticas descritivas",
        "result": desc,
        "explanation": "Resumo estatístico com média, mediana, mínimo, máximo e variabilidade."
    })

    # Distribuições (numéricas)
    for col in df.select_dtypes(include=["int64","float64"]).columns:
        fig = px.histogram(df, x=col, title=f"Distribuição da variável {col}")
        resultados.append({
            "query": f"Distribuição da variável {col}",
            "result": fig,
            "explanation": f"Histograma mostrando a distribuição da coluna {col}."
        })

    # 2. Identificação de Padrões e Tendências
    for col in df.select_dtypes(include=["object","category"]).columns:
        freq = df[col].value_counts().head(5)
        resultados.append({
            "query": f"Valores mais frequentes em {col}",
            "result": freq.to_dict(),
            "explanation": f"Mostrando os valores mais comuns da coluna {col}."
        })

    temporal_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    if not temporal_cols:
        temporal_cols = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()]
    if temporal_cols:
        col = temporal_cols[0]
        fig = px.line(df, x=col, y=df.select_dtypes(include=["int64","float64"]).columns[0],
                      title=f"Tendência temporal usando {col}")
        resultados.append({
            "query": "Tendências temporais",
            "result": fig,
            "explanation": f"Gráfico de linha mostrando a evolução da primeira variável numérica ao longo da coluna temporal '{col}'."
        })

    # 3. Detecção de Anomalias (Outliers)
    for col in df.select_dtypes(include=["int64","float64"]).columns:
        fig, ax = plt.subplots()
        sns.boxplot(x=df[col], ax=ax)
        resultados.append({
            "query": f"Outliers na variável {col}",
            "result": fig,
            "explanation": f"Boxplot mostrando possíveis outliers na coluna {col}."
        })

    # 4. Relações entre Variáveis
    corr = df.corr(numeric_only=True)
    fig_corr, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=False, cmap="coolwarm", ax=ax)
    resultados.append({
        "query": "Correlação entre variáveis numéricas",
        "result": fig_corr,
        "explanation": "Mapa de calor mostrando a correlação entre variáveis numéricas."
    })

    num_cols = df.select_dtypes(include=["int64","float64"]).columns
    if len(num_cols) >= 2:
        fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                         title=f"Relação entre {num_cols[0]} e {num_cols[1]}")
        resultados.append({
            "query": f"Relação entre {num_cols[0]} e {num_cols[1]}",
            "result": fig,
            "explanation": f"Gráfico de dispersão mostrando a relação entre {num_cols[0]} e {num_cols[1]}."
        })

    return resultados

HISTORY_FILE = "history.json"

def salvar_historico():
    """Salva o histórico em formato JSON serializável"""
    serializavel = []
    for item in st.session_state.history:
        serializavel.append({
            "query": str(item.get("query")),
            "result": str(item.get("result")),
            "explanation": str(item.get("explanation")),
            "code": str(item.get("code")) if item.get("code") else None,
            "thought_action": str(item.get("thought_action")) if item.get("thought_action") else None
        })
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(serializavel, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {e}")

def carregar_historico():
    """Carrega o histórico salvo, ignorando arquivos corrompidos"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("⚠️ O arquivo de histórico está corrompido ou inválido. Ele será ignorado.")
            return []
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
            return []
    return []

# Inicialização segura do histórico
if "history" not in st.session_state:
    st.session_state.history = carregar_historico()

if "report" not in st.session_state:
    st.session_state.report = []

# Botão para limpar histórico corrompido ou reiniciar
if st.button("🧹 Limpar histórico salvo"):
    if os.path.exists(HISTORY_FILE):
        try:
            os.remove(HISTORY_FILE)
            st.success("Arquivo de histórico removido com sucesso.")
        except Exception as e:
            st.error(f"Erro ao remover arquivo: {e}")
    st.session_state.history = []
    st.session_state.report = []



st.set_page_config(page_title="Agente Interativo EDA", layout="wide")
st.title("🧠 EDA Interativo com Memória")

# Inicializa memória
if "history" not in st.session_state:
    st.session_state.history = carregar_historico()

if "report" not in st.session_state:
    st.session_state.report = []

if "analise_inicial_feita" not in st.session_state:
    st.session_state.analise_inicial_feita = False

# Upload do CSV
uploaded_file = st.file_uploader("📂 Faça upload do seu arquivo CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Visualização dos dados")
    st.dataframe(df)

    # Inicialização de variáveis de sessão
if "analise_inicial_feita" not in st.session_state:
    st.session_state.analise_inicial_feita = False
if "analise_inicial_resultados" not in st.session_state:
    st.session_state.analise_inicial_resultados = []

# Botão para gerar análise inicial (sem mostrar)
if not st.session_state.analise_inicial_feita:
    if st.button("⚙️ Gerar análise inicial automática"):
        st.session_state.analise_inicial_resultados = analise_inicial(df)
        st.session_state.analise_inicial_feita = True
        st.success("Análise inicial gerada e armazenada com sucesso!")

# Botão para mostrar a análise inicial como relatório
if st.session_state.analise_inicial_feita:
    if st.button("📊 Mostrar análise inicial"):
        st.subheader("📊 Relatório da Análise Inicial")
        for r in st.session_state.analise_inicial_resultados:
            st.write(f"**{r['query']}**")
            # Limita tamanho dos gráficos
            if "plotly" in str(type(r['result'])):
                st.plotly_chart(r['result'], use_container_width=True)
            elif "matplotlib" in str(type(r['result'])):
                st.pyplot(r['result'])
            elif hasattr(r['result'], "to_string"):
                st.text(r['result'].to_string()[:1000])  # corta se for muito grande
            elif isinstance(r['result'], dict):
                st.json(r['result'])
            else:
                st.write(r['result'])
            st.caption(r['explanation'])

    # Pergunta do usuário
    query = st.text_input("💬 Pergunte algo sobre os dados:")
    if query:
        structured_response = orquestrador(query, df)

        st.session_state.history.append(structured_response)
        st.session_state.report.append(structured_response)
        salvar_historico()

    # Histórico
    st.subheader("📜 Histórico")

    if st.button("🗑️ Resetar Histórico"):
        st.session_state.history = []
        st.session_state.report = []
        if os.path.exists("history.json"):
            os.remove("history.json")
        st.success("Histórico resetado com sucesso!")

    for item in st.session_state.history[::-1]:
        st.markdown(f"**Você:** {item['query']}")
        st.write("**Resultado:**", item['result'])
        st.write("**Explicação:**", item['explanation'])

# EDA manual
st.subheader("🔍 EDA Interativo")

# Verifica se o dataset foi carregado
if "df" in locals() or "df" in globals():
    col = st.selectbox("Escolha uma coluna para explorar", df.columns)

    tipo_analise = st.selectbox(
        "Escolha o tipo de análise",
        ["Histograma", "Identificação de Padrões e Tendências", "Detecção de Anomalias (Outliers)", "Relações entre Variáveis"]
    )

    if tipo_analise == "Histograma":
        if df[col].dtype in ["int64", "float64"]:
            st.plotly_chart(px.histogram(df, x=col), use_container_width=True)
        else:
            st.bar_chart(df[col].value_counts())

    elif tipo_analise == "Identificação de Padrões e Tendências":
        if df[col].dtype in ["int64", "float64"]:
            st.line_chart(df[col])
        else:
            st.bar_chart(df[col].value_counts())

    elif tipo_analise == "Detecção de Anomalias (Outliers)":
        if df[col].dtype in ["int64", "float64"]:
            st.plotly_chart(px.box(df, y=col), use_container_width=True)
        else:
            st.warning("Outliers só podem ser analisados em colunas numéricas.")

    elif tipo_analise == "Relações entre Variáveis":
        outras_cols = [c for c in df.columns if c != col]
        outra = st.selectbox("Escolha outra coluna para relacionar", outras_cols)
        if df[col].dtype in ["int64", "float64"] and df[outra].dtype in ["int64", "float64"]:
            st.plotly_chart(px.scatter(df, x=col, y=outra), use_container_width=True)
        else:
            st.warning("Relações gráficas só podem ser exibidas entre colunas numéricas.")
else:
    st.info("📂 Carregue um dataset para habilitar a análise interativa.")

    # Relatório final em PDF
    if st.button("📥 Gerar Relatório Final (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Relatório de Análises - Agente EDA", ln=True, align="C")
        pdf.ln(10)

        for r in st.session_state.report:
            pdf.multi_cell(0, 10, f"Pergunta: {r['query']}")
            pdf.multi_cell(0, 10, f"Resultado: {r['result']}")
            pdf.multi_cell(0, 10, f"Explicação: {r['explanation']}")
            pdf.ln(5)

        pdf_output = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "⬇️ Baixar Relatório em PDF",
            data=pdf_output,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )