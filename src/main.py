import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from config import get_ai_config
from database import get_database_connection
from data_processors.excel_processor import process_excel
from data_processors.xml_processor import process_xml
from data_processors.sql_processor import process_sql
from data_processors.csv_processor import process_csv
from ai_providers import get_ai_provider

# Page configuration
st.set_page_config(
    page_title="Análise de Dados com PandasAI",
    page_icon="📊",
    layout="wide"
)

# Main title
st.title("📊 Análise de Dados com PandasAI")

# Sidebar for configuration
st.sidebar.title("Configurações")

# AI Provider selection
ai_provider_type = st.sidebar.radio(
    "Selecione o Tipo de IA",
    options=["API", "Local"],
    index=0
)

# Get AI provider based on selection
if ai_provider_type == "API":
    ai_provider = get_ai_provider("api")
    st.sidebar.info("Usando IA baseada em API (configurada no código)")
    
    # Display which API is being used (for developer information)
    api_type = os.getenv("API_TYPE", "openai")
    st.sidebar.text(f"API Atual: {api_type}")
    
else:
    ai_provider = get_ai_provider("local")
    st.sidebar.info("Usando IA Local (Ollama)")
    
    # Display which model is being used
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    st.sidebar.text(f"Modelo Atual: {model_name}")

# Data source selection
data_source = st.sidebar.selectbox(
    "Selecione a Fonte de Dados",
    options=["Arquivo CSV", "Arquivo Excel", "Documento XML", "Banco de Dados MySQL"]
)

# Main content area
st.header("Análise de Dados")

# Handle different data sources
df = None
if data_source == "Arquivo CSV":
    uploaded_file = st.file_uploader("Carregar Arquivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = process_csv(uploaded_file)
        st.success("Arquivo CSV carregado com sucesso!")
        
elif data_source == "Arquivo Excel":
    uploaded_file = st.file_uploader("Carregar Arquivo Excel", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = process_excel(uploaded_file)
        st.success("Arquivo Excel carregado com sucesso!")
        
elif data_source == "Documento XML":
    uploaded_file = st.file_uploader("Carregar Documento XML", type=["xml"])
    if uploaded_file is not None:
        df = process_xml(uploaded_file)
        st.success("Documento XML carregado com sucesso!")
        
elif data_source == "Banco de Dados MySQL":
    # Database connection form
    with st.expander("Conexão com o Banco de Dados"):
        st.info("Os detalhes da conexão podem ser configurados no arquivo .env ou inseridos aqui")
        
        # Use environment variables as defaults
        default_host = os.getenv("DB_HOST", "localhost")
        default_user = os.getenv("DB_USER", "")
        default_password = os.getenv("DB_PASSWORD", "")
        default_database = os.getenv("DB_NAME", "")
        
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("Host", value=default_host)
            user = st.text_input("Usuário", value=default_user)
        with col2:
            password = st.text_input("Senha", value=default_password, type="password")
            database = st.text_input("Banco de Dados", value=default_database)
        
        # SQL query input
        sql_query = st.text_area("Consulta SQL", height=100)
        
        if st.button("Executar Consulta"):
            if sql_query.strip():
                try:
                    df = process_sql(host, user, password, database, sql_query)
                    st.success("Consulta executada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao executar consulta: {e}")
            else:
                st.warning("Por favor, insira uma consulta SQL")

# Display the data if available
if df is not None:
    st.subheader("Visualização dos Dados")
    st.dataframe(df.head())
    
    # PandasAI analysis
    st.subheader("Faça Perguntas Sobre Seus Dados")
    user_query = st.text_area("Digite sua pergunta", height=100, 
                            placeholder="Exemplo: Qual é a média da coluna X? Mostre um gráfico de Y ao longo do tempo.")
    
    if st.button("Analisar"):
        if user_query.strip():
            with st.spinner("Analisando dados..."):
                try:
                    # Configure PandasAI with the selected AI provider
                    from pandasai import SmartDataframe
                    smart_df = SmartDataframe(df, config={"llm": ai_provider})
                    
                    # Get the response
                    response = smart_df.chat(user_query)
                    
                    # Display the response
                    st.subheader("Resultado da Análise")
                    
                    # Handle different response types
                    if isinstance(response, pd.DataFrame):
                        st.dataframe(response)
                    elif isinstance(response, str) and response.endswith((".png", ".jpg", ".jpeg")):
                        st.image(response)
                    else:
                        st.write(response)
                        
                except Exception as e:
                    st.error(f"Erro durante a análise: {e}")
        else:
            st.warning("Por favor, digite uma pergunta para analisar os dados")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "Esta aplicação usa PandasAI para analisar dados de várias fontes. "
    "Configure o provedor de IA e a fonte de dados para começar."
)