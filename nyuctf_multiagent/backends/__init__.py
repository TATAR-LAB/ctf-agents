from .openai_backend import OpenAIBackend
from .anthropic_backend import AnthropicBackend
from .together_backend import TogetherBackend
from .gemini_backend import GeminiBackend
from .ollama_backend import OllamaBackend
from .vertexai_backend import VertexAIBackend
from .openrouter_backend import OpenRouterBackend
from .backend import Role

BACKENDS = [OpenAIBackend, AnthropicBackend, TogetherBackend, GeminiBackend, OllamaBackend, VertexAIBackend, OpenRouterBackend]
MODELS = {m: b for b in BACKENDS for m in b.MODELS}

