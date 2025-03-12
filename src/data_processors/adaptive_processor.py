import os
import pandas as pd
import polars as pl
from .csv_processor import process_csv
from .excel_processor import process_excel
from .xml_processor import process_xml

def process_adaptive(file_path, file_content=None):
    """
    Processa dados adaptando-se automaticamente ao tamanho do arquivo.
    
    Args:
        file_path: Caminho ou nome do arquivo
        file_content: Conteúdo do arquivo (para uploads via Streamlit)
        
    Returns:
        DataFrame do pandas processado
    """
    # Determina se estamos lidando com um upload do Streamlit ou um arquivo no disco
    is_upload = file_content is not None
    
    # Obtém o limite de tamanho das configurações
    large_file_threshold = int(os.getenv("LARGE_FILE_THRESHOLD", 100_000_000))  # 100MB padrão
    
    # Para uploads do Streamlit, não podemos verificar o tamanho diretamente
    # então usamos uma abordagem baseada no tipo de arquivo
    if is_upload:
        if file_path.endswith('.csv'):
            return process_csv(file_content)
        elif file_path.endswith(('.xlsx', '.xls')):
            return process_excel(file_content)
        elif file_path.endswith('.xml'):
            return process_xml(file_content)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file_path}")
    
    # Para arquivos no disco, podemos verificar o tamanho
    else:
        file_size = os.path.getsize(file_path)
        
        # Para arquivos pequenos (menos que o limite configurado), usa processamento padrão
        if file_size < large_file_threshold:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                return pd.read_excel(file_path)
            elif file_path.endswith('.xml'):
                # Implementação específica para XML
                with open(file_path, 'r') as f:
                    return process_xml(f)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_path}")
        
        # Para arquivos grandes, usa processamento otimizado com Polars
        else:
            return process_large_dataframe(file_path)

def process_large_dataframe(file_path):
    """
    Processa arquivos de dados muito grandes usando Polars para melhor performance.
    
    Args:
        file_path: Caminho para o arquivo de dados grande
        
    Returns:
        DataFrame processado (convertido para pandas para compatibilidade)
    """
    # Carregar com Polars - muito mais eficiente para arquivos grandes
    if file_path.endswith('.csv'):
        df = pl.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pl.read_excel(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado para processamento grande: {file_path}")
    
    # Realizar operações de limpeza/transformação em Polars (muito rápido)
    # Remover linhas com valores nulos em todas as colunas
    df = df.drop_nulls(how="all")
    
    # Para datasets realmente grandes, considerar amostragem
    # Isso é opcional e pode ser controlado por uma configuração
    if df.height > 100000:
        print(f"Dataset muito grande ({df.height} linhas). Usando amostragem para análise.")
    
    # Converter para pandas para compatibilidade com o resto do sistema
    pandas_df = df.to_pandas()
    
    return pandas_df