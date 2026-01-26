from pathlib import Path
import yaml

from .openai_backend import OpenAIBackend
from .anthropic_backend import AnthropicBackend
from .together_backend import TogetherBackend
from .gemini_backend import GeminiBackend
from .ollama_backend import OllamaBackend
from .vertexai_backend import VertexAIBackend
from .openrouter_backend import OpenRouterBackend
from .backend import Role

# Map backend names to their classes
BACKEND_CLASSES = {
    'openai': OpenAIBackend,
    'anthropic': AnthropicBackend,
    'gemini': GeminiBackend,
    'vertexai': VertexAIBackend,
    'ollama': OllamaBackend,
    'openrouter': OpenRouterBackend,
    'together': TogetherBackend,
}

def load_models_config():
    """Load model definitions from models.yaml"""
    models_path = Path(__file__).parent / 'models.yaml'
    with open(models_path) as f:
        return yaml.safe_load(f)

# Load models configuration at module import time
_models_config = load_models_config()

# MODEL_INFO: model name -> {max_context, cost_per_input_token, cost_per_output_token}
# Used by Backend base class for pricing and context limits
MODEL_INFO = {
    name: {k: v for k, v in info.items() if k != 'backend'}
    for name, info in _models_config.items()
}

# MODELS: model name -> Backend class
# Used to select the correct backend for a given model
MODELS = {
    name: BACKEND_CLASSES[info['backend']]
    for name, info in _models_config.items()
}

# For backwards compatibility, also export the list of backend classes
BACKENDS = list(BACKEND_CLASSES.values())

