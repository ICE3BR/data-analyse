import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def get_ai_config(provider_type="api"):
    """
    Obtém a configuração de IA com base no tipo de provedor.
    
    Args:
        provider_type (str): Tipo de provedor de IA ('api' ou 'local')
        
    Returns:
        dict: Dicionário de configuração para o provedor de IA
    """
    if provider_type == "api":
        # Determina qual API usar (OpenAI ou DeepSeek)
        api_type = os.getenv("API_TYPE", "openai").lower()
        
        if api_type == "openai":
            return {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            }
        elif api_type == "deepseek":
            return {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            }
        else:
            raise ValueError(f"Tipo de API não suportado: {api_type}")
    
    elif provider_type == "local":
        # Configuração para Ollama
        return {
            "model": os.getenv("OLLAMA_MODEL", "mistral"),
            "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        }
    
    else:
        raise ValueError(f"Tipo de provedor não suportado: {provider_type}")