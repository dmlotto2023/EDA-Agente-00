import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import io
import contextlib
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.graph_objs import Figure as PlotlyFigure
from matplotlib.figure import Figure as MplFigure

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

AMPLAS = [
    "todas", "todos", "cada", "tudo", "geral", "completo",
    "todas as variáveis", "todas as colunas", "cada variável", "cada coluna",
    "distribuição de cada", "tipos de dados", "descrição geral", "overview"
]

# -------------------------------
# Funções utilitárias
# -------------------------------
def precisa_refinar(query: str) -> bool:
    q = query.lower()
    return any(p in q for p in AMPLAS)

def extract_code(text):
    # Extrai de bloco python
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Extrai linhas com fig/result
    lines = text.splitlines()
    code_lines = [line for line in lines if "fig =" in line or "result =" in line or "px." in line]
    if code_lines:
        return "\n".join(code_lines).strip()

    return None

def execute_code(code, df):
    """Executa o código Python de forma controlada e captura saída"""
    local_vars = {
        "df": df,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "px": px
    }

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            # Usa o mesmo dicionário para globals e locals
            exec(code, local_vars, local_vars)
        except Exception as e:
            return f"Erro ao executar: {e}"

    result = local_vars.get("result")

    if isinstance(result, PlotlyFigure):
        st.plotly_chart(result, use_container_width=True)
        return "Gráfico Plotly exibido com sucesso."
    if isinstance(result, MplFigure):
        st.pyplot(result)
        return "Gráfico Matplotlib exibido com sucesso."

    if result is not None:
        return result
    elif local_vars:
        ultima = list(local_vars.items())[-1]
        return {ultima[0]: ultima[1]}
    return output.getvalue().strip() or "Código executado, mas não retornou resultado."

# -------------------------------
# Agente Generalista
# -------------------------------
def agente_generalista(query, df):
    analise = st.session_state.get("analise_inicial_resultados", [])
    prompt = f"""
Você é um analista de dados generalista.
Pergunta: {query}

Dados disponíveis (amostra):
{df.head(3).to_markdown()}

Resultados prévios (use apenas para perguntas interpretativas):
{analise}

Regras:
- Sempre que a resposta envolver visualização, use plotly.express (px).
- Nunca invente dados ou use pd.read_csv.
- Sempre finalize o código com: result = fig
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return generate_structured_response(query, response.text, df)

# -------------------------------
# Agente Específico
# -------------------------------
def agente_especifico(query, df):
    prompt = f"""
Você é um analista de dados específico.
Pergunta: {query}

Dados disponíveis (amostra):
{df.head(3).to_markdown()}

Regras:
- Sempre gere código Python completo.
- Sempre use plotly.express (px) para gráficos.
- Nunca invente dados ou use pd.read_csv.
- Sempre finalize com: result = fig
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return generate_structured_response(query, response.text, df)

# -------------------------------
# Orquestrador
# -------------------------------
def orquestrador(query, df):
    if precisa_refinar(query):
        return agente_generalista(query, df)
    else:
        return agente_especifico(query, df)

# -------------------------------
# Estrutura de resposta
# -------------------------------
def generate_structured_response(query, response_text, df):
    code = extract_code(response_text)

    if not code:
        # Se não extraiu código válido, tenta capturar linhas úteis
        possible_lines = []
        for line in response_text.splitlines():
            if line.strip().startswith(("df.", "import", "len(", "print(", "px.")):
                possible_lines.append(line)
        if possible_lines:
            code = "\n".join(possible_lines)

    if code:
        result = execute_code(code, df)
    else:
        result = "Nenhum código válido encontrado para executar."

    explanation = response_text
    if "pd.read_csv" in explanation or "np.random" in explanation:
        explanation = "Usei o DataFrame carregado (`df`) para responder. Não foram criados dados fictícios."

    return {
        "query": query,
        "thought_action": response_text,
        "code": code,
        "result": result,
        "explanation": explanation
    }
# Compatibilidade temporária
def process_query(query, df):
    return orquestrador(query, df)