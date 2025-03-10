# Análise de Dados com PandasAI

Este projeto fornece uma interface web para análise de dados usando PandasAI. Permite aos usuários analisar várias fontes de dados, incluindo arquivos CSV, documentos XML, arquivos Excel e bancos de dados MySQL.

## Funcionalidades

- Interface web construída com Streamlit
- Suporte para múltiplos backends de IA:
  - Baseados em API: OpenAI GPT e DeepSeek
  - Local: Ollama
- Suporte para fontes de dados:
  - Arquivos CSV
  - Documentos XML
  - Arquivos Excel
  - Bancos de dados MySQL
- Interface de usuário intuitiva
- Configuração fácil para desenvolvedores

## Estrutura do Projeto

```
data_analyse/
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── ai_providers.py
│   ├── data_processors/
│   │   ├── __init__.py
│   │   ├── csv_processor.py
│   │   ├── excel_processor.py
│   │   ├── xml_processor.py
│   │   └── sql_processor.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
└── tests/
    └── __init__.py
```

## Configuração

1. Clone o repositório
2. Instale as dependências: `pip install -e .`
3. Copie `.env.example` para `.env` e preencha suas chaves de API
4. Execute a aplicação: `streamlit run src/main.py`

## Configuração

A aplicação pode ser configurada através do arquivo `.env` ou pela interface web. Desenvolvedores podem facilmente modificar modelos de IA, chaves de API e conexões de banco de dados.

## Requisitos

- Python 3.10+
- MySQL
- Streamlit
- PandasAI
- Ollama (para IA local)

## Licença

MIT