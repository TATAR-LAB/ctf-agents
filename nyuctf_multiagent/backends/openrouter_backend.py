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
    # Models are now defined in models.yaml
    # Full model list: https://openrouter.ai/models

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
