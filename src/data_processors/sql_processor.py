import pandas as pd
from sqlalchemy.engine import Connection
from database import get_database_connection, get_sqlalchemy_engine

def process_sql(host, user, password, database, query):
    """
    Processa uma consulta SQL e retorna um DataFrame pandas.
    
    Args:
        host (str): Host do banco de dados
        user (str): Usuário do banco de dados
        password (str): Senha do banco de dados
        database (str): Nome do banco de dados
        query (str): Consulta SQL a ser executada
        
    Returns:
        pandas.DataFrame: DataFrame contendo os resultados da consulta
    """
    try:
        # Cria o motor SQLAlchemy
        engine = get_sqlalchemy_engine(host, user, password, database)
        
        # Executa a consulta usando pandas read_sql
        df = pd.read_sql(query, engine)
        
        # Limpa os nomes das colunas
        df.columns = df.columns.astype(str).str.strip()
        
        # Limpeza básica de dados
        df = df.replace('', pd.NA)
        
        return df
    
    except Exception as e:
        raise Exception(f"Erro ao executar consulta SQL: {e}")

def process_sql_with_connection(connection, query):
    """
    Process a SQL query using an existing connection and return a pandas DataFrame.
    
    Args:
        connection: Database connection object
        query (str): SQL query to execute
        
    Returns:
        pandas.DataFrame: DataFrame containing the query results
    """
    try:
        # Execute query using pandas read_sql
        df = pd.read_sql(query, connection)
        
        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Basic data cleaning
        df = df.replace('', pd.NA)
        
        return df
    
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Error executing SQL query: {str(e)}")