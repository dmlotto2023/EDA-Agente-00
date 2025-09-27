import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def build_prompt(user_query, df):
    rules = open("prompt.txt", encoding="utf-8").read()
    preview = df.head(3).to_markdown()
    return f"""{rules}

Aqui estão os primeiros registros do DataFrame:
{preview}

Pergunta: {user_query}
"""

def process_query(query, df):
    prompt = build_prompt(query, df)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
