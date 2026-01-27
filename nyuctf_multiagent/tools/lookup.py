import csv
import os
from pathlib import Path

from ..logging import logger
from .tool import Tool


class LookupCommandTool(Tool):
    """Tool to look up documentation for shell commands available in Kali Linux."""
    
    NAME = "lookup_command"
    DESCRIPTION = """Look up documentation for a shell command. Use this to learn about available security tools and their usage.
- Pass a command name to get its documentation (e.g., "nmap", "sqlmap", "john")
- Pass "list" or "all" to see all available commands with brief descriptions
- Pass a category like "network", "web", "crypto", "forensics", "reversing", "password" to list commands in that category"""
    
    PARAMETERS = {
        "query": ("string", "The command name to look up, 'list'/'all' to see all commands, or a category name"),
    }
    REQUIRED_PARAMETERS = {"query"}
    
    # Default path to the documentation CSV
    DEFAULT_CSV_PATH = Path(__file__).parent.parent.parent.parent / "docker" / "kali" / "commands_documentation.csv"
    
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
    
    def call(self, query=None):
        if query is None:
            return {"error": "Query not provided. Pass a command name, 'list', or a category."}
        
        query = query.strip().lower()
        commands = self._load_commands()
        
        if not commands:
            return {"error": "Commands documentation not available. The CSV file may be missing or empty."}
        
        # List all commands
        if query in ('list', 'all'):
            result = "# Available Commands\n\n"
            by_category = {}
            for cmd_name, cmd_info in sorted(commands.items()):
                cat = cmd_info['category'] or 'other'
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(f"- **{cmd_info['command']}**: {cmd_info['brief']}")
            
            for cat in sorted(by_category.keys()):
                result += f"## {cat.title()}\n"
                result += "\n".join(by_category[cat]) + "\n\n"
            
            return {"documentation": result}
        
        # List commands by category
        categories = set(cmd['category'].lower() for cmd in commands.values() if cmd['category'])
        if query in categories:
            result = f"# {query.title()} Commands\n\n"
            for cmd_name, cmd_info in sorted(commands.items()):
                if cmd_info['category'].lower() == query:
                    result += f"- **{cmd_info['command']}**: {cmd_info['brief']}\n"
            return {"documentation": result}
        
        # Look up specific command
        if query in commands:
            cmd = commands[query]
            result = f"# {cmd['command']}\n\n"
            result += f"**Category:** {cmd['category']}\n\n"
            result += f"**Description:** {cmd['description']}\n\n"
            if cmd['usage']:
                result += f"**Usage:**\n```\n{cmd['usage']}\n```\n\n"
            if cmd['examples']:
                result += f"**Examples:**\n```\n{cmd['examples']}\n```\n"
            return {"documentation": result}
        
        # Fuzzy match - suggest similar commands
        suggestions = [cmd for cmd in commands.keys() if query in cmd or cmd in query]
        if suggestions:
            return {
                "error": f"Command '{query}' not found.",
                "suggestions": f"Did you mean: {', '.join(suggestions[:5])}?"
            }
        
        return {
            "error": f"Command '{query}' not found.",
            "hint": "Use 'list' to see all available commands, or a category like 'network', 'web', 'crypto'."
        }
    
    def print_tool_call(self, tool_call):
        logger.assistant_action(f"**{self.NAME}:** `{tool_call.parsed_arguments.get('query', '')}`")
    
    def print_result(self, tool_result):
        if "error" in tool_result.result:
            logger.print(f"[bold]{self.NAME}[/bold]: [red]{tool_result.result['error']}[/red]", markup=True)
            if "suggestions" in tool_result.result:
                logger.print(f"  {tool_result.result['suggestions']}", markup=True)
        else:
            # Just show a brief confirmation - the full doc goes to the model
            logger.print(f"[bold]{self.NAME}[/bold]: Documentation retrieved", markup=True)
