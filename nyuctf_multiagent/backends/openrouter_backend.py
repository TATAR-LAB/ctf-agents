"""
OpenRouter Backend for D-CIPHER
Access 200+ models including Claude, GPT, Llama, Mistral via OpenRouter API
Get API key from: https://openrouter.ai/keys
"""
import json
from openai import OpenAI, APIError
from openai.types.chat import ChatCompletionMessage

from ..conversation import MessageRole
from ..tools import ToolCall, ToolResult

from .backend import Backend, BackendResponse


class OpenRouterBackend(Backend):
    NAME = 'openrouter'
    # Popular models available on OpenRouter
    # Full list: https://openrouter.ai/models
    MODELS = {
        # Anthropic Claude
        "anthropic/claude-sonnet-4": {
            "max_context": 200000,
            "cost_per_input_token": 3e-06,
            "cost_per_output_token": 15e-06
        },
        "anthropic/claude-3.5-sonnet": {
            "max_context": 200000,
            "cost_per_input_token": 3e-06,
            "cost_per_output_token": 15e-06
        },
        "anthropic/claude-3.5-haiku": {
            "max_context": 200000,
            "cost_per_input_token": 0.8e-06,
            "cost_per_output_token": 4e-06
        },
        # OpenAI
        "openai/gpt-4o": {
            "max_context": 128000,
            "cost_per_input_token": 2.5e-06,
            "cost_per_output_token": 10e-06
        },
        "openai/gpt-4o-mini": {
            "max_context": 128000,
            "cost_per_input_token": 0.15e-06,
            "cost_per_output_token": 0.6e-06
        },
        "openai/o1": {
            "max_context": 200000,
            "cost_per_input_token": 15e-06,
            "cost_per_output_token": 60e-06
        },
        "openai/o1-mini": {
            "max_context": 128000,
            "cost_per_input_token": 3e-06,
            "cost_per_output_token": 12e-06
        },
        # Google
        "google/gemini-2.0-flash-001": {
            "max_context": 1000000,
            "cost_per_input_token": 0.1e-06,
            "cost_per_output_token": 0.4e-06
        },
        "google/gemini-pro-1.5": {
            "max_context": 2000000,
            "cost_per_input_token": 1.25e-06,
            "cost_per_output_token": 5e-06
        },
        # Meta Llama
        "meta-llama/llama-3.3-70b-instruct": {
            "max_context": 131072,
            "cost_per_input_token": 0.3e-06,
            "cost_per_output_token": 0.4e-06
        },
        "meta-llama/llama-3.1-405b-instruct": {
            "max_context": 131072,
            "cost_per_input_token": 2e-06,
            "cost_per_output_token": 2e-06
        },
        # Mistral
        "mistralai/mistral-large-2411": {
            "max_context": 128000,
            "cost_per_input_token": 2e-06,
            "cost_per_output_token": 6e-06
        },
        "mistralai/codestral-2501": {
            "max_context": 256000,
            "cost_per_input_token": 0.3e-06,
            "cost_per_output_token": 0.9e-06
        },
        # DeepSeek
        "deepseek/deepseek-chat": {
            "max_context": 64000,
            "cost_per_input_token": 0.14e-06,
            "cost_per_output_token": 0.28e-06
        },
        "deepseek/deepseek-r1": {
            "max_context": 64000,
            "cost_per_input_token": 0.55e-06,
            "cost_per_output_token": 2.19e-06
        },
        # Qwen
        "qwen/qwen-2.5-72b-instruct": {
            "max_context": 131072,
            "cost_per_input_token": 0.35e-06,
            "cost_per_output_token": 0.4e-06
        },
        "qwen/qwen-2.5-coder-32b-instruct": {
            "max_context": 32768,
            "cost_per_input_token": 0.18e-06,
            "cost_per_output_token": 0.18e-06
        },
    }

    def __init__(self, role, model, tools, api_key, config):
        super().__init__(role, model, tools, config)
        # OpenRouter uses OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.tool_schemas = [self.get_tool_schema(tool) for tool in tools.values()]

    @staticmethod
    def get_tool_schema(tool):
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
            max_tokens=self.get_param(self.role, "max_tokens"),
            extra_headers={
                "HTTP-Referer": "https://github.com/NYU-LLM-CTF",
                "X-Title": "D-CIPHER CTF Agent"
            }
        )

    def calculate_cost(self, response):
        if response.usage:
            return self.in_price * response.usage.prompt_tokens + self.out_price * response.usage.completion_tokens
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
            return BackendResponse(error=f"OpenRouter Error: {e}")
        except Exception as e:
            return BackendResponse(error=f"OpenRouter Connection Error: {e}")

        if response.tool_calls and len(response.tool_calls) > 0:
            oai_call = response.tool_calls[0]
            tool_call = ToolCall(name=oai_call.function.name, id=oai_call.id,
                                 arguments=oai_call.function.arguments)
        else:
            tool_call = None

        return BackendResponse(content=response.content, tool_call=tool_call, cost=cost)
