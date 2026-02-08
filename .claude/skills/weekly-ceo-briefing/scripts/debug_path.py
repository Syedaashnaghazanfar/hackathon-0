#!/usr/bin/env python3
from pathlib import Path
import sys

# Simulate being in revenue_analyzer.py
p = Path(__file__).parent.parent.parent.parent / "scripts"
print(f"Calculated path: {p}")
print(f"Absolute path: {p.resolve()}")
print(f"Exists: {p.resolve().exists()}")

# Check if shared folder exists at that location
shared_path = p.resolve() / "shared"
print(f"Shared path: {shared_path}")
print(f"Shared exists: {shared_path.exists()}")

if shared_path.exists():
    print(f"Files in shared: {list(shared_path.glob('*.py'))}")

sys.path.insert(0, str(p.resolve()))
print(f"\nsys.path[0]: {sys.path[0]}")

try:
    import shared
    print("Import shared successful!")
    from shared.vault_ops import VaultOps
    print("Import VaultOps successful!")
except Exception as e:
    print(f"Import failed: {e}")
