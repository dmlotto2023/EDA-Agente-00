# 🧠 Agente EDA Interativo com Memória (Streamlit + Gemini Flash 2.5)

Este projeto é um **assistente de análise de dados CSV** que realiza **EDA (Exploração de Dados)** de forma interativa.  
Ele utiliza o **Gemini Flash 2.5** para interpretar perguntas em linguagem natural, gera e executa código Python sobre o DataFrame, e mantém **memória** das interações para gerar um relatório final consolidado.

---

## 🚀 Funcionalidades

- 📂 Upload de arquivos CSV diretamente no app  
- 💬 Perguntas em linguagem natural sobre os dados  
- 🧠 Respostas estruturadas no formato Thought / Action / Action Input  
- 🐍 Execução real do código Python sugerido pelo modelo  
- 📊 EDA interativo com gráficos (histogramas, boxplots, scatterplots)  
- 📝 Memória das interações para geração de relatório final em Markdown  

---

## 📦 Requisitos

- Python **3.9+**
- Conta no [Google AI Studio](https://aistudio.google.com/) para gerar a chave da API do Gemini

---

## ⚙️ Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/csv-agent.git
cd csv-agent
```

2. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto e adicione sua chave do Gemini:

```env
O Uso desse campo seria apenas para uma redundância, porque a página do agente 
já a solicita.
GEMINI_API_KEY=sua_chave_aqui
```

---

## ▶️ Execução no VS Code

1. Abra o projeto no **VS Code**  
2. Certifique-se de que o ambiente virtual está ativado no terminal integrado  
3. Rode o app com:

```bash
python -m streamlit run app.py
```

4. O navegador abrirá automaticamente em:  
👉 [http://localhost:8501](http://localhost:8501)

---

## 🧭 Como usar

1. Insira sua API Key no primeiro campo da página
2. Faça upload de um arquivo CSV  
3. Gere a Análise inicial. Ela tem como principal objetivo gerar uma análise padronizada
para auxiliar nas respostas, trazendo maior estabilidade.
4. Você tem a opção de mostrar ou não essa análise, mas dependendo do tamanho do dataset
pode não ser vantajoso mostrá-la porque pode sobrecarregar a tela.
2. Digite uma pergunta em linguagem natural (ex.: *"Quais são as colunas disponíveis?"*)  
3. O agente irá:
   - Gerar um raciocínio (Thought)  
   - Definir a ação (Action)  
   - Criar o código Python (Action Input)  
   - Executar o código e mostrar o resultado  
4. Todas as interações ficam salvas no histórico  
5. Ao final, clique em **📥 Gerar Relatório Final** para baixar um resumo em Markdown  

---

## 📊 EDA Interativo

Além do chat, você pode explorar manualmente os dados:
- Selecionar colunas
- Gerar histogramas para variáveis numéricas
- Gerar gráficos de barras para variáveis categóricas
- Identificar outliers

---

## 📘 Estrutura do Projeto

```
csv-agent/
├── app.py              # Interface Streamlit
├── agent.py            # Lógica do agente (Gemini + execução de código)
├── prompt.txt          # Regras e formato do agente
├── requirements.txt    # Dependências
├── .env                # Chave da API do Gemini (não versionar)
└── README.md           # Este guia
```

---

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) → Interface web interativa  
- [Pandas](https://pandas.pydata.org/) → Manipulação de dados  
- [Plotly](https://plotly.com/python/) → Visualizações interativas  
- [Google Generative AI](https://ai.google.dev/) → Gemini Flash 2.0  para interpretação de linguagem natural  

---

## ⚠️ Observações

- O arquivo `.env` **não deve ser versionado** (adicione ao `.gitignore`).  
- Cada execução de gráfico salva a imagem em arquivo (`grafico_n.png`) para evitar sobrescrita.  
- O relatório final é gerado em **Markdown** e pode ser aberto em qualquer editor.  

---

## 📄 Licença

Este projeto é de uso livre para fins de estudo e experimentação.  

---


