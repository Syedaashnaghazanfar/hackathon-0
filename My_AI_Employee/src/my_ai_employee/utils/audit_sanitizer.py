"""
Audit log sanitization for compliance.
"""

import re
import logging

logger = logging.getLogger(__name__)

SENSITIVE_PATTERNS = [
    (r'api[_-]?key\s*[:=]\s*[\'"]?[\w-]+[\'"]?', 'API_KEY'),
    (r'password\s*[:=]\s*[\'"]?[\w-]+[\'"]?', 'PASSWORD'),
    (r'token\s*[:=]\s*[\'"]?[\w.-]+[\'"]?', 'TOKEN'),
]

def sanitize_credentials(data, mask_char='***'):
    """Sanitize sensitive credentials from data."""
    if isinstance(data, dict):
        return {k: sanitize_credentials(v, mask_char) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [sanitize_credentials(item, mask_char) for item in data]
    elif isinstance(data, str):
        sanitized = data
        for pattern, name in SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, mask_char, sanitized, flags=re.IGNORECASE)
        return sanitized
    else:
        return data

def sanitize_for_log(data):
    """Convert data to safe log string with credentials masked."""
    import json
    safe_data = sanitize_credentials(data)
    try:
        return json.dumps(safe_data, default=str)
    except:
        return str(safe_data)
