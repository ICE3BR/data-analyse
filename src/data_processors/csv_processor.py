import pandas as pd

def process_csv(file):
    """
    Processa um arquivo CSV e retorna um DataFrame pandas.
    
    Args:
        file: Objeto tipo arquivo contendo dados CSV
        
    Returns:
        pandas.DataFrame: DataFrame contendo os dados do CSV
    """
    try:
        # Tenta detectar o encoding e o delimitador automaticamente
        # Primeiro, lê uma amostra do arquivo para detecção
        sample = file.read(1024)
        file.seek(0)  # Retorna ao início do arquivo
        
        # Tenta diferentes encodings comuns
        encodings = ['utf-8', 'latin1', 'iso-8859-1']
        for encoding in encodings:
            try:
                sample.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        # Lê o arquivo CSV para um DataFrame
        df = pd.read_csv(
            file,
            encoding=encoding,
            on_bad_lines='warn',  # Avisa sobre linhas problemáticas
            low_memory=False      # Melhor inferência de tipos
        )
        
        # Limpa os nomes das colunas (remove espaços em branco, converte para string)
        df.columns = df.columns.astype(str).str.strip()
        
        # Converte colunas numéricas para o tipo correto
        # Identifica colunas que parecem ser numéricas
        for col in df.columns:
            # Tenta converter para numérico, ignorando erros
            try:
                # Primeiro, substitui vírgulas por pontos (formato brasileiro para decimal)
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '.', regex=False)
                
                # Tenta converter para numérico
                pd.to_numeric(df[col], errors='raise')
                # Se não der erro, converte a coluna
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                # Se não for possível converter, mantém como está
                pass
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo CSV: {str(e)}")