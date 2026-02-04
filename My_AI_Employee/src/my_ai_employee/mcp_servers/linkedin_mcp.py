"""
LinkedIn MCP server for Silver Tier AI Employee.

Implements FastMCP server with publish_post tool using LinkedIn REST API v2.
"""

import os
import logging
import time
from typing import Optional

import requests
from fastmcp import FastMCP

from my_ai_employee.config import get_config


logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("linkedin")


def _exponential_backoff_retry(func, max_retries=3, backoff_seconds=[1, 2, 4]):
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        backoff_seconds: List of backoff durations

    Returns:
        Function result or raises last exception
    """
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    wait_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
                    logger.warning(
                        f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
                logger.warning(
                    f"Request failed, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}"
                )
                time.sleep(wait_time)
            else:
                raise


@mcp.tool()
def publish_post(
    content: str,
    visibility: str = "PUBLIC",
    hashtags: Optional[list[str]] = None,
) -> dict:
    """
    Publish post to LinkedIn.

    Args:
        content: Post content text
        visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
        hashtags: Optional list of hashtags to include

    Returns:
        Dictionary with status and post_id or error

    Example:
        >>> publish_post(
        ...     content="Excited to share my latest project!",
        ...     visibility="PUBLIC",
        ...     hashtags=["AI", "Python"]
        ... )
        {'status': 'success', 'post_id': 'urn:li:share:123456'}
    """
    config = get_config()

    # Add hashtags to content
    if hashtags:
        content += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would publish LinkedIn post with visibility '{visibility}'")
        logger.info(f"DRY RUN: Content preview: {content[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: LinkedIn post not actually published",
            "content_preview": content[:100],
            "visibility": visibility,
        }

    try:
        # Get access token and person URN from config
        access_token = config.linkedin_access_token
        person_urn = config.linkedin_person_urn

        if not access_token or not person_urn:
            return {
                "status": "error",
                "error_type": "missing_credentials",
                "error_message": "LinkedIn access token or person URN not configured in .env",
            }

        # LinkedIn API endpoint
        url = "https://api.linkedin.com/v2/ugcPosts"

        # Request headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # Map visibility to LinkedIn visibility code
        visibility_map = {
            "PUBLIC": "PUBLIC",
            "CONNECTIONS": "CONNECTIONS",
            "LOGGED_IN": "LOGGED_IN",
        }
        linkedin_visibility = visibility_map.get(visibility.upper(), "PUBLIC")

        # Request payload
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": linkedin_visibility},
        }

        # Retry with exponential backoff
        def _post():
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response

        response = _exponential_backoff_retry(_post, max_retries=3, backoff_seconds=[1, 2, 4])

        # Extract post ID from response
        post_data = response.json()
        post_id = post_data.get("id")

        logger.info(f"LinkedIn post published successfully, post ID: {post_id}")

        return {
            "status": "success",
            "post_id": post_id,
            "visibility": linkedin_visibility,
            "content_preview": content[:100],
        }

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        error_message = str(e)

        # Handle specific error codes
        if error_code == 401:
            logger.error(f"Authentication failed: {error_message}")
            return {
                "status": "error",
                "error_type": "authentication_failed",
                "error_message": "LinkedIn access token expired or invalid. Re-authenticate.",
            }
        elif error_code == 429:
            logger.error(f"Rate limit exceeded: {error_message}")
            retry_after = int(e.response.headers.get("Retry-After", 60))
            return {
                "status": "error",
                "error_type": "rate_limit_exceeded",
                "error_message": "LinkedIn API rate limit exceeded. Retry later.",
                "retry_after_seconds": retry_after,
            }
        else:
            logger.error(f"LinkedIn API error: {error_message}")
            return {
                "status": "error",
                "error_type": "api_error",
                "error_message": error_message,
                "error_code": error_code,
            }

    except Exception as e:
        logger.error(f"Failed to publish LinkedIn post: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": "unknown_error",
            "error_message": str(e),
        }


@mcp.tool()
def get_post_status(post_id: str) -> dict:
    """
    Get status of published LinkedIn post.

    Args:
        post_id: LinkedIn post URN

    Returns:
        Dictionary with post status

    Example:
        >>> get_post_status("urn:li:share:123456")
        {'status': 'published', 'post_id': 'urn:li:share:123456', 'visibility': 'PUBLIC'}
    """
    config = get_config()

    try:
        # Get access token from config
        access_token = config.linkedin_access_token

        if not access_token:
            return {
                "status": "error",
                "post_id": post_id,
                "error": "LinkedIn access token not configured",
            }

        # LinkedIn API endpoint
        url = f"https://api.linkedin.com/v2/ugcPosts/{post_id}"

        # Request headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # Get post details
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        post_data = response.json()

        return {
            "status": "published",
            "post_id": post_id,
            "lifecycle_state": post_data.get("lifecycleState"),
            "visibility": post_data.get("visibility", {}).get("com.linkedin.ugc.MemberNetworkVisibility"),
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "status": "not_found",
                "post_id": post_id,
                "error": "Post not found",
            }
        else:
            return {
                "status": "error",
                "post_id": post_id,
                "error": str(e),
            }

    except Exception as e:
        logger.error(f"Failed to get LinkedIn post status: {e}", exc_info=True)
        return {
            "status": "error",
            "post_id": post_id,
            "error": str(e),
        }


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
