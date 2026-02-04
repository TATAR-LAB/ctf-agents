from .tool import Tool, ToolCall, ToolResult

# Tools
from .misc import SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool, GenAutoPromptTool
from .run_command import RunCommandTool
from .editing import CreateFileTool
from .reversing import DisassembleTool, DecompileTool
from .lookup import LookupCommandTool, ListCommandsTool

ALLTOOLS = {RunCommandTool, SubmitFlagTool, GiveupTool, CreateFileTool, GenAutoPromptTool,
            DelegateTool, FinishTaskTool, DisassembleTool, DecompileTool, LookupCommandTool,
            ListCommandsTool}
# Not needed, defined in config
# TOOLSETS = {
#     "default": {RunCommandTool, CreateFileTool, SubmitFlagTool, GiveupTool},
#     "planner": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
#     "executor": {RunCommandTool, CreateFileTool, FinishTaskTool, DisassembleTool, DecompileTool} # TODO add other tools
# }

