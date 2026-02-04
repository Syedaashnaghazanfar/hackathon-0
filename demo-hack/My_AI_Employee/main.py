#!/usr/bin/env python3
"""
Main entry point for Bronze Tier AI Employee.

This is a simpler alternative to run_watcher.py that follows the
reference implementation pattern.

Usage:
    uv run python -m My_AI_Employee.main
    python -m My_AI_Employee.main

Configuration is loaded from .env file in the project root.
"""

import sys
from .run_watcher import main

if __name__ == '__main__':
    sys.exit(main())
