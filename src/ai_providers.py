import os
from typing import Dict, Any

# Mapeamento de modelos para alternativas compatíveis com PandasAI
MODEL_MAPPING = {
    "gpt-4": "gpt-3.5-turbo",
    "gpt-4-turbo": "gpt-3.5-turbo",
    "gpt-4-vision-preview": "gpt-3.5-turbo",
}

def get_ai_config(provider_type: str) -> Dict[str, Any]:
    """
    Obtém a configuração para o provedor de IA especificado.
    
    Args:
        provider_type (str): Tipo de provedor ('api' ou 'local')
        
    Returns:
        Dict[str, Any]: Configuração do provedor
    """
    if provider_type == "api":
        api_type = os.getenv("API_TYPE", "openai").lower()
        
        if api_type == "openai":
            return {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            }
        elif api_type == "deepseek":
            return {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            }
        else:
            raise ValueError(f"Tipo de API não suportado: {api_type}")
    
    elif provider_type == "local":
        return {
            "model": os.getenv("OLLAMA_MODEL", "mistral"),
            "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        }
    
    else:
        raise ValueError(f"Tipo de provedor não suportado: {provider_type}")

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
            from langchain_openai import ChatOpenAI
            
            # Cria e retorna o cliente OpenAI para LangChain
            return ChatOpenAI(
                api_key=config["api_key"],
                model=config["model"],
                temperature=config["temperature"]
            )
            
        elif api_type == "deepseek":
            # Importa aqui para evitar carregar dependências desnecessárias
            from langchain_community.llms import DeepSeek
            
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
        raise ValueError(f"Tipo de provedor não suportado: {provider_type}")