import os
from subprocess import Popen

from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_markdown(text) -> None:
    """Prints a rich info message. Support Markdown syntax."""

    md = Padding(Markdown(text), 2)
    console.print(md)


def print_step(text) -> None:
    """Prints a rich info message."""

    panel = Panel(Text(text, justify="left"))
    console.print(panel)


def print_table(items) -> None:
    """Prints items in a table."""

    console.print(Columns([Panel(f"[yellow]{item}", expand=True) for item in items]))


def print_substep(text, style="") -> None:
    """Prints a rich colored info message without the panelling."""
    console.print(text, style=style)

     
def format_ordinal(x):
    if 10 <= x % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(x % 10, 'th')
    return f"{x}{suffix}"

def clear_console() -> int:
    return Popen("cls" if os.name == "nt" else "clear", shell=True).wait()

if __name__ == "__main__":
    for i in range(20):
        print(format_ordinal(i))