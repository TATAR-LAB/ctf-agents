"""
Vertex AI Backend for D-CIPHER
Uses Application Default Credentials (ADC) - no API key needed!
Authenticate with: gcloud auth application-default login
"""
import json
import uuid
from google import genai
from google.genai.types import (
    FunctionDeclaration, 
    GenerateContentConfig, 
    Tool, 
    Part, 
    Content,
    FunctionCall
)

from ..conversation import MessageRole
from ..tools import ToolCall, ToolResult

from .backend import Backend, BackendResponse


class VertexAIBackend(Backend):
    NAME = 'vertexai'
    # Models are now defined in models.yaml
    
    # Default location, can be overridden
    LOCATION = "us-central1"

    def __init__(self, role, model, tools, api_key, config):
        super().__init__(role, model, tools, config)
        # api_key can contain "project_id:location" or just use defaults
        # e.g., "my-project:us-central1" or just "my-project"
        project_id = None
        location = self.LOCATION
        
        if api_key and api_key.lower() != "adc":
            parts = api_key.split(":")
            project_id = parts[0] if parts[0] else None
            if len(parts) > 1:
                location = parts[1]
        
        # Initialize client with Vertex AI (uses ADC automatically)
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        self.model = model
        self.tool_declarations = [self.get_tool_schema(tool) for tool in tools.values()]
        self.tool = Tool(function_declarations=self.tool_declarations)

    @staticmethod
    def get_tool_schema(tool):
        """Convert tool to Vertex AI FunctionDeclaration format"""
        return FunctionDeclaration(
            name=tool.NAME,
            description=tool.DESCRIPTION,
            parameters={
                "type": "object",
                "properties": {n: {"type": p[0], "description": p[1]} for n, p in tool.PARAMETERS.items()},
                "required": list(tool.REQUIRED_PARAMETERS),
            }
        )

    def _call_model(self, system, messages):
        config = GenerateContentConfig(
            temperature=self.get_param(self.role, "temperature"),
            max_output_tokens=int(self.get_param(self.role, "max_tokens")),
            tools=[self.tool],
            system_instruction=str(system) if system else None
        )
        
        return self.client.models.generate_content(
            model=self.model,
            contents=messages,
            config=config
        )

    def calculate_cost(self, response):
        usage = response.usage_metadata
        if usage:
            # Token counts can be None for some responses
            prompt_tokens = usage.prompt_token_count or 0
            output_tokens = usage.candidates_token_count or 0
            return (self.in_price * prompt_tokens + 
                    self.out_price * output_tokens)
        return 0

    def send(self, messages):
        formatted_messages = []
        system = None
        
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                system = m.content
                continue
            if m.role == MessageRole.OBSERVATION:
                # Function response - wrap in Content
                part = Part.from_function_response(
                    name=m.tool_data.name,
                    response={"result": m.tool_data.result}
                )
                msg = Content(role="user", parts=[part])
            elif m.role == MessageRole.ASSISTANT:
                if m.tool_data is not None:
                    # Function call from assistant - must preserve thought_signature for Gemini 3
                    args = m.tool_data.arguments
                    if isinstance(args, str):
                        args = json.loads(args)
                    
                    # Check if we have a thought_signature to preserve (required for Gemini 3)
                    thought_sig = getattr(m.tool_data, 'thought_signature', None)
                    # Gemini 3 models REQUIRE thought_signature for function calls
                    # If we don't have one from a previous response, use the skip validator workaround
                    if not thought_sig:
                        thought_sig = "skip_thought_signature_validator"
                    
                    # Create Part with thought_signature for Gemini 3 compatibility
                    part = Part(
                        function_call=FunctionCall(name=m.tool_data.name, args=args),
                        thought_signature=thought_sig
                    )
                    msg = Content(role="model", parts=[part])
                else:
                    part = Part.from_text(text=m.content or "No response")
                    msg = Content(role="model", parts=[part])
            else:
                # User message
                part = Part.from_text(text=m.content or "")
                msg = Content(role="user", parts=[part])
            formatted_messages.append(msg)

        try:
            response = self._call_model(system, formatted_messages)
            cost = self.calculate_cost(response)
        except Exception as e:
            return BackendResponse(error=f"Vertex AI Error: {e}")

        try:
            candidates = response.candidates
            if not candidates:
                return BackendResponse(content=None, tool_call=None, cost=0)
            
            parts = candidates[0].content.parts
            content = None
            tool_call = None
            
            for part in parts:
                if hasattr(part, 'text') and part.text:
                    content = part.text
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    # Capture thought_signature from response (required for Gemini 3)
                    thought_sig = getattr(part, 'thought_signature', None)
                    tool_call = ToolCall(
                        name=fc.name, 
                        id=str(uuid.uuid4()),
                        arguments=dict(fc.args) if fc.args else {},
                        thought_signature=thought_sig
                    )
                    
        except Exception as e:
            return BackendResponse(error=f"Response parsing error: {e}")

        return BackendResponse(content=content, tool_call=tool_call, cost=cost)
