"""
Display utilities for beautiful CLI output using Rich.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from typing import Dict, Optional

console = Console()


def print_header(title: str):
    """Print a prominent section header."""
    console.print()
    console.print(Panel(
        f"[bold cyan]{title}[/bold cyan]",
        style="cyan",
        padding=(0, 2)
    ))


def print_separator():
    """Print a separator line."""
    console.print("[dim]" + "─" * 70 + "[/dim]")


def print_success(message: str, details: Optional[Dict[str, str]] = None):
    """Print a beautiful success message with optional details."""
    content = f"[bold green]✅ {message}[/bold green]"
    
    if details:
        content += "\n\n"
        for key, value in details.items():
            content += f"[cyan]{key}:[/cyan] {value}\n"
    
    console.print()
    console.print(Panel(
        content.strip(),
        border_style="green",
        padding=(1, 2)
    ))


def print_error(message: str, fix: Optional[str] = None, title: str = "Error"):
    """Print a beautiful error message with optional fix suggestion."""
    content = f"[bold red]❌ {message}[/bold red]"
    
    if fix:
        content += "\n\n[bold cyan]💡 How to fix:[/bold cyan]\n"
        content += f"[yellow]{fix}[/yellow]"
    
    console.print()
    console.print(Panel(
        content,
        title=title,
        border_style="red",
        padding=(1, 2)
    ))


def print_warning(message: str, details: Optional[str] = None):
    """Print a warning message."""
    content = f"[bold yellow]⚠️  {message}[/bold yellow]"
    
    if details:
        content += f"\n\n{details}"
    
    console.print()
    console.print(Panel(
        content,
        border_style="yellow",
        padding=(1, 2)
    ))


def print_info(message: str, details: Optional[str] = None):
    """Print an info message."""
    content = f"[bold blue]💡 {message}[/bold blue]"
    
    if details:
        content += f"\n\n{details}"
    
    console.print()
    console.print(Panel(
        content,
        border_style="blue",
        padding=(1, 2)
    ))


def print_section(title: str):
    """Print a section title."""
    console.print(f"\n[bold]{title}[/bold]")
    print_separator()


def format_dict_table(data: Dict[str, str], title: str = "") -> Table:
    """Format a dictionary as a nice table."""
    table = Table(title=title, show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan", justify="right")
    table.add_column("Value", style="white")
    
    for key, value in data.items():
        table.add_row(key, str(value))
    
    return table


def confirm(question: str, default: bool = True) -> bool:
    """Ask a yes/no question with rich formatting."""
    from rich.prompt import Confirm
    return Confirm.ask(f"[bold cyan]{question}[/bold cyan]", default=default)


def prompt(question: str, default: str = None, password: bool = False) -> str:
    """Prompt for input with rich formatting."""
    from rich.prompt import Prompt
    return Prompt.ask(f"[bold cyan]{question}[/bold cyan]", default=default, password=password)


def handle_exception(error: Exception):
    """Handle exceptions with beautiful error display."""
    from ..exceptions import LoggerheadsError
    
    if isinstance(error, LoggerheadsError):
        print_error(error.message, fix=error.fix, title=error.__class__.__name__)
    else:
        # Unknown error
        print_error(
            str(error),
            fix="If this persists, please report at: https://github.com/stElmitchay/loggerheads/issues",
            title="Unexpected Error"
        )


# Backwards compatibility - legacy print functions still work
def print_simple_header(title: str):
    """Simple header for backwards compatibility."""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_simple_error(message: str):
    """Simple error for backwards compatibility."""
    print(f"\n❌ {message}")
