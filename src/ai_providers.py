import os
from config import get_ai_config

# Dictionary mapping unsupported models to supported alternatives
# Mapeamento para modelos gpt-4o e gpt-4o-mini para alternativas suportadas
MODEL_MAPPING = {
    "gpt-4o": "gpt-4",        # Map gpt-4o to gpt-4
    "gpt-4o-mini": "gpt-3.5-turbo"  # Map gpt-4o-mini to gpt-3.5-turbo
}

def get_ai_provider(provider_type="api"):
    """
    Obtém o provedor de IA apropriado com base na configuração.
    
    Args:
        provider_type (str): Tipo de provedor de IA ('api' ou 'local')
        
    Returns:
        object: Instância configurada do provedor de IA
    """
    # Obtém a configuração para o tipo de provedor especificado
    config = get_ai_config(provider_type)
    
    if provider_type == "api":
        # Determina qual API usar (OpenAI ou DeepSeek)
        api_type = os.getenv("API_TYPE", "openai").lower()
        
        if api_type == "openai":
            # Importa aqui para evitar carregar dependências desnecessárias
            from pandasai.llm import OpenAI as PandasOpenAI
            
            # Verifica se o modelo está no mapeamento e substitui se necessário
            model = config["model"]
            if model in MODEL_MAPPING:
                model = MODEL_MAPPING[model]
                print(f"Modelo {config['model']} não suportado pelo PandasAI. Usando {model} como alternativa.")
            
            # Cria e retorna o cliente OpenAI adaptado para PandasAI
            return PandasOpenAI(
                api_token=config["api_key"],
                model=model,
                temperature=config["temperature"]
            )
            
        elif api_type == "deepseek":
            # Importa aqui para evitar carregar dependências desnecessárias
            from langchain.llms import DeepSeek
            
            # Cria e retorna o cliente DeepSeek
            return DeepSeek(
                api_key=config["api_key"],
                model_name=config["model"],
                temperature=config["temperature"]
            )
        else:
            raise ValueError(f"Tipo de API não suportado: {api_type}")
    
    elif provider_type == "local":
        # Importa aqui para evitar carregar dependências desnecessárias
        from langchain_community.llms import Ollama
        
        # Cria e retorna o cliente Ollama
        return Ollama(
            model=config["model"],
            base_url=config["host"]
        )
    
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")