import pandas as pd

def process_excel(file):
    """
    Processa um arquivo Excel e retorna um DataFrame pandas.
    
    Args:
        file: Objeto tipo arquivo contendo dados Excel
        
    Returns:
        pandas.DataFrame: DataFrame contendo os dados do Excel
    """
    try:
        # Lê o arquivo Excel para um DataFrame
        # Usaremos a primeira planilha por padrão
        df = pd.read_excel(file, engine='openpyxl')
        
        # Limpa os nomes das colunas (remove espaços em branco, converte para string)
        df.columns = df.columns.astype(str).str.strip()
        
        # Limpeza básica de dados
        # Substitui strings vazias por NaN
        df = df.replace('', pd.NA)
        
        # Remove linhas e colunas completamente vazias
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        return df
    
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo Excel: {e}")