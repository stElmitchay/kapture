"""
Command-line interface for loggerheads - refactored and modular.

This file is now a simple wrapper that delegates to the new modular cli/ package.
The old 1,014 line implementation has been split into clean, maintainable modules.
"""

from .cli import main

# Preserve backwards compatibility
if __name__ == "__main__":
    main()
