# Análise de Dados com LangChain

Uma ferramenta avançada de análise de dados que utiliza LangChain e múltiplos backends de IA para extrair insights valiosos de diversos tipos de dados.

![Análise de Dados](https://via.placeholder.com/800x400?text=An%C3%A1lise+de+Dados+com+LangChain)

## Visão Geral

Este projeto oferece uma interface intuitiva baseada em Streamlit para analisar dados de diferentes fontes (CSV, Excel, XML, bancos de dados) utilizando modelos de linguagem avançados. A ferramenta é capaz de processar tanto conjuntos de dados pequenos quanto grandes, adaptando-se automaticamente para oferecer a melhor performance.

### Principais Recursos

- **Múltiplos Backends de IA**: Suporte para OpenAI, DeepSeek e modelos locais via Ollama
- **Processamento Adaptativo**: Otimização automática baseada no tamanho do arquivo
- **Formatos Flexíveis**: Análise de dados em CSV, Excel, XML e bancos de dados MySQL
- **Visualizações Interativas**: Gráficos com Matplotlib e Plotly
- **Relatórios Personalizáveis**: Saída em texto simples, Markdown ou JSON

## Requisitos

- Python 3.10 ou superior
- Dependências listadas em `pyproject.toml`
- Chave de API da OpenAI (opcional se usar Ollama)
- Ollama instalado localmente (opcional se usar API)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/data-analyse.git
cd data-analyse
```
2. Instale as dependências:
```bash
pip install -e .
```
3. Configure o arquivo `.env` :
```bash	
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Uso
Execute a aplicação Streamlit:
```bash
streamlit run src/main.py
```

### Fluxo de Trabalho Básico
1. Selecione a fonte de dados (arquivo ou banco de dados)
2. Carregue ou conecte-se aos dados
3. Faça perguntas em linguagem natural sobre os dados
4. Visualize os resultados e insights gerados pela IA

## Estrutura do Projeto
```text
data_analyse/
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   ├── main.py                    # Ponto de entrada da aplicação Streamlit
│   ├── config.py                  # Configurações e carregamento de variáveis de ambiente
│   ├── langchain_analyzer.py      # Implementação principal do analisador com LangChain
│   ├── data_processors/           # Processadores para diferentes tipos de dados
│   │   ├── __init__.py
│   │   ├── adaptive_processor.py  # Processador adaptativo baseado no tamanho
│   │   ├── csv_processor.py       # Processador para arquivos CSV
│   │   ├── excel_processor.py     # Processador para arquivos Excel
│   │   ├── xml_processor.py       # Processador para arquivos XML
│   │   └── large_data_processor.py # Processador otimizado para dados grandes
│   ├── database/                  # Módulos para conexão com bancos de dados
│   │   ├── __init__.py
│   │   └── mysql_connector.py     # Conector para MySQL
│   ├── prompts/                   # Definições de prompts para os modelos de IA
│   │   ├── __init__.py
│   │   └── system_prompts.py      # System prompts para diferentes formatos de saída
│   └── visualizations/            # Módulos para visualização de dados
│       ├── __init__.py
│       ├── matplotlib_viz.py      # Visualizações com Matplotlib
│       └── plotly_viz.py          # Visualizações interativas com Plotly
```
## Arquivos Editáveis
Os seguintes arquivos podem ser editados para personalizar o comportamento da aplicação:

### Configuração
- .env : Configurações de API, modelos, banco de dados e comportamento do sistema
- src/config.py : Funções para carregar e processar configurações
### Processamento de Dados
- src/data_processors/*.py : Módulos para processamento de diferentes tipos de dados
- src/database/*.py : Conectores para diferentes bancos de dados
### IA e Prompts
- src/prompts/system_prompts.py : Definições de system prompts para orientar o comportamento da IA
- src/langchain_analyzer.py : Implementação principal do analisador com LangChain
### Interface
- src/main.py : Interface Streamlit e fluxo principal da aplicação
- src/visualizations/*.py : Módulos para visualização de dados
## Como o Sistema Funciona
### 1. Carregamento e Processamento de Dados
O sistema utiliza um processador adaptativo que:

- Detecta automaticamente o tamanho do arquivo
- Para arquivos pequenos (<100MB por padrão), usa pandas diretamente
- Para arquivos grandes (>100MB), utiliza Polars para processamento eficiente
- Converte os resultados para pandas para manter compatibilidade
### 2. Análise com LangChain
- Cria um contexto com informações sobre os dados
- Utiliza o LLM configurado (OpenAI, DeepSeek ou Ollama)
- Aplica system prompts específicos baseados no formato de saída desejado
- Processa perguntas em linguagem natural sobre os dados
### 3. Visualização e Relatórios
- Gera visualizações usando Matplotlib ou Plotly
- Formata a saída conforme solicitado (texto, Markdown, JSON)
- Apresenta insights e recomendações baseados nos dados
## Configurações Avançadas
### Processamento de Dados Grandes
O limite para considerar um arquivo como "grande" pode ser ajustado na variável LARGE_FILE_THRESHOLD no arquivo .env . O valor padrão é 100MB (100000000 bytes).

### Visualizações Interativas
Para ativar visualizações interativas com Plotly por padrão, defina DEFAULT_USE_PLOTLY=true no arquivo .env .

### Formatos de Saída
O formato de saída padrão pode ser configurado com DEFAULT_OUTPUT_FORMAT no arquivo .env . Opções disponíveis:

- texto : Saída em texto simples
- markdown : Relatório formatado em Markdown
- json : Dados estruturados em formato JSON
## Contribuição
Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests ou abrir issues para melhorias e correções.

## Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.