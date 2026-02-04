"""
Security validation script for Silver Tier AI Employee.

Scans vault and repository for exposed credentials (API keys, tokens, passwords).
Ensures success criterion SC-003: Zero credentials in vault/repo.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Credential patterns to detect
CREDENTIAL_PATTERNS = {
    "API Key": [
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI-style API keys
        r"API[_-]?KEY[\"']?\s*[:=]\s*[\"']?[a-zA-Z0-9]{16,}",  # Generic API keys
        r"api[_-]?key[\"']?\s*[:=]\s*[\"']?[a-zA-Z0-9]{16,}",  # Lowercase api key
    ],
    "OAuth Token": [
        r"ya29\.[a-zA-Z0-9_-]{100,}",  # Google OAuth tokens
        r"[Bb]earer\s+[a-zA-Z0-9_-]{40,}",  # Bearer tokens
        r"access[_-]?token[\"']?\s*[:=]\s*[\"']?[a-zA-Z0-9]{32,}",  # Access tokens
    ],
    "AWS Credentials": [
        r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
        r"aws[_-]?secret[_-]?access[_-]?key",  # AWS secret key
    ],
    "GitHub Token": [
        r"ghp_[a-zA-Z0-9]{36,}",  # GitHub personal access token
        r"gho_[a-zA-Z0-9]{36,}",  # GitHub OAuth token
    ],
    "Password": [
        r"password[\"']?\s*[:=]\s*[\"']?[a-zA-Z0-9!@#$%^&*]{8,}[\"']?",  # Generic passwords
    ],
    "LinkedIn Token": [
        r"LINKEDIN[_-]?ACCESS[_-]?TOKEN[\"']?\s*[:=]",  # LinkedIn token
    ],
}

# Files/directories to exclude from scanning
EXCLUDE_PATTERNS = [
    ".git/",
    ".venv/",
    "venv/",
    "__pycache__/",
    "node_modules/",
    ".pytest_cache/",
    ".env.example",  # Example file is OK
    ".specify/",  # Spec files are OK
    "scripts/validate/",  # This script itself
    "history/",  # Prompt history is OK
]

# Allowed credential references (templates, documentation)
ALLOWED_PATTERNS = [
    r"<WILL_BE_FILLED_DURING_SETUP>",  # Template placeholder
    r"<REDACTED",  # Already redacted
    r"\*\*\*\*",  # Masked credential
    r"EXAMPLE",  # Example credentials
    r"your-api-key-here",  # Documentation placeholder
]


def should_exclude(filepath: Path, base_path: Path) -> bool:
    """
    Check if file should be excluded from scanning.

    Args:
        filepath: Path to file
        base_path: Base path of repository

    Returns:
        True if file should be excluded
    """
    relative_path = str(filepath.relative_to(base_path))

    for pattern in EXCLUDE_PATTERNS:
        if pattern in relative_path:
            return True

    return False


def is_allowed_credential(line: str) -> bool:
    """
    Check if detected credential is actually a placeholder/template.

    Args:
        line: Line containing potential credential

    Returns:
        True if this is an allowed placeholder
    """
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Scan a single file for credentials.

    Args:
        filepath: Path to file to scan

    Returns:
        List of (line_number, credential_type, matching_line) tuples
    """
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip if this line contains allowed placeholders
                if is_allowed_credential(line):
                    continue

                # Check against all credential patterns
                for cred_type, patterns in CREDENTIAL_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append((line_num, cred_type, line.strip()))
                            break  # Only report once per line

    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return findings


def scan_directory(directory: Path) -> Dict[Path, List[Tuple[int, str, str]]]:
    """
    Recursively scan directory for credentials.

    Args:
        directory: Directory to scan

    Returns:
        Dictionary mapping file paths to list of findings
    """
    all_findings = {}

    for filepath in directory.rglob("*"):
        if not filepath.is_file():
            continue

        if should_exclude(filepath, directory):
            continue

        findings = scan_file(filepath)
        if findings:
            all_findings[filepath] = findings

    return all_findings


def print_findings(findings: Dict[Path, List[Tuple[int, str, str]]], base_path: Path) -> None:
    """
    Print findings in a readable format.

    Args:
        findings: Dictionary of file paths to findings
        base_path: Base path for relative path display
    """
    if not findings:
        print("✅ No credentials found in vault or repository!")
        print("")
        print("Security scan PASSED:")
        print("  - Zero API keys detected")
        print("  - Zero OAuth tokens detected")
        print("  - Zero passwords detected")
        print("  - Zero AWS credentials detected")
        print("  - Zero GitHub tokens detected")
        print("")
        print("Success criterion SC-003: SATISFIED ✓")
        return

    print("❌ SECURITY SCAN FAILED - Credentials detected!")
    print("")
    print(f"Found {len(findings)} file(s) with potential credential exposure:")
    print("")

    for filepath, file_findings in findings.items():
        relative_path = filepath.relative_to(base_path)
        print(f"📁 {relative_path}")

        for line_num, cred_type, line in file_findings:
            print(f"   Line {line_num}: [{cred_type}]")
            print(f"   {line[:100]}...")  # Truncate long lines

        print("")

    print("🔧 Remediation steps:")
    print("  1. Move credentials to .env file (already in .gitignore)")
    print("  2. Use environment variables: os.getenv('API_KEY')")
    print("  3. Update .env.example with placeholder values")
    print("  4. Ensure .env is in .gitignore")
    print("  5. Re-run this script to verify")
    print("")
    print("Success criterion SC-003: FAILED ✗")


def main():
    """
    Main entry point for security validation.
    """
    print("=" * 70)
    print("  Silver Tier AI Employee - Security Validation")
    print("=" * 70)
    print("")

    # Get repository root
    repo_root = Path(__file__).parent.parent.parent
    print(f"Scanning repository: {repo_root}")
    print("")

    # Scan vault
    vault_path = repo_root / "AI_Employee_Vault"
    print(f"Scanning vault: {vault_path}")

    vault_findings = {}
    if vault_path.exists():
        vault_findings = scan_directory(vault_path)
        print(f"  Found {len(vault_findings)} file(s) with potential issues in vault")
    else:
        print(f"  Vault not found (skipping)")

    # Scan repository (excluding vault since we already scanned it)
    print(f"Scanning repository files...")
    repo_findings = scan_directory(repo_root)

    # Remove vault findings from repo findings (avoid double-counting)
    for vault_file in vault_findings.keys():
        repo_findings.pop(vault_file, None)

    print(f"  Found {len(repo_findings)} file(s) with potential issues in repository")
    print("")

    # Combine findings
    all_findings = {**vault_findings, **repo_findings}

    # Print results
    print_findings(all_findings, repo_root)

    # Exit with appropriate code
    sys.exit(0 if not all_findings else 1)


if __name__ == "__main__":
    main()
