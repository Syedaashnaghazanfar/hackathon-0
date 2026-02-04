#!/usr/bin/env python3
"""Check executor status and health."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_executor_status():
    """Display executor status."""
    vault_root = Path(os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault'))

    approved = list((vault_root / 'Approved').glob('*.md')) if (vault_root / 'Approved').exists() else []
    done = list((vault_root / 'Done').glob('*.md')) if (vault_root / 'Done').exists() else []
    failed = list((vault_root / 'Failed').glob('*.md')) if (vault_root / 'Failed').exists() else []

    print("\n" + "=" * 70)
    print("MCP EXECUTOR STATUS DASHBOARD")
    print("=" * 70 + "\n")

    print(f"Pending Execution: {len(approved)} items")
    print(f"Successfully Executed: {len(done)} items")
    print(f"Failed (awaiting retry): {len(failed)} items")

    if approved:
        print(f"\nPending Items:")
        for f in approved[:5]:
            print(f"  - {f.name}")
        if len(approved) > 5:
            print(f"  ... and {len(approved) - 5} more")

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    check_executor_status()
