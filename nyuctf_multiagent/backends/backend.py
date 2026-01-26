import json
from dataclasses import dataclass
from enum import Enum

from ..tools import ToolResult

class Role(Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    AUTOPROMPTER = "autoprompter"

@dataclass(kw_only=True)
class BackendResponse:
    """Holds the backend response"""
    content: str=None
    error: str=None
    tool_call: object=None
    cost: float=0

    def __str__(self):
        return (f"content='{self.content}'" if self.content else "") + \
                (f"tool_call='{self.tool_call.arguments}'" if self.tool_call else "") + \
                (f"error='{self.error}'" if self.error else "") + \
                (f"cost={self.cost}")

class Backend:
    """Base class for LLM Backend"""
    NAME = "base"  # Set the backend name in subclass

    def __init__(self, role: Role, model, tools, config):
        # Import MODEL_INFO here to avoid circular imports
        from . import MODEL_INFO
        
        if self.NAME == "base":
            raise NotImplementedError("Backend name not set, initialize NAME in the subclass")
        
        if model not in MODEL_INFO:
            # List models available for this backend
            available = [m for m, info in MODEL_INFO.items() 
                        if info.get('backend', self.NAME) == self.NAME or m in getattr(self.__class__, 'MODELS', {})]
            raise KeyError(f"Model {model} not found in models.yaml.\n" + \
                          f"Available models for {self.NAME}: {', '.join(available[:10])}{'...' if len(available) > 10 else ''}")
        
        model_info = MODEL_INFO[model]
        self.role = role
        self.model = model
        self.tools = tools
        self.config = config
        # Explicitly convert to float in case YAML parsed as string
        self.in_price = float(model_info["cost_per_input_token"])
        self.out_price = float(model_info["cost_per_output_token"])

    def get_param(self, role: Role, param: str):
        try:
            return getattr(getattr(self.config, role.value), param)
        except AttributeError as e:
            raise ValueError(f"Parameter did not exist '{role.value}.{param}'") from e

    def parse_tool_arguments(self, tool_call):
        # Don't need to parse if the arguments are already parsed;
        # this can happen if the tool call was created with parsed arguments
        if tool_call.parsed_arguments:
            return True, tool_call
        try:
            if type(tool_call.arguments) == str:
                tool_call.parsed_arguments = json.loads(tool_call.arguments)
            else:
                tool_call.parsed_arguments = tool_call.arguments

            if tool_call.name not in self.tools:
                # The parsed tool call was not found in our set of tools, return error
                tool_res = ToolResult.error_for_call(
                                tool_call, f"Tool {tool_call.name} not found. Use one of the provided tools: {list(self.tools.keys())}")
                return False, tool_res

            tool = self.tools[tool_call.name]

            present = set(tool_call.parsed_arguments.keys())
            if missing := (tool.REQUIRED_PARAMETERS - present):
                tool_res = ToolResult.error_for_call(
                                tool_call, f"Missing required parameters for {tool_call.name}: {missing}")
                return False, tool_res
            # Cleanup extra params
            for extra_param in (present - set(tool.PARAMETERS.keys())):
                del tool_call.parsed_arguments[extra_param]
            # Cast the params correctly
            for param in tool.PARAMETERS:
                ty = tool.PARAMETERS[param][0]
                if param in tool_call.parsed_arguments and ty == "number":
                    tool_call.parsed_arguments[param] = float(tool_call.parsed_arguments[param])

            return True, tool_call
        except json.JSONDecodeError as e:
            tool_res = ToolResult.error_for_call(
                            tool_call, f"{type(e).__name__} while decoding parameters for {tool_call.name}: {e}")
            return False, tool_res
        except ValueError as e:
            msg = f"Type error in parameters for {tool_call.name}: {e}"
            tool_res = ToolResult.error_for_call(tool_call, msg)
            return False, tool_res

