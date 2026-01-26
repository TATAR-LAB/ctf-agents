import json
from together import Together
from together.error import InvalidRequestError, RateLimitError
from together.types.chat_completions import ChatCompletionMessage

from ..conversation import MessageRole
from ..tools import ToolCall, ToolResult

from .backend import Backend, BackendResponse

class TogetherBackend(Backend):
    """
    Backend for Together.ai
    """
    NAME = "together"
    # Models are now defined in models.yaml

    def __init__(self, role, model, tools, api_key, config):
        super().__init__(role, model, tools, config)
        self.client = Together(api_key=api_key)
        if self.get_param(self.role, "strict"):
            self.tool_schemas = [self.get_tool_schema_strict(tool) for tool in tools.values()]
        else:
            self.tool_schemas = [self.get_tool_schema(tool) for tool in tools.values()]

    @staticmethod
    def get_tool_schema(tool):
        # Based on required format: https://docs.together.ai/docs/function-calling
        return {
            "type": "function",
            "function": {
                "name": tool.NAME,
                "description": tool.DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {n: {"type": p[0], "description": p[1]} for n, p in tool.PARAMETERS.items()},
                    "required": list(tool.REQUIRED_PARAMETERS),
                },
            }
        }

    @staticmethod
    def get_tool_schema_strict(tool):
        # Based on required format: https://docs.together.ai/docs/function-calling
        # Strict mode for structured outputs
        schema = {
            "type": "function",
            "function": {
                "name": tool.NAME,
                "description": tool.DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {n: {"type": p[0], "description": p[1]} for n, p in tool.PARAMETERS.items()},
                    "required": list(tool.PARAMETERS.keys()),
                    "additionalProperties": False
                },
                "strict": True
            }
        }
        # Add null type to property for strict mode
        for propname, prop in schema["function"]["parameters"]["properties"].items():
            if propname not in tool.REQUIRED_PARAMETERS:
                prop["type"] = [prop["type"], "null"]
        return schema

    def _call_model(self, messages) -> ChatCompletionMessage:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_schemas,
            tool_choice="auto", # TODO try "required" here to force a function call
            temperature=self.get_param(self.role, "temperature"),
            max_tokens=self.get_param(self.role, "max_tokens")
        )

    def calculate_cost(self, response):
        return self.in_price * response.usage.prompt_tokens + self.out_price * response.usage.completion_tokens

    def send(self, messages):
        formatted_messages = []
        for m in messages:
            if m.role == MessageRole.OBSERVATION:
                msg = {"role": "tool",
                       "content": json.dumps(m.tool_data.result),
                       "tool_call_id": m.tool_data.id,
                       "name": m.tool_data.name}
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
        except InvalidRequestError as e:
            return BackendResponse(error=f"Backend Error: {e}")

        if response.tool_calls and len(response.tool_calls) > 0:
            f_call = response.tool_calls[0]
            tool_call = ToolCall(name=f_call.function.name, id=f_call.id,
                                 arguments=f_call.function.arguments)
        else:
            tool_call = None

        return BackendResponse(content=response.content, tool_call=tool_call, cost=cost)
