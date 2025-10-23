"""
Display utilities for clean CLI output.
"""

def print_header(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_separator():
    """Print a separator line."""
    print("-"*70)


def print_success(message):
    """Print success message."""
    print(f"\n✅ {message}")


def print_error(message):
    """Print error message."""
    print(f"\n❌ {message}")


def print_warning(message):
    """Print warning message."""
    print(f"\n⚠️  {message}")


def print_info(message):
    """Print info message."""
    print(f"\n💡 {message}")


def print_section(title):
    """Print a section title."""
    print(f"\n{title}")
    print_separator()
