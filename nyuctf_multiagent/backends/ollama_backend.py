"""
Ollama Backend for D-CIPHER
Uses local Ollama server with OpenAI-compatible API
"""
import json
from openai import OpenAI, APIError
from openai.types.chat import ChatCompletionMessage

from ..conversation import MessageRole
from ..tools import ToolCall, ToolResult

from .backend import Backend, BackendResponse


class OllamaBackend(Backend):
    NAME = 'ollama'
    # Common Ollama models - add more as needed
    # Cost is 0 since it's local
    MODELS = {
        # Large models with good tool calling support
        "qwen2.5:32b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "qwen2.5:14b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "qwen2.5:7b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "qwen2.5-coder:32b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "qwen2.5-coder:14b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "qwen2.5-coder:7b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "llama3.3:70b": {
            "max_context": 131072,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "llama3.2:3b": {
            "max_context": 131072,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "llama3.2:1b": {
            "max_context": 131072,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "llama3.1:8b": {
            "max_context": 131072,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "llama3.1:70b": {
            "max_context": 131072,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "mistral:7b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "mixtral:8x7b": {
            "max_context": 32768,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "codellama:34b": {
            "max_context": 16384,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "deepseek-coder-v2:16b": {
            "max_context": 65536,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "phi3:14b": {
            "max_context": 128000,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "gemma2:27b": {
            "max_context": 8192,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
        "gemma2:9b": {
            "max_context": 8192,
            "cost_per_input_token": 0,
            "cost_per_output_token": 0
        },
    }

    def __init__(self, role, model, tools, api_key, config):
        super().__init__(role, model, tools, config)
        # Ollama uses OpenAI-compatible API at localhost:11434
        # api_key can be "ollama" or anything (not used by Ollama)
        base_url = "http://localhost:11434/v1"
        self.client = OpenAI(base_url=base_url, api_key=api_key or "ollama")
        self.tool_schemas = [self.get_tool_schema(tool) for tool in tools.values()]

    @staticmethod
    def get_tool_schema(tool):
        # Based on OpenAI format
        return {
            "type": "function",
            "function": {
                "name": tool.NAME,
                "description": tool.DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {n: {"type": p[0], "description": p[1]} for n, p in tool.PARAMETERS.items()},
                    "required": list(tool.REQUIRED_PARAMETERS),
                }
            }
        }

    def _call_model(self, messages) -> ChatCompletionMessage:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_schemas,
            tool_choice="auto",
            temperature=self.get_param(self.role, "temperature"),
            max_tokens=self.get_param(self.role, "max_tokens")
        )

    def calculate_cost(self, response):
        # Local models are free
        return 0

    def send(self, messages):
        formatted_messages = []
        for m in messages:
            if m.role == MessageRole.OBSERVATION:
                msg = {"role": "tool",
                       "content": json.dumps(m.tool_data.result),
                       "tool_call_id": m.tool_data.id}
            elif m.role == MessageRole.ASSISTANT:
                msg = {"role": m.role.value}
                if m.content is not None:
                    msg["content"] = m.content
                if m.tool_data is not None:
                    msg["tool_calls"] = [{"id": m.tool_data.id,
                                          "type": "function",
                                          "function": {
                                              "name": m.tool_data.name,
                                              "arguments": m.tool_data.arguments
                                            }}]
            else:
                msg = {"role": m.role.value, "content": m.content}
            formatted_messages.append(msg)

        try:
            response = self._call_model(formatted_messages)
            cost = self.calculate_cost(response)
            response = response.choices[0].message
        except APIError as e:
            return BackendResponse(error=f"Ollama Backend Error: {e}")
        except Exception as e:
            return BackendResponse(error=f"Ollama Connection Error: {e}. Is Ollama running?")

        if response.tool_calls and len(response.tool_calls) > 0:
            oai_call = response.tool_calls[0]
            tool_call = ToolCall(name=oai_call.function.name, id=oai_call.id,
                                 arguments=oai_call.function.arguments)
        else:
            tool_call = None

        return BackendResponse(content=response.content, tool_call=tool_call, cost=cost)
