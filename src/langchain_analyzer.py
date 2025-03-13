import os
import pandas as pd
from typing import Union, Dict, Any
import json
import matplotlib.pyplot as plt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain.chains import create_extraction_chain
from langchain.output_parsers.json import SimpleJsonOutputParser

# Importar os system prompts
from prompts.system_prompts import get_system_prompt

class DataFrameAnalyzer:
    """
    Classe para analisar DataFrames usando LangChain como substituto do PandasAI.
    Suporta exportação para JSON e Markdown.
    """
    
    def __init__(self, llm, output_format="texto"):
        """
        Inicializa o analisador com um modelo de linguagem.
        
        Args:
            llm: Modelo de linguagem LangChain (pode ser API ou local)
            output_format: Formato de saída desejado ('texto', 'markdown', 'json')
        """
        self.llm = llm
        self.df = None
        self.df_info = None
        self.output_format = output_format
        self.system_prompt = get_system_prompt(output_format)
    
    def set_output_format(self, output_format):
        """
        Atualiza o formato de saída e o system prompt correspondente.
        
        Args:
            output_format: Novo formato de saída
        """
        self.output_format = output_format
        self.system_prompt = get_system_prompt(output_format)
    
    # Atualização do método load_dataframe para lidar com datasets grandes
    def load_dataframe(self, df: pd.DataFrame):
        """
        Carrega um DataFrame para análise.
        
        Args:
            df: DataFrame do pandas
        """
        self.df = df
        
        # Para datasets grandes, criar resumos estatísticos em vez de usar o DataFrame completo
        if len(df) > 10000:
            print(f"Dataset grande com {len(df)} linhas. Criando resumos estatísticos.")
            
        # Gerar informações sobre o DataFrame
        self._generate_df_info()
    
    def _generate_df_info(self):
        """Gera informações sobre o DataFrame para contextualizar o LLM."""
        if self.df is None:
            return
        
        # Função auxiliar para converter tipos não serializáveis
        def json_serializable(obj):
            if hasattr(obj, 'isoformat'):  # Para objetos de data/hora
                return obj.isoformat()
            elif pd.isna(obj):  # Para valores NaN/None
                return None
            else:
                return str(obj)  # Fallback para outros tipos não serializáveis
        
        # Coletar informações básicas
        try:
            # Informações básicas sobre o DataFrame
            info = {
                "colunas": list(self.df.columns),
                "dimensoes": self.df.shape,
                "tipos_dados": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
                "total_registros": len(self.df),
            }
            
            # Incluir todos os dados para garantir consultas completas
            # Convertemos para dicionário para facilitar a serialização
            all_data = self.df.applymap(json_serializable).to_dict(orient="records")
            info["dados_completos"] = all_data
            
            # Adicionar valores únicos de cada coluna para facilitar consultas de filtragem
            # Isso ajuda o modelo a ter uma visão completa dos valores possíveis
            unique_values = {}
            for col in self.df.columns:
                try:
                    # Limitar a 1000 valores únicos para evitar tokens excessivos
                    unique_vals = self.df[col].dropna().unique()
                    if len(unique_vals) <= 1000:
                        unique_values[col] = [json_serializable(val) for val in unique_vals]
                    else:
                        unique_values[col] = f"Mais de 1000 valores únicos ({len(unique_vals)} no total)"
                except:
                    unique_values[col] = "Não foi possível determinar valores únicos"
            
            info["valores_unicos"] = unique_values
            
            # Adicionar contagens para colunas categóricas
            # Isso ajuda em consultas de contagem e distribuição
            counts = {}
            for col in self.df.columns:
                try:
                    if self.df[col].dtype == 'object' or len(self.df[col].unique()) < 50:
                        value_counts = self.df[col].value_counts().head(50).to_dict()
                        counts[col] = {json_serializable(k): v for k, v in value_counts.items()}
                except:
                    pass
            
            info["contagens"] = counts
            
            # Tenta incluir estatísticas descritivas
            try:
                desc_df = self.df.describe(include='all')
                info["descricao"] = {col: {idx: json_serializable(val) 
                                         for idx, val in desc_df[col].items()}
                                    for col in desc_df.columns}
            except Exception as e:
                info["descricao"] = f"Não foi possível gerar estatísticas descritivas: {str(e)}"
            
            self.df_info = info
            
        except Exception as e:
            # Fallback para caso ainda haja problemas
            self.df_info = {
                "erro": f"Erro ao processar informações do DataFrame: {str(e)}",
                "colunas": list(self.df.columns),
                "dimensoes": self.df.shape,
                "tipos_dados": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
                "dados_completos": self.df.applymap(lambda x: str(x)).to_dict(orient="records")
            }
    
    def chat(self, query: str) -> Any:
        """
        Processa uma consulta sobre o DataFrame.
        
        Args:
            query: Pergunta ou instrução do usuário
            
        Returns:
            Resposta que pode ser texto, DataFrame, ou caminho para uma imagem
        """
        if self.df is None:
            return "Nenhum DataFrame carregado. Por favor, carregue os dados primeiro."
        
        # Detectar se é uma consulta de filtragem simples
        is_filter_query = any(keyword in query.lower() for keyword in ["quais", "filtrar", "mostrar", "listar", "encontrar", "tem", "possui"])
        
        # Converter informações do DataFrame para documentos
        df_info_str = json.dumps(self.df_info, indent=2, ensure_ascii=False)
        doc = Document(page_content=df_info_str)
        
        # Criar prompt para análise com system prompt
        system_template = self.system_prompt
        
        # Adicionar instruções específicas para consultas de filtragem
        if is_filter_query:
            system_template += """
            IMPORTANTE: Esta parece ser uma consulta de filtragem simples.
            1. Use TODOS os dados disponíveis em "dados_completos", não apenas amostras.
            2. Retorne TODOS os resultados que correspondem aos critérios, sem limitar a quantidade.
            3. Não forneça explicações ou código, apenas liste os resultados.
            4. Certifique-se de verificar cada registro nos dados completos.
            """
        
        human_template = """
        Informações sobre o DataFrame:
        {context}
        
        Quando solicitado a criar visualizações, gere código Python que use matplotlib ou outras bibliotecas 
        e execute o código para salvar a imagem.
        
        Se a resposta incluir código Python para análise ou visualização, execute o código e retorne os resultados.
        
        Pergunta do usuário: {question}
        """
        
        # Criar mensagens do chat
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])
        
        # Criar cadeia de processamento
        chain = create_stuff_documents_chain(self.llm, chat_prompt)
        
        # Executar a cadeia
        result = chain.invoke({
            "context": [doc],
            "question": query
        })
        
        # Processar o resultado para executar código Python se necessário
        return self._process_result(result, query)
    
    def _process_result(self, result: str, query: str) -> Any:
        """
        Processa o resultado da consulta, executando código Python se necessário.
        
        Args:
            result: Resultado da consulta ao LLM
            query: Consulta original
            
        Returns:
            Resultado processado
        """
        # Verificar se o resultado contém código Python para executar
        if "```python" in result:
            # Extrair código Python
            code_blocks = []
            lines = result.split("\n")
            in_code_block = False
            current_block = []
            
            for line in lines:
                if line.startswith("```python"):
                    in_code_block = True
                elif line.startswith("```") and in_code_block:
                    in_code_block = False
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                elif in_code_block:
                    current_block.append(line)
            
            # Executar cada bloco de código
            for code in code_blocks:
                try:
                    # Preparar ambiente de execução
                    local_vars = {
                        "df": self.df,
                        "pd": pd,
                        "plt": plt,
                        "os": os
                    }
                    
                    # Executar código
                    exec(code, globals(), local_vars)
                    
                    # Verificar se uma figura foi gerada
                    if plt.get_fignums():
                        # Salvar figura
                        fig_path = "temp_figure.png"
                        plt.savefig(fig_path)
                        plt.close()
                        return fig_path
                    
                    # Verificar se um novo DataFrame foi gerado
                    if "result_df" in local_vars:
                        return local_vars["result_df"]
                    
                except Exception as e:
                    return f"Erro ao executar código: {str(e)}\n\nResposta original:\n{result}"
        
        return result
    
    def to_json(self, query: str = None) -> str:
        """
        Converte os resultados da análise para JSON.
        
        Args:
            query: Consulta opcional para análise específica
            
        Returns:
            String JSON com os resultados
        """
        if query:
            # Definir esquema de extração
            schema = {
                "properties": {
                    "analise": {"type": "string"},
                    "insights": {"type": "array", "items": {"type": "string"}},
                    "resumo": {"type": "string"}
                },
                "required": ["analise", "insights", "resumo"]
            }
            
            # Criar cadeia de extração
            chain = create_extraction_chain(schema, self.llm)
            
            # Executar consulta e extrair informações estruturadas
            result = chain.run(f"Analise os seguintes dados e forneça insights: {self.df_info}\n\nConsulta: {query}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Retornar informações básicas do DataFrame em JSON
            return json.dumps(self.df_info, indent=2, ensure_ascii=False)
    
    def to_markdown(self, query: str = None) -> str:
        """
        Converte os resultados da análise para Markdown.
        
        Args:
            query: Consulta opcional para análise específica
            
        Returns:
            String Markdown com os resultados
        """
        if query:
            # Criar prompt para gerar markdown
            prompt = ChatPromptTemplate.from_template("""
            Você é um assistente especializado em análise de dados.
            
            Informações sobre o DataFrame:
            {df_info}
            
            Gere um relatório em formato Markdown sobre os dados com base na seguinte consulta:
            {query}
            
            O relatório deve incluir:
            1. Um título e introdução
            2. Resumo dos dados
            3. Principais insights
            4. Análise detalhada
            5. Conclusão
            
            Use formatação Markdown adequada com títulos, subtítulos, listas e tabelas.
            
            Responda em português do Brasil.
            """)
            
            # Criar cadeia
            chain = prompt | self.llm | StrOutputParser()
            
            # Executar cadeia
            return chain.invoke({
                "df_info": json.dumps(self.df_info, indent=2, ensure_ascii=False),
                "query": query
            })
        else:
            # Gerar markdown básico com informações do DataFrame
            md = f"# Análise de DataFrame\n\n"
            md += f"## Informações Básicas\n\n"
            md += f"- Dimensões: {self.df_info['dimensoes'][0]} linhas × {self.df_info['dimensoes'][1]} colunas\n"
            md += f"- Colunas: {', '.join(self.df_info['colunas'])}\n\n"
            
            md += f"## Amostra de Dados\n\n"
            # Criar tabela markdown
            header = "| " + " | ".join(self.df_info['colunas']) + " |"
            separator = "| " + " | ".join(["---"] * len(self.df_info['colunas'])) + " |"
            
            rows = []
            for record in self.df_info['amostra']:
                row = "| " + " | ".join([str(record[col]) for col in self.df_info['colunas']]) + " |"
                rows.append(row)
            
            md += header + "\n" + separator + "\n" + "\n".join(rows)
            
            return md