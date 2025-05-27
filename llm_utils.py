import requests
from typing import Optional, Dict, Any

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3:latest"

def check_model_installed(model_name: str) -> bool:
    """
    Check if a specific model is installed in Ollama.
    
    Args:
        model_name (str): Name of the model to check
        
    Returns:
        bool: True if the model is installed, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.ok:
            models = [m["name"] for m in response.json().get("models", [])]
            return model_name in models
        return False
    except requests.RequestException:
        return False

def query_ollama(
    prompt: str,
    model: str = MODEL_NAME,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Query the Ollama model with the given prompt.
    
    Args:
        prompt (str): The input prompt to send to the model
        model (str): The model to use (default: "llama3:latest")
        system_prompt (Optional[str]): Optional system prompt to guide the model's behavior
        temperature (float): Controls randomness in the output (0.0 to 1.0)
        max_tokens (int): Maximum number of tokens to generate
        **kwargs: Additional parameters to pass to the Ollama API
        
    Returns:
        Dict[str, Any]: The model's response containing the generated text and metadata
    """
    if not check_model_installed(model):
        raise Exception(f"❌ Model '{model}' is not available. Please run: ollama pull {model}")

    try:
        # Prepare the request parameters
        request_params = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False,
            **kwargs
        }
        
        # Add system prompt if provided
        if system_prompt:
            request_params["system"] = system_prompt
            
        # Make the request to Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=request_params
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "text": result.get("response", "No response from model."),
            "model": model,
            "total_tokens": result.get("total_tokens", 0),
            "prompt_tokens": result.get("prompt_tokens", 0),
            "completion_tokens": result.get("completion_tokens", 0)
        }
        
    except requests.RequestException as e:
        raise Exception(f"Error querying Ollama model: {str(e)}")

def get_available_models() -> list[str]:
    """
    Get a list of available Ollama models.
    
    Returns:
        list[str]: List of model names available in Ollama
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        models = response.json()
        return [model["name"] for model in models.get("models", [])]
    except requests.RequestException as e:
        raise Exception(f"Error getting available models: {str(e)}")

def check_model_availability(model_name: str) -> bool:
    """
    Check if a specific model is available in Ollama.
    
    Args:
        model_name (str): Name of the model to check
        
    Returns:
        bool: True if the model is available, False otherwise
    """
    try:
        available_models = get_available_models()
        return model_name in available_models
    except Exception:
        return False 