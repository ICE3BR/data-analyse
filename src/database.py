import os
import pymysql
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def get_database_connection(host=None, user=None, password=None, database=None):
    """
    Obtém uma conexão com o banco de dados usando as credenciais fornecidas ou variáveis de ambiente.
    
    Args:
        host (str, optional): Host do banco de dados. Padrão é None (usa variável de ambiente).
        user (str, optional): Usuário do banco de dados. Padrão é None (usa variável de ambiente).
        password (str, optional): Senha do banco de dados. Padrão é None (usa variável de ambiente).
        database (str, optional): Nome do banco de dados. Padrão é None (usa variável de ambiente).
        
    Returns:
        pymysql.Connection: Objeto de conexão com o banco de dados
    """
    # Usa as credenciais fornecidas ou recorre às variáveis de ambiente
    host = host or os.getenv("DB_HOST", "localhost")
    user = user or os.getenv("DB_USER")
    password = password or os.getenv("DB_PASSWORD")
    database = database or os.getenv("DB_NAME")
    
    # Verifica se as credenciais necessárias estão disponíveis
    if not all([user, password, database]):
        raise ValueError("Credenciais de banco de dados ausentes. Por favor, forneça-as ou defina variáveis de ambiente.")
    
    # Cria conexão
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    return connection

def get_sqlalchemy_engine(host=None, user=None, password=None, database=None):
    """
    Obtém um motor SQLAlchemy usando as credenciais fornecidas ou variáveis de ambiente.
    
    Args:
        host (str, optional): Host do banco de dados. Padrão é None (usa variável de ambiente).
        user (str, optional): Usuário do banco de dados. Padrão é None (usa variável de ambiente).
        password (str, optional): Senha do banco de dados. Padrão é None (usa variável de ambiente).
        database (str, optional): Nome do banco de dados. Padrão é None (usa variável de ambiente).
        
    Returns:
        sqlalchemy.engine.Engine: Motor SQLAlchemy para o banco de dados
    """
    # Usa as credenciais fornecidas ou recorre às variáveis de ambiente
    host = host or os.getenv("DB_HOST", "localhost")
    user = user or os.getenv("DB_USER")
    password = password or os.getenv("DB_PASSWORD")
    database = database or os.getenv("DB_NAME")
    
    # Verifica se as credenciais necessárias estão disponíveis
    if not all([user, password, database]):
        raise ValueError("Credenciais de banco de dados ausentes. Por favor, forneça-as ou defina variáveis de ambiente.")
    
    # Cria string de conexão
    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    
    # Cria e retorna o motor
    return create_engine(connection_string)

def execute_query(query, connection=None, **connection_params):
    """
    Execute a SQL query and return the results as a pandas DataFrame.
    
    Args:
        query (str): SQL query to execute.
        connection (pymysql.Connection, optional): Existing database connection. 
                                                 Defaults to None (creates a new connection).
        **connection_params: Additional parameters to pass to get_database_connection.
        
    Returns:
        pandas.DataFrame: Query results as a DataFrame
    """
    # Create a new connection if one wasn't provided
    close_connection = False
    if connection is None:
        connection = get_database_connection(**connection_params)
        close_connection = True
    
    try:
        # Execute query and fetch results
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        
        # Convert results to DataFrame
        df = pd.DataFrame(results)
        
        return df
    
    finally:
        # Close the connection if we created it
        if close_connection:
            connection.close()