import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def process_xml(file):
    """
    Processa um arquivo XML e retorna um DataFrame pandas.
    
    Args:
        file: Objeto tipo arquivo contendo dados XML
        
    Returns:
        pandas.DataFrame: DataFrame contendo os dados do XML
    """
    try:
        # Lê o conteúdo do arquivo
        content = file.read()
        
        # Analisa o XML
        root = ET.parse(BytesIO(content)).getroot()
        
        # Extrai dados do XML
        # Esta é uma implementação simples que assume uma estrutura plana
        # Para XML mais complexos, isso precisaria ser personalizado
        data = []
        
        # Encontra todos os registros (assumindo um pai comum para itens de dados)
        # Esta é uma abordagem simplificada - a implementação real dependeria da estrutura XML
        records = root.findall('.//*')
        
        if not records:
            # Se nenhum registro for encontrado com a abordagem acima, tenta filhos diretos
            records = list(root)
        
        # Se temos registros, processa-os
        if records:
            # Obtém todas as tags únicas para usar como colunas
            all_tags = set()
            for record in records:
                # Adiciona a tag do próprio registro
                all_tags.add(record.tag)
                # Adiciona tags de todos os filhos
                for child in record:
                    all_tags.add(child.tag)
            
            # Processa cada registro
            for record in records:
                row = {}
                # Adiciona o texto do registro, se houver
                if record.text and record.text.strip():
                    row[record.tag] = record.text.strip()
                
                # Adiciona todos os dados dos filhos
                for child in record:
                    # Usa a tag como nome da coluna
                    tag = child.tag
                    # Usa o texto como valor, ou string vazia se None
                    value = child.text.strip() if child.text else ''
                    # Adiciona à linha
                    row[tag] = value
                
                # Adiciona atributos, se houver
                for attr, value in record.attrib.items():
                    row[f"{record.tag}_{attr}"] = value
                
                # Adiciona apenas linhas não vazias
                if row:
                    data.append(row)
        
        # Cria DataFrame
        if data:
            df = pd.DataFrame(data)
            
            # Limpa os nomes das colunas
            df.columns = df.columns.astype(str).str.strip()
            
            # Limpeza básica de dados
            df = df.replace('', pd.NA)
            df = df.dropna(how='all')
            
            return df
        else:
            # Se nenhum dado estruturado for encontrado, retorna DataFrame vazio com uma mensagem
            return pd.DataFrame({'mensagem': ['Nenhum dado estruturado encontrado no XML']})
    
    except Exception as e:
        # Re-levanta com mais contexto
        raise Exception(f"Erro ao processar arquivo XML: {str(e)}")