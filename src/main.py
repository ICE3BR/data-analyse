import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa módulos personalizados
from config import get_ai_config
from database import get_database_connection
from data_processors.excel_processor import process_excel
from data_processors.xml_processor import process_xml
from data_processors.sql_processor import process_sql
from data_processors.csv_processor import process_csv
from ai_providers import get_ai_provider
from langchain_analyzer import DataFrameAnalyzer  # Importa nosso novo analisador

# Configuração da página
st.set_page_config(
    page_title="Análise de Dados com LangChain",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Análise de Dados com LangChain")

# Barra lateral para configuração
st.sidebar.title("Configurações")

# Seleção do provedor de IA
ai_provider_type = st.sidebar.radio(
    "Selecione o Tipo de IA",
    options=["API", "Local"],
    index=0
)

# Obtém o provedor de IA com base na seleção
if ai_provider_type == "API":
    ai_provider = get_ai_provider("api")
    st.sidebar.info("Usando IA baseada em API (configurada no código)")
    
    # Exibe qual API está sendo usada (para informação do desenvolvedor)
    api_type = os.getenv("API_TYPE", "openai")
    st.sidebar.text(f"API Atual: {api_type}")
    
else:
    ai_provider = get_ai_provider("local")
    st.sidebar.info("Usando IA Local (Ollama)")
    
    # Exibe qual modelo está sendo usado
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    st.sidebar.text(f"Modelo Atual: {model_name}")

# Seleção da fonte de dados
data_source = st.sidebar.selectbox(
    "Selecione a Fonte de Dados",
    options=["Arquivo CSV", "Arquivo Excel", "Documento XML", "Banco de Dados MySQL"]
)

# Seleção do formato de saída (novo recurso)
output_format = st.sidebar.selectbox(
    "Formato de Saída",
    options=["Texto", "JSON", "Markdown"],
    index=0
)

# Opção para personalizar o System Prompt
with st.sidebar.expander("Configurações Avançadas"):
    use_custom_prompt = st.checkbox("Usar System Prompt personalizado")
    
    if use_custom_prompt:
        from prompts.system_prompts import get_system_prompt
        default_prompt = get_system_prompt(output_format.lower())
        
        custom_prompt = st.text_area(
            "System Prompt Personalizado",
            value=default_prompt,
            height=300
        )
    else:
        custom_prompt = None

# Área de conteúdo principal
st.header("Análise de Dados")

# Trata diferentes fontes de dados
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
    # Formulário de conexão com o banco de dados
    with st.expander("Conexão com o Banco de Dados"):
        st.info("Os detalhes da conexão podem ser configurados no arquivo .env ou inseridos aqui")
        
        # Usa variáveis de ambiente como padrões
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
        
        # Entrada de consulta SQL
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

# Exibe os dados se disponíveis
if df is not None:
    st.subheader("Visualização dos Dados")
    st.dataframe(df.head())
    
    # Análise com LangChain (substituindo PandasAI)
    st.subheader("Faça Perguntas Sobre Seus Dados")
    user_query = st.text_area("Digite sua pergunta", height=100, 
                            placeholder="Exemplo: Qual é a média da coluna X? Mostre um gráfico de Y ao longo do tempo.")
    
    if st.button("Analisar"):
        if user_query.strip():
            with st.spinner("Analisando dados..."):
                try:
                    # Inicializa nosso DataFrameAnalyzer com o provedor de IA selecionado
                    analyzer = DataFrameAnalyzer(ai_provider, output_format.lower())
                    analyzer.load_dataframe(df)
                    
                    # Aplica system prompt personalizado se fornecido
                    if use_custom_prompt and custom_prompt:
                        analyzer.system_prompt = custom_prompt
                    
                    # Processa com base no formato de saída selecionado
                    if output_format == "JSON":
                        response = analyzer.to_json(user_query)
                        st.json(response)
                    elif output_format == "Markdown":
                        response = analyzer.to_markdown(user_query)
                        st.markdown(response)
                    else:  # Formato de texto padrão
                        response = analyzer.chat(user_query)
                        
                        # Trata diferentes tipos de resposta
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

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info(
    "Esta aplicação usa LangChain para analisar dados de várias fontes. "
    "Configure o provedor de IA, a fonte de dados e o formato de saída para começar."
)