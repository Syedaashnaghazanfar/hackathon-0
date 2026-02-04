#!/usr/bin/env python3
"""
LinkedIn MCP Server - REST API v2 Implementation

Publish posts to LinkedIn via official REST API v2 (not browser automation).
Uses OAuth2 authentication and complies with LinkedIn Terms of Service.

Type-safe with Pydantic v2 models for validation.
Integrated with AuditLogger for Silver tier compliance.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any, Literal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv
import requests

from utils.audit_logger import AuditLogger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="linkedin-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# LinkedIn API Configuration
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN')
LINKEDIN_API_BASE_URL = os.getenv('LINKEDIN_API_BASE_URL', 'https://api.linkedin.com/rest')
LINKEDIN_API_VERSION = os.getenv('LINKEDIN_API_VERSION', '202601')

# Rate limiting
_last_post_time: float = 0
_post_delay_seconds: float = 5.0  # Minimum delay between posts

# Error codes
ErrorCode = Literal[
    'AUTH_EXPIRED',
    'RATE_LIMIT_EXCEEDED',
    'INVALID_CONTENT',
    'NETWORK_ERROR',
    'UNKNOWN'
]


# ============================================================================
# PYDANTIC MODELS - Type-safe LinkedIn post validation
# ============================================================================

class LinkedInPostRequest(BaseModel):
    """LinkedIn post request model with validation."""

    text: str = Field(..., description="Post content text (1-3000 characters)")
    visibility: str = Field(default='PUBLIC', description="Post visibility: PUBLIC or CONNECTIONS")
    hashtags: list[str] = Field(default_factory=list, description="Hashtags (without # symbol, max 10)")
    link_url: Optional[str] = Field(default=None, description="Optional URL to share")
    link_title: Optional[str] = Field(default=None, description="Title for shared link")
    link_description: Optional[str] = Field(default=None, description="Description for shared link")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Post text must be 1-3000 characters."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Post text cannot be empty')
        if len(v) > 3000:
            raise ValueError(f'Post text exceeds 3000 character limit ({len(v)} chars)')
        return v

    @field_validator('hashtags')
    @classmethod
    def validate_hashtags(cls, v):
        """Limit hashtags to 10."""
        if len(v) > 10:
            raise ValueError(f'Maximum 10 hashtags allowed ({len(v)} provided)')
        return v


class LinkedInPostResponse(BaseModel):
    """LinkedIn post response model."""

    status: str = Field(..., description="Status: published or error")
    post_id: str = Field(default="", description="LinkedIn post ID")
    post_url: str = Field(default="", description="URL of published post")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_code: Optional[ErrorCode] = Field(default=None, description="Error code if failed")


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimitHandler:
    """Handles rate limiting with exponential backoff retry."""

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 16.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_after: Optional[float] = None

    def should_retry(self, response: requests.Response, attempt: int) -> bool:
        """Check if request should be retried based on response."""
        if attempt >= self.max_retries:
            return False

        if response.status_code == 429:
            # Get retry-after header if present
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                self.retry_after = float(retry_after)
            else:
                self.retry_after = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
            return True

        return False

    def wait_for_retry(self, attempt: int) -> None:
        """Wait before retrying request."""
        delay = self.retry_after or min(
            self.base_delay * (2 ** attempt),
            self.max_delay
        )
        logger.info(f"Waiting {delay}s before retry (attempt {attempt + 1})")
        time.sleep(delay)
        self.retry_after = None


def _classify_linkedin_error(response: requests.Response) -> tuple[str, ErrorCode]:
    """
    Classify LinkedIn API error response into error message and code.

    Args:
        response: The requests Response object.

    Returns:
        Tuple of (error_message, error_code).
    """
    status_code = response.status_code

    try:
        error_data = response.json()
        error_msg = error_data.get('message', error_data.get('error', str(response.text)))
    except Exception:
        error_msg = response.text[:500] if response.text else f'HTTP {status_code}'

    if status_code == 401:
        return error_msg, 'AUTH_EXPIRED'
    elif status_code == 403:
        return error_msg, 'AUTH_EXPIRED'
    elif status_code == 429:
        return error_msg, 'RATE_LIMIT_EXCEEDED'
    elif status_code in (400, 422):
        return error_msg, 'INVALID_CONTENT'
    elif status_code in (502, 503, 504):
        return error_msg, 'NETWORK_ERROR'
    else:
        return error_msg, 'UNKNOWN'


def _enforce_rate_limit() -> None:
    """Enforce minimum delay between posts."""
    global _last_post_time

    if _last_post_time > 0:
        elapsed = time.time() - _last_post_time
        if elapsed < _post_delay_seconds:
            wait_time = _post_delay_seconds - elapsed
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)


def _get_headers() -> dict[str, str]:
    """Get headers required for LinkedIn API v2 requests."""
    return {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': LINKEDIN_API_VERSION,
        'Content-Type': 'application/json'
    }


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def create_post(
    text: str,
    visibility: str = 'PUBLIC',
    hashtags: list[str] | None = None,
    link_url: str | None = None,
    link_title: str | None = None,
    link_description: str | None = None,
    entry_id: str = ""
) -> dict[str, Any]:
    """
    Create a new LinkedIn post on user's profile via REST API v2.

    Args:
        text: Post content/commentary (1-3000 chars).
        visibility: Post visibility level - 'PUBLIC' or 'CONNECTIONS'.
        hashtags: Optional list of hashtags (without # symbol, max 10).
        link_url: Optional URL to share.
        link_title: Title for shared link.
        link_description: Description for shared link.
        entry_id: Audit log entry ID for tracking (optional).

    Returns:
        Dict with status, post_id, post_url, timestamp, or error details.
    """
    global _last_post_time
    start_time = datetime.now(timezone.utc)

    try:
        # Validate inputs with Pydantic
        request = LinkedInPostRequest(
            text=text,
            visibility=visibility,
            hashtags=hashtags or [],
            link_url=link_url,
            link_title=link_title,
            link_description=link_description
        )

        # Check configuration
        if not LINKEDIN_ACCESS_TOKEN:
            return {
                'status': 'error',
                'error': 'LinkedIn access token not configured. Run: python scripts/linkedin_oauth2_setup.py',
                'error_code': 'AUTH_EXPIRED',
                'timestamp': start_time.isoformat()
            }

        if not LINKEDIN_PERSON_URN:
            return {
                'status': 'error',
                'error': 'LinkedIn person URN not configured',
                'error_code': 'AUTH_EXPIRED',
                'timestamp': start_time.isoformat()
            }

        # Enforce rate limit between posts
        _enforce_rate_limit()

        # Build post commentary with hashtags
        commentary = request.text
        if request.hashtags:
            hashtag_text = ' '.join(f'#{tag}' for tag in request.hashtags[:10])
            if hashtag_text not in commentary:
                commentary = f'{commentary}\n\n{hashtag_text}'

        # Build request payload per LinkedIn API v2
        payload: dict[str, Any] = {
            'author': LINKEDIN_PERSON_URN,
            'commentary': commentary,
            'visibility': request.visibility,
            'distribution': {
                'feedDistribution': 'MAIN_FEED',
                'targetEntities': [],
                'thirdPartyDistributionChannels': []
            },
            'lifecycleState': 'PUBLISHED',
            'isReshareDisabledByAuthor': False
        }

        # Add link content if provided
        if request.link_url:
            payload['content'] = {
                'article': {
                    'source': request.link_url,
                    'title': request.link_title or '',
                    'description': request.link_description or ''
                }
            }

        # Make request with retry handling
        rate_limiter = RateLimitHandler()
        url = f'{LINKEDIN_API_BASE_URL}/posts'

        for attempt in range(rate_limiter.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=_get_headers(),
                    json=payload,
                    timeout=30
                )

                if response.status_code == 201:
                    # Success - get post ID from header
                    post_id = response.headers.get('x-restli-id', '')
                    post_url = f'https://www.linkedin.com/feed/update/{post_id}'

                    _last_post_time = time.time()
                    execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

                    # Log to audit logger
                    if entry_id:
                        audit_logger.log_action_executed(
                            entry_id=entry_id,
                            action_type='create_linkedin_post',
                            mcp_server='linkedin_mcp',
                            execution_time_ms=execution_time_ms,
                            success=True,
                            result={
                                'post_id': post_id,
                                'post_url': post_url,
                                'text_length': len(request.text)
                            }
                        )

                    return {
                        'status': 'published',
                        'post_id': post_id,
                        'post_url': post_url,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }

                elif rate_limiter.should_retry(response, attempt):
                    rate_limiter.wait_for_retry(attempt)
                    continue

                else:
                    error_msg, error_code = _classify_linkedin_error(response)
                    execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

                    if entry_id:
                        audit_logger.log_action_executed(
                            entry_id=entry_id,
                            action_type='create_linkedin_post',
                            mcp_server='linkedin_mcp',
                            execution_time_ms=execution_time_ms,
                            success=False,
                            error=error_msg
                        )

                    return {
                        'status': 'error',
                        'error': error_msg,
                        'error_code': error_code,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }

            except requests.exceptions.Timeout:
                if attempt < rate_limiter.max_retries - 1:
                    rate_limiter.wait_for_retry(attempt)
                    continue
                return {
                    'status': 'error',
                    'error': 'Request timed out',
                    'error_code': 'NETWORK_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

            except requests.exceptions.ConnectionError as e:
                if attempt < rate_limiter.max_retries - 1:
                    rate_limiter.wait_for_retry(attempt)
                    continue
                return {
                    'status': 'error',
                    'error': str(e),
                    'error_code': 'NETWORK_ERROR',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'error_code': 'UNKNOWN',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

        return {
            'status': 'error',
            'error': 'Max retries exceeded',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    except ValueError as e:
        # Validation error
        return {
            'status': 'error',
            'error': f'Validation error: {str(e)}',
            'error_code': 'INVALID_CONTENT',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_code': 'UNKNOWN',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """
    Check if LinkedIn API is reachable and access token is valid.

    Returns:
        Dict with status, api_reachable, token_valid, and checked_at timestamp.
    """
    result = {
        'status': 'error',
        'api_reachable': False,
        'token_valid': False,
        'checked_at': datetime.now(timezone.utc).isoformat()
    }

    if not LINKEDIN_ACCESS_TOKEN:
        result['error'] = 'LinkedIn access token not configured'
        return result

    try:
        # Use userinfo endpoint to verify token
        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=_get_headers(),
            timeout=10
        )

        result['api_reachable'] = True

        if response.status_code == 200:
            result['token_valid'] = True
            result['status'] = 'available'

            # Extract user info
            data = response.json()
            if 'sub' in data:
                result['person_urn'] = f"urn:li:person:{data['sub']}"
            if 'name' in data:
                result['user_name'] = data['name']

        elif response.status_code == 401:
            result['error'] = 'Access token expired or invalid. Run: python scripts/linkedin_oauth2_setup.py'

        else:
            error_msg, _ = _classify_linkedin_error(response)
            result['error'] = error_msg

    except requests.exceptions.Timeout:
        result['error'] = 'Request timed out'

    except requests.exceptions.ConnectionError as e:
        result['error'] = f'Cannot connect to LinkedIn API: {e}'

    except Exception as e:
        result['error'] = str(e)

    return result


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting LinkedIn MCP Server (REST API v2)")
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Access token configured: {bool(LINKEDIN_ACCESS_TOKEN)}")
    logger.info(f"Person URN: {LINKEDIN_PERSON_URN or 'Not configured'}")
    mcp.run()
