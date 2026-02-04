"""
Deduplication utility for Silver Tier AI Employee.

Provides SHA256 content hashing for preventing duplicate message processing across watchers.
"""

import hashlib
from typing import Optional


def compute_content_hash(content: str, metadata: Optional[dict] = None) -> str:
    """
    Compute SHA256 hash of message content for deduplication.

    Args:
        content: The message content (email body, WhatsApp message, LinkedIn notification)
        metadata: Optional metadata to include in hash (sender, timestamp, subject)

    Returns:
        Hexadecimal SHA256 hash string

    Example:
        >>> compute_content_hash("Hello world", {"sender": "user@example.com"})
        'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'
    """
    hasher = hashlib.sha256()

    # Hash content
    hasher.update(content.encode("utf-8"))

    # Hash metadata if provided
    if metadata:
        # Sort keys for deterministic hashing
        for key in sorted(metadata.keys()):
            value = str(metadata[key])
            hasher.update(f"{key}:{value}".encode("utf-8"))

    return hasher.hexdigest()


def is_duplicate(content_hash: str, processed_hashes: set[str]) -> bool:
    """
    Check if content hash has been processed before.

    Args:
        content_hash: The SHA256 hash to check
        processed_hashes: Set of previously processed hashes

    Returns:
        True if duplicate, False otherwise

    Example:
        >>> processed = {"abc123", "def456"}
        >>> is_duplicate("abc123", processed)
        True
        >>> is_duplicate("xyz789", processed)
        False
    """
    return content_hash in processed_hashes


def add_to_processed(content_hash: str, processed_hashes: set[str]) -> None:
    """
    Add content hash to processed set.

    Args:
        content_hash: The SHA256 hash to add
        processed_hashes: Set of previously processed hashes (modified in-place)

    Example:
        >>> processed = set()
        >>> add_to_processed("abc123", processed)
        >>> "abc123" in processed
        True
    """
    processed_hashes.add(content_hash)
