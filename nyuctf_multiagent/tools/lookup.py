import csv
import os
from pathlib import Path

from ..logging import logger
from .tool import Tool


class ListCommandsTool(Tool):
    """Tool to list all available security commands with brief descriptions."""
    
    NAME = "list_commands"
    DESCRIPTION = "List all available security commands with brief descriptions. Use this to discover what tools are available in the environment."
    
    PARAMETERS = {}
    REQUIRED_PARAMETERS = set()
    
    # Default path to the documentation CSV
    # Path: tools/lookup.py -> nyuctf_multiagent/ -> ctf-agents/ -> docker/kali/
    DEFAULT_CSV_PATH = Path(__file__).parent.parent.parent / "docker" / "kali" / "commands_documentation.csv"
    
    def __init__(self, environment=None, csv_path=None):
        super().__init__()
        self.csv_path = csv_path or self.DEFAULT_CSV_PATH
        self._commands = None
    
    def _load_commands(self):
        """Load commands from CSV file."""
        if self._commands is not None:
            return self._commands
        
        self._commands = {}
        if not os.path.exists(self.csv_path):
            return self._commands
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cmd_name = row.get('command', '').strip().lower()
                    if cmd_name:
                        self._commands[cmd_name] = {
                            'command': row.get('command', '').strip(),
                            'category': row.get('category', '').strip(),
                            'brief': row.get('brief', '').strip(),
                        }
        except Exception:
            pass
        
        return self._commands
    
    def call(self):
        commands = self._load_commands()
        
        if not commands:
            return {"error": "Commands list not available."}
        
        # Group by category
        by_category = {}
        for cmd_name, cmd_info in sorted(commands.items()):
            cat = cmd_info['category'] or 'other'
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f"- {cmd_info['command']} - {cmd_info['brief']}")
        
        result = ""
        for cat in sorted(by_category.keys()):
            result += f"## {cat.title()}\n"
            result += "\n".join(by_category[cat]) + "\n\n"
        
        return {"commands": result}
    
    def print_tool_call(self, tool_call):
        logger.assistant_action(f"**{self.NAME}**")
    
    def print_result(self, tool_result):
        if "error" in tool_result.result:
            logger.print(f"[bold]{self.NAME}[/bold]: [red]{tool_result.result['error']}[/red]", markup=True)
        else:
            logger.print(f"[bold]{self.NAME}[/bold]: Listed {len(self._load_commands())} commands", markup=True)


class LookupCommandTool(Tool):
    """Tool to look up documentation for shell commands available in Kali Linux."""
    
    NAME = "lookup_command"
    DESCRIPTION = """Look up detailed documentation for a specific shell command. Use this to learn about a tool's usage, options, and examples.
Pass the command name to get its documentation (e.g., "nmap", "sqlmap", "john")."""
    
    PARAMETERS = {
        "command": ("string", "The command name to look up (e.g., 'nmap', 'sqlmap', 'john')"),
    }
    REQUIRED_PARAMETERS = {"command"}
    
    # Default path to the documentation CSV
    # Path: tools/lookup.py -> nyuctf_multiagent/ -> ctf-agents/ -> docker/kali/
    DEFAULT_CSV_PATH = Path(__file__).parent.parent.parent / "docker" / "kali" / "commands_documentation.csv"
    
    def __init__(self, environment=None, csv_path=None):
        super().__init__()
        self.csv_path = csv_path or self.DEFAULT_CSV_PATH
        self._commands = None  # Lazy load
    
    def _load_commands(self):
        """Load commands from CSV file."""
        if self._commands is not None:
            return self._commands
        
        self._commands = {}
        if not os.path.exists(self.csv_path):
            logger.print(f"[yellow]Warning: Commands documentation not found at {self.csv_path}[/yellow]", markup=True)
            return self._commands
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cmd_name = row.get('command', '').strip().lower()
                    if cmd_name:
                        self._commands[cmd_name] = {
                            'command': row.get('command', '').strip(),
                            'category': row.get('category', '').strip(),
                            'brief': row.get('brief', '').strip(),
                            'description': row.get('description', '').strip(),
                            'usage': row.get('usage', '').strip(),
                            'examples': row.get('examples', '').strip(),
                        }
        except Exception as e:
            logger.print(f"[red]Error loading commands documentation: {e}[/red]", markup=True)
        
        return self._commands
    
    def call(self, command=None):
        if command is None:
            return {"error": "Command name not provided. Use list_commands to see available commands."}
        
        command = command.strip().lower()
        commands = self._load_commands()
        
        if not commands:
            return {"error": "Commands documentation not available."}
        
        # Look up specific command
        if command in commands:
            cmd = commands[command]
            result = f"# {cmd['command']}\n\n"
            result += f"**Category:** {cmd['category']}\n\n"
            result += f"**Description:** {cmd['description']}\n\n"
            if cmd['usage']:
                result += f"**Usage:**\n```\n{cmd['usage']}\n```\n\n"
            if cmd['examples']:
                result += f"**Examples:**\n```\n{cmd['examples']}\n```\n"
            return {"documentation": result}
        
        # Fuzzy match - suggest similar commands
        suggestions = [cmd for cmd in commands.keys() if command in cmd or cmd in command]
        if suggestions:
            return {
                "error": f"Command '{command}' not found.",
                "suggestions": f"Did you mean: {', '.join(suggestions[:5])}?"
            }
        
        return {
            "error": f"Command '{command}' not found.",
            "hint": "Use list_commands to see all available commands."
        }
    
    def print_tool_call(self, tool_call):
        logger.assistant_action(f"**{self.NAME}:** `{tool_call.parsed_arguments.get('command', '')}`")
    
    def print_result(self, tool_result):
        if "error" in tool_result.result:
            logger.print(f"[bold]{self.NAME}[/bold]: [red]{tool_result.result['error']}[/red]", markup=True)
            if "suggestions" in tool_result.result:
                logger.print(f"  {tool_result.result['suggestions']}", markup=True)
        else:
            # Just show a brief confirmation - the full doc goes to the model
            logger.print(f"[bold]{self.NAME}[/bold]: Documentation retrieved", markup=True)
